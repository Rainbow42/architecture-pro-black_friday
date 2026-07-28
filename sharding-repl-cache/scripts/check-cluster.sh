#!/bin/bash

###
# Проверка кластера: общее количество документов, количество на каждом шарде,
# состав replica set каждого шарда
###

echo "=== Общее количество документов (через mongos_router) ==="
podman compose exec -T mongos_router mongosh --port 27020 --quiet <<EOF
use somedb
db.helloDoc.countDocuments()
EOF

echo "=== Количество документов на shard1 ==="
podman compose exec -T shard1-1 mongosh --port 27018 --quiet <<EOF
use somedb
db.helloDoc.countDocuments()
EOF

echo "=== Количество документов на shard2 ==="
podman compose exec -T shard2-1 mongosh --port 27019 --quiet <<EOF
use somedb
db.helloDoc.countDocuments()
EOF

echo "=== Replica set shard1 ==="
podman compose exec -T shard1-1 mongosh --port 27018 --quiet <<EOF
rs.status().members.forEach(m => print(m.name, m.stateStr))
EOF

echo "=== Replica set shard2 ==="
podman compose exec -T shard2-1 mongosh --port 27019 --quiet <<EOF
rs.status().members.forEach(m => print(m.name, m.stateStr))
EOF
