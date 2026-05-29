# import required packages
from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum
import json
import pandas as pd
import boto3
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

WORKFLOW_SCHEDULE = "@once"  
bucket_name = "de300-airflow-yi-barnett"

default_args = {
    "owner": "yi-barnett",
    "depends_on_past": False,
    "start_date": pendulum.today("UTC").add(days=-1),
    "retries": 0,
}

def process_cars_data(ds):
    s3_client = boto3.client('s3')
    # response = s3_client.get_object(Bucket='dinglin-spring26', Key='lab6/cars.csv')
    # dont have permission to read in from dinglin-spring26

    response = s3_client.get_object(Bucket=bucket_name, Key='lab6/cars.csv')

    df = pd.read_csv(response['Body'])
    
    df = df.select_dtypes(include=['number'])
    
    X = df.drop('MPG', axis=1) 
    y = df['MPG']              
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=67676767
    )
    
    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    metrics = {
        'mse': mean_squared_error(y_test, predictions),
        'r2': r2_score(y_test, predictions)
    }
    print(f"Metrics: {metrics}")

    metrics_key = f'lab6/output/dt={ds}/metrics.json'
    print(f"Saving metrics to s3://{bucket_name}/{metrics_key}...")
    
    s3_client.put_object(
        Bucket=bucket_name,
        Key=metrics_key,
        Body=json.dumps(metrics, indent=4)
    )

    print("Task completed successfully *yawns*")


with DAG(
    dag_id="lab6",
    default_args=default_args,
    description="Lab 6 DAG -- tuff",
    schedule=WORKFLOW_SCHEDULE,
    tags=["de300"],
    catchup=False,  
) as dag:
    
    process_data = PythonOperator(
        task_id='process_data',
        python_callable=process_cars_data,
        op_kwargs={'ds': '{{ ds }}'} 
    )