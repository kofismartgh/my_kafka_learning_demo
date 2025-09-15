#!/usr/bin/env python3
"""
Test script to demonstrate Kafka producer and consumer functionality
This script helps test the setup by sending sample messages
"""
import requests
import time
import json
import sys

def test_producer_api():
    """
    Test the producer API by sending sample messages
    """
    base_url = "http://localhost:5000"
    
    # Test messages
    test_messages = [
        {"topic": "payments", "msg": "Payment processed for order 12345"},
        {"topic": "orders", "msg": "New order created: Order #67890"},
        {"topic": "logs", "msg": "Application started successfully"},
        {"topic": "payments", "msg": "Refund processed for order 12345"},
        {"topic": "orders", "msg": "Order #67890 shipped"},
    ]
    
    print("🧪 Testing Kafka Producer API")
    print("=" * 50)
    
    for i, test_msg in enumerate(test_messages, 1):
        try:
            print(f"\n📤 Sending test message {i}/{len(test_messages)}")
            print(f"   Topic: {test_msg['topic']}")
            print(f"   Message: {test_msg['msg']}")
            
            response = requests.get(f"{base_url}/produce", params=test_msg)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("   ✅ Success!")
                else:
                    print(f"   ❌ Failed: {result.get('error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection Error: Make sure the producer is running on port 5000")
            break
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Small delay between messages
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

def check_producer_health():
    """
    Check if the producer API is running and healthy
    """
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Producer API is healthy")
            print(f"   Environment: {health_data.get('environment')}")
            return True
        else:
            print(f"❌ Producer API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Producer API is not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Error checking producer health: {str(e)}")
        return False

def main():
    """
    Main function
    """
    print("🚀 Kafka Test Script")
    print("=" * 50)
    
    # Check if producer is running
    if not check_producer_health():
        print("\n💡 To start the producer, run:")
        print("   python producer.py")
        print("\n💡 To start Kafka locally, run:")
        print("   docker-compose up -d")
        sys.exit(1)
    
    # Run tests
    test_producer_api()
    
    print("\n💡 To consume messages, run:")
    print("   python consumer.py payments")
    print("   python consumer.py orders")
    print("   python consumer.py logs")

if __name__ == "__main__":
    main()
