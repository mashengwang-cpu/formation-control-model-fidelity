# JBSMSE article and reproduction files

Article: Effects of actuation models and retuning on controller rankings in heterogeneous vehicle formation control

Journal: Journal of the Brazilian Society of Mechanical Sciences and Engineering

Authors: Fuliang Ma; Yuzhen Dang; Yuping Ma; Ying Jiang; Hongbin Ma

Affiliations: Qinghai University, Xining 810016, Qinghai, China (Fuliang Ma, Yuzhen Dang, Ying Jiang); China Mobile Group Qinghai Co., Ltd., Xining 810001, Qinghai, China (Yuping Ma, Hongbin Ma).

Corresponding author: Yuzhen Dang; dyzivy@qhu.edu.cn

The repository root provides the compact experimental reproduction interface. Journal_figure_reproduction.zip provides the current article's 16 figures, using frozen plotting inputs and the journal-specific rendering script. Extract it into a separate directory, retain its directory structure, install baseline/requirements.txt, and run python -B generate_jbsmse_artwork.py from the extracted directory. It reads frozen tables; it does not rerun experiments or refit statistics. Earlier payload archives and preview images retain their original edition's titles and numbering.

The compact release does not include the complete dense trajectories or original PX4 logs. See DATA_COVERAGE.md for coverage and limits. Original code is MIT; original data and figures are CC BY 4.0; third-party licenses remain applicable. These files do not claim acceptance by the journal or physical-vehicle validation.
