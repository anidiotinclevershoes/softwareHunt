# Software Opportunity Hunt — V3.7 Randomised Demand Residue

**Approved:** 2026-10-13 by explicit user instruction  
**Status:** active method amendment on `research/fresh-discovery-2026-10-12-partial`; supplements V3–V3.6 without weakening commercial, graveyard, outreach or build gates  
**Scope:** how entry points for attempts #961–#1060 are chosen, and the fixed search procedure to use if that hunt is later ordered  
**Not in scope:** this amendment does not itself execute searches, change a verdict, or authorise outreach, spending, a product build or a merge

## Purpose

The next hunt is a pain-first, money-gated Demand Residue Hunt. Its entry points are mechanically random. An AI model must not choose the items, the ordering, the seed or the combinations, and must not reroll a row because the combination looks useless, absurd or commercially unpromising.

V3–V3.6 still govern what happens after a row advances. Zero survivors remains a valid outcome.

## 1. Frozen manifest

The live draw is already frozen. Do not generate another one.

| Artifact | Path |
|---|---|
| JSON, with full item provenance and beacon metadata | `research/randomisation/2026-10-13-demand-residue-manifest-961-1060.json` |
| CSV | `research/randomisation/2026-10-13-demand-residue-manifest-961-1060.csv` |
| Markdown table | `research/randomisation/2026-10-13-demand-residue-manifest-961-1060.md` |
| SHA-256 sidecar | `research/randomisation/2026-10-13-demand-residue-manifest-961-1060.sha256` |
| Generator | `tools/generate_randomised_demand_manifest.py` |
| Fixed pools | `research/randomisation/pools/` |
| Beacon response and record | `research/randomisation/beacon/` |
| Readback | `research/randomisation/2026-10-13-demand-residue-manifest-961-1060-validation.md` |

Every row is `UNRESEARCHED`. The table has no hypotheses, product ideas, queries, pain claims or results.

## 2. Randomiser design

One hundred rows, numbered #961–#1060. Each row has four seeds, A–D. The four seeds in a row use four different types. Across the 400 cells, each of the eight types appears exactly 50 times.

The eight types are, in canonical order:

1. `word`
2. `occupation`
3. `commodity`
4. `location`
5. `wikipedia_page`
6. `public_record`
7. `historical_date`
8. `paired_seed`

Construction, implemented by `build_type_rows`:

1. Perform 50 rounds.
2. In each round, shuffle the eight type names.
3. Split that permutation into two groups of four.
4. Shuffle the resulting 100 groups.
5. Number them #961–#1060 in that shuffled order.

## 3. Entropy and PRNG

The live master entropy is the drand League of Entropy public beacon:

`https://api.drand.sh/public/latest`

The recorded draw uses round **6549822**, retrieved **2026-10-13T21:08:08Z**. The exact response bytes are in `research/randomisation/beacon/drand-public-latest.response.json`. Their SHA-256 is `a07a4d99b3616e16314afd1d51a84a13690fe373235c475ded61899cf5112376`. The same round was fetched again from `https://api.drand.sh/public/6549822` and matched on round, randomness and signature. The randomness SHA-256 is `48833016cd47ef8ef0e056eab6f697eebccc84ea50369bf28f8f32e9d3dba09d`.

The PRNG seed is the 32 bytes obtained by hex-decoding the beacon `randomness` field. Algorithm id: `sha256-counter-fisher-yates-v1`.

- Block `i` is SHA-256(seed || uint64 big-endian `i`), with `i` starting at 0.
- `randbelow(n)` reads the minimum number of bytes that can represent `n`, interprets them as a big-endian integer, and rejects values in the incomplete final residue so the result is unbiased. `randbelow(1)` returns 0 and consumes no bytes.
- Shuffle is Fisher–Yates from the last index down to 1, swapping with `randbelow(i+1)`.

Item draws continue on that same stream, after the type shuffle, in attempt order and then seed order A–D. A direct cell draws one unused item from its pool. A `paired_seed` cell shuffles the first seven types, takes the first two, and draws one unused item from each, in that order.

