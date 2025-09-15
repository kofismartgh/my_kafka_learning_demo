# Kafka Configuration & Operations Guide for SREs

This guide provides detailed technical information about Kafka configuration, replication, scaling, and troubleshooting for Site Reliability Engineers.

## 📋 Table of Contents

1. [Current Configuration Analysis](#current-configuration-analysis)
2. [Replication & High Availability](#replication--high-availability)
3. [Scaling to Multiple Brokers](#scaling-to-multiple-brokers)
4. [Production Configuration](#production-configuration)
5. [Monitoring & Alerting](#monitoring--alerting)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Official Resources](#official-resources)

## 🔍 Current Configuration Analysis

### Single Broker Setup

Your current setup uses a **single Kafka broker**, which is suitable for development but not production:

```yaml
# Current docker-compose.yml configuration
kafka:
  environment:
    KAFKA_BROKER_ID: 1
    KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
    KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
```

### Key Configuration Parameters Explained

| Parameter | Current Value | Purpose | Production Impact |
|-----------|---------------|---------|-------------------|
| `KAFKA_BROKER_ID` | 1 | Unique identifier for this broker | Must be unique across cluster |
| `KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR` | 1 | How many brokers store consumer offsets | **Critical**: Should be ≥ 3 for HA |
| `KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR` | 1 | Replication for transaction logs | **Critical**: Should be ≥ 3 for HA |
| `KAFKA_TRANSACTION_STATE_LOG_MIN_ISR` | 1 | Minimum in-sync replicas for transactions | **Critical**: Should be ≥ 2 for HA |
| `KAFKA_AUTO_CREATE_TOPICS_ENABLE` | true | Auto-create topics when first accessed | **Security**: Should be false in production |

### Client Configuration Analysis

```python
# Current client configuration
LOCAL_CONFIG = {
    'bootstrap.servers': 'localhost:9092',
    'security.protocol': 'PLAINTEXT',
    'auto.offset.reset': 'earliest',
    'api.version.request': True,
    'api.version.fallback.ms': 0,
    'broker.version.fallback': '0.10.0.0'
}
```

**Client Configuration Breakdown:**
- `bootstrap.servers`: Entry point to Kafka cluster
- `security.protocol`: PLAINTEXT (no encryption) - suitable for local dev
- `auto.offset.reset`: What to do when no committed offset exists
- `api.version.request`: Let client negotiate API version with broker
- `broker.version.fallback`: Fallback version for older brokers

## 🔄 Replication & High Availability

### Why Replication Matters

**Single Broker Risks:**
- ❌ **No fault tolerance** - broker failure = complete outage
- ❌ **Data loss risk** - no backup copies of data
- ❌ **No load distribution** - all traffic hits one broker
- ❌ **Maintenance windows** - updates require downtime

**Multi-Broker Benefits:**
- ✅ **Fault tolerance** - can lose N-1 brokers (where N = replication factor)
- ✅ **Data durability** - multiple copies of each message
- ✅ **Load distribution** - traffic spread across brokers
- ✅ **Zero-downtime maintenance** - rolling updates possible

### Replication Concepts

#### Replication Factor (RF)
- **Definition**: Number of copies of each partition across brokers
- **Current**: 1 (single copy)
- **Recommended**: 3 (can lose 2 brokers and still function)
- **Maximum**: Number of brokers in cluster

#### In-Sync Replicas (ISR)
- **Definition**: Replicas that are up-to-date with the leader
- **Current**: 1 (only the leader)
- **Recommended**: 2+ (for fault tolerance)

#### Leader Election
- **When**: Leader broker fails or becomes unavailable
- **How**: Zookeeper coordinates election of new leader
- **Time**: Usually 1-3 seconds

## 🚀 Scaling to Multiple Brokers

### 3-Broker Production Setup

Here's how to modify your `docker-compose.yml` for a 3-broker cluster:

```yaml
version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    hostname: zookeeper
    container_name: kafka-zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
      ZOOKEEPER_SERVER_ID: 1
      ZOOKEEPER_SERVERS: zookeeper:2888:3888
    volumes:
      - zookeeper-data:/var/lib/zookeeper/data
      - zookeeper-logs:/var/lib/zookeeper/log

  kafka-1:
    image: confluentinc/cp-kafka:7.4.0
    hostname: kafka-1
    container_name: kafka-broker-1
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
      - "9101:9101"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-1:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_JMX_PORT: 9101
      KAFKA_JMX_HOSTNAME: localhost
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'false'
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: 2
    volumes:
      - kafka-1-data:/var/lib/kafka/data

  kafka-2:
    image: confluentinc/cp-kafka:7.4.0
    hostname: kafka-2
    container_name: kafka-broker-2
    depends_on:
      - zookeeper
    ports:
      - "9093:9092"
      - "9102:9101"
    environment:
      KAFKA_BROKER_ID: 2
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-2:29092,PLAINTEXT_HOST://localhost:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_JMX_PORT: 9101
      KAFKA_JMX_HOSTNAME: localhost
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'false'
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: 2
    volumes:
      - kafka-2-data:/var/lib/kafka/data

  kafka-3:
    image: confluentinc/cp-kafka:7.4.0
    hostname: kafka-3
    container_name: kafka-broker-3
    depends_on:
      - zookeeper
    ports:
      - "9094:9092"
      - "9103:9101"
    environment:
      KAFKA_BROKER_ID: 3
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-3:29092,PLAINTEXT_HOST://localhost:9094
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_JMX_PORT: 9101
      KAFKA_JMX_HOSTNAME: localhost
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'false'
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: 2
    volumes:
      - kafka-3-data:/var/lib/kafka/data

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    depends_on:
      - kafka-1
      - kafka-2
      - kafka-3
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local-cluster
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka-1:29092,kafka-2:29092,kafka-3:29092
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181

volumes:
  zookeeper-data:
  zookeeper-logs:
  kafka-1-data:
  kafka-2-data:
  kafka-3-data:
```

### Updated Client Configuration

For the multi-broker setup, update your `config.py`:

```python
# Multi-broker configuration
LOCAL_CONFIG = {
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
    'security.protocol': 'PLAINTEXT',
    'auto.offset.reset': 'earliest',
    'api.version.request': True,
    'api.version.fallback.ms': 0,
    'broker.version.fallback': '0.10.0.0',
    # Additional reliability settings
    'retries': 3,
    'retry.backoff.ms': 100,
    'request.timeout.ms': 30000,
    'metadata.max.age.ms': 300000
}
```

## 🏭 Production Configuration

### Security Settings

```yaml
# Production security configuration
environment:
  KAFKA_SECURITY_INTER_BROKER_PROTOCOL: SASL_SSL
  KAFKA_SASL_MECHANISM_INTER_BROKER_PROTOCOL: PLAIN
  KAFKA_SASL_ENABLED_MECHANISMS: PLAIN
  KAFKA_OPTS: "-Djava.security.auth.login.config=/etc/kafka/secrets/kafka_server_jaas.conf"
  KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: SASL_SSL:SASL_SSL,PLAINTEXT:PLAINTEXT
  KAFKA_ADVERTISED_LISTENERS: SASL_SSL://kafka-1:9092,PLAINTEXT://localhost:9092
```

### Performance Tuning

```yaml
# Performance optimization
environment:
  # Memory settings
  KAFKA_HEAP_OPTS: "-Xmx2G -Xms2G"
  
  # Log settings
  KAFKA_LOG_RETENTION_HOURS: 168  # 7 days
  KAFKA_LOG_SEGMENT_BYTES: 1073741824  # 1GB
  KAFKA_LOG_RETENTION_CHECK_INTERVAL_MS: 300000  # 5 minutes
  
  # Network settings
  KAFKA_SOCKET_SEND_BUFFER_BYTES: 102400
  KAFKA_SOCKET_RECEIVE_BUFFER_BYTES: 102400
  KAFKA_SOCKET_REQUEST_MAX_BYTES: 104857600  # 100MB
  
  # Replication settings
  KAFKA_REPLICA_FETCH_MAX_BYTES: 1048576  # 1MB
  KAFKA_MESSAGE_MAX_BYTES: 1048576  # 1MB
```

## 📊 Monitoring & Alerting

### Key Metrics to Monitor

#### Broker Metrics
- **UnderReplicatedPartitions**: Should be 0
- **ActiveControllerCount**: Should be 1
- **OfflinePartitionsCount**: Should be 0
- **RequestLatency**: P95 < 100ms
- **BytesInPerSec**: Throughput monitoring
- **BytesOutPerSec**: Throughput monitoring

#### Topic Metrics
- **MessagesInPerSec**: Topic throughput
- **BytesInPerSec**: Topic data volume
- **ReplicationFactor**: Should match desired RF
- **MinInSyncReplicas**: Should be ≥ 2

#### Consumer Metrics
- **ConsumerLag**: Should be low and stable
- **ConsumerGroupMembers**: Active consumers
- **RecordsConsumedRate**: Consumer throughput

### Alerting Rules

```yaml
# Example Prometheus alerting rules
groups:
- name: kafka
  rules:
  - alert: KafkaUnderReplicatedPartitions
    expr: kafka_server_replicamanager_underreplicatedpartitions > 0
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Kafka has under-replicated partitions"
      
  - alert: KafkaOfflinePartitions
    expr: kafka_controller_kafkacontroller_offline_partitions_count > 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Kafka has offline partitions"
      
  - alert: KafkaHighConsumerLag
    expr: kafka_consumer_lag_sum > 10000
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High consumer lag detected"
```

## 🔧 Troubleshooting Guide

### Common Issues & Solutions

#### 1. Under-Replicated Partitions
```bash
# Check under-replicated partitions
docker exec kafka-broker-1 kafka-topics --bootstrap-server localhost:9092 --describe --under-replicated-partitions

# Check broker status
docker exec kafka-broker-1 kafka-broker-api-versions --bootstrap-server localhost:9092
```

#### 2. Consumer Lag
```bash
# Check consumer groups
docker exec kafka-broker-1 kafka-consumer-groups --bootstrap-server localhost:9092 --list

# Check specific consumer group lag
docker exec kafka-broker-1 kafka-consumer-groups --bootstrap-server localhost:9092 --group my-group --describe
```

#### 3. Broker Failures
```bash
# Check broker logs
docker logs kafka-broker-1
docker logs kafka-broker-2
docker logs kafka-broker-3

# Check Zookeeper status
docker exec kafka-zookeeper zkServer.sh status
```

#### 4. Topic Management
```bash
# List all topics
docker exec kafka-broker-1 kafka-topics --bootstrap-server localhost:9092 --list

# Create topic with replication
docker exec kafka-broker-1 kafka-topics --bootstrap-server localhost:9092 --create --topic my-topic --partitions 3 --replication-factor 3

# Describe topic
docker exec kafka-broker-1 kafka-topics --bootstrap-server localhost:9092 --describe --topic my-topic
```

### Performance Troubleshooting

#### High Latency
1. Check network connectivity between brokers
2. Monitor disk I/O and CPU usage
3. Review log segment sizes
4. Check for memory pressure

#### Low Throughput
1. Increase partition count
2. Tune batch sizes
3. Check consumer group configuration
4. Monitor broker resources

## 📚 Official Resources

### Apache Kafka Documentation
- **Main Documentation**: https://kafka.apache.org/documentation/
- **Operations Guide**: https://kafka.apache.org/documentation/#operations
- **Configuration Reference**: https://kafka.apache.org/documentation/#configuration
- **JMX Metrics**: https://kafka.apache.org/documentation/#monitoring

### Confluent Resources
- **Platform Documentation**: https://docs.confluent.io/
- **Kafka Operations**: https://docs.confluent.io/platform/current/kafka/operations.html
- **Troubleshooting Guide**: https://docs.confluent.io/platform/current/kafka/troubleshooting.html
- **Performance Tuning**: https://docs.confluent.io/platform/current/kafka/deployment.html#performance-tuning

### AWS MSK Resources
- **Developer Guide**: https://docs.aws.amazon.com/msk/latest/developerguide/
- **Best Practices**: https://docs.aws.amazon.com/msk/latest/developerguide/best-practices.html
- **Monitoring**: https://docs.aws.amazon.com/msk/latest/developerguide/monitoring.html
- **Security**: https://docs.aws.amazon.com/msk/latest/developerguide/security.html

### Monitoring & Observability
- **Kafka JMX Metrics**: https://kafka.apache.org/documentation/#monitoring
- **Prometheus Integration**: https://github.com/prometheus/jmx_exporter
- **Grafana Dashboards**: https://grafana.com/grafana/dashboards/721
- **Confluent Control Center**: https://docs.confluent.io/platform/current/control-center/

### Community Resources
- **Kafka Summit**: https://kafka-summit.org/
- **Confluent Community**: https://www.confluent.io/community/
- **Stack Overflow**: https://stackoverflow.com/questions/tagged/apache-kafka
- **Kafka Mailing Lists**: https://kafka.apache.org/contact

## 🎯 SRE Best Practices

### 1. Capacity Planning
- Monitor disk usage and plan for growth
- Set up automated scaling based on metrics
- Plan for peak traffic scenarios

### 2. Disaster Recovery
- Regular backups of critical topics
- Cross-region replication for critical data
- Documented recovery procedures

### 3. Security
- Enable authentication and authorization
- Use TLS for all communications
- Regular security audits and updates

### 4. Monitoring
- Comprehensive metrics collection
- Proactive alerting on anomalies
- Regular health checks and testing

### 5. Documentation
- Keep runbooks updated
- Document all configuration changes
- Maintain incident post-mortems

This guide provides the foundation for managing Kafka in production environments. Regular review and updates of these configurations will ensure optimal performance and reliability.
