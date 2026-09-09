# Data coverage and reproduction levels

| Evidence | Included | Scope |
|---|---:|---|
| Earlier public compact baseline | Original ZIP, byte-identical | Controller/model source, original cohorts, PX4 metric/failure records and existing figure sources; its raw-log omissions remain documented |
| Section S15 addendum | 25 files | Direct contrasts, sensitivity, selection and algebraic allocation analyses |
| Three independent training stages | 55,296 execution JSON files | All candidates and seeds |
| Three validation stages | 13,824 execution JSON files | All shortlisted evaluations, not only winners |
| Three independent formal tests | 33,900 unique execution JSON files | Design references map to shared execution IDs |
| Factorial formal tests | 9,600 execution JSON files | Both parameter backgrounds and all four module configurations |
| Numerical cases | 1,740 case JSON files | 468/450/438 search cases and 384 factorial cases; production-step limitations retained |
| Latest statistical outputs | 31 files | Paired values, primary families, local effects, search variability and numerical qualification |
| Latest figure materials | 23 files | Exact source tables, code and reference outputs for Figures 9, 10, S6 and graphical abstract |
| Deterministic formal trace examples | 56 NPZ | Search 1: 24 combinations; factorial: 32 combinations |
| RISE limitation diagnostics | 15 NPZ | All four steps and reference for each of the three unresolved production conditions |

The 112,620 ordinary execution records exclude stage metadata files. Case records
are counted separately; they are not extra formal-test samples. All original files
are losslessly compressed and hash-mapped in INPUT_MEMBERS.csv.gz. The metadata
hashes, source code, original statistical outputs and failed/blocked outcomes are
not changed by packaging. Compressed records are restored to their expected paths
by reproduce.py; no statistical producer code has been rewritten for compression.

Formal trace selection is specified in TRACE_SUBSET.json: the lowest formal-test
seed for each platform, ellipse and zero current, all four methods and three models
under search-1 transfer; both parameter backgrounds, both models and four module
configurations in the factorial experiment. This is an outcome-independent example
selection, not random sampling or additional validation data. All statistical
analyses use the full stored metric records rather than these examples.

Three RISE numerical cases: search 2, 99417932b6c0ff103498ac66 and
705c944ef11a47c4b375f9bd; search 3, 7c5482278e00870578eed59b. All stored
reference and 10/5/2.5/1.25-ms arrays are included. Their production flags remain
unresolved; passing at 1.25 ms does not qualify results computed at 2.5 ms.

Reproduction levels are distinct: exact input restoration; full metric-based
statistical/selection replay; selected raw-array checks; optional representative
simulation reruns; and complete scientific reruns. The last level needs substantial
computation and storage. This package does not include all 120,804 new arrays or
legacy complete PX4 logs, and does not assert that full raw public deposition is
complete. This release provides no new hardware evidence.
