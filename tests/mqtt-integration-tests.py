import json
import os

import pytest
from unittest.mock import Mock, patch, MagicMock
import paho.mqtt.client as mqtt
import logging

from winter_supplement_engine.mqtt_client import WinterSupplementMQTTClient
from winter_supplement_engine.calculator import WinterSupplementCalculator
from winter_supplement_engine.config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_INPUT_TOPIC_BASE,
    MQTT_OUTPUT_TOPIC_BASE
)
from winter_supplement_engine.schemas import validate_input, validate_output


class TestMQTTIntegration:
    @pytest.fixture
    def mqtt_client(self):
        """
        Fixture to create a mock MQTT client for testing
        """
        client = WinterSupplementMQTTClient()
        client.client = MagicMock(spec=mqtt.Client)
        return client

    def test_mqtt_connection_success(self, mqtt_client):
        """
        Integration test for successful MQTT connection
        """
        mqtt_client.client.connect.return_value = 0
        with patch('time.sleep'):
            mqtt_client.connect()

        mqtt_client.client.connect.assert_called_once_with(MQTT_BROKER, MQTT_PORT)
        mqtt_client.client.loop_forever.assert_called_once()

    def test_on_connect_with_specific_topic_id(self, mqtt_client):
        """
        Test successful MQTT connection with a specific topic ID
        """
        # Mock the environment variable for a specific topic ID
        with patch.dict(os.environ, {'MQTT_TOPIC_ID': 'specific_test_topic'}):
            # Reinitialize the client to pick up the environment variable
            mqtt_client = WinterSupplementMQTTClient()
            mock_client = Mock()
            mqtt_client.client = mock_client

            # Simulate successful connection (rc = 0)
            mqtt_client._on_connect(mock_client, None, None, 0)

            # Verify subscription to the specific topic
            expected_topic = f"{MQTT_INPUT_TOPIC_BASE}specific_test_topic"
            mock_client.subscribe.assert_called_once_with(expected_topic)

    def test_message_processing(self, mqtt_client):
        """
        Integration test for message processing workflow
        """
        # Mock input data
        input_data = {
            "id": "test_integration",
            "numberOfChildren": 1,
            "familyComposition": "single",
            "familyUnitInPayForDecember": True
        }

        # Simulate message reception and processing
        msg = MagicMock()
        msg.topic = f"{MQTT_INPUT_TOPIC_BASE}test_integration"
        msg.payload = json.dumps(input_data).encode()

        # Call message processing method
        mqtt_client._on_message(mqtt_client.client, None, msg)

        # Verify publishing of result
        mqtt_client.client.publish.assert_called_once()
        published_topic = mqtt_client.client.publish.call_args[0][0]
        published_payload = json.loads(mqtt_client.client.publish.call_args[0][1])

        assert published_topic == f"{MQTT_OUTPUT_TOPIC_BASE}test_integration"
        assert published_payload['id'] == "test_integration"
        assert published_payload['isEligible'] is True

    def test_on_connect_success(self, mqtt_client):
        """
        Test successful MQTT broker connection
        """
        # Mock the client's subscribe method
        mock_client = Mock()
        mqtt_client.client = mock_client

        # Simulate successful connection (rc = 0)
        mqtt_client._on_connect(mock_client, None, None, 0)

        # Verify subscription to input topics
        mock_client.subscribe.assert_called_once_with(f"{MQTT_INPUT_TOPIC_BASE}+")

    def test_on_connect_failure(self, caplog, mqtt_client):
        """
        Test connection failure logging
        """
        # Mock the client
        mock_client = Mock()
        mqtt_client.client = mock_client

        # Simulate connection failure (rc != 0)
        mqtt_client._on_connect(mock_client, None, None, 1)

        # Check error log was created
        assert "Failed to connect. Return code: 1" in caplog.text

    def test_on_message_invalid_json(self, caplog, mqtt_client):
        """
        Test handling of invalid JSON input
        """
        # Mock MQTT client and message with invalid JSON
        mock_client = Mock()
        mqtt_client.client = mock_client

        mock_msg = Mock()
        mock_msg.topic = f"{MQTT_INPUT_TOPIC_BASE}unique_topic_id"
        mock_msg.payload.decode.return_value = "Invalid JSON"

        # Call the on_message method
        mqtt_client._on_message(mock_client, None, mock_msg)

        # Verify error logging
        assert "Invalid JSON received" in caplog.text

    def test_on_message_input_validation_failure(self, caplog, mqtt_client):
        """
        Test handling of input validation failure
        """
        # Mock MQTT client and message with invalid input data
        mock_client = Mock()
        mqtt_client.client = mock_client

        # Create an input data that will fail validation
        mock_msg = Mock()
        mock_msg.topic = f"{MQTT_INPUT_TOPIC_BASE}invalid_input"
        invalid_input_data = {
            "id": "invalid_input",
            # Missing required fields to trigger validation error
        }
        mock_msg.payload = json.dumps(invalid_input_data).encode()

        # Patch the validate_input function to raise an exception
        with patch('winter_supplement_engine.schemas.validate_input', side_effect=ValueError("Validation failed")):
            # Call the on_message method
            mqtt_client._on_message(mock_client, None, mock_msg)

        # Verify error logging
        assert "Input validation failed" in caplog.text

    def test_on_message_general_exception(self, caplog, mqtt_client):
        """
        Test handling of a general unexpected exception
        """
        # Mock MQTT client and message
        mock_client = Mock()
        mqtt_client.client = mock_client

        # Create an input data
        mock_msg = Mock()
        mock_msg.topic = f"{MQTT_INPUT_TOPIC_BASE}exception_test"
        input_data = {
            "id": "exception_test",
            "numberOfChildren": 1,
            "familyComposition": "single",
            "familyUnitInPayForDecember": True
        }
        mock_msg.payload = json.dumps(input_data).encode()

        # Patch the calculate method to raise an unexpected exception
        with patch('winter_supplement_engine.calculator.WinterSupplementCalculator.calculate_supplement',
                   side_effect=Exception("Unexpected error")):
            # Call the on_message method
            mqtt_client._on_message(mock_client, None, mock_msg)

        # Verify error logging
        assert "Error processing message" in caplog.text
        assert "Unexpected error" in caplog.text

        # Ensure no publishing occurred
        mock_client.publish.assert_not_called()

    def test_connect_max_retries_exceeded(self, caplog, mqtt_client):
        """
        Test that the maximum retries error is logged after exhausting connection attempts.
        """
        from winter_supplement_engine.mqtt_client import WinterSupplementMQTTClient

        # Create an instance of the client
        mqtt_client = WinterSupplementMQTTClient()

        # Patch the connect method of the MQTT client to always raise an exception
        with patch.object(mqtt.Client, 'connect', side_effect=Exception("Mocked connection failure")):
            # Run the connect method
            with patch('time.sleep', return_value=None):  # Avoid actual delays in test
                mqtt_client.connect()

        # Verify the log contains the maximum retries error
        assert "Maximum connection attempts reached. Exiting." in caplog.text

    def test_on_message_output_validation_failure(self, caplog, mqtt_client):
        """
        Test handling of output validation failure
        """
        # Mock MQTT client and message with valid input
        mock_client = Mock()
        mqtt_client.client = mock_client

        # Create an input data that will process normally
        mock_msg = Mock()
        mock_msg.topic = f"{MQTT_INPUT_TOPIC_BASE}output_validation_test"
        input_data = {
            "id": "output_validation_test",
            "numberOfChildren": 1,
            "familyComposition": "single",
            "familyUnitInPayForDecember": True
        }
        mock_msg.payload = json.dumps(input_data).encode()

        # Create a mock result that will fail validation
        mock_result = {
            "id": "output_validation_test",
            # Missing required fields to trigger validation error
        }

        # Patch the calculate_supplement method to return a result that will fail validation
        with patch('winter_supplement_engine.calculator.WinterSupplementCalculator.calculate_supplement',
                   return_value=mock_result), \
                patch('winter_supplement_engine.schemas.validate_output',
                      side_effect=ValueError("Output validation failed")):
            # Call the on_message method
            mqtt_client._on_message(mock_client, None, mock_msg)

        # Verify error logging
        assert any("Output validation failed" in record.message for record in caplog.records)

        # Ensure no publishing occurred
        mock_client.publish.assert_not_called()
