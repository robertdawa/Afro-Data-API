# Data pipeline

Built in **Phase 5** (see [SPEC.md §7](../SPEC.md#7-data-pipeline)).

| Folder | Purpose |
|---|---|
| `connectors/` | One module per source (`faostat.py`, `world_bank.py`, …), each with `fetch()` → raw files, `clean()` → cleaned table, `harmonise()` → standard records |
| `validation/` | Schema, unit, country-code, duplicate, outlier and sudden-jump checks; a failing dataset is not published |
| `harmonise/` | Shared helpers for the standard record format (SPEC §3.2): series ids, unit list, ISO3 codes, region groups |

Raw files go to the `adp-raw` bucket unchanged, with a checksum and retrieval date.
