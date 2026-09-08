# Formation control: actuation models and equal-budget tuning

Data and code for **Controller rankings and module benefits in heterogeneous formation control: Actuation models and equal-budget tuning**.

Authors: Fuliang Ma, Yuzhen Dang, Yuping Ma, Ying Jiang and Hongbin Ma.

## Download and use

Download [formation-control-repro-github.zip](formation-control-repro-github.zip), extract it, and open the `formation-control-repro` directory. Use Python 3.12 and install its `requirements.txt` in a dedicated environment. Read the included README before running:

```text
python reproduce.py verify
python reproduce.py results
python reproduce.py selection
python reproduce.py figures
```

The compact package includes frozen designs, development and execution-level metric records, statistical and simulation code, and plotting inputs for 8 main-text and 5 supplementary figures. Default PNG output is 150 dpi; use `python reproduce.py figures --dpi 1000` for publication-resolution PNG. PDF/SVG are vector outputs.

The ZIP preserves directory structure and frozen file bytes. Its SHA-256 is recorded in [DOWNLOAD_SHA256.txt](DOWNLOAD_SHA256.txt); the internal manifest checks individual files.

## Data availability and evidence boundaries

Full original time-series arrays and PX4 raw logs are **not included**. Their separate public archive remains pending. This compact release supports metric-based reanalysis, selection replay, figure reproduction and representative simulations, but not re-auditing every original raw trajectory or PX4 log. No published dataset DOI is claimed.

RISE delayed/noisy source-condition reconstruction remains unresolved. Failed PX4 designs and unevaluated hypothesis families are retained. Computational results are not physical or hardware-in-the-loop validation. Prior validation reports and scientific provenance are retained inside the archive with their scope and limitations.

## Licensing

Original code: MIT. Original data and figures: CC BY 4.0. Third-party materials retain their licenses and attribution. See [LICENSES.md](LICENSES.md), [LICENSE_CODE.txt](LICENSE_CODE.txt), and notices inside the archive. The manuscript and submission correspondence are not part of this release.

Repository: https://github.com/mashengwang-cpu/formation-control-model-fidelity
