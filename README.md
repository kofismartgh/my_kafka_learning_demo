# Kafka Learning Environment

A comprehensive Kafka testing setup for SREs to understand and troubleshoot Kafka in production environments. This setup includes both local Docker-based Kafka and AWS MSK configuration support.

## 🏗️ Architecture

- **Producer**: Flask REST API that accepts messages via HTTP and publishes to Kafka
- **Consumer**: CLI application that consumes messages from specified topics
- **Kafka**: Local Docker setup with Zookeeper, Kafka broker, and Kafka UI
- **Configuration**: Easy switching between local and AWS MSK environments

## 📁 Project Structure

```
kafka-learn/
├── producer.py          # Flask API for producing messages
├── consumer.py          # CLI consumer application
├── config.py            # Configuration management (local vs AWS)
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Local Kafka setup
├── test_script.py       # Automated testing script
├── env.template         # Environment configuration template
└── README.md           # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or install individually
pip install flask confluent-kafka python-dotenv requests
```

### 2. Start Local Kafka (Docker)

```bash
# Start Kafka, Zookeeper, and Kafka UI
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f kafka
```

### 3. Start the Producer API

```bash
# In one terminal
python producer.py
```

The API will be available at `http://localhost:5000`

### 4. Start the Consumer

```bash
# In another terminal
python consumer.py payments
```

### 5. Test the Setup

```bash
# Run the automated test script
python test_script.py

# Or manually test with curl
curl "http://localhost:5000/produce?topic=payments&msg=Test payment"
```

## 🔧 Configuration

### Local Environment (Default)

The setup uses local Docker Kafka by default. No additional configuration needed.

### AWS MSK Environment

1. Copy the environment template:
   ```bash
   cp env.template .env
   ```

2. Update `.env` with your MSK details:
   ```bash
   KAFKA_ENV=aws
   MSK_BOOTSTRAP_SERVERS=your-msk-cluster-endpoint:9092
   AWS_REGION=us-east-1
   ```

3. Ensure AWS credentials are configured (IAM role, AWS CLI, or environment variables)

## 📖 Usage Examples

### Producer API Endpoints

```bash
# Health check
curl http://localhost:5000/health

# Produce a message
curl "http://localhost:5000/produce?topic=payments&msg=Payment processed"

# API documentation
curl http://localhost:5000/
```

### Consumer Examples

```bash
# Consume from payments topic
python consumer.py payments

# Consume from orders topic
python consumer.py orders

# Consume from logs topic
python consumer.py logs
```

### Testing Different Scenarios

```bash
# Test with multiple topics
python test_script.py

# Test error handling (missing parameters)
curl "http://localhost:5000/produce?topic=payments"
curl "http://localhost:5000/produce?msg=test"
```

## 🔍 Monitoring and Troubleshooting

### Kafka UI

Access the web interface at `http://localhost:8080` to:
- View topics and messages
- Monitor consumer groups
- Check broker status
- Browse message contents

### Common Issues

1. **Connection Refused**: Ensure Kafka is running (`docker-compose ps`)
2. **Topic Not Found**: Topics are auto-created, but check Kafka UI
3. **Consumer Not Receiving Messages**: Check topic name and consumer group
4. **Producer Errors**: Check Kafka broker logs (`docker-compose logs kafka`)

### Logs and Debugging

```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs kafka
docker-compose logs zookeeper

# Follow logs in real-time
docker-compose logs -f kafka
```

## 🏢 Production Considerations

### For AWS MSK

1. **Security**: Use IAM roles and VPC security groups
2. **Monitoring**: Enable CloudWatch metrics and logs
3. **Scaling**: Configure auto-scaling based on metrics
4. **Backup**: Enable MSK cluster backup and point-in-time recovery

### For Local Development

1. **Data Persistence**: Volumes are configured for data persistence
2. **Resource Limits**: Adjust Docker resource limits as needed
3. **Network**: Ensure ports 9092, 8080, and 5000 are available

## 🧪 Testing Scenarios

### Basic Functionality
- Produce messages to different topics
- Consume messages from topics
- Verify message ordering and delivery

### Error Handling
- Invalid topic names
- Network connectivity issues
- Kafka broker failures

### Performance Testing
- High message throughput
- Large message sizes
- Multiple consumer groups

## 📚 Learning Resources

- [Confluent Kafka Python Client](https://docs.confluent.io/kafka-clients/python/current/overview.html)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [AWS MSK Developer Guide](https://docs.aws.amazon.com/msk/latest/developerguide/)

## 🛠️ Development

### Adding New Features

1. **New Producer Endpoints**: Add routes in `producer.py`
2. **Consumer Filters**: Modify `consumer.py` for message filtering
3. **Configuration Options**: Update `config.py` for new settings

### Code Structure

- **Producer**: Flask app with async message production
- **Consumer**: Polling-based consumer with error handling
- **Configuration**: Environment-based config switching
- **Testing**: Automated test script with sample data

## 🚨 Troubleshooting Guide

### Producer Issues

```bash
# Check if producer is running
curl http://localhost:5000/health

# Check producer logs
python producer.py  # Run in foreground to see logs
```

### Consumer Issues

```bash
# Check topic exists
docker exec kafka-broker kafka-topics --bootstrap-server localhost:9092 --list

# Check consumer group
docker exec kafka-broker kafka-consumer-groups --bootstrap-server localhost:9092 --list
```

### Kafka Issues

```bash
# Check broker status
docker-compose ps

# Restart services
docker-compose restart

# Clean restart (removes data)
docker-compose down -v
docker-compose up -d
```

This setup provides a solid foundation for understanding Kafka operations and troubleshooting in production environments.
