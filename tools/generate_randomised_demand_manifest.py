#!/usr/bin/env python3
"""Frozen randomised demand-residue manifest generator.

The live draw is seeded only by the drand League of Entropy public beacon.
Pool snapshots are inputs. Regeneration from the recorded beacon response and
the committed pool files is byte-identical for the manifest JSON, CSV and
Markdown.

An operating-system CSPRNG helper exists for tests and for a refused fallback.
The live command never uses it.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
import tarfile
import time
import urllib.error
import urllib.request
import zipfile
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOL_ROOT = ROOT / "research" / "randomisation" / "pools"
OUT_DIR = ROOT / "research" / "randomisation"
BEACON_DIR = OUT_DIR / "beacon"
BEACON_RESPONSE = BEACON_DIR / "drand-public-latest.response.json"
BEACON_RECORD = BEACON_DIR / "drand-public-latest.record.json"

MANIFEST_STEM = "2026-10-13-demand-residue-manifest-961-1060"
JSON_NAME = f"{MANIFEST_STEM}.json"
CSV_NAME = f"{MANIFEST_STEM}.csv"
MD_NAME = f"{MANIFEST_STEM}.md"
SHA_NAME = f"{MANIFEST_STEM}.sha256"

BEACON_LATEST_URL = "https://api.drand.sh/public/latest"
ALGORITHM = "sha256-counter-fisher-yates-v1"
SCHEMA = "demand-residue-manifest/v1"
FIRST_ATTEMPT = 961
ROW_COUNT = 100
MINIMUM_POOL = 200
USER_AGENT = (
    "softwareHunt-demand-residue/1.0 "
    "(research snapshot; https://github.com/anidiotinclevershoes/softwareHunt)"
)

TYPES = (
    "word",
    "occupation",
    "commodity",
    "location",
    "wikipedia_page",
    "public_record",
    "historical_date",
    "paired_seed",
)
UNDERLYING = TYPES[:7]
POSITIONS = ("A", "B", "C", "D")

# ISO 3166-1 alpha-2 codes for Ireland, the United Kingdom, the EU-27 and the
# additional EEA states. GeoNames uses GB for the United Kingdom and GR for Greece.
IE_UK_EU_EEA = frozenset(
    {
        "AT",
        "BE",
        "BG",
        "HR",
        "CY",
        "CZ",
        "DK",
        "EE",
        "FI",
        "FR",
        "DE",
        "GR",
        "HU",
        "IE",
        "IT",
        "LV",
        "LT",
        "LU",
        "MT",
        "NL",
        "PL",
        "PT",
        "RO",
        "SK",
        "SI",
        "ES",
        "SE",
        "IS",
        "LI",
        "NO",
        "GB",
    }
)

DATE_START = date(1950, 1, 1)
DATE_END = date(2026, 10, 12)

FORBIDDEN_KEYS = frozenset(
    {
        "hypothesis",
        "hypotheses",
        "product",
        "product_idea",
        "proposed_product",
        "verdict",
        "pain",
        "pain_claim",
        "query",
        "queries",
        "research_result",
        "research_results",
        "opportunity",
        "recommendation",
        "willingness_to_pay",
        "outreach",
        "mrr",
    }
)

REQUIRED_ITEM_FIELDS = (
    "source_type",
    "item_id",
    "value",
    "source_organisation",
    "source_url",
    "retrieval_timestamp",
    "licence",
    "raw_file_sha256",
    "filtering_rules",
    "pool_row_count",
    "pool_file",
)


class PoolExhausted(RuntimeError):
    pass


class ManifestError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_dumps(obj: object) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


class Sha256CounterRNG:
    """Deterministic stream: SHA-256(seed || uint64be counter), counter from 0.

    randbelow uses rejection sampling so the residue is unbiased.
    """

    def __init__(self, seed: bytes):
        if not isinstance(seed, (bytes, bytearray)) or len(seed) == 0:
            raise ValueError("seed must be non-empty bytes")
        self.seed = bytes(seed)
        self.counter = 0
        self._buf = b""

    def read(self, n: int) -> bytes:
        if n < 0:
            raise ValueError("n")
        while len(self._buf) < n:
            block = hashlib.sha256(
                self.seed + self.counter.to_bytes(8, "big")
            ).digest()
            self.counter += 1
            self._buf += block
        out, self._buf = self._buf[:n], self._buf[n:]
        return out

    def randbelow(self, limit: int) -> int:
        if limit <= 0:
            raise ValueError("limit must be positive")
        if limit == 1:
            return 0
        nbytes = (limit.bit_length() + 7) // 8
        space = 1 << (nbytes * 8)
        cutoff = space - (space % limit)
        while True:
            value = int.from_bytes(self.read(nbytes), "big")
            if value < cutoff:
                return value % limit


def os_csprng_seed(nbytes: int = 32) -> bytes:
    """Operating-system CSPRNG. Not used for the committed live manifest."""
    if nbytes < 32:
        raise ValueError("nbytes")
    import os

    return os.urandom(nbytes)


def shuffle(rng: Sha256CounterRNG, items: list) -> list:
    out = list(items)
    for i in range(len(out) - 1, 0, -1):
        j = rng.randbelow(i + 1)
        out[i], out[j] = out[j], out[i]
    return out


def seed_from_randomness(randomness_hex: str) -> bytes:
    if not re.fullmatch(r"[0-9a-fA-F]{64}", randomness_hex):
        raise ManifestError("beacon randomness must be 32 bytes of hex")
    return bytes.fromhex(randomness_hex)


def build_type_rows(rng: Sha256CounterRNG) -> list[list[str]]:
    """50 rounds: shuffle the eight types, split 4+4, then shuffle row order."""
    groups: list[list[str]] = []
    for _ in range(50):
        shuffled = shuffle(rng, list(TYPES))
        if sorted(shuffled) != sorted(TYPES) or len(set(shuffled)) != 8:
            raise ManifestError("type shuffle was not a permutation")
        groups.append(shuffled[:4])
        groups.append(shuffled[4:])
    return shuffle(rng, groups)


def _draw(rng: Sha256CounterRNG, remaining: list[dict]) -> dict:
    if not remaining:
        raise PoolExhausted("source pool cannot supply another unique item")
    index = rng.randbelow(len(remaining))
    return remaining.pop(index)


def assign_rows(rng: Sha256CounterRNG, pools: dict[str, list[dict]]) -> list[dict]:
    """Draw unique items. pools values are mutated via copies made here."""
    remaining = {typ: list(pools[typ]) for typ in UNDERLYING}
    rows = []
    for offset, types_in_row in enumerate(build_type_rows(rng)):
        seeds = []
        for position, randomiser_type in zip(POSITIONS, types_in_row):
            if randomiser_type != "paired_seed":
                item = _draw(rng, remaining[randomiser_type])
                seeds.append(
                    {
                        "position": position,
                        "randomiser_type": randomiser_type,
                        "item": item,
                    }
                )
                continue
            order = shuffle(rng, list(UNDERLYING))
            first_type, second_type = order[0], order[1]
            if first_type == second_type:
                raise ManifestError("paired seed types were not distinct")
            first = _draw(rng, remaining[first_type])
            second = _draw(rng, remaining[second_type])
            seeds.append(
                {
                    "position": position,
                    "randomiser_type": "paired_seed",
                    "components": [first, second],
                }
            )
        rows.append(
            {
                "attempt": FIRST_ATTEMPT + offset,
                "status": "UNRESEARCHED",
                "seeds": seeds,
            }
        )
    return rows


def direct_display(randomiser_type: str, value: str) -> str:
    return f"{randomiser_type}: {value}"


def paired_display(first: dict, second: dict) -> str:
    return (
        "paired_seed: "
        f"{first['source_type']}: {first['value']} || "
        f"{second['source_type']}: {second['value']}"
    )


def seed_display(seed: dict) -> str:
    if seed["randomiser_type"] == "paired_seed":
        return paired_display(seed["components"][0], seed["components"][1])
    return direct_display(seed["randomiser_type"], seed["item"]["value"])


def attach_provenance(item: dict, provenance: dict) -> dict:
    typ = item["source_type"]
    base = provenance[typ]
    out = {
        "source_type": typ,
        "item_id": item["item_id"],
        "value": item["value"],
        "source_organisation": base["source_organisation"],
        "source_url": base["source_url"],
        "retrieval_timestamp": base["retrieval_timestamp"],
        "licence": base["licence"],
        "raw_file_sha256": base["raw_file_sha256"],
        "filtering_rules": base["filtering_rules"],
        "pool_row_count": base["row_count"],
        "pool_file": base["pool_file"],
    }
    for key in ("canonical_url", "revision_id", "publication_date", "country_code"):
        if key in item and item[key] not in (None, ""):
            out[key] = item[key]
    return out


def materialise_rows(raw_rows: list[dict], provenance: dict) -> list[dict]:
    rows = []
    for raw in raw_rows:
        seeds = []
        for seed in raw["seeds"]:
            if seed["randomiser_type"] == "paired_seed":
                components = [
                    attach_provenance(component, provenance)
                    for component in seed["components"]
                ]
                seeds.append(
                    {
                        "position": seed["position"],
                        "randomiser_type": "paired_seed",
                        "display": paired_display(components[0], components[1]),
                        "components": components,
                    }
                )
            else:
                item = attach_provenance(seed["item"], provenance)
                seeds.append(
                    {
                        "position": seed["position"],
                        "randomiser_type": seed["randomiser_type"],
                        "display": direct_display(seed["randomiser_type"], item["value"]),
                        "item": item,
                    }
                )
        rows.append(
            {
                "attempt": raw["attempt"],
                "status": "UNRESEARCHED",
                "seeds": seeds,
            }
        )
    return rows


def pool_file_hashes(pool_root: Path = POOL_ROOT) -> dict[str, dict]:
    recorded = {}
    for typ in list(UNDERLYING) + ["paired_seed"]:
        path = pool_root / typ / "provenance.json"
        payload = {
            "provenance_sha256": sha256_bytes(path.read_bytes()),
        }
        pool_path = pool_root / typ / "pool.jsonl"
        if pool_path.exists():
            payload["pool_sha256"] = sha256_bytes(pool_path.read_bytes())
            payload["pool_file"] = pool_path.relative_to(ROOT).as_posix()
        recorded[typ] = payload
    return recorded


def build_manifest(
    randomness_hex: str,
    pools: dict[str, list[dict]],
    provenance: dict,
    beacon: dict,
    pool_hashes: dict,
) -> dict:
    rng = Sha256CounterRNG(seed_from_randomness(randomness_hex))
    raw_rows = assign_rows(rng, pools)
    rows = materialise_rows(raw_rows, provenance)
    return {
        "schema": SCHEMA,
        "algorithm": ALGORITHM,
        "attempt_range": [FIRST_ATTEMPT, FIRST_ATTEMPT + ROW_COUNT - 1],
        "status_policy": "UNRESEARCHED",
        "note": (
            "Frozen randomisation manifest only. No opportunity research, "
            "product idea, hypothesis or verdict is recorded."
        ),
        "randomisation": {
            "algorithm": ALGORITHM,
            "construction": (
                "Fifty rounds. Each round shuffles the eight randomiser types "
                "and splits them into two groups of four. The 100 groups are "
                "shuffled, then numbered 961-1060. Items are drawn without "
                "replacement in attempt order and seed order A-D."
            ),
            "canonical_type_order": list(TYPES),
            "beacon": beacon,
            "pool_files": pool_hashes,
        },
        "rows": rows,
    }


def render_csv(manifest: dict) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["Attempt", "Seed A", "Seed B", "Seed C", "Seed D", "Status"])
    for row in manifest["rows"]:
        displays = [seed["display"] for seed in row["seeds"]]
        writer.writerow([row["attempt"], *displays, row["status"]])
    return buffer.getvalue()


def markdown_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def render_markdown(manifest: dict) -> str:
    beacon = manifest["randomisation"]["beacon"]
    randomness = beacon["randomness"]
    lines = [
        "# Demand residue manifest #961–#1060",
        "",
        "Every row status is UNRESEARCHED.",
        "This table is a frozen randomisation record. It contains no product ideas, hypotheses, pain claims, queries or research results.",
        "",
        f"Beacon URL: {beacon['beacon_url']}",
        f"Beacon round: {beacon['round']}",
        f"Beacon response SHA-256: {beacon['response_sha256']}",
        f"Beacon randomness SHA-256: {sha256_bytes(randomness.encode('utf-8'))}",
        f"Algorithm: {manifest['algorithm']}",
        "",
        "| Attempt | Seed A | Seed B | Seed C | Seed D | Status |",
        "|---:|---|---|---|---|---|",
    ]
    for row in manifest["rows"]:
        cells = [markdown_escape(seed["display"]) for seed in row["seeds"]]
        lines.append(
            f"| {row['attempt']} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} | {row['status']} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_sha256(named_text: dict[str, str]) -> str:
    order = [JSON_NAME, CSV_NAME, MD_NAME]
    lines = []
    for name in order:
        digest = sha256_bytes(named_text[name].encode("utf-8"))
        lines.append(f"{digest}  {name}")
    return "\n".join(lines) + "\n"


def render_outputs(manifest: dict) -> dict[str, str]:
    json_text = canonical_dumps(manifest)
    csv_text = render_csv(manifest)
    md_text = render_markdown(manifest)
    named = {JSON_NAME: json_text, CSV_NAME: csv_text, MD_NAME: md_text}
    named[SHA_NAME] = render_sha256(named)
    return named


def walk_keys(obj: object, found: set[str]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            found.add(str(key))
            walk_keys(value, found)
    elif isinstance(obj, list):
        for value in obj:
            walk_keys(value, found)


def logical_errors(manifest: dict) -> list[str]:
    errors: list[str] = []
    rows = manifest.get("rows")
    if not isinstance(rows, list) or len(rows) != ROW_COUNT:
        errors.append(f"expected {ROW_COUNT} rows")
        return errors
    ids = [row.get("attempt") for row in rows]
    expected = list(range(FIRST_ATTEMPT, FIRST_ATTEMPT + ROW_COUNT))
    if ids != expected:
        errors.append("attempt ids are not contiguous 961-1060 in order")
    counts = {typ: 0 for typ in TYPES}
    used: dict[str, set[str]] = {typ: set() for typ in UNDERLYING}
    keys: set[str] = set()
    walk_keys(manifest, keys)
    banned = sorted(keys & FORBIDDEN_KEYS)
    if banned:
        errors.append("forbidden fields present: " + ", ".join(banned))
    for row in rows:
        if row.get("status") != "UNRESEARCHED":
            errors.append(f"attempt {row.get('attempt')} status is not UNRESEARCHED")
        seeds = row.get("seeds")
        if not isinstance(seeds, list) or len(seeds) != 4:
            errors.append(f"attempt {row.get('attempt')} does not have four seeds")
            continue
        positions = [seed.get("position") for seed in seeds]
        if positions != list(POSITIONS):
            errors.append(f"attempt {row.get('attempt')} seed positions are not A-D")
        types_here = [seed.get("randomiser_type") for seed in seeds]
        if len(set(types_here)) != 4:
            errors.append(f"attempt {row.get('attempt')} randomiser types are not distinct")
        for seed in seeds:
            typ = seed.get("randomiser_type")
            if typ not in counts:
                errors.append(f"unknown randomiser type {typ}")
                continue
            counts[typ] += 1
            if typ == "paired_seed":
                components = seed.get("components")
                if not isinstance(components, list) or len(components) != 2:
                    errors.append(f"attempt {row.get('attempt')} paired seed is not a pair")
                    continue
                if components[0].get("source_type") == components[1].get("source_type"):
                    errors.append(
                        f"attempt {row.get('attempt')} paired components share a type"
                    )
                if seed.get("display") != paired_display(components[0], components[1]):
                    errors.append(f"attempt {row.get('attempt')} paired display mismatch")
                for component in components:
                    _check_item(errors, row.get("attempt"), component, used)
            else:
                item = seed.get("item") or {}
                if item.get("source_type") != typ:
                    errors.append(
                        f"attempt {row.get('attempt')} item type does not match cell"
                    )
                if seed.get("display") != direct_display(typ, item.get("value", "")):
                    errors.append(f"attempt {row.get('attempt')} display mismatch")
                _check_item(errors, row.get("attempt"), item, used)
    for typ, count in counts.items():
        if count != 50:
            errors.append(f"{typ} appears {count} times, expected 50")
    return errors


def _check_item(errors: list[str], attempt: object, item: dict, used: dict[str, set[str]]) -> None:
    typ = item.get("source_type")
    item_id = item.get("item_id")
    if typ not in used:
        errors.append(f"attempt {attempt} has item outside the seven source types")
        return
    if not item_id:
        errors.append(f"attempt {attempt} item has no item_id")
        return
    if item_id in used[typ]:
        errors.append(f"reused {typ} item {item_id}")
    used[typ].add(str(item_id))
    for field in REQUIRED_ITEM_FIELDS:
        if field not in item or item[field] in (None, ""):
            errors.append(f"attempt {attempt} {typ} missing provenance field {field}")
    if typ == "wikipedia_page" and not item.get("canonical_url"):
        errors.append(f"attempt {attempt} wikipedia item has no canonical_url")
    if typ == "wikipedia_page" and not item.get("revision_id"):
        errors.append(f"attempt {attempt} wikipedia item has no revision_id")
    if typ == "public_record":
        if not item.get("canonical_url") or not item.get("publication_date"):
            errors.append(f"attempt {attempt} public record missing url or date")


def _split_unescaped(line: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    i = 0
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line):
            buf.append(line[i])
            buf.append(line[i + 1])
            i += 2
            continue
        if line[i] == "|":
            parts.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(line[i])
        i += 1
    parts.append("".join(buf))
    return parts


def _unescape(value: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(value):
        if value[i] == "\\" and i + 1 < len(value):
            out.append(value[i + 1])
            i += 2
        else:
            out.append(value[i])
            i += 1
    return "".join(out).strip()


def markdown_rows(md_text: str) -> list[dict]:
    rows = []
    for line in md_text.splitlines():
        if not line.startswith("| ") or line.startswith("| Attempt") or line.startswith("|---"):
            continue
        cells = [_unescape(part) for part in _split_unescaped(line)[1:-1]]
        if len(cells) != 6:
            raise ManifestError("markdown row does not have six cells")
        rows.append(
            {
                "attempt": int(cells[0]),
                "seeds": cells[1:5],
                "status": cells[5],
            }
        )
    return rows


def csv_rows(csv_text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = []
    for record in reader:
        rows.append(
            {
                "attempt": int(record["Attempt"]),
                "seeds": [
                    record["Seed A"],
                    record["Seed B"],
                    record["Seed C"],
                    record["Seed D"],
                ],
                "status": record["Status"],
            }
        )
    return rows


def json_logical_rows(manifest: dict) -> list[dict]:
    return [
        {
            "attempt": row["attempt"],
            "seeds": [seed["display"] for seed in row["seeds"]],
            "status": row["status"],
        }
        for row in manifest["rows"]
    ]


def assert_same_logical_rows(manifest: dict, csv_text: str, md_text: str) -> list[str]:
    errors = []
    left = json_logical_rows(manifest)
    try:
        middle = csv_rows(csv_text)
    except Exception as exc:  # noqa: BLE001 - report as validation error
        return [f"csv parse failed: {exc}"]
    try:
        right = markdown_rows(md_text)
    except Exception as exc:  # noqa: BLE001
        return [f"markdown parse failed: {exc}"]
    if left != middle:
        errors.append("JSON and CSV logical rows differ")
    if left != right:
        errors.append("JSON and Markdown logical rows differ")
    return errors


def load_pool_items(pool_root: Path = POOL_ROOT) -> tuple[dict[str, list[dict]], dict]:
    pools: dict[str, list[dict]] = {}
    provenance: dict = {}
    for typ in UNDERLYING:
        prov_path = pool_root / typ / "provenance.json"
        pool_path = pool_root / typ / "pool.jsonl"
        provenance[typ] = json.loads(prov_path.read_text(encoding="utf-8"))
        items = []
        for line in pool_path.read_text(encoding="utf-8").splitlines():
            if line:
                items.append(json.loads(line))
        pools[typ] = items
        if len(items) != provenance[typ]["row_count"]:
            raise ManifestError(f"{typ} row count does not match provenance")
    paired_path = pool_root / "paired_seed" / "provenance.json"
    provenance["paired_seed"] = json.loads(paired_path.read_text(encoding="utf-8"))
    return pools, provenance


def load_beacon_record() -> tuple[dict, bytes]:
    response = BEACON_RESPONSE.read_bytes()
    record = json.loads(BEACON_RECORD.read_text(encoding="utf-8"))
    if sha256_bytes(response) != record["response_sha256"]:
        raise ManifestError("recorded beacon response hash does not match the file")
    parsed = json.loads(response.decode("utf-8"))
    if parsed.get("randomness") != record["randomness"]:
        raise ManifestError("beacon record randomness does not match the response file")
    if parsed.get("round") != record["round"] or parsed.get("signature") != record["signature"]:
        raise ManifestError("beacon record round or signature does not match the response file")
    return record, response


def beacon_public_fields(record: dict) -> dict:
    return {
        "beacon_url": record["beacon_url"],
        "round": record["round"],
        "randomness": record["randomness"],
        "signature": record["signature"],
        "previous_signature": record.get("previous_signature"),
        "retrieval_timestamp": record["retrieval_timestamp"],
        "response_sha256": record["response_sha256"],
        "round_url": record["round_url"],
        "round_response_sha256": record["round_response_sha256"],
        "verification": record["verification"],
    }


def write_outputs(named: dict[str, str], out_dir: Path = OUT_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, text in named.items():
        (out_dir / name).write_text(text, encoding="utf-8", newline="\n")


def generate_from_recorded_beacon() -> dict:
    pools, provenance = load_pool_items()
    for typ in UNDERLYING:
        if len(pools[typ]) < MINIMUM_POOL:
            raise ManifestError(
                f"{typ} pool has {len(pools[typ])} rows; need at least {MINIMUM_POOL}"
            )
    record, _response = load_beacon_record()
    manifest = build_manifest(
        record["randomness"],
        pools,
        provenance,
        beacon_public_fields(record),
        pool_file_hashes(),
    )
    return manifest


def validate_saved_manifest(out_dir: Path = OUT_DIR) -> list[str]:
    errors: list[str] = []
    paths = {name: out_dir / name for name in (JSON_NAME, CSV_NAME, MD_NAME, SHA_NAME)}
    for path in paths.values():
        if not path.exists():
            errors.append(f"missing {path.name}")
    if errors:
        return errors
    texts = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
    expected_sha = render_sha256(
        {name: texts[name] for name in (JSON_NAME, CSV_NAME, MD_NAME)}
    )
    if texts[SHA_NAME] != expected_sha:
        errors.append("sha256 sidecar does not match JSON, CSV and Markdown bytes")
    manifest = json.loads(texts[JSON_NAME])
    regenerated = canonical_dumps(manifest)
    if regenerated != texts[JSON_NAME]:
        errors.append("JSON is not in canonical form")
    errors.extend(logical_errors(manifest))
    errors.extend(assert_same_logical_rows(manifest, texts[CSV_NAME], texts[MD_NAME]))
    if render_csv(manifest) != texts[CSV_NAME]:
        errors.append("CSV renderer does not reproduce the saved CSV")
    if render_markdown(manifest) != texts[MD_NAME]:
        errors.append("Markdown renderer does not reproduce the saved Markdown")
    try:
        fresh = generate_from_recorded_beacon()
    except Exception as exc:  # noqa: BLE001
        errors.append(f"regeneration failed: {exc}")
        return errors
    fresh_outputs = render_outputs(fresh)
    for name in (JSON_NAME, CSV_NAME, MD_NAME, SHA_NAME):
        if fresh_outputs[name] != texts[name]:
            errors.append(f"regeneration did not reproduce {name}")
    return errors


# --- source snapshots -------------------------------------------------------


def http_request(url: str, data: bytes | None = None, headers: dict | None = None, timeout: int = 120) -> bytes:
    req_headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if headers:
        req_headers.update(headers)
    request = urllib.request.Request(url, data=data, headers=req_headers)
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in {429, 500, 502, 503, 504} or attempt == 3:
                detail = exc.read()[:500]
                raise ManifestError(f"HTTP {exc.code} for {url}: {detail!r}") from exc
        except urllib.error.URLError as exc:
            last_error = exc
            if attempt == 3:
                raise ManifestError(f"failed to fetch {url}: {exc}") from exc
        time.sleep(1.5 * (attempt + 1))
    raise ManifestError(f"failed to fetch {url}: {last_error}")


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_dumps(obj), encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8", newline="\n")


def collapse_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def clean_description(value: str) -> str:
    text = collapse_ws(value)
    text = re.sub(r"\(\d+\)", "", text)
    text = re.sub(r"^[\s\-–—]+", "", text)
    text = collapse_ws(text).strip(" -–—:")
    return text


def enumerate_dates() -> list[str]:
    rows = []
    cursor = DATE_START
    while cursor <= DATE_END:
        rows.append(cursor.isoformat())
        cursor += timedelta(days=1)
    return rows


class _HtmlTableParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_cell = False
        self.nested = 0
        self.parts: list[str] = []
        self.row: list[str] = []
        self.in_row = False
        self.table_rows: list[list[str]] = []
        self.tables: list[list[list[str]]] = []
        self.in_table = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            if self.in_cell:
                self.nested += 1
            else:
                self.in_table = True
                self.table_rows = []
            return
        if self.nested or not self.in_table:
            return
        if tag == "tr" and not self.in_row:
            self.in_row = True
            self.row = []
        elif tag == "td" and self.in_row and not self.in_cell:
            self.in_cell = True
            self.parts = []

    def handle_endtag(self, tag):
        if tag == "table":
            if self.nested:
                self.nested -= 1
                return
            self.in_table = False
            self.tables.append(self.table_rows)
            self.table_rows = []
            return
        if self.nested or not self.in_table:
            return
        if tag == "td" and self.in_cell:
            self.in_cell = False
            self.row.append(collapse_ws("".join(self.parts)))
        elif tag == "tr" and self.in_row:
            self.in_row = False
            if self.row:
                self.table_rows.append(self.row)

    def handle_data(self, data):
        if self.in_cell and self.nested == 0:
            self.parts.append(data)


def _is_nomenclature_table(table: list[list[str]]) -> bool:
    for row in table[:6]:
        blob = " ".join(row).casefold()
        if (
            "cn code" in blob
            and "description" in blob
            and "conventional rate of duty" in blob
            and "supplementary unit" in blob
        ):
            return True
    return False


def parse_cn_html(html_text: str) -> list[dict]:
    parser = _HtmlTableParser()
    parser.feed(html_text)
    found: dict[str, str] = {}
    order: list[str] = []
    for table in parser.tables:
        if not _is_nomenclature_table(table):
            continue
        for row in table:
            if len(row) < 2:
                continue
            code = re.sub(r"\s+", "", row[0].replace("\xa0", ""))
            if not re.fullmatch(r"\d{4}(\d{2}){0,2}", code):
                continue
            description = clean_description(row[1])
            if not description or code in found:
                continue
            found[code] = description
            order.append(code)
    rows = [
        {
            "item_id": code,
            "source_type": "commodity",
            "value": f"{code} {found[code]}",
        }
        for code in order
    ]
    rows.sort(key=lambda item: item["item_id"])
    return rows


def parse_wordnet_index(index_text: str) -> list[dict]:
    found: dict[str, dict] = {}
    for line in index_text.splitlines():
        if not line or line.startswith(" "):
            continue
        parts = line.split()
        if len(parts) < 2 or parts[1] != "n":
            continue
        lemma = parts[0].strip()
        if not lemma or " " in lemma:
            continue
        value = collapse_ws(lemma.replace("_", " "))
        if not value:
            continue
        found[lemma] = {
            "item_id": lemma,
            "source_type": "word",
            "value": value,
        }
    return [found[key] for key in sorted(found)]


def parse_geonames(text: str) -> list[dict]:
    found: dict[str, dict] = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 9:
            continue
        geoname_id, name, _ascii, _alts, _lat, _lon, feature_class, _feature, country = parts[:9]
        if feature_class != "P" or country not in IE_UK_EU_EEA:
            continue
        if not re.fullmatch(r"\d+", geoname_id):
            continue
        name = collapse_ws(name)
        if not name:
            continue
        found[geoname_id] = {
            "country_code": country,
            "item_id": geoname_id,
            "source_type": "location",
            "value": f"{name}, {country}",
        }
    return [found[key] for key in sorted(found, key=int)]


def parse_esco_pages(pages: list[bytes]) -> list[dict]:
    found: dict[str, dict] = {}
    for raw in pages:
        payload = json.loads(raw.decode("utf-8"))
        for result in payload.get("_embedded", {}).get("results", []):
            uri = result.get("uri") or ""
            label = ""
            preferred = result.get("preferredLabel")
            if isinstance(preferred, dict):
                label = preferred.get("en") or ""
            elif isinstance(preferred, str):
                label = preferred
            label = collapse_ws(str(label))
            if not uri or not label:
                continue
            found[uri] = {
                "canonical_url": uri,
                "item_id": uri,
                "source_type": "occupation",
                "value": label,
            }
    return [found[key] for key in sorted(found)]


def parse_wikipedia_pages(pages: list[bytes]) -> list[dict]:
    found: dict[str, dict] = {}
    for raw in pages:
        payload = json.loads(raw.decode("utf-8"))
        query = payload.get("query") or {}
        for page in (query.get("pages") or {}).values():
            if page.get("ns") not in (0, None) and page.get("ns") != 0:
                continue
            if page.get("ns", 0) != 0 or "missing" in page:
                continue
            page_id = page.get("pageid")
            title = collapse_ws(str(page.get("title") or ""))
            revisions = page.get("revisions") or []
            revision_id = None
            if revisions and isinstance(revisions[0], dict):
                revision_id = revisions[0].get("revid")
            revision_id = revision_id or page.get("lastrevid")
            url = page.get("canonicalurl") or page.get("fullurl") or ""
            if not page_id or not title or not revision_id or not url:
                continue
            item_id = str(page_id)
            found[item_id] = {
                "canonical_url": url,
                "item_id": item_id,
                "revision_id": int(revision_id),
                "source_type": "wikipedia_page",
                "value": title,
            }
    return [found[key] for key in sorted(found, key=int)]


def _pick_local_text(value: object) -> tuple[str, str]:
    if isinstance(value, str) and collapse_ws(value):
        return collapse_ws(value), "und"
    if isinstance(value, dict):
        english = value.get("eng")
        if isinstance(english, str) and collapse_ws(english):
            return collapse_ws(english), "eng"
        if isinstance(english, list):
            for entry in english:
                if isinstance(entry, str) and collapse_ws(entry):
                    return collapse_ws(entry), "eng"
        for lang in sorted(value):
            entry = value[lang]
            if isinstance(entry, str) and collapse_ws(entry):
                return collapse_ws(entry), lang
            if isinstance(entry, list):
                for item in entry:
                    if isinstance(item, str) and collapse_ws(item):
                        return collapse_ws(item), lang
    return "", ""


def pick_ted_title(notice: dict) -> str:
    for field in ("notice-title", "title-proc", "title-lot"):
        text, _lang = _pick_local_text(notice.get(field))
        if text:
            return text
    return ""


def parse_ted_pages(pages: list[bytes]) -> list[dict]:
    found: dict[str, dict] = {}
    for raw in pages:
        payload = json.loads(raw.decode("utf-8"))
        for notice in payload.get("notices") or []:
            publication = str(notice.get("publication-number") or "")
            if not re.fullmatch(r"\d+-\d{4}", publication):
                continue
            title = pick_ted_title(notice)
            published = str(notice.get("publication-date") or "")
            date_match = re.match(r"(\d{4}-\d{2}-\d{2})", published)
            if not title or not date_match:
                continue
            links = notice.get("links") or {}
            html = (links.get("html") or {}) if isinstance(links, dict) else {}
            url = ""
            if isinstance(html, dict):
                url = html.get("ENG") or ""
            if not url:
                url = f"https://ted.europa.eu/en/notice/-/detail/{publication}"
            number, year = publication.split("-")
            found[publication] = {
                "canonical_url": url,
                "item_id": publication,
                "publication_date": date_match.group(1),
                "sort_key": (int(year), int(number)),
                "source_type": "public_record",
                "value": title,
            }
    rows = [found[key] for key in sorted(found, key=lambda item: found[item]["sort_key"])]
    for row in rows:
        row.pop("sort_key")
    return rows


def _save_concat(raw_dir: Path, pages: list[bytes]) -> str:
    raw_dir.mkdir(parents=True, exist_ok=True)
    blob = b"".join(pages)
    (raw_dir / "concatenated-responses.bin").write_bytes(blob)
    lengths = "\n".join(str(len(page)) for page in pages) + "\n"
    (raw_dir / "lengths.txt").write_text(lengths, encoding="utf-8", newline="\n")
    return sha256_bytes(blob)


def _read_concat(raw_dir: Path) -> list[bytes]:
    blob = (raw_dir / "concatenated-responses.bin").read_bytes()
    lengths = [
        int(line)
        for line in (raw_dir / "lengths.txt").read_text(encoding="utf-8").splitlines()
        if line
    ]
    pages = []
    cursor = 0
    for length in lengths:
        pages.append(blob[cursor : cursor + length])
        cursor += length
    if cursor != len(blob):
        raise ManifestError(f"concatenated responses in {raw_dir} do not match lengths")
    return pages


def _base_provenance(
    *,
    source_type: str,
    organisation: str,
    url: str,
    retrieved: str,
    licence: str,
    raw_hash: str,
    rules: str,
    row_count: int,
    pool_file: str,
    extra: dict | None = None,
) -> dict:
    payload = {
        "filtering_rules": rules,
        "licence": licence,
        "pool_file": pool_file,
        "raw_file_sha256": raw_hash,
        "retrieval_timestamp": retrieved,
        "row_count": row_count,
        "source_organisation": organisation,
        "source_type": source_type,
        "source_url": url,
    }
    if extra:
        payload.update(extra)
    return payload


def build_word_pool(retrieved: str | None = None) -> None:
    url = "https://wordnetcode.princeton.edu/wn3.1.dict.tar.gz"
    retrieved = retrieved or utc_now()
    print("fetch wordnet", flush=True)
    blob = http_request(url)
    raw_dir = POOL_ROOT / "word" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "wn3.1.dict.tar.gz").write_bytes(blob)
    items = parse_wordnet_index(_wordnet_index_text(blob))
    _finish_pool(
        "word",
        items,
        _base_provenance(
            source_type="word",
            organisation="Princeton University WordNet",
            url=url,
            retrieved=retrieved,
            licence=(
                "WordNet 3.1 licence. Free to use with the attribution and "
                "licence terms distributed at "
                "https://wordnet.princeton.edu/license-and-commercial-use "
                "and in the database archive."
            ),
            raw_hash=sha256_bytes(blob),
            rules=(
                "Use dict/index.noun from the WordNet 3.1 database archive. "
                "Skip blank and header lines. Keep lines whose part of speech is n. "
                "Drop malformed lines and exact duplicate lemmas. "
                "Display value replaces underscores with spaces and collapses whitespace. "
                "No subjective removal."
            ),
            row_count=len(items),
            pool_file="research/randomisation/pools/word/pool.jsonl",
        ),
    )


def _wordnet_index_text(blob: bytes) -> str:
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as archive:
        member = next(
            (info for info in archive.getmembers() if info.name.endswith("index.noun")),
            None,
        )
        if member is None:
            raise ManifestError("WordNet archive has no index.noun")
        extracted = archive.extractfile(member)
        if extracted is None:
            raise ManifestError("WordNet index.noun could not be read")
        data = extracted.read()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def build_occupation_pool(retrieved: str | None = None) -> None:
    retrieved = retrieved or utc_now()
    print("fetch esco", flush=True)
    pages: list[bytes] = []
    page_index = 0
    total = None
    while True:
        url = (
            "https://ec.europa.eu/esco/api/search?"
            "language=en&type=occupation&limit=100"
            f"&offset={page_index}&selectedVersion=v1.2.0"
        )
        blob = http_request(url, headers={"Accept": "application/json"})
        pages.append(blob)
        payload = json.loads(blob.decode("utf-8"))
        total = int(payload["total"])
        returned = len(payload.get("_embedded", {}).get("results", []))
        print(f"  esco page {page_index} returned {returned} / {total}", flush=True)
        page_index += 1
        if returned == 0 or page_index * 100 >= total:
            break
        if page_index > 100:
            raise ManifestError("ESCO pagination exceeded 100 pages")
    items = parse_esco_pages(pages)
    raw_hash = _save_concat(POOL_ROOT / "occupation" / "raw", pages)
    _finish_pool(
        "occupation",
        items,
        _base_provenance(
            source_type="occupation",
            organisation="European Commission, ESCO",
            url=(
                "https://ec.europa.eu/esco/api/search?language=en&type=occupation"
                "&limit=100&offset=0&selectedVersion=v1.2.0"
            ),
            retrieved=retrieved,
            licence=(
                "European Commission ESCO v1.2.0. Free of charge for reuse "
                "with source acknowledgement. "
                "https://esco.ec.europa.eu/en/use-esco/download"
            ),
            raw_hash=raw_hash,
            rules=(
                "Read ESCO v1.2.0 from the official occupation search API. "
                "With selectedVersion=v1.2.0 the offset parameter is a page index "
                "at limit=100. Request pages until the reported total is consumed. "
                "Keep the English preferredLabel. Drop blank labels, missing URIs "
                "and exact duplicate URIs. No subjective removal. "
                "Raw file is the concatenation of unmodified responses."
            ),
            row_count=len(items),
            pool_file="research/randomisation/pools/occupation/pool.jsonl",
            extra={"api_pages": len(pages), "api_total_reported": total},
        ),
    )


def build_commodity_pool(retrieved: str | None = None) -> None:
    url = (
        "http://publications.europa.eu/resource/cellar/"
        "c3c0d050-b5fa-11f0-b37f-01aa75ed71a1.0006.03/DOC_1"
    )
    retrieved = retrieved or utc_now()
    print("fetch combined nomenclature", flush=True)
    blob = http_request(url, timeout=180)
    raw_dir = POOL_ROOT / "commodity" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "L_202501926EN.html").write_bytes(blob)
    items = parse_cn_html(blob.decode("utf-8"))
    _finish_pool(
        "commodity",
        items,
        _base_provenance(
            source_type="commodity",
            organisation="Publications Office of the European Union / European Commission",
            url="http://publications.europa.eu/resource/oj/L_202501926.ENG.xhtml",
            retrieved=retrieved,
            licence=(
                "Official Journal of the European Union, L series, 2025/1926, English. "
                "Commission Implementing Regulation (EU) 2025/1926. Public legal text. "
                "Reuse of Commission documents is subject to Commission Decision 2011/833/EU."
            ),
            raw_hash=sha256_bytes(blob),
            rules=(
                "Parse the English XHTML of OJ L 2025/1926. Keep rows only from tables "
                "whose header contains CN code, Description, Conventional rate of duty "
                "and Supplementary unit. Keep 4, 6 and 8 digit codes. "
                "Collapse whitespace, strip numeric footnote markers and leading hierarchy dashes. "
                "Drop blank descriptions and exact duplicate codes. "
                "Value is the code, one space, then the cleaned description. "
                "No subjective removal."
            ),
            row_count=len(items),
            pool_file="research/randomisation/pools/commodity/pool.jsonl",
            extra={
                "legal_act": "Commission Implementing Regulation (EU) 2025/1926",
                "download_url": url,
            },
        ),
    )


def build_location_pool(retrieved: str | None = None) -> None:
    retrieved = retrieved or utc_now()
    print("fetch geonames", flush=True)
    url = "https://download.geonames.org/export/dump/cities15000.zip"
    blob = http_request(url)
    readme = http_request("https://download.geonames.org/export/dump/readme.txt")
    raw_dir = POOL_ROOT / "location" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "cities15000.zip").write_bytes(blob)
    (raw_dir / "readme.txt").write_bytes(readme)
    items = parse_geonames(_geonames_text(blob))
    dataset = "cities15000.zip"
    if len(items) < MINIMUM_POOL:
        url = "https://download.geonames.org/export/dump/cities500.zip"
        blob = http_request(url)
        (raw_dir / "cities500.zip").write_bytes(blob)
        items = parse_geonames(_geonames_text(blob))
        dataset = "cities500.zip"
    _finish_pool(
        "location",
        items,
        _base_provenance(
            source_type="location",
            organisation="GeoNames",
            url=f"https://download.geonames.org/export/dump/{dataset}",
            retrieved=retrieved,
            licence=(
                "GeoNames data is licensed under Creative Commons Attribution 4.0. "
                "https://creativecommons.org/licenses/by/4.0/ "
                "https://www.geonames.org/"
            ),
            raw_hash=sha256_bytes(blob),
            rules=(
                f"Use the published GeoNames {dataset} populated-place dump. "
                "Keep feature class P. Keep country codes for Ireland, the United "
                "Kingdom (GB), the EU-27 and the other EEA states (IS, LI, NO). "
                "Drop short rows, non-numeric ids, blank names and exact duplicate geoname ids. "
                "Value is the place name, a comma, the country code. "
                "cities500.zip is used only if cities15000.zip yields fewer than 200 rows. "
                "No subjective removal."
            ),
            row_count=len(items),
            pool_file="research/randomisation/pools/location/pool.jsonl",
            extra={
                "dataset_file": dataset,
                "readme_sha256": sha256_bytes(readme),
                "country_codes": sorted(IE_UK_EU_EEA),
            },
        ),
    )


def _geonames_text(blob: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        name = next(info for info in archive.namelist() if info.endswith(".txt"))
        return archive.read(name).decode("utf-8")


def build_wikipedia_pool(retrieved: str | None = None) -> None:
    retrieved = retrieved or utc_now()
    print("fetch wikipedia", flush=True)
    pages: list[bytes] = []
    found: dict[str, dict] = {}
    attempts = 0
    while len(found) < 300 and attempts < 40:
        attempts += 1
        url = (
            "https://en.wikipedia.org/w/api.php?action=query&format=json"
            "&generator=random&grnnamespace=0&grnlimit=20"
            "&prop=info|revisions&rvprop=ids&inprop=url&redirects=1"
        )
        blob = http_request(url, headers={"Accept": "application/json"})
        pages.append(blob)
        for item in parse_wikipedia_pages([blob]):
            found[item["item_id"]] = item
        print(f"  wikipedia unique {len(found)}", flush=True)
        time.sleep(0.2)
    items = [found[key] for key in sorted(found, key=int)]
    raw_hash = _save_concat(POOL_ROOT / "wikipedia_page" / "raw", pages)
    _finish_pool(
        "wikipedia_page",
        items,
        _base_provenance(
            source_type="wikipedia_page",
            organisation="Wikimedia Foundation, English Wikipedia",
            url=(
                "https://en.wikipedia.org/w/api.php?action=query&format=json"
                "&generator=random&grnnamespace=0&grnlimit=20"
                "&prop=info|revisions&rvprop=ids&inprop=url&redirects=1"
            ),
            retrieved=retrieved,
            licence=(
                "English Wikipedia content is available under CC BY-SA 4.0. "
                "This snapshot stores page id, title, revision id and canonical URL only, "
                "not article text. https://creativecommons.org/licenses/by-sa/4.0/"
            ),
            raw_hash=raw_hash,
            rules=(
                "Call the MediaWiki random generator for namespace 0 until 300 unique "
                "pages are stored or 40 responses are received. "
                "Keep page id, title, revision id and canonical URL. "
                "Drop missing, non-namespace-0, blank or duplicate page ids. "
                "No subjective removal. The manifest later draws from this frozen snapshot."
            ),
            row_count=len(items),
            pool_file="research/randomisation/pools/wikipedia_page/pool.jsonl",
            extra={"api_responses": len(pages)},
        ),
    )


def build_public_record_pool(retrieved: str | None = None) -> None:
    retrieved = retrieved or utc_now()
    print("fetch ted", flush=True)
    pages: list[bytes] = []
    found: dict[str, dict] = {}
    for page in range(1, 21):
        if len(found) >= 300:
            break
        body = json.dumps(
            {
                "query": "notice-type=cn-standard AND PD>=20260101",
                "fields": [
                    "publication-number",
                    "publication-date",
                    "notice-title",
                    "title-proc",
                    "title-lot",
                    "links",
                    "notice-type",
                ],
                "limit": 50,
                "page": page,
                "scope": "ALL",
                "paginationMode": "PAGE_NUMBER",
            }
        ).encode("utf-8")
        blob = http_request(
            "https://api.ted.europa.eu/v3/notices/search",
            data=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        pages.append(blob)
        for item in parse_ted_pages([blob]):
            found.setdefault(item["item_id"], item)
        print(f"  ted page {page} unique {len(found)}", flush=True)
    items = list(found.values())
    items.sort(key=lambda item: _ted_sort(item["item_id"]))
    raw_hash = _save_concat(POOL_ROOT / "public_record" / "raw", pages)
    _finish_pool(
        "public_record",
        items,
        _base_provenance(
            source_type="public_record",
            organisation="Publications Office of the European Union, Tenders Electronic Daily",
            url="https://api.ted.europa.eu/v3/notices/search",
            retrieved=retrieved,
            licence=(
                "TED public procurement notices published by the Publications Office. "
                "Reuse with attribution under the Publications Office / Commission reuse policy. "
                "https://ted.europa.eu/"
            ),
            raw_hash=raw_hash,
            rules=(
                "Fixed expert query: notice-type=cn-standard AND PD>=20260101. "
                "Read API pages in order until 300 unique publication numbers are kept "
                "or 20 pages are read. Require publication number N-YYYY, a non-blank title "
                "and a YYYY-MM-DD publication date. Title preference is English notice-title, "
                "then English procedure/lot title, then the lexicographically first available language. "
                "Canonical URL is the English HTML link. Drop malformed rows and exact duplicate notice ids. "
                "No subjective removal. Manifest sampling is a later beacon draw from this snapshot."
            ),
            row_count=len(items),
            pool_file="research/randomisation/pools/public_record/pool.jsonl",
            extra={
                "query": "notice-type=cn-standard AND PD>=20260101",
                "api_pages": len(pages),
            },
        ),
    )


def _ted_sort(publication: str) -> tuple[int, int]:
    number, year = publication.split("-")
    return (int(year), int(number))


def build_historical_date_pool(retrieved: str | None = None) -> None:
    retrieved = retrieved or utc_now()
    dates = enumerate_dates()
    raw_dir = POOL_ROOT / "historical_date" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_text = "\n".join(dates) + "\n"
    (raw_dir / "dates.txt").write_text(raw_text, encoding="utf-8", newline="\n")
    items = [
        {"item_id": day, "source_type": "historical_date", "value": day}
        for day in dates
    ]
    _finish_pool(
        "historical_date",
        items,
        _base_provenance(
            source_type="historical_date",
            organisation="Proleptic Gregorian calendar enumeration",
            url="mechanical:1950-01-01/2026-10-12",
            retrieved=retrieved,
            licence="Calendar dates are uncopyrightable facts. No external dataset licence.",
            raw_hash=sha256_bytes(raw_text.encode("utf-8")),
            rules=(
                "Enumerate every proleptic Gregorian date from 1950-01-01 through "
                "2026-10-12 inclusive, using Python datetime. "
                "No external file and no subjective removal."
            ),
            row_count=len(items),
            pool_file="research/randomisation/pools/historical_date/pool.jsonl",
        ),
    )


def build_paired_seed_record(retrieved: str) -> None:
    component_counts = {}
    for typ in UNDERLYING:
        prov = json.loads((POOL_ROOT / typ / "provenance.json").read_text(encoding="utf-8"))
        component_counts[typ] = prov["row_count"]
    payload = {
        "component_pool_row_counts": component_counts,
        "filtering_rules": (
            "paired_seed has no independent item list. Each paired cell draws two "
            "unused items from two different pools among the first seven types. "
            "Those items are consumed and cannot appear again. "
            "The component order is the first two types after a shuffle of the seven."
        ),
        "licence": "Inherits the licence of each component item.",
        "pool_file": "",
        "raw_file_sha256": "",
        "retrieval_timestamp": retrieved,
        "row_count": None,
        "source_organisation": "Derived from the seven frozen source pools",
        "source_type": "paired_seed",
        "source_url": "derived:research/randomisation/pools",
    }
    # Empty hash fields fail required-item checks if copied onto components.
    # Paired cells copy component provenance, not this record, onto items.
    # Keep the pool-level record explicit that there is no raw file.
    payload["raw_file_sha256"] = "not-applicable"
    write_json(POOL_ROOT / "paired_seed" / "provenance.json", payload)


def _finish_pool(typ: str, items: list[dict], provenance: dict) -> None:
    if len(items) < MINIMUM_POOL:
        raise ManifestError(
            f"{typ} produced {len(items)} rows; need at least {MINIMUM_POOL}"
        )
    ids = [item["item_id"] for item in items]
    if len(ids) != len(set(ids)):
        raise ManifestError(f"{typ} snapshot contains duplicate ids")
    provenance["row_count"] = len(items)
    write_jsonl(POOL_ROOT / typ / "pool.jsonl", items)
    write_json(POOL_ROOT / typ / "provenance.json", provenance)
    print(f"pool {typ}: {len(items)}", flush=True)


def rebuild_checks() -> list[str]:
    """Re-parse committed raw files and compare them with pool.jsonl."""
    errors = []
    word_blob = (POOL_ROOT / "word" / "raw" / "wn3.1.dict.tar.gz").read_bytes()
    errors.extend(
        _compare_pool("word", parse_wordnet_index(_wordnet_index_text(word_blob)))
    )
    errors.extend(
        _compare_pool(
            "occupation",
            parse_esco_pages(_read_concat(POOL_ROOT / "occupation" / "raw")),
        )
    )
    html = (POOL_ROOT / "commodity" / "raw" / "L_202501926EN.html").read_text(encoding="utf-8")
    errors.extend(_compare_pool("commodity", parse_cn_html(html)))
    location_prov = json.loads(
        (POOL_ROOT / "location" / "provenance.json").read_text(encoding="utf-8")
    )
    dataset = location_prov["dataset_file"]
    geo_blob = (POOL_ROOT / "location" / "raw" / dataset).read_bytes()
    errors.extend(_compare_pool("location", parse_geonames(_geonames_text(geo_blob))))
    errors.extend(
        _compare_pool(
            "wikipedia_page",
            parse_wikipedia_pages(_read_concat(POOL_ROOT / "wikipedia_page" / "raw")),
        )
    )
    errors.extend(
        _compare_pool(
            "public_record",
            parse_ted_pages(_read_concat(POOL_ROOT / "public_record" / "raw")),
        )
    )
    dates = (POOL_ROOT / "historical_date" / "raw" / "dates.txt").read_text(encoding="utf-8").splitlines()
    items = [
        {"item_id": day, "source_type": "historical_date", "value": day}
        for day in dates
        if day
    ]
    errors.extend(_compare_pool("historical_date", items))
    return errors


def _compare_pool(typ: str, items: list[dict]) -> list[str]:
    path = POOL_ROOT / typ / "pool.jsonl"
    expected = "\n".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) for row in items
    ) + "\n"
    actual = path.read_text(encoding="utf-8")
    if actual != expected:
        return [f"{typ} pool.jsonl does not rebuild from its raw snapshot"]
    return []


def fetch_and_verify_beacon() -> dict:
    retrieved = utc_now()
    print("fetch drand latest", flush=True)
    body = http_request(BEACON_LATEST_URL, headers={"Accept": "application/json"})
    try:
        parsed = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ManifestError("drand latest response was not JSON") from exc
    for field in ("round", "randomness", "signature"):
        if field not in parsed:
            raise ManifestError(f"drand latest response missing {field}")
    randomness = str(parsed["randomness"])
    signature = str(parsed["signature"])
    if not re.fullmatch(r"[0-9a-fA-F]{64}", randomness):
        raise ManifestError("drand randomness failed verification")
    if not re.fullmatch(r"[0-9a-fA-F]+", signature):
        raise ManifestError("drand signature failed verification")
    round_number = parsed["round"]
    if not isinstance(round_number, int):
        raise ManifestError("drand round was not an integer")
    round_url = f"https://api.drand.sh/public/{round_number}"
    round_body = http_request(round_url, headers={"Accept": "application/json"})
    round_parsed = json.loads(round_body.decode("utf-8"))
    if (
        round_parsed.get("round") != round_number
        or round_parsed.get("randomness") != randomness
        or round_parsed.get("signature") != signature
    ):
        raise ManifestError(
            "drand round endpoint did not match the latest beacon; refusing to draw"
        )
    record = {
        "beacon_url": BEACON_LATEST_URL,
        "previous_signature": parsed.get("previous_signature"),
        "randomness": randomness,
        "response_sha256": sha256_bytes(body),
        "retrieval_timestamp": retrieved,
        "round": round_number,
        "round_response_sha256": sha256_bytes(round_body),
        "round_url": round_url,
        "signature": signature,
        "verification": (
            "HTTPS GET of /public/latest matched HTTPS GET of /public/{round} "
            "on round, randomness and signature."
        ),
    }
    BEACON_DIR.mkdir(parents=True, exist_ok=True)
    BEACON_RESPONSE.write_bytes(body)
    write_json(BEACON_RECORD, record)
    return record


def fetch_pools() -> None:
    steps = [
        ("word", build_word_pool),
        ("occupation", build_occupation_pool),
        ("commodity", build_commodity_pool),
        ("location", build_location_pool),
        ("wikipedia_page", build_wikipedia_pool),
        ("public_record", build_public_record_pool),
        ("historical_date", build_historical_date_pool),
    ]
    pending = [typ for typ, _fn in steps if not (POOL_ROOT / typ / "pool.jsonl").exists()]
    if not pending and (POOL_ROOT / "paired_seed" / "provenance.json").exists():
        raise SystemExit("pool snapshots already exist; refusing to redraw source pools")
    for typ, builder in steps:
        if (POOL_ROOT / typ / "pool.jsonl").exists():
            print(f"keep existing {typ} snapshot", flush=True)
            continue
        builder(utc_now())
    build_paired_seed_record(utc_now())
    errors = rebuild_checks()
    if errors:
        raise SystemExit("pool rebuild failed: " + "; ".join(errors))
    print("pools frozen and rebuild checks passed", flush=True)


def generate_live() -> None:
    if (OUT_DIR / JSON_NAME).exists():
        raise SystemExit("live manifest already exists; refusing to redraw")
    test_path = ROOT / "tools" / "test_randomised_demand_manifest.py"
    import subprocess

    print("running dummy-seed tests before beacon retrieval", flush=True)
    completed = subprocess.run([sys.executable, str(test_path)], check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    if not BEACON_RESPONSE.exists():
        fetch_and_verify_beacon()
    else:
        print("reusing already recorded beacon response", flush=True)
    manifest = generate_from_recorded_beacon()
    errors = logical_errors(manifest)
    if errors:
        raise SystemExit("generated manifest failed validation: " + "; ".join(errors))
    named = render_outputs(manifest)
    write_outputs(named)
    errors = validate_saved_manifest()
    if errors:
        raise SystemExit("saved manifest failed validation: " + "; ".join(errors))
    record, _response = load_beacon_record()
    counts = {typ: 0 for typ in TYPES}
    for row in manifest["rows"]:
        for seed in row["seeds"]:
            counts[seed["randomiser_type"]] += 1
    print("live manifest written", flush=True)
    print(f"beacon round {record['round']}", flush=True)
    print(
        "randomness sha256 "
        + sha256_bytes(record["randomness"].encode("utf-8")),
        flush=True,
    )
    print("type counts " + json.dumps(counts, sort_keys=True), flush=True)


def validate_command() -> None:
    errors = validate_saved_manifest()
    rebuild = rebuild_checks()
    errors.extend(rebuild)
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    manifest = json.loads((OUT_DIR / JSON_NAME).read_text(encoding="utf-8"))
    counts = {typ: 0 for typ in TYPES}
    for row in manifest["rows"]:
        for seed in row["seeds"]:
            counts[seed["randomiser_type"]] += 1
    record, _response = load_beacon_record()
    summary = {
        "attempts": [FIRST_ATTEMPT, FIRST_ATTEMPT + ROW_COUNT - 1],
        "beacon_round": record["round"],
        "randomness_sha256": sha256_bytes(record["randomness"].encode("utf-8")),
        "response_sha256": record["response_sha256"],
        "rows": len(manifest["rows"]),
        "status": "UNRESEARCHED",
        "type_counts": counts,
        "validation": "passed",
    }
    print(canonical_dumps(summary), end="")


def main(argv: list[str]) -> None:
    if len(argv) != 2 or argv[1] not in {
        "fetch-pools",
        "generate-live",
        "validate",
    }:
        raise SystemExit(
            "usage: generate_randomised_demand_manifest.py "
            "{fetch-pools|generate-live|validate}"
        )
    command = argv[1]
    if command == "fetch-pools":
        fetch_pools()
    elif command == "generate-live":
        generate_live()
    else:
        validate_command()


if __name__ == "__main__":
    main(sys.argv)
