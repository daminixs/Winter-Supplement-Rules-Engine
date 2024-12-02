import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Optional: Specific MQTT topic ID for exclusive subscription (if not set, uses wildcard subscription)
MQTT_TOPIC_ID = os.getenv('MQTT_TOPIC_ID')

# MQTT Configuration
MQTT_BROKER = os.getenv('MQTT_BROKER', 'test.mosquitto.org')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_INPUT_TOPIC_BASE = os.getenv('MQTT_INPUT_TOPIC_BASE', 'BRE/calculateWinterSupplementInput/')
MQTT_OUTPUT_TOPIC_BASE = os.getenv('MQTT_OUTPUT_TOPIC_BASE', 'BRE/calculateWinterSupplementOutput/')

# Connection Retry Configuration
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 5))  # Maximum number of connection retries
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 3))  # Delay (in seconds) between retries

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOGGING_CONFIG = {
    'level': LOG_LEVEL,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}
