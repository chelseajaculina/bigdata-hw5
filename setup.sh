#!/bin/bash

# ✅ Set this to your Pinot installation directory
PINOT_DIR="/Users/chelseajaculina/GitHub/bigdata-hw5/pinot/pinot-distribution/target/apache-pinot-1.4.0-SNAPSHOT-bin/apache-pinot-1.4.0-SNAPSHOT-bin"

cd "$PINOT_DIR" || { echo "❌ Failed to access Pinot directory"; exit 1; }

echo "🚀 Starting Apache Pinot components..."

# 🟡 Start Zookeeper
echo "🔁 Starting Zookeeper..."
/Users/chelseajaculina/GitHub/bigdata-hw5/pinot/pinot-distribution/target/apache-pinot-1.4.0-SNAPSHOT-bin/apache-pinot-1.4.0-SNAPSHOT-bin/bin/pinot-admin.sh StartZookeeper > logs/zookeeper.log 2>&1 &
sleep 3

# 🟢 Start Controller
echo "🔁 Starting Controller..."
/Users/chelseajaculina/GitHub/bigdata-hw5/pinot/pinot-distribution/target/apache-pinot-1.4.0-SNAPSHOT-bin/apache-pinot-1.4.0-SNAPSHOT-bin/bin/pinot-admin.sh StartController -zkAddress localhost:2181 > logs/controller.log 2>&1 &
sleep 3

# 🔵 Start Broker
echo "🔁 Starting Broker..."
/Users/chelseajaculina/GitHub/bigdata-hw5/pinot/pinot-distribution/target/apache-pinot-1.4.0-SNAPSHOT-bin/apache-pinot-1.4.0-SNAPSHOT-bin/bin/pinot-admin.sh StartBroker -zkAddress localhost:2181 > logs/broker.log 2>&1 &
sleep 3

# 🟣 Start Server
echo "🔁 Starting Server..."
/Users/chelseajaculina/GitHub/bigdata-hw5/pinot/pinot-distribution/target/apache-pinot-1.4.0-SNAPSHOT-bin/apache-pinot-1.4.0-SNAPSHOT-bin/bin/pinot-admin.sh StartServer -zkAddress localhost:2181 > logs/server.log 2>&1 &
sleep 3

echo "✅ All Pinot services launched. Open http://localhost:9000 to access the UI."#!/bin/bash

SCHEMA_PATH="/Users/chelseajaculina/GitHub/bigdata-hw5/traffic-schema.json"
TABLE_CONFIG_PATH="/Users/chelseajaculina/GitHub/bigdata-hw5/traffic-table.json"
CONTROLLER_HOST="localhost"
CONTROLLER_PORT="9000"

echo "📦 Re-uploading schema..."
curl -X POST "http://${CONTROLLER_HOST}:${CONTROLLER_PORT}/schemas" \
  -H "Content-Type: application/json" \
  -d @"${SCHEMA_PATH}"

echo "📦 Re-uploading table config..."
curl -X POST "http://${CONTROLLER_HOST}:${CONTROLLER_PORT}/tables" \
  -H "Content-Type: application/json" \
  -d @"${TABLE_CONFIG_PATH}"

echo "✅ Schema and table config uploaded successfully!"

