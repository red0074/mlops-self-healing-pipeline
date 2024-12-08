import requests
import subprocess
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class SelfHealingPipeline:
    def __init__(self, monitoring_url, retraining_script, openai_api_key):
        self.monitoring_url = monitoring_url
        self.retraining_script = retraining_script
        self.openai_client = OpenAI(api_key=openai_api_key)

    def check_metrics(self):
        try:
            response = requests.get(f"{self.monitoring_url}/metrics")
            response.raise_for_status()
            metrics = response.text
            
            # Parse metrics for key performance indicators
            if "fraud_prediction_probability" in metrics:
                last_prediction = float(metrics.split("fraud_prediction_probability")[1].split("\n")[0].strip())
                return last_prediction
            return None
        except Exception as e:
            logger.error(f"Metrics check failed: {e}")
            return None

    def trigger_retraining(self):
        try:
            subprocess.run(["python", self.retraining_script], check=True)
            logger.info("Retraining triggered successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Retraining failed: {e}")
            self.ai_debugging(str(e))

    def ai_debugging(self, error_log):
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a system reliability expert."},
                    {"role": "user", "content": f"Analyze this error log and suggest fixes:\n{error_log}"}
                ]
            )
            suggestion = response.choices[0].message.content
            logger.info(f"AI Debugging Suggestion: {suggestion}")
        except Exception as e:
            logger.error(f"AI debugging failed: {e}")

    def run(self):
        last_prediction = self.check_metrics()
        
        if last_prediction is not None and last_prediction < 0.5:  # Example threshold
            logger.warning("Detected performance drop. Triggering retraining...")
            self.trigger_retraining()

if __name__ == "__main__":
    self_healer = SelfHealingPipeline(
        monitoring_url="http://localhost:9100",
        retraining_script="./scripts/model_training.py",
        openai_api_key="your-openai-api-key"
    )
    
    # Periodic monitoring
    while True:
        self_healer.run()
        time.sleep(60)
