#!/usr/bin/env python3
"""
Kafka Connection Diagnostic Script
Helps identify the correct configuration for your Kafka setup
"""
import socket
import ssl
from confluent_kafka import Producer, Consumer, KafkaError
import json

def test_connection(host, port):
    """Test basic TCP connection"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

def test_ssl_connection(host, port):
    """Test SSL connection"""
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        ssl_sock = context.wrap_socket(sock, server_hostname=host)
        ssl_sock.connect((host, port))
        ssl_sock.close()
        return True
    except Exception as e:
        print(f"SSL connection test failed: {e}")
        return False

def test_kafka_config(config, config_name):
    """Test Kafka configuration"""
    print(f"\n🔍 Testing {config_name} configuration:")
    print(f"   Config: {config}")
    
    try:
        producer = Producer(config)
        
        # Try to get metadata (this will trigger the API version request)
        metadata = producer.list_topics(timeout=10)
        print(f"   ✅ Success! Found {len(metadata.topics)} topics")
        
        # List some topics
        if metadata.topics:
            print("   📋 Available topics:")
            for topic_name in list(metadata.topics.keys())[:5]:  # Show first 5 topics
                print(f"      - {topic_name}")
        else:
            print("   📋 No topics found (this is normal for a fresh Kafka setup)")
        
        producer.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Failed: {str(e)}")
        return False

def main():
    print("🔍 Kafka Connection Diagnostic Tool")
    print("=" * 50)
    
    host = "localhost"
    port = 9092
    
    # Test 1: Basic TCP connection
    print(f"\n1️⃣ Testing basic TCP connection to {host}:{port}")
    if test_connection(host, port):
        print("   ✅ TCP connection successful")
    else:
        print("   ❌ TCP connection failed")
        print("   💡 Make sure Kafka is running and accessible on this port")
        return
    
    # Test 2: SSL connection
    print(f"\n2️⃣ Testing SSL connection to {host}:{port}")
    if test_ssl_connection(host, port):
        print("   ✅ SSL connection successful")
        ssl_available = True
    else:
        print("   ❌ SSL connection failed (this is normal for PLAINTEXT setup)")
        ssl_available = False
    
    # Test 3: Different Kafka configurations
    configs_to_test = [
        {
            'name': 'PLAINTEXT (current)',
            'config': {
                'bootstrap.servers': f'{host}:{port}',
                'security.protocol': 'PLAINTEXT',
                'api.version.request': True,
                'api.version.fallback.ms': 0,
                'broker.version.fallback': '0.10.0.0'
            }
        },
        {
            'name': 'PLAINTEXT (no API version request)',
            'config': {
                'bootstrap.servers': f'{host}:{port}',
                'security.protocol': 'PLAINTEXT',
                'api.version.request': False
            }
        },
        {
            'name': 'PLAINTEXT (with timeout)',
            'config': {
                'bootstrap.servers': f'{host}:{port}',
                'security.protocol': 'PLAINTEXT',
                'api.version.request': True,
                'api.version.fallback.ms': 0,
                'broker.version.fallback': '0.10.0.0',
                'socket.timeout.ms': 10000,
                'metadata.request.timeout.ms': 10000
            }
        }
    ]
    
    # Add SSL config if SSL is available
    if ssl_available:
        configs_to_test.append({
            'name': 'SSL',
            'config': {
                'bootstrap.servers': f'{host}:{port}',
                'security.protocol': 'SSL',
                'api.version.request': True,
                'api.version.fallback.ms': 0,
                'broker.version.fallback': '0.10.0.0'
            }
        })
    
    print(f"\n3️⃣ Testing different Kafka configurations:")
    successful_configs = []
    
    for config_test in configs_to_test:
        if test_kafka_config(config_test['config'], config_test['name']):
            successful_configs.append(config_test)
    
    # Results
    print(f"\n📊 Results:")
    print("=" * 50)
    
    if successful_configs:
        print("✅ Working configurations found:")
        for config in successful_configs:
            print(f"   - {config['name']}")
            print(f"     {config['config']}")
        
        print(f"\n💡 Recommended configuration for your config.py:")
        best_config = successful_configs[0]['config']
        print(f"LOCAL_CONFIG = {best_config}")
        
    else:
        print("❌ No working configurations found")
        print("\n🔧 Troubleshooting suggestions:")
        print("   1. Check if Kafka is fully started: docker logs <kafka_container>")
        print("   2. Verify the port mapping: docker port <kafka_container>")
        print("   3. Check Kafka broker configuration for listeners")
        print("   4. Try different ports (9093, 9094) if your Kafka uses different mapping")

if __name__ == "__main__":
    main()
