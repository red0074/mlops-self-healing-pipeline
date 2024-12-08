from prometheus_client import start_http_server, Summary, Gauge, Counter
import time
import requests
import logging

# Initialize Prometheus metrics
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
PREDICTION_COUNT = Counter('fraud_prediction_requests', 'Number of prediction requests')
FRAUD_PREDICTION = Gauge('fraud_prediction_probability', 'Fraud prediction probability')

logger = logging.getLogger(__name__)

class FraudDetectionMonitor:
    def __init__(self, api_url):
        self.api_url = api_url

    @REQUEST_TIME.time()
    def monitor_predictions(self, input_data):
        try:
            response = requests.post(f"{self.api_url}/predict", json=input_data)
            response.raise_for_status()
            result = response.json()

            PREDICTION_COUNT.inc()
            FRAUD_PREDICTION.set(result['probability'])

            return result
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")
            return None

if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(9100)
    
    monitor = FraudDetectionMonitor(api_url="http://localhost:8000")
    
    # Simulate requests for monitoring
    while True:
        mock_input = {
            "transaction_id": 12345,
            "amount": 100.5,
            "timestamp": "2024-12-06T10:00:00",
            "customer_id": "C123",
            "merchant_id": "M456"
        }
        monitor.monitor_predictions(mock_input)
        time.sleep(10)
