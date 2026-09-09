# Controller rankings and module benefits in heterogeneous formation control: Actuation models and equal-budget tuning

**Authors:** Fuliang Ma¹, Yuzhen Dang¹, Yuping Ma², Ying Jiang¹, Hongbin Ma².

¹ Qinghai University, Xining 810016, Qinghai, China.  
² China Mobile Group Qinghai Co., Ltd., Xining 810001, Qinghai, China.  
Corresponding author: Yuzhen Dang (dyzivy@qhu.edu.cn).

## Abstract

Comparisons of formation controllers depend on the vehicle model and the parameters selected for it. We cross three model layers with parameter-selection strategy on an eight-vehicle aerial–surface platform and an independent four-vessel Otter model. Three modular controllers and a sampled distributed robust integral of the sign of the error (RISE) controller receive equal evaluation budgets. Three independent searches each allocate 2,880 development evaluations per method and platform, followed by 50 held-out seed blocks per platform. Twelve paired contrasts per search receive simultaneous bootstrap intervals. A separate factorial experiment crosses two module switches with two frozen parameter backgrounds. Across the three searches, the native Full-minus-Minimal complete-minus-point error interaction ranges from -0.177 to 1.290 m under point-selected transfer, but from 0.00073 to 0.00198 m after model-specific retuning. The retuned Otter interaction remains positive, ranging from 0.267 to 0.469 m. On the complete native model, deleting the gain schedule changes mean error by -0.7224 m under point-selected parameters and +0.00485 m under complete-model-selected parameters; signed-power deletion also changes sign. All 33,900 repeated-search and 9,600 factorial test executions have finite endpoints. Of 1,740 numerical checks, three RISE conditions fail at the production step and pass after refinement. The comparisons vary with the search, and module effects depend on the parameter background; neither supports a universal controller ordering. Three searches provide limited evidence about search variability. Unresolved source-condition reconstruction, stress diagnostics and software-in-the-loop failures further limit the computational conclusions.

## Complete compact reproduction release — 9 September 2026

[中文说明](README_zh-CN.md) · [Data coverage](DATA_COVERAGE.md) · [Validation](VALIDATION.md) · [Licenses](LICENSES.md)

Download the whole repository using **Code → Download ZIP**, or clone it. Keep
all files and the payloads directory together. Individual payloads are valid
archives; each is smaller than 25 MiB. The complete download is larger than the
GitHub single-file browser-upload limit, so upload the contents of this repository
directory, not the enclosing delivery ZIP. No Git LFS or external data download
is needed for the documented metric replays and stored-trace checks.

This release contains the earlier public compact baseline byte-for-byte, the
additional Section S15 analyses, all records from the three independent searches
and crossed module experiment, and the latest figure source tables. It also adds
71 original, losslessly preserved NPZ arrays. These are deterministic examples
and numerical-limit diagnostics, not all raw trajectories.

## Install

Use Python 3.12 and a separate environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\Activate.ps1
```

The pinned versions match the inspected Windows Python 3.12.14 environment.
Package installation needs internet or cached wheels. A new clean installation
and Linux/macOS execution have not been validated. The frozen campaign source
ledger contains Windows paths; the scientific replay commands are validated on
Windows. Do not use `python -O`, which disables scientific contract assertions.

## Run without launching simulations

Run from the repository root:

```powershell
python -B reproduce.py verify
python -B reproduce.py prepare
python -B reproduce.py verify-inputs
python -B reproduce.py latest-results
python -B reproduce.py latest-audit
python -B reproduce.py traces
python -B reproduce.py latest-figures --dpi 150
```

- `verify` checks the repository and compressed-payload SHA-256 hashes.
- `prepare` verifies and extracts the payloads under `outputs/workspace`.
- `verify-inputs` rechecks every extracted input and the baseline's own ledger.
- `latest-results` regenerates all 31 latest analysis files and compares them
  byte-for-byte with the frozen outputs. It does not choose parameters from test data.
- `latest-audit` independently reconstructs the three development selections,
  paired means and simultaneous intervals for the four primary contrast families.
- `traces` decompresses all 71 supplied NPZ files, verifies their integrity and
  mappings, and recomputes tracking error and saved interval force/moment effort.
  It does not independently re-establish the numerical qualification decisions.
- `latest-figures` renders Figures 9, 10, S6 and the graphical abstract. Use
  `--dpi 1000` for publication raster output; vector PDF and SVG are also written.

`latest-all` runs the four latest analysis, audit, figure and trace commands.
The preparation step is cached; `verify-inputs` explicitly checks its extracted
contents. Results, validation reports and logs remain in ignored `outputs/`.
Use a fresh extraction if inputs have been edited. No command above runs a new
simulation campaign. Metric replay is not a substitute for rerunning dynamics.

## Earlier cohorts

```powershell
python -B reproduce.py baseline-results
python -B reproduce.py baseline-selection
python -B reproduce.py baseline-figures
python -B reproduce.py previous-results
python -B reproduce.py baseline-test
```

The baseline figure command produces Figures 1–8 and S1–S5 from the earlier
cohorts; combine them with the latest figure command for the current figure set.
`previous-results` regenerates and audits the Section S15 direct contrasts,
condition sensitivities, development selections and algebraic allocation examples.
The public baseline is retained in `payloads/baseline.zip`, with SHA-256
`c395fa58838d5420c8f896ba52cfd25f0ad5465142f4095e7abf37431f94ad79`.
It corresponds to the previously cited GitHub commit
`fbfa3fb2a2eb6eb2e63f28258e1ab59db86a84f5`; that old commit does not contain the
new experiment data. Frozen baseline documents describe their original version.
This root README and DATA_COVERAGE.md describe the present release.

## New simulations and full raw data

`python -B reproduce.py baseline-smoke` explicitly launches the earlier baseline's
32 representative simulations. It is separate from statistical replay.
After preparation, original campaign code is available under
`outputs/workspace/campaign`, including the three independent searches and
factorial design. The compact archive does not contain the complete trace cache
needed to resume the frozen runner without missing simulations. Do not launch
`campaign_runner.py all` as a quick validation: it may regenerate missing jobs
and requires substantial time and storage. No full campaign was rerun to prepare
this release.

All 112,620 new ordinary execution records and 1,740 numerical-case records are
included. Only 71 of the 120,804 new NPZ files are supplied here. Complete raw
arrays and legacy PX4 logs remain in the authors' separate full collection;
their complete public deposition is not claimed by this compact package.

## Scientific interpretation

Three independent searches are three searches, not 150 independent searches.
The three search families and factorial family retain their separately defined
12-contrast simultaneous intervals; secondary pointwise intervals remain
secondary. Shared execution IDs are not counted twice. The three RISE
production-step limitations, incomplete source-condition reconstruction, original
stress diagnostics and blocked PX4 hypothesis families are retained. Passing a
package audit does not validate hardware or establish universal controller rankings.

Original code is MIT and original data/figures are CC BY 4.0. Third-party rights
and attribution are preserved. OpenAI Codex assisted with code, documentation
and checks; authors remain responsible for the scientific content and approval.
Submission correspondence and author-only checklists are not included.


## Result previews

![Independent searches](docs/Figure_9_preview.png)

![Crossed module interventions](docs/Figure_10_preview.png)
