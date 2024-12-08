import kfp
from kfp import dsl

def data_prep_op():
    return dsl.ContainerOp(
        name="Data Preparation",
        image="python:3.9-slim",
        command=["python", "/scripts/data_ingestion.py"],
        arguments=[
            "--input_path", "/data/processed",
            "--output_path", "/data/features"
        ],
        file_outputs={
            "features": "/data/features/engineered_fraud_data.parquet"
        }
    )

def training_op(features_path):
    return dsl.ContainerOp(
        name="Model Training",
        image="python:3.9-slim",
        command=["python", "/scripts/model_training.py"],
        arguments=[
            "--data_path", features_path,
            "--output_path", "/models"
        ],
        file_outputs={
            "model": "/models/fraud_model.pth"
        }
    )

def validation_op(model_path, features_path):
    return dsl.ContainerOp(
        name="Model Validation",
        image="python:3.9-slim",
        command=["python", "/scripts/model_validation.py"],
        arguments=[
            "--model_path", model_path,
            "--data_path", features_path,
            "--preprocessor_path", "/data/features/feature_preprocessor.joblib"
        ],
        file_outputs={}
    )

def deployment_op(model_path):
    return dsl.ContainerOp(
        name="Model Deployment",
        image="python:3.9-slim",
        command=["python", "/scripts/deploy_model.py"],
        arguments=[
            "--model_path", model_path
        ]
    )

@dsl.pipeline(
    name="Fraud Detection Pipeline",
    description="Pipeline for fraud detection using Kubeflow"
)
def fraud_detection_pipeline():
    # Step 1: Data Preparation
    data_prep = data_prep_op()

    # Step 2: Model Training
    training = training_op(data_prep.outputs["features"])

    # Step 3: Model Validation
    validation = validation_op(training.outputs["model"], data_prep.outputs["features"])

    # Step 4: Model Deployment
    deployment = deployment_op(training.outputs["model"])

    # Define dependencies
    training.after(data_prep)
    validation.after(training)
    deployment.after(validation)

if __name__ == "__main__":
    kfp.compiler.Compiler().compile(fraud_detection_pipeline, "fraud_detection_pipeline.yaml")
