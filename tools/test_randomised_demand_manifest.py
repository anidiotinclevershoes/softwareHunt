#!/usr/bin/env python3
"""Fixed-seed tests for the demand-residue manifest generator.

These tests do not contact the network and do not draw the live manifest.
"""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate_randomised_demand_manifest as gen

# Canonical JSON SHA-256 of the dummy manifest for seed 0001... The value is
# locked after the generator's render rules. A change here means the draw changed.
GOLDEN_DUMMY_JSON_SHA256 = (
    "ca923b3e2f3f735edbac339e8040ca1e0caa099f09f99bdc8d5be15904d34986"
)


def fail(message: str) -> None:
    raise SystemExit(message)


def dummy_pools(size: int = 160, value_suffix: str = "") -> dict:
    pools = {}
    for typ in gen.UNDERLYING:
        pools[typ] = [
            {
                "item_id": f"{typ}-{index:04d}",
                "source_type": typ,
                "value": f"{typ}-{index:04d}{value_suffix}",
                **_extra(typ, index),
            }
            for index in range(size)
        ]
    return pools


def _extra(typ: str, index: int) -> dict:
    if typ == "wikipedia_page":
        return {
            "canonical_url": f"https://en.wikipedia.org/wiki/Item_{index}",
            "revision_id": 1000 + index,
        }
    if typ == "public_record":
        return {
            "canonical_url": f"https://ted.europa.eu/en/notice/-/detail/{index}-2026",
            "publication_date": "2026-01-02",
        }
    if typ == "occupation":
        return {"canonical_url": f"http://data.europa.eu/esco/occupation/{index}"}
    if typ == "location":
        return {"country_code": "IE"}
    return {}


def dummy_provenance(pools: dict) -> dict:
    provenance = {}
    for typ, items in pools.items():
        provenance[typ] = {
            "filtering_rules": "dummy mechanical filter",
            "licence": "dummy",
            "pool_file": f"dummy/{typ}.jsonl",
            "raw_file_sha256": "a" * 64,
            "retrieval_timestamp": "2026-10-13T00:00:00Z",
            "row_count": len(items),
            "source_organisation": "dummy",
            "source_type": typ,
            "source_url": f"https://example.invalid/{typ}",
        }
    provenance["paired_seed"] = {
        "filtering_rules": "derived",
        "licence": "derived",
        "pool_file": "",
        "raw_file_sha256": "not-applicable",
        "retrieval_timestamp": "2026-10-13T00:00:00Z",
        "row_count": None,
        "source_organisation": "derived",
        "source_type": "paired_seed",
        "source_url": "derived",
    }
    return provenance


def dummy_beacon() -> dict:
    return {
        "beacon_url": "https://api.drand.sh/public/latest",
        "previous_signature": None,
        "randomness": "11" * 32,
        "response_sha256": "b" * 64,
        "retrieval_timestamp": "2026-10-13T00:00:00Z",
        "round": 1,
        "round_response_sha256": "c" * 64,
        "round_url": "https://api.drand.sh/public/1",
        "signature": "d" * 96,
        "verification": "dummy",
    }


def manifest_for(seed_byte: int, pools: dict | None = None) -> dict:
    pools = pools or dummy_pools()
    randomness = f"{seed_byte:02x}" * 32
    return gen.build_manifest(
        randomness,
        pools,
        dummy_provenance(pools),
        dummy_beacon(),
        {"dummy": {"pool_sha256": "e" * 64}},
    )


def test_rng_bounds_and_repeatability() -> None:
    first = gen.Sha256CounterRNG(b"bounds")
    second = gen.Sha256CounterRNG(b"bounds")
    for limit in (1, 2, 3, 7, 50, 256, 1000):
        for _ in range(30):
            left = first.randbelow(limit)
            right = second.randbelow(limit)
            if left != right or not 0 <= left < limit:
                fail(f"randbelow unstable or out of range for {limit}: {left} {right}")
    if gen.shuffle(gen.Sha256CounterRNG(b"same"), [1, 2, 3, 4]) != gen.shuffle(
        gen.Sha256CounterRNG(b"same"), [1, 2, 3, 4]
    ):
        fail("shuffle was not repeatable")
    shuffled = gen.shuffle(gen.Sha256CounterRNG(b"perm"), ["a", "b", "c", "d", "e"])
    if sorted(shuffled) != ["a", "b", "c", "d", "e"]:
        fail("shuffle dropped or duplicated an item")


def test_balance_uniqueness_and_regen() -> None:
    seen_digests = set()
    for seed_byte in range(20):
        pools = dummy_pools()
        manifest = manifest_for(seed_byte, pools)
        errors = gen.logical_errors(manifest)
        if errors:
            fail(f"seed {seed_byte} logical errors: {errors[:5]}")
        outputs = gen.render_outputs(manifest)
        again = manifest_for(seed_byte, dummy_pools())
        if gen.canonical_dumps(manifest) != gen.canonical_dumps(again):
            fail(f"seed {seed_byte} did not regenerate")
        logical_errors = gen.assert_same_logical_rows(
            manifest, outputs[gen.CSV_NAME], outputs[gen.MD_NAME]
        )
        if logical_errors:
            fail(f"seed {seed_byte} output mismatch: {logical_errors}")
        if outputs[gen.SHA_NAME] != gen.render_sha256(
            {name: outputs[name] for name in (gen.JSON_NAME, gen.CSV_NAME, gen.MD_NAME)}
        ):
            fail("sha256 sidecar mismatch")
        seen_digests.add(gen.sha256_bytes(outputs[gen.JSON_NAME].encode("utf-8")))
        statuses = {row["status"] for row in manifest["rows"]}
        if statuses != {"UNRESEARCHED"}:
            fail("status drifted")
    if len(seen_digests) < 20:
        fail("distinct dummy seeds collided")


