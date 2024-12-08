import torch
from fastapi import FastAPI, HTTPException
import uvicorn
import joblib
import pandas as pd
import logging

# Initialize FastAPI app
app = FastAPI()
logger = logging.getLogger(__name__)

class FraudDetectionAPI:
    def __init__(self, model_path, preprocessor_path):
        self.model = self.load_model(model_path)
        self.preprocessor = self.load_preprocessor(preprocessor_path)

    def load_model(self, model_path):
        try:
            model = torch.load(model_path)
            model.eval()
            return model
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            raise

    def load_preprocessor(self, preprocessor_path):
        try:
            return joblib.load(preprocessor_path)
        except Exception as e:
            logger.error(f"Preprocessor loading failed: {e}")
            raise

    def predict(self, input_data):
        try:
            df = pd.DataFrame([input_data])
            processed_data = self.preprocessor.transform(df)
            tensor_data = torch.FloatTensor(processed_data)
            
            with torch.no_grad():
                predictions = self.model(tensor_data)
                return {"is_fraud": bool(predictions[0].item() > 0.5), "probability": predictions[0].item()}
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise

# Load model and preprocessor
fraud_api = FraudDetectionAPI(
    model_path="./models/fraud_model.pth",
    preprocessor_path="./data/features/feature_preprocessor.joblib"
)

@app.post("/predict")
async def predict(input_data: dict):
    try:
        result = fraud_api.predict(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
