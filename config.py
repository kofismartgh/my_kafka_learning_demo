"""
Kafka Configuration
Easy switching between local Docker and AWS MSK environments
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment configuration
ENVIRONMENT = os.getenv('KAFKA_ENV', 'local')  # 'local' or 'aws'

# Local Docker Kafka configuration
# Local Docker Kafka configuration
LOCAL_CONFIG = {
    'bootstrap.servers': 'localhost:9092',
    'security.protocol': 'PLAINTEXT',
    'auto.offset.reset': 'earliest',
    'api.version.request': True,
    'api.version.fallback.ms': 0,
    'broker.version.fallback': '0.10.0.0'
}
# AWS MSK configuration (update with your MSK cluster details)
AWS_CONFIG = {
    'bootstrap.servers': os.getenv('MSK_BOOTSTRAP_SERVERS', 'your-msk-cluster-endpoint:9092'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'AWS_MSK_IAM',
    'sasl.aws.region': os.getenv('AWS_REGION', 'us-east-1'),
    'auto.offset.reset': 'earliest'
}

def get_kafka_config():
    """
    Returns Kafka configuration based on environment
    """
    if ENVIRONMENT.lower() == 'aws':
        return AWS_CONFIG
    else:
        return LOCAL_CONFIG

def get_environment():
    """Returns current environment"""
    return ENVIRONMENT