The operating-system CSPRNG helper `os_csprng_seed` is present for tests only. It was not used for this manifest. Do not replace the recorded beacon without explicit user approval.

Regeneration from the recorded beacon response and the committed pool snapshots must reproduce the JSON, CSV, Markdown and SHA-256 sidecar byte for byte. `python3 tools/generate_randomised_demand_manifest.py validate` performs that check. Do not rerun the live draw to obtain different combinations.

## 4. Fixed source pools

Snapshots were built before the beacon draw. Entries were not written by a language model. Filtering is mechanical: blank values, malformed records and exact duplicate identifiers only. Strange or commercially unpromising entries stay in the pool.

| Type | Source | Eligible rows |
|---|---|---|
| `word` | Princeton WordNet 3.1 `index.noun` | 117953 |
| `occupation` | European Commission ESCO v1.2.0 English preferred labels | 3039 |
| `commodity` | English OJ L 2025/1926 Combined Nomenclature duty tables | 12583 |
| `location` | GeoNames `cities15000.zip`, feature class P, Ireland / UK / EU / EEA | 6310 |
| `wikipedia_page` | English Wikipedia namespace-0 random pages, with page id, title, revision id and canonical URL | 300 |
| `public_record` | TED `cn-standard` notices with publication number, title, date and canonical URL | 300 |
| `historical_date` | Every proleptic Gregorian date from 1950-01-01 through 2026-10-12 | 28044 |
| `paired_seed` | Two unused items from two different pools among the first seven | derived, not a separate list |

Each pool directory contains `provenance.json` (organisation, URL, retrieval time, licence, raw-file SHA-256, filtering rules, row count) and, where applicable, `pool.jsonl` plus the raw snapshot. `python3 tools/generate_randomised_demand_manifest.py validate` rebuilds each `pool.jsonl` from its raw snapshot.

## 5. Uniqueness

- Do not reuse an item within its source type anywhere in the 100 rows.
- An item used inside `paired_seed` is used. It cannot appear as a direct seed or inside another pair.
- The two items inside one paired seed come from different source types.
- Identity is the source identifier (WordNet lemma, ESCO URI, CN code, GeoNames id, Wikipedia page id, TED publication number, or ISO date), not a judgement about whether two labels look similar.
- If a pool cannot supply the next unique item, validation fails. Do not weaken the rule and do not substitute a convenient neighbour.

## 6. Future search protocol — document only

Do not run this protocol unless a later user instruction orders the #961–#1060 hunt. When that happens, use the frozen rows. Do not reroll.

1. Label each row’s four frozen inputs A, B, C and D.
2. Search all six literal pairings: AB, AC, AD, BC, BD and CD.
3. Begin with literal input terms rather than selecting an attractive metaphor.
4. The six searches together are one discovery attempt, not six.
5. Do not reroll a row if the searches are useless.
6. A row advances only if at least two routes converge on substantially the same real unresolved job.
7. A demand cluster requires multiple independent people or organisations seeking the same complete outcome.
8. Only then apply buyer, consequence, current workaround/spend, complete-software-outcome, competitor, repeated-AI, AI-built-entry, recurrence and first-ten tests.
9. Compare against the full #1–#960 history before counting a resulting job as distinct.
10. Preserve zero survivors as an acceptable outcome.

After step 6, V3–V3.6 remain binding, including M0–M4, S0–S4, C0–C4, D0–D4, the sidecar and adoption tests, founder-fit, Ireland > UK > EU/EEA, graveyard integrity, and the OUTREACH-READY / BUILD-READY thresholds. A converged job is not a promotion. Competition, an expensive human service, or a familiar noun does not by itself kill or save a row; the existing gates do that work after the convergence test.

## 7. What this amendment does not change

- #861–#960 remains complete at 100 kills.
- The live commercial board is unchanged: 195 KILLED, #761 ANOMALY, #762 / #779 / #825 BANKED, #843 INCOMPLETE, and no new OUTREACH-READY or BUILD-READY result from the hunts.
- CPO remains separately OUTREACH-READY and was not modified.
- Historical kills stay killed. This manifest is not evidence about any of them.
- No outreach, product build, spending or merge is authorised by creating or reading the manifest.
