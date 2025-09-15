"""
Kafka Producer Flask Application
Exposes a REST API to produce messages to Kafka topics
"""
from flask import Flask, request, jsonify
from confluent_kafka import Producer
import json
import logging
from config import get_kafka_config, get_environment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Kafka producer
kafka_config = get_kafka_config()
producer = Producer(kafka_config)

def delivery_callback(err, msg):
    """
    Callback function to handle message delivery confirmation
    This is called when Kafka confirms the message was sent
    """
    if err:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')

@app.route('/produce', methods=['GET'])
def produce_message():
    """
    GET endpoint to produce messages to Kafka
    
    Query Parameters:
    - topic: Kafka topic name (required)
    - msg: Message content (required)
    
    Returns:
    - JSON response with success/failure status
    """
    try:
        # Get query parameters
        topic = request.args.get('topic')
        message = request.args.get('msg')
        
        # Validate required parameters
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic parameter is required'
            }), 400
            
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message parameter is required'
            }), 400
        
        # Create message payload
        from datetime import datetime
        message_data = {
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'environment': get_environment()
        }
        
        # Convert to JSON string
        message_json = json.dumps(message_data)
        
        # Produce message to Kafka
        # The produce() method is asynchronous - it returns immediately
        producer.produce(
            topic=topic,
            value=message_json,
            callback=delivery_callback
        )
        
        # Wait for any outstanding messages to be delivered
        # This ensures the message is actually sent before responding
        producer.flush(timeout=10)
        
        logger.info(f'Successfully produced message to topic: {topic}')
        
        return jsonify({
            'success': True,
            'message': 'Message produced successfully',
            'topic': topic,
            'data': message_data
        })
        
    except Exception as e:
        logger.error(f'Error producing message: {str(e)}')
        return jsonify({
            'success': False,
            'error': f'Failed to produce message: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'environment': get_environment(),
        'kafka_config': kafka_config
    })

@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint with usage instructions
    """
    return jsonify({
        'message': 'Kafka Producer API',
        'endpoints': {
            'produce': 'GET /produce?topic=<topic_name>&msg=<message>',
            'health': 'GET /health'
        },
        'example': 'GET /produce?topic=payments&msg=Payment processed for order 123'
    })

if __name__ == '__main__':
    logger.info(f'Starting Kafka Producer API in {get_environment()} environment')
    logger.info(f'Kafka config: {kafka_config}')
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
