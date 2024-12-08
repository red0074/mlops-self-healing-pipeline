from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['alerts@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'data_preprocessing_pipeline',
    default_args=default_args,
    description='Data ingestion and preprocessing pipeline',
    schedule_interval='@daily',  # Run daily
    start_date=datetime(2024, 12, 1),
    catchup=False,
) as dag:

    def run_data_ingestion():
        """Run the data ingestion script"""
        subprocess.run(["python", "./scripts/data_ingestion.py"], check=True)

    def run_feature_engineering():
        """Run the feature engineering script"""
        subprocess.run(["python", "./scripts/feature_engineering.py"], check=True)

    # Tasks
    data_ingestion_task = PythonOperator(
        task_id='data_ingestion',
        python_callable=run_data_ingestion
    )

    feature_engineering_task = PythonOperator(
        task_id='feature_engineering',
        python_callable=run_feature_engineering
    )

    # Task dependencies
    data_ingestion_task >> feature_engineering_task
