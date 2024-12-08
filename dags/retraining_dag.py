from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
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
    'model_retraining_pipeline',
    default_args=default_args,
    description='Model retraining pipeline triggered by monitoring',
    schedule_interval=None,  # Triggered manually or by an external event
    start_date=datetime(2024, 12, 1),
    catchup=False,
) as dag:

    def run_model_training():
        """Run the model training script"""
        subprocess.run(["python", "./scripts/model_training.py"], check=True)

    def validate_model():
        """Run the model validation script"""
        subprocess.run(["python", "./scripts/model_validation.py"], check=True)

    def deploy_model():
        """Deploy the trained model"""
        subprocess.run(["python", "./scripts/deploy_model.py"], check=True)

    # Tasks
    start_task = DummyOperator(task_id='start')

    model_training_task = PythonOperator(
        task_id='model_training',
        python_callable=run_model_training
    )

    model_validation_task = PythonOperator(
        task_id='model_validation',
        python_callable=validate_model
    )

    model_deployment_task = PythonOperator(
        task_id='model_deployment',
        python_callable=deploy_model
    )

    end_task = DummyOperator(task_id='end')

    # Task dependencies
    start_task >> model_training_task >> model_validation_task >> model_deployment_task >> end_task
