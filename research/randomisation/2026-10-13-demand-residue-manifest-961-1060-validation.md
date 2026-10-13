# Readback — frozen demand-residue manifest #961–#1060

**Date:** 2026-10-13  
**Branch:** `research/fresh-discovery-2026-10-12-partial`  
**Authority:** V3–V3.6 read before this draw. `V3_7_RANDOMISED_DEMAND_RESIDUE.md` records the approved method.  
**Commercial board:** unchanged. #861–#960 remains 100 kills. Live hunt board remains 195 KILLED, #761 ANOMALY, #762 / #779 / #825 BANKED, #843 INCOMPLETE. CPO was not modified.  
**This record:** randomisation and validation only. No opportunity research, interpretation of seeds as products, outreach, product build, spending or merge.

## Commands

```text
python3 tools/test_randomised_demand_manifest.py
python3 tools/generate_randomised_demand_manifest.py fetch-pools
python3 tools/generate_randomised_demand_manifest.py generate-live
python3 tools/generate_randomised_demand_manifest.py validate
```

`generate-live` ran the dummy-seed tests again before retrieving the beacon, then wrote the manifest once. The operating-system CSPRNG helper was not used.

## Dummy-seed tests

`dummy-seed tests passed`.

Covered: unbiased `randbelow` bounds and repeatability; permutation shuffle; 20 fixed seeds; 100 rows; ids #961–#1060; four distinct types per row; each type 50 times; unique items within each source type; paired components from different types; paired items consumed; provenance fields; `UNRESEARCHED` only; no forbidden research fields; JSON/CSV/Markdown logical equality including `|`, comma and quote; SHA-256 sidecar; regeneration; empty-pool failure; date endpoints 1950-01-01 and 2026-10-12; Combined Nomenclature parser fixture; TED English-title fixture; rejection of a short beacon seed. The live generator source does not call the CSPRNG helper.

Locked dummy manifest SHA-256 for seed byte `0x01` repeated to 32 bytes: `ca923b3e2f3f735edbac339e8040ca1e0caa099f09f99bdc8d5be15904d34986`.

## Beacon

| Field | Value |
|---|---|
| URL | `https://api.drand.sh/public/latest` |
| Round | 6549822 |
| Randomness | `29c46ebee073e9e02e2a0094a39d0bd1ff50dba43a8f1ab723418675332fa992` |
| Randomness SHA-256 | `48833016cd47ef8ef0e056eab6f697eebccc84ea50369bf28f8f32e9d3dba09d` |
| Signature | `9505bf773fcad4be7aed97858953b0920e090cff0968e25ef73eb8bf404929c71a425a995e403400492d3e418cbfbc651996f345c9a72bbb1a6a16b748ae22a7c1f2495312b9124c0d1e2cf8de9ea83b7ac4277432fe01885718972498538613` |
| Retrieval | 2026-10-13T21:08:08Z |
| Response SHA-256 | `a07a4d99b3616e16314afd1d51a84a13690fe373235c475ded61899cf5112376` |
| Verification | Round endpoint `https://api.drand.sh/public/6549822` returned the same round, randomness and signature |

The full signature is stored in `research/randomisation/beacon/drand-public-latest.record.json` and in the manifest. It is not shortened in those files.

## Pools

| Type | Rows | Raw SHA-256 |
|---|---:|---|
| word | 117953 | `3f7d8be8ef6ecc7167d39b10d66954ec734280b5bdcd57f7d9eafe429d11c22a` |
| occupation | 3039 | `189983588cb276e81a0db2377647979bbc6b3b26065dbab1222981fcc865a84c` |
| commodity | 12583 | `608fe2429fed1e9261f5a9d9870157cf48abe85ea0716aa06c97d5c4af4420fb` |
| location | 6310 | `19de48da195cd1ef7f636c2293bb8b6d1591addf23b45cd94d5684de5f261aed` |
| wikipedia_page | 300 | `a63f5414255623163c09f1d636ed1f527951c3cb49f2a43212fe0845fe3604dc` |
| public_record | 300 | `96eeecea83f0583f1ddc29b7a7f517a9981d5a051e8e4152e79fd6e695cea521` |
| historical_date | 28044 | `181d604f69b65d67c640b4c20f33f2ad6881d874204b57059e33cdd462153ff9` |
| paired_seed | derived | not applicable |

`validate` rebuilt every `pool.jsonl` from its raw snapshot and matched the committed bytes.

## Live validation

```json
{
  "attempts": [961, 1060],
  "beacon_round": 6549822,
  "randomness_sha256": "48833016cd47ef8ef0e056eab6f697eebccc84ea50369bf28f8f32e9d3dba09d",
  "response_sha256": "a07a4d99b3616e16314afd1d51a84a13690fe373235c475ded61899cf5112376",
  "rows": 100,
  "status": "UNRESEARCHED",
  "type_counts": {
    "commodity": 50,
    "historical_date": 50,
    "location": 50,
    "occupation": 50,
    "paired_seed": 50,
    "public_record": 50,
    "wikipedia_page": 50,
    "word": 50
  },
  "validation": "passed"
}
```

Output hashes:

```text
e38102daacd788ee7370a40c64d60ab153834fe84111645e5c126465d3f6433a  2026-10-13-demand-residue-manifest-961-1060.json
7bc482edeea325210cd27a48b8df8bbb89dbd45d7342830ab2dad895ff572fca  2026-10-13-demand-residue-manifest-961-1060.csv
8c671103e1eef996649f35feb865ca3a041747fe5eb274a5c56940ce91f497d5  2026-10-13-demand-residue-manifest-961-1060.md
```

Regeneration from the recorded beacon and pool snapshots reproduced those four files. Every row status is `UNRESEARCHED`. No product, verdict or research-result field is present.

## Not done

No row was searched. No seed was interpreted as a product. No candidate verdict changed. No outreach, product build, spending or merge occurred.
