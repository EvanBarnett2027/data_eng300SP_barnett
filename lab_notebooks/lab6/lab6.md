# Amazon MWAA
Amazon Managed Workflows for Apache Airflow (MWAA) is Amazon Web Services’s managed offering of Apache Airflow. Here, you write Airflow DAGs as Python files, and AWS runs/operates the Airflow infrastructure for you—scheduler, workers, web UI, logging, upgrades/patching, and the metadata database.

Your MWAA environment watches an S3 bucket structure like:

- `s3://MWAA_DAG_BUCKET/dags/` → DAG python files

- `s3://MWAA_DAG_BUCKET/plugins/` → Airflow plugins (optional, like APIs, databases, UI extensions)

- `s3://MWAA_DAG_BUCKET/requirements.txt` → pip dependencies installed into the MWAA environment

MWAA can push Airflow logs and environment metrics to Amazon CloudWatch for troubleshooting and monitoring.

<!-- CloudWatch -->

## 1. Why orchestration
Orchestration: **a script** that does everything --> a managed workflow that runs the right tasks at the right time, with guardrails.

Scripts are fine for single-run and simple dependencies. However, Orchestration shines when you need:
- **scheduling + retries**: Run daily/hourly/on-demand; handle calendars and time windows; if something fails, retry, alert, or compensate.

- **Observability (UI, logs, lineage)**: What ran? When? What failed? What’s currently running.

- **dependency management across multiple steps**: Step B runs only after Step A succeeds (or based on conditions).

- **backfills and reproducibility**: re-run past time windows.

- **multi-team ownership and controls**: it manages who can trigger/retry/edit workflows.

## 2. Basic Steps to run a DAG
1.  Create a python file to define DAG and upload it to `s3://MWAA_DAG_BUCKET/dags/` folder
2.  Confirm it shows up in the UI
3.  Trigger and inspect logs
    
    To check the logs, open Grid → click a task square → Log. Find:
    - printed lines

    - retries (if any)

    - timestamps and execution info  

## 3. Scheduling, catchup, backfill, idempotency
### 1) Scheduling: what runs, when, and for which dates
```python
# 1. Define the workflow schedule frequency
WORKFLOW_SCHEDULE = "@hourly"

# 4. Initialize the DAG
dag = DAG(
    'example_dag',  # Name of the DAG
    default_args=default_args,
    description='An example DAG with dependencies',
    schedule=WORKFLOW_SCHEDULE,  # Schedule interval for DAG execution
    tags=["de300"]  # DAG tagging for categorization
)
```
- With `@hourly`, Airflow creates one run per hour (per logical date interval).
- Format to schedule date - Airflow uses standard cron semantics, which contains 5 fields
  - `minute hour date_of_month month day_of_week`
  - `"0 * * * *"` means “hourly”
  - `"30 2 * * 1-5"` means “weekdays at 2:30am”
For example,
```python
dag = DAG(
    'example_dag',  # Name of the DAG
    default_args=default_args,
    description='An example DAG with dependencies',
    schedule="30 2 * * 1-5",  # weekdays 2:30am
    tags=["de300"]  # DAG tagging for categorization
)
```

### 2) Catchup: create past runs since start_date
Where it is in the rewritten code
```python
dag = DAG(
    dag_id="example_dag",
    default_args=default_args,
    schedule="0 * * * *",   # hourly on the hour
    catchup=False,
)
```
If my DAG has a `start_date` in the past and I deploy/enable it today:
- `catchup=True`: It will create a run for every missed interval since start_date.
- `catchup=False`: It will start from “current-ish” and not flood you with old runs.

### 3) Backfill: intentionally run a range of past dates
Backfill is an action if you want to run this DAG for a historical range (even if catchup is off).

“I want to run Feb 15–Feb 21 again” (often after fixing code).

  - Go to the DAG → Grid view

  - Find the historical runs for Feb 15–Feb 21 (hourly = many runs)

  - Select tasks / runs → Clear

  - Airflow will rerun them following dependencies
  
Note: Backfill doesn’t “replay time”; it queues historical runs. 
- Feb 15 00:00 → Feb 21 23:00 (inclusive) is typically 7 × 24 = 168 runs
- If your DAG has:
  ```python
  max_active_runs=1
  ```
  Airflow will only run one DAG run at a time for this DAG. In that case, total time is roughly
  ```
  (#runs) × (average runtime per run)
  ```


### 4）Idempotency: make reruns safe
You can run the same operation multiple times, and after the first successful run, re-running it doesn’t change the final result

- Use deterministic, partitioned outputs like `curated/dt=2026-02-20/summary.json`
- `ds` in logs is the logical date; you can show that output keys include `dt={{ ds }}` (e.g., you may create a prefix like `s3://.../dt={{ ds }}/result.json` to store the data specific for the daate `ds`).
- Re-running the same date overwrites the same key.

## 4. Dependencies in MWAA (requirements vs plugins vs bundled code)
1. `requirements.txt` **(Python packages installed with pip)**: MWAA’s supported and recommended way to install Python libraries.
2. **Bash Operator** installing packages with pip

```python
with DAG(
    dag_id="bash_install_packages_example",
    start_date=pendulum.datetime(2026, 2, 24, tz="UTC"),
    schedule=None,
    catchup=False,
) as dag:

    install_and_check = BashOperator(
        task_id="install_and_check",
        bash_command="""
        set -euo pipefail

        python -m pip install --upgrade pip
        python -m pip install --user "textblob==0.17.1"

        python -c "import textblob; print('textblob version:', textblob.__version__)"
        """,
    )
```

3. **plugins.zip** (Airflow plugin mechanism + optional bundled artifacts): Shipping Airflow plugins: custom Operators/Hooks/Sensors, UI extensions, etc., via Airflow’s built-in plugin manager.
4. **Bundled code in the dags/ folder (your own modules packaged with DAGs**)**: Airflow can import local modules if they’re on the Python path (commonly by being in/under the DAGs folder).

Sensors: Use sensors when you must wait for a condition

## Homework: Linear regression on a CSV file
- Download CSV files from `s3://dinglin-spring26/lab6/cars.csv`
- CSV has numeric columns and one target column named `MPG`
- You are going to predict vehicle fuel consumption in `MPG` with the following features: `Weight`, `Drive Ratio`, `Horsepower`, `Displacement`, `Cylinders`.
- Dependencies installed (in requirements.txt):
  - pandas, numpy, scikit-learn

You should define the following tasks:
- read data files from S3.
- Split data into train and test sets
- Train linear regression
- Evaluate linear regression

and you may add other tasks you need

### Deliverables:
- DAG python file
- Output written to `s3://YOUR_BUCKET_NAME/lab6/output/dt={{ ds }}/metrics.json`
- (Optional) Model pickle to `s3://YOUR_BUCKET_NAME/lab6/output/dt={{ ds }}/model.pkl`

