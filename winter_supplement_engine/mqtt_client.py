import json
import logging
import time
import os

import paho.mqtt.client as mqtt

from .config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_INPUT_TOPIC_BASE,
    MQTT_OUTPUT_TOPIC_BASE,
    MAX_RETRIES,
    RETRY_DELAY,
    LOGGING_CONFIG
)
from .schemas import validate_input, validate_output
from .calculator import WinterSupplementCalculator


class WinterSupplementMQTTClient:
    """
    MQTT Client for processing Winter Supplement calculations.
    """

    def __init__(self):
        """
        Initialize MQTT client with configuration and logging.
        """
        # Configure logging
        logging.basicConfig(
            level=LOGGING_CONFIG['level'],
            format=LOGGING_CONFIG['format']
        )
        self.logger = logging.getLogger(__name__)

        # Get specific topic ID from environment variable if set
        self.specific_topic_id = os.getenv('MQTT_TOPIC_ID')

        # Initialize MQTT client
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def connect(self):
        """
        Connect to MQTT broker with retries and start message loop.
        """
        retries = 0
        while retries < MAX_RETRIES:
            try:
                self.logger.info(f"Attempting to connect to {MQTT_BROKER}:{MQTT_PORT} (Attempt {retries + 1})")
                self.client.connect(MQTT_BROKER, MQTT_PORT)
                self.logger.info("Successfully connected to MQTT broker")
                self.client.loop_forever()
                break  # Exit loop on successful connection
            except Exception as e:
                self.logger.error(f"Connection attempt failed: {e}")
                retries += 1
                if retries < MAX_RETRIES:
                    self.logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    self.logger.error("Maximum connection attempts reached. Exiting.")
                    break

    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback for successful MQTT connection.

        Args:
            rc (int): Connection result code
        """
        if rc == 0:
            self.logger.info("Connected to MQTT broker successfully")

            # If a specific topic ID is set, subscribe only to that specific topic
            if self.specific_topic_id:
                specific_topic = f"{MQTT_INPUT_TOPIC_BASE}{self.specific_topic_id}"
                self.logger.info(f"Subscribing to specific topic: {specific_topic}")
                client.subscribe(specific_topic)
            else:
                # If no specific topic ID, subscribe to wildcard topic
                client.subscribe(f"{MQTT_INPUT_TOPIC_BASE}+")
        else:
            self.logger.error(f"Failed to connect. Return code: {rc}")

    def _on_message(self, client, userdata, msg):
        """
        Process incoming MQTT messages for Winter Supplement calculation.

        Args:
            msg (mqtt.MQTTMessage): Received message
        """
        try:
            # Extract topic ID from received message topic
            topic_parts = msg.topic.split('/')
            topic_id = topic_parts[-1]
            self.logger.debug(f"Extracted topic ID: {topic_id}")

            # Parse input data
            input_data = json.loads(msg.payload.decode())
            self.logger.debug(f"Received input data: {input_data}")

            # Validate input schema
            try:
                validate_input(input_data)
                self.logger.debug("Input data validated successfully.")
            except Exception as e:
                self.logger.error(f"Input validation failed: {str(e)}")
                return

            # Calculate supplement
            result = WinterSupplementCalculator.calculate_supplement(input_data)
            self.logger.debug(f"Calculated supplement for ID: {input_data['id']}")
            self.logger.debug(f"Calculation result: {result}")

            # Validate output schema
            try:
                validate_output(result)
                self.logger.debug("Output data validated successfully.")
            except Exception as e:
                self.logger.error(f"Output validation failed: {str(e)}")
                return

            # Publish result to output topic
            output_topic = f"{MQTT_OUTPUT_TOPIC_BASE}{topic_id}"
            self.logger.debug(f"Publishing result to output topic: {output_topic}")
            client.publish(output_topic, json.dumps(result))
            self.logger.info(f"Published result for ID: {input_data['id']}")

        except json.JSONDecodeError:
            self.logger.error("Invalid JSON received")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
