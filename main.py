import logging
from winter_supplement_engine.mqtt_client import WinterSupplementMQTTClient
from winter_supplement_engine.config import LOGGING_CONFIG

# Configure logging
logging.basicConfig(
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format']
)
logger = logging.getLogger(__name__)


def main():
    """
    Entry point for Winter Supplement Rules Engine.
    Initializes and starts MQTT client.
    """
    logger.info("Starting Winter Supplement Rules Engine...")
    mqtt_client = WinterSupplementMQTTClient()
    mqtt_client.connect()


if __name__ == "__main__":
    main()