def test_special_characters_roundtrip() -> None:
    pools = dummy_pools(value_suffix='|x, "q"')
    manifest = manifest_for(7, pools)
    outputs = gen.render_outputs(manifest)
    errors = gen.assert_same_logical_rows(
        manifest, outputs[gen.CSV_NAME], outputs[gen.MD_NAME]
    )
    if errors:
        fail("special-character logical rows diverged: " + "; ".join(errors))
    if '|"' not in outputs[gen.CSV_NAME] and '""' not in outputs[gen.CSV_NAME]:
        # csv module quotes fields containing quotes. Either form is acceptable
        # as long as the logical parse matched above.
        pass


def test_exhaustion() -> None:
    pools = dummy_pools(size=160)
    pools["word"] = []
    try:
        manifest_for(3, pools)
    except gen.PoolExhausted:
        return
    fail("empty word pool did not fail the draw")


def test_no_os_csprng_in_live_path() -> None:
    source = inspect.getsource(gen.generate_live)
    if "os_csprng_seed" in source or "urandom" in source:
        fail("live generation references the operating-system CSPRNG")
    seed = gen.os_csprng_seed()
    if len(seed) != 32:
        fail("os csprng helper did not return 32 bytes")


def test_dates() -> None:
    days = gen.enumerate_dates()
    if days[0] != "1950-01-01" or days[-1] != "2026-10-12":
        fail("date endpoints are wrong")
    if "2026-10-13" in days or "1949-12-31" in days:
        fail("date range includes an excluded day")
    if len(days) < gen.MINIMUM_POOL or len(days) != len(set(days)):
        fail("date pool is short or duplicated")


def test_cn_parser_keeps_duty_table_only() -> None:
    html = """
    <table><tr><td>CN code</td><td>Description</td></tr>
    <tr><td>9999</td><td>Decoy goods</td></tr></table>
    <table><tr><td>CN code</td><td>Description</td><td>Conventional rate of duty (%)</td><td>Supplementary unit</td></tr>
    <tr><td>0101 21 00</td><td>– – Pure-bred breeding animals (19)</td><td>Free</td><td>p/st</td></tr>
    <tr><td>0101 21 00</td><td>Duplicate</td><td>Free</td><td>p/st</td></tr>
    <tr><td></td><td>– Horses:</td><td></td><td></td></tr>
    </table>
    """
    rows = gen.parse_cn_html(html)
    if rows != [
        {
            "item_id": "01012100",
            "source_type": "commodity",
            "value": "01012100 Pure-bred breeding animals",
        }
    ]:
        fail(f"CN parser mismatch: {rows}")


def test_title_and_ted_rules() -> None:
    notice = {
        "publication-number": "12-2026",
        "publication-date": "2026-03-04+01:00",
        "notice-title": {"deu": "Titel", "eng": " English title "},
        "links": {"html": {"ENG": "https://ted.europa.eu/en/notice/-/detail/12-2026"}},
    }
    rows = gen.parse_ted_pages([json.dumps({"notices": [notice]}).encode("utf-8")])
    if len(rows) != 1 or rows[0]["value"] != "English title":
        fail(f"TED title selection failed: {rows}")
    if rows[0]["publication_date"] != "2026-03-04":
        fail("TED date was not normalised")


def test_forbidden_seed_shape() -> None:
    try:
        gen.seed_from_randomness("abcd")
    except gen.ManifestError:
        return
    fail("short randomness was accepted")


def test_golden_dummy_manifest() -> None:
    manifest = manifest_for(1)
    digest = gen.sha256_bytes(gen.canonical_dumps(manifest).encode("utf-8"))
    if digest != GOLDEN_DUMMY_JSON_SHA256:
        fail(
            "golden dummy manifest hash changed\n"
            f"expected {GOLDEN_DUMMY_JSON_SHA256}\n"
            f"actual   {digest}"
        )


def main() -> None:
    test_rng_bounds_and_repeatability()
    test_balance_uniqueness_and_regen()
    test_special_characters_roundtrip()
    test_exhaustion()
    test_no_os_csprng_in_live_path()
    test_dates()
    test_cn_parser_keeps_duty_table_only()
    test_title_and_ted_rules()
    test_forbidden_seed_shape()
    if "--print-golden" in sys.argv:
        manifest = manifest_for(1)
        print(gen.sha256_bytes(gen.canonical_dumps(manifest).encode("utf-8")))
        return
    test_golden_dummy_manifest()
    print("dummy-seed tests passed")


if __name__ == "__main__":
    main()
