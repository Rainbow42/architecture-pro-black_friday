#!/bin/bash

###
# Инициализация шардирования с репликацией:
# 1) сервер конфигурации,
# 2) replica set каждого шарда (по 3 узла),
# 3) роутер (добавление шардов и включение шардирования)
###

echo "Инициализация сервера конфигурации..."
podman compose exec -T configSrv mongosh --port 27017 --quiet <<EOF
rs.initiate(
  {
    _id: "config_server",
    configsvr: true,
    members: [
      { _id: 0, host: "configSrv:27017" }
    ]
  }
);
EOF

echo "Инициализация replica set shard1 (3 узла)..."
podman compose exec -T shard1-1 mongosh --port 27018 --quiet <<EOF
rs.initiate(
  {
    _id: "shard1",
    members: [
      { _id: 0, host: "shard1-1:27018" },
      { _id: 1, host: "shard1-2:27018" },
      { _id: 2, host: "shard1-3:27018" }
    ]
  }
);
EOF

echo "Инициализация replica set shard2 (3 узла)..."
podman compose exec -T shard2-1 mongosh --port 27019 --quiet <<EOF
rs.initiate(
  {
    _id: "shard2",
    members: [
      { _id: 0, host: "shard2-1:27019" },
      { _id: 1, host: "shard2-2:27019" },
      { _id: 2, host: "shard2-3:27019" }
    ]
  }
);
EOF

echo "Ожидание выбора PRIMARY в replica set..."
sleep 15

echo "Добавление шардов в кластер и включение шардирования для somedb.helloDoc..."
podman compose exec -T mongos_router mongosh --port 27020 --quiet <<EOF
sh.addShard("shard1/shard1-1:27018,shard1-2:27018,shard1-3:27018");
sh.addShard("shard2/shard2-1:27019,shard2-2:27019,shard2-3:27019");
sh.enableSharding("somedb");
sh.shardCollection("somedb.helloDoc", { "name": "hashed" });
EOF

echo "Шардирование с репликацией настроено."
