# Homework 3 — NYC Taxi Analytics with PySpark

Loads the January 2026 NYC yellow- and green-taxi trip records, standardizes
their schemas, cleans them, answers four summary questions, and trains a
linear-regression model to predict `fare_amount` from non-fare predictors.

## Environment

- Python with `pyspark`, `pandas`, and `matplotlib` installed.
- The two parquet files:
  - `yellow_tripdata_2026-01.parquet`
  - `green_tripdata_2026-01.parquet`

## How to run

1. Open `hw3.ipynb` 
2. Run every cell from top to bottom -- double check that data files are present and paths are correct. 
3. Analysis and plotting cells output results and final output is written to S3.

## What the notebook does

1. **Start Spark** — builds a local `SparkSession` named
   `"NYC Taxi Analytics Assignment"` with 8 shuffle partitions.
2. **Load data** — reads both parquet files into Spark DataFrames and
   prints their schemas.
3. **Standardize schemas** — renames `tpep_*` / `lpep_*` timestamps to a
   shared `pickup_datetime` / `dropoff_datetime`, tags each row with a
   `taxi_type` literal (`yellow` / `green`), selects a common column set,
   and unions them into `trips_df`.
4. **Clean** — filters out rows with null timestamps, non-positive
   distance, negative fare or total, drop-off before pickup, or duration
   over 24 hours; result is cached as `trips_clean`.
5. **Analysis questions** — Q1 trips per taxi type, Q2 busiest pickup
   hour, Q3 share of trips under 2 miles, Q4 average distance by taxi
   type, Q5 linear-regression model for `fare_amount` (80/20 split, RMSE
   on both folds, coefficient analysis).
6. **Plot** — scatter of predicted vs. actual fare on a 5% sample of
   the test set, saved to `predicted_vs_actual.png`.

## Outputs

- Cell outputs inline in the notebook (counts, RMSE, coefficient table,
  markdown analysis).
- `predicted_vs_actual.png` — predicted vs. actual fare scatter with a
  `y = x` reference line.

## AI usage

- Claude Code (Opus 4.7) Usage:
   - Used to help with data cleaning debugging. 
      - Example prompt: "Given this code, why did it produce this error"
   - Used to create hw3_report.pdf
      - Example prompt: "Based on the notebook I used for my assignment, and my EC2 setup, generate a report pdf that includes ..."
   - Used to aid in uploading results to S3.
      - Example prompt: "Given my EC2 setup, can I upload these results to my AWS s3 bucket"
