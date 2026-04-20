# Homework 1 — Aircraft Inventory EDA & Modeling

Analysis of the BTS *F41 Schedule B-43* aircraft inventory. The notebook covers missing-data analysis, column-level imputation, categorical standardization, feature engineering, a Box-Cox transformation, and four regression baselines.

## Files

- `01_hw.ipynb` — main notebook; all six tasks.
- `T_F41SCHEDULE_B43_with_missing.zip` — raw input (pandas reads the zip directly).
- `column_descriptions.png` — image used by the EDA section.
- `hw1_writeup.pdf` — concatenated written responses for Tasks 1–6.
- `lbs_check.csv` — a sample of rows written out during the Task 1 capacity manual check.

## Environment

Python ≥ 3.10. Install dependencies:

```bash
pip install pandas numpy scipy scikit-learn matplotlib seaborn missingno
```

Optional: `jupyter` / VS Code Notebooks to run `01_hw.ipynb` interactively.

## How to run

Open `01_hw.ipynb` and **Run All** top-to-bottom. Cells are ordered so later tasks can refer to objects built earlier:

- Task 1 defines the imputation functions.
- Task 2 defines the standardization functions.
- The "Apply Imputation and Standardization" cell builds `clean` (the fully imputed / standardized frame).
- Task 3 produces `clean_dropped` (rows with any residual NaN removed).
- Task 4 uses `clean_dropped` to build `transformed` with `_BOXCOX` columns.
- Task 5 uses `clean_dropped` to build `sized` with the `SIZE` column.
- Task 6 trains the four regression models on `clean_dropped`.

## Expected outputs

**Task 1 / Task 2 — cleaning pipeline**
After running the *Apply* cell, residual missingness should match:

| column            | residual NaNs |
|-------------------|--------------:|
| AIRCRAFT_TYPE     |        29,933 |
| ACQUISITION_DATE  |           967 |
| UNIQUE_CARRIER    |           164 |
| AIRCRAFT_STATUS   |           122 |
| UNIQUE_CARRIER_NAME |         105 |
| MODEL             |            11 |
| OPERATING_STATUS  |             1 |

Standardization reduces `MANUFACTURER` from **183 → ~104** unique values and `MODEL` from **1,340 → ~1,132** unique values.

**Task 3 — drop-na**
- Rows before drop: **132,313**
- Rows after drop: **101,153**
- Retained: **76.45%**

**Task 4 — Box-Cox**
- `NUMBER_OF_SEATS` skew: −0.21 → −0.64 (bimodal, Box-Cox cannot fix)
- `CAPACITY_IN_POUNDS` skew: 4.04 → 0.11
- λ (seats+1) ≈ 0.54, λ (capacity) ≈ 0.15

**Task 5 — SIZE quartiles**
Edges from `pd.qcut`: `0 → 50 → 117 → 154 → 190`. Group counts: `SMALL ≈ 30,310`, `MEDIUM ≈ 13,826`, `LARGE ≈ 22,741`, `XLARGE ≈ 21,219`. Operating rate rises monotonically with size; regional-jet (`MEDIUM`) carriers are the operating-lease outlier.

**Task 6 — regression baselines (RMSE)**

See model results table.

Random forest beats linear regression on both targets; linear regression underfits (train ≈ test).

## Build PDF

Run the following terminal command to regenerate the pdf:

```bash
pandoc writeup.md -o hw1_writeup.pdf --pdf-engine=xelatex -V mainfont="Arial Unicode MS"
```


## Gen AI Usage

- Two main AI tools used: Chat GPT 5.4, Claude Code (Vscode extension)
- Main tasks delegated:
    - Generating plots
        - Example prompt: "Create a colored coded plot for AIRCRAFT_STATUS proportion by SIZE"
    - Creating README.md file
        - Prompt: "include a readme.md file including how to run the code and what your expected outputs."
    - Formatting markdown tables:
        - Prompt: "Turn this pandas output dataframe into a markdown table"
    - Finding spelling variants for manufacturers.
        - Prompt: "Look at this CSV, create a MANUFACTURER_PATTERNS list that maps multiple spellings of manufacturers to one spelling for data standardization"
        - Checked spelling to ensure correctness and checked code output
    - Data Checking
        - Prompt: "look at lbs_check.csv, search online to see if the capacity_in_pounds value makes sense for these aircrafts"
        - Looked at cite sources in response. Used this to understand incorrect values in `CAPACITY_IN_POUNDS` column.
    - To writeup.md into pdf
        - prompt: "turn this md file into a pdf for my homework assignment"

