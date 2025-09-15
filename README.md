# My Kafka Learning Journey 🚀

Hey there! This is my personal Kafka playground where I'm learning how Kafka works from an SRE perspective. I built this to understand the ins and outs of Kafka - from basic message passing to production configurations and troubleshooting.

## What I Built Here

- **Producer**: A simple Flask API that I can hit with HTTP requests to send messages to Kafka
- **Consumer**: A CLI tool that shows me messages in real-time as they come through
- **Kafka Setup**: Local Docker setup so I can experiment without breaking anything
- **Config Management**: Easy switching between my local setup and AWS MSK (for when I'm ready to go cloud)

## Why I Made This

As an SRE, I needed to understand:
- How Kafka actually works under the hood
- What happens when brokers fail
- How replication and partitioning work
- How to troubleshoot common issues
- What production configurations look like

## 📁 What's in This Project

```
kafka-learn/
├── producer.py          # My Flask API - hit this to send messages
├── consumer.py          # My CLI tool - run this to see messages
├── config.py            # Smart config switching (local vs AWS)
├── requirements.txt     # Python stuff I need
├── docker-compose.yml   # My local Kafka setup
├── test_script.py       # Helper script to test everything
├── diagnose_kafka.py    # Debug tool I made when things broke
├── KAFKA_CONFIG_GUIDE.md # My SRE notes on Kafka configs
└── README.md           # This file
```

## 🚀 Let's Get This Running

### Step 1: Install the Python Stuff

```bash
# Install what I need
pip install -r requirements.txt

# Or if you want to be specific
pip install flask confluent-kafka python-dotenv requests
```

### Step 2: Start My Kafka (I'm using Docker)

```bash
# Fire up Kafka, Zookeeper, and the UI
docker-compose up -d

# Make sure everything is running
docker-compose ps

# Check the logs if something's wrong
docker-compose logs -f kafka
```

### Step 3: Start My Producer API

```bash
# In one terminal
python producer.py
```

Now I can hit `http://localhost:5000` to send messages!

### Step 4: Start My Consumer

```bash
# In another terminal
python consumer.py payments
```

This will show me messages as they come through in real-time.

### Step 5: Test It Out

```bash
# Use my test script
python test_script.py

# Or manually send a message
curl "http://localhost:5000/produce?topic=payments&msg=Test payment"
```

## 🔧 How I Switch Between Environments

### Local Development (What I Use Most)

By default, everything points to my local Docker Kafka. No extra setup needed - just works!

### AWS MSK (When I Want to Go Cloud)

1. Copy the template:
   ```bash
   cp env.template .env
   ```

2. Update `.env` with my MSK details:
   ```bash
   KAFKA_ENV=aws
   MSK_BOOTSTRAP_SERVERS=my-msk-cluster-endpoint:9092
   AWS_REGION=us-east-1
   ```

3. Make sure my AWS credentials are set up

## 📖 How I Use This Stuff

### My Producer API

```bash
# Check if it's healthy
curl http://localhost:5000/health

# Send a message
curl "http://localhost:5000/produce?topic=payments&msg=Payment processed"

# See what endpoints are available
curl http://localhost:5000/
```

### My Consumer

```bash
# Watch payments
python consumer.py payments

# Watch orders
python consumer.py orders

# Watch logs
python consumer.py logs
```

### Testing Things Out

```bash
# Run my test script (sends a bunch of sample messages)
python test_script.py

# Test error handling
curl "http://localhost:5000/produce?topic=payments"  # Missing message
curl "http://localhost:5000/produce?msg=test"        # Missing topic
```

## 🔍 How I Monitor and Debug

### Kafka UI (My Favorite Tool)

I can access the web interface at `http://localhost:8080` to:
- See all my topics and messages
- Watch consumer groups in action
- Check if brokers are healthy
- Browse through message contents

### Common Issues I've Hit

1. **Connection Refused**: Usually means Kafka isn't running (`docker-compose ps`)
2. **Topic Not Found**: Topics auto-create, but I check Kafka UI to be sure
3. **Consumer Not Getting Messages**: Check topic name and consumer group
4. **Producer Errors**: Check Kafka broker logs (`docker-compose logs kafka`)

### When Things Go Wrong

```bash
# See all the logs
docker-compose logs

# Just Kafka logs
docker-compose logs kafka

# Just Zookeeper logs
docker-compose logs zookeeper

# Follow logs live (useful when testing)
docker-compose logs -f kafka
```

## 🏢 What I Learned About Production

### AWS MSK (When I Go Cloud)

1. **Security**: IAM roles and VPC security groups are a must
2. **Monitoring**: CloudWatch metrics and logs are essential
3. **Scaling**: Auto-scaling based on metrics saves headaches
4. **Backup**: Point-in-time recovery is crucial for important data

### My Local Setup

1. **Data Persistence**: My volumes keep data between restarts
2. **Resource Limits**: I can adjust Docker limits if needed
3. **Network**: Ports 9092, 8080, and 5000 need to be free

## 🧪 What I Test With This

### Basic Stuff
- Send messages to different topics
- Watch messages come through
- Make sure ordering works

### Error Scenarios
- What happens with bad topic names
- Network issues
- Broker failures

### Performance Testing
- High message volume
- Big messages
- Multiple consumers

## 📚 Resources That Helped Me

- [Confluent Kafka Python Client](https://docs.confluent.io/kafka-clients/python/current/overview.html) - Great Python docs
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/) - The official stuff
- [AWS MSK Developer Guide](https://docs.aws.amazon.com/msk/latest/developerguide/) - Cloud-specific info

## 🛠️ How I Extend This

### Adding New Features

1. **New Producer Endpoints**: Just add routes in `producer.py`
2. **Consumer Filters**: Modify `consumer.py` to filter messages
3. **Configuration Options**: Update `config.py` for new settings

### My Code Structure

- **Producer**: Flask app that sends messages asynchronously
- **Consumer**: Polling-based consumer with proper error handling
- **Configuration**: Smart switching between local and cloud
- **Testing**: Scripts to test everything automatically

## 🚨 When Things Break (My Debugging Checklist)

### Producer Acting Up

```bash
# Is it even running?
curl http://localhost:5000/health

# Run it in foreground to see what's happening
python producer.py
```

### Consumer Not Working

```bash
# Does the topic exist?
docker exec kafka-broker kafka-topics --bootstrap-server localhost:9092 --list

# Check my consumer group
docker exec kafka-broker kafka-consumer-groups --bootstrap-server localhost:9092 --list
```

### Kafka Itself Having Issues

```bash
# Are the services running?
docker-compose ps

# Restart everything
docker-compose restart

# Nuclear option - clean restart (loses data)
docker-compose down -v
docker-compose up -d
```

## 🎯 What This Project Taught Me

This setup gave me hands-on experience with:
- How Kafka producers and consumers actually work
- What happens when brokers fail (spoiler: it's not pretty with single broker)
- How replication and partitioning affect performance
- Common configuration mistakes and how to fix them
- The difference between local dev and production setups

Perfect for any SRE who needs to understand Kafka without breaking production systems! 🚀
