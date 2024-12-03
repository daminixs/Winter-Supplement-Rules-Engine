# Winter-Supplement-Rules-Engine
* * *

**Project Overview**

The **Winter Supplement Rules Engine** determines eligibility and calculates the winter supplement amount based on predefined rules. It uses MQTT for messaging, JSON for data interchange and supports a frontend interface for easy interaction.

#### **Features Implemented:**

* **Rules Engine**: Implements policies for winter supplement calculations.
* **MQTT Integration**: Real-time messaging support via MQTT protocol.
* **Configurable**: Easy to adapt using `.env` files and JSON schemas.
* **Input/Output Validation**: Ensures incoming data and output data adheres to predefined JSON schemas.
* **Frontend Interface**: Interactive UI (if applicable) for managing inputs and outputs.
* **Testing Suite**: Comprehensive tests to ensure reliability and edge-case coverage.

* * *

# Table of Contents

1. [Directory Structure](#directory-structure)
2. [Setting Up Instructions](#setting-up-instructions)
3. [Running the Application](#running-the-application)
4. [MQTT Broker Setup/ Configuration](#mqtt-broker-setupconfiguration)
5. [Testing](#testing)
6. [Messaging Format](#messaging-format)
7. [Demo with Frontend](#demo-with-frontend)
8. [Conclusion](#conclusion)

# **Directory Structure**

    Winter Supplement Calculator/
    │
    ├── frontend/                 # Contains frontend files (UI)
    ├── main.py                   # Entry point for the application
    ├── pytest.ini                # Test configuration
    ├── requirements.txt          # Dependencies list
    ├── tests/                    # Unit and integration tests
    ├── winter_supplement_engine/ # Core logic and utilities
    │   ├── mqtt_client.py        # MQTT client implementation
    │   ├── config.py             # Configuration settings
    │   └── ...                   # Other modules
    └── README.md                 # Project documentation

* * *

# **Setting Up Instructions**

Prerequisites:

### System Requirements

* Python 3.12+
* pip (Python package manager)
* Internet connection for MQTT broker

### Required Tools

* Git
* Virtual environment tool (recommended: `venv`)

* * *

Installation and Setup:

### 1. Clone the Repository

    git clone https://github.com/daminixs/Winter-Supplement-Rules-Engine.git  
    cd Winter-Supplement-Rules-Engine  

### 2. Create a Virtual Environment

    # On Unix/macOS  
    python3 -m venv venv  
    source venv/bin/activate  
    
    # On Windows  
    python -m venv venv  
    venv\Scripts\activate  

### 3. Install Dependencies

    pip install -r requirements.txt  

* * *

# Running the Application

Optional Step: Defaults have been already set according to requirements, to modify mqtt broker config refer to [MQTT Broker Setup/Configuration](# mqtt-broker-setup/configuration) .

### Start the Rules Engine:

    python main.py  

### Integration with Winter Supplement Web App:

* **Option 1: Integration with the Existing Web App** - Refer to the relevant section for detailed instructions.
* **Option 2: Custom Web App Demo** - (add website link) or open `frontend/winter-supplement-calculator.html`.

### Comprehensive Tests for Each Module:

    # Run all tests  
    pytest tests/  
    
    # Run a specific test file  
    pytest tests/test_calculator.py  
    
    # Generate a coverage report
    pytest --cov=winter_supplement_engine tests/

* * *

# MQTT Broker Setup/Configuration

To configure these options, create a `.env` file in the project root with the desired values or copy the existing example env file and edit:

    cp .env.example .env 

### MQTT Topic Handling

You can configure the `MQTT_TOPIC_ID` in the `.env` file for more precise topic handling:

1. **When `MQTT_TOPIC_ID` is set (e.g., `MQTT_TOPIC_ID=123`)**:
  
  * The MQTT client will subscribe to the specific topic `BRE/calculateWinterSupplementInput/123`.
  * The rules engine will only process messages with the topic ID `123`, ensuring focused operation.
2. **When `MQTT_TOPIC_ID` is not set**:
  
  * The MQTT client will subscribe to the wildcard topic `BRE/calculateWinterSupplementInput/+`.
  * It will process all messages received on the wildcard topic.

This flexibility allows the engine to handle both broad and specific use cases depending on the configuration.

### Other Configuration Options

* **MQTT_BROKER**: MQTT broker address (default: `test.mosquitto.org`)
* **MQTT_PORT**: Broker port (default: `1883`)
* **LOG_LEVEL**: Logging verbosity (options: `DEBUG`, `INFO`, `WARNING`, `ERROR`; default: `INFO`)
* **MQTT_INPUT_TOPIC_BASE**: Input message topic base (default: `BRE/calculateWinterSupplementInput/`)
* **MQTT_OUTPUT_TOPIC_BASE**: Output message topic base (default: `BRE/calculateWinterSupplementOutput/`)
* **MAX_RETRIES**: Maximum number of connection retries (default: `5`)
* **RETRY_DELAY**: Delay in seconds between retries (default: `3`)

You can modify these options by setting the corresponding environment variables in your configuration.

* * *

# Testing

Testing is segmented into four specialized test files, each addressing distinct aspects of the application.

* * *

#### **1. Calculation Tests (`calculation-tests.py`)**

**Purpose:** Ensure accurate and consistent supplement calculations.

**Key Scenarios:**

* Diverse family configurations (single, couples, with/without children).
* Edge cases (zero or extreme child counts, non-eligibility scenarios).
* Type safety, ensuring immutability and correct data types.

#### **2. MQTT Integration Tests (`mqtt-integration-tests.py`)**

**Purpose:** Validate reliable message handling in the MQTT workflow.

**Key Scenarios:**

* Connection management (successful connections, retries on failure).
* Message processing (valid/invalid inputs, schema validation).
* Topic management (subscriptions and payloads).

#### **3. Performance and Stress Tests (`performance-stress-tests.py`)**

**Purpose:** Evaluate system scalability, throughput, and memory efficiency.

**Key Scenarios:**

* Performance under increasing calculation volumes.
  
* Monitoring memory usage for leaks and inefficiencies.
  
* Simulating concurrent calculations for thread safety.
  

**4. Validation Tests (`validation-tests.py`)**

**Purpose:** Enforce strict input/ output validation and security standards.

**Key Scenarios:**

* Validating schema compliance and type correctness.
* Rejection of invalid inputs (missing fields, negative counts).
* Security checks (input sanitization, XSS prevention).

* * *

Following strict data format requirements are enforced:

### Sample Input

    {
        "id": "client123",
        "numberOfChildren": 2,
        "familyComposition": "couple",
        "familyUnitInPayForDecember": true
    }

### Sample Output

    {
        "id": "client123",
        "isEligible": true,
        "baseAmount": 120.0,
        "childrenAmount": 40.0,
        "supplementAmount": 160.0
    }

* * *

# Web App Integration and Demo with Frontend

### Integration with Existing Winter Supplement Web App

The rules engine can be integrated with the existing Winter Supplement web app as follows:

1. Log in to the Winter Supplement web app to generate a unique topic ID.
2. Add the generated topic ID to the `.env` file as specified in the configuration section.
3. Run the rules engine.

The web app generates input data and publishes it to the MQTT topic:`BRE/calculateWinterSupplementInput/<MQTT_TOPIC_ID>`.

The rules engine processes and validates the input, calculates results, and publishes them in the specified format to the MQTT topic:`BRE/calculateWinterSupplementOutput/<MQTT_TOPIC_ID>`.

This workflow was verified using **MQTT Explorer**. However, the provided web app was not displaying the result.

Despite extensive troubleshooting, the exact cause could not be identified. However, the issue might originate from mismatched IDs in the GET and POST requests. While monitoring the network tab, it was observed that the GET and POST requests were using different IDs. However, without backend source code, it can not be confirmed if this discrepancy is the root cause. There is a possibility that this behavior is intentional (as there is no strict requirement for the requests to use the same ID) and the issue could entirely lie elsewhere.

* * *

### Custom Frontend Solution

To address the display issue and ensure a seamless testing experience, a custom frontend application was developed. This frontend utilizes the **Paho MQTT client library** to communicate with the MQTT broker over WebSockets and mirrors the functionality of the provided web app.

Key features include:

1. Publishing input data to the MQTT topic:`BRE/calculateWinterSupplementInput/<MQTT_TOPIC_ID>`.
2. Subscribing to the corresponding output topic:`BRE/calculateWinterSupplementOutput/<MQTT_TOPIC_ID>`, to retrieve and display processed results.

The **MQTT_TOPIC_ID** is dynamically generated for each session using the UUID library, similar to the provided app.

* * *

### How to Use

The **Winter Supplement Frontend Application** is hosted via GitHub Pages for accessibility and demonstration purposes. It can also be downloaded and executed locally.

1. Access the application (via GitHub Pages link or locally).
2. Input the required data (family composition, number of children, and December eligibility).
3. Submit the data to the MQTT server.
4. View the calculated results displayed in real-time on the application page.

gif/video

* * *

# Conclusion

The Winter Supplement Calculator ensures seamless communication with the web application via MQTT for real-time input and output handling. It accurately determines eligibility based on the familyUnitInPayForDecember field, returning 0.0 for ineligible clients. The engine precisely calculates base amounts, additional amounts for children, and total supplements, adhering strictly to defined rules. Comprehensive testing ensures reliability, scalability, and accuracy, making it a robust solution for winter supplement processing.
