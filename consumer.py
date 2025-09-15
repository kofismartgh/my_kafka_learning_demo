"""
Kafka Consumer CLI Application
Consumes messages from a specified Kafka topic
"""
import sys
import json
import logging
from confluent_kafka import Consumer, KafkaError
from config import get_kafka_config, get_environment

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def consume_messages(topic_name):
    """
    Consume messages from the specified Kafka topic
    
    Args:
        topic_name (str): Name of the Kafka topic to consume from
    """
    try:
        # Get Kafka configuration
        kafka_config = get_kafka_config()
        
        # Add consumer-specific configuration
        consumer_config = kafka_config.copy()
        consumer_config.update({
            'group.id': 'kafka-learn-consumer-group',
            'enable.auto.commit': True,
            'auto.commit.interval.ms': 1000,
            'session.timeout.ms': 30000,
            'max.poll.interval.ms': 300000
        })
        
        # Create consumer
        consumer = Consumer(consumer_config)
        
        logger.info(f'Starting consumer for topic: {topic_name}')
        logger.info(f'Environment: {get_environment()}')
        logger.info(f'Kafka config: {kafka_config}')
        
        # Subscribe to topic
        consumer.subscribe([topic_name])
        
        print(f"\n🚀 Consumer started! Listening to topic: '{topic_name}'")
        print("Press Ctrl+C to stop the consumer\n")
        print("-" * 60)
        
        # Message consumption loop
        message_count = 0
        try:
            while True:
                # Poll for messages (timeout after 1 second)
                msg = consumer.poll(timeout=1.0)
                
                if msg is None:
                    # No message received within timeout
                    continue
                    
                if msg.error():
                    # Handle errors
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event - not an error
                        logger.debug(f'End of partition reached for {msg.topic()} [{msg.partition()}]')
                        continue
                    else:
                        logger.error(f'Consumer error: {msg.error()}')
                        continue
                
                # Process the message
                message_count += 1
                try:
                    # Try to parse as JSON first
                    message_data = json.loads(msg.value().decode('utf-8'))
                    print(f"📨 Message #{message_count}")
                    print(f"   Topic: {msg.topic()}")
                    print(f"   Partition: {msg.partition()}")
                    print(f"   Offset: {msg.offset()}")
                    print(f"   Timestamp: {message_data.get('timestamp', 'N/A')}")
                    print(f"   Environment: {message_data.get('environment', 'N/A')}")
                    print(f"   Content: {message_data.get('message', 'N/A')}")
                    print("-" * 60)
                    
                except json.JSONDecodeError:
                    # If not JSON, print as plain text
                    print(f"📨 Message #{message_count}")
                    print(f"   Topic: {msg.topic()}")
                    print(f"   Partition: {msg.partition()}")
                    print(f"   Offset: {msg.offset()}")
                    print(f"   Content: {msg.value().decode('utf-8')}")
                    print("-" * 60)
                    
        except KeyboardInterrupt:
            print(f"\n\n🛑 Consumer stopped by user")
            print(f"📊 Total messages consumed: {message_count}")
            
    except Exception as e:
        logger.error(f'Error in consumer: {str(e)}')
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
        
    finally:
        # Close consumer
        if 'consumer' in locals():
            consumer.close()
            logger.info('Consumer closed')

def main():
    """
    Main function - handles command line arguments
    """
    if len(sys.argv) != 2:
        print("Usage: python consumer.py <topic_name>")
        print("\nExample:")
        print("  python consumer.py payments")
        print("  python consumer.py orders")
        print("  python consumer.py logs")
        sys.exit(1)
    
    topic_name = sys.argv[1]
    
    # Validate topic name
    if not topic_name or not topic_name.strip():
        print("❌ Error: Topic name cannot be empty")
        sys.exit(1)
    
    # Start consuming messages
    consume_messages(topic_name.strip())

if __name__ == '__main__':
    main()
