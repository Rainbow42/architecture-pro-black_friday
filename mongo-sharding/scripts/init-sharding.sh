#!/bin/bash

###
# Инициализация шардирования MongoDB:
# 1) сервер конфигурации, 2) шарды, 3) роутер (добавление шардов и включение шардирования)
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

echo "Инициализация shard1..."
podman compose exec -T shard1 mongosh --port 27018 --quiet <<EOF
rs.initiate(
  {
    _id: "shard1",
    members: [
      { _id: 0, host: "shard1:27018" }
    ]
  }
);
EOF

echo "Инициализация shard2..."
podman compose exec -T shard2 mongosh --port 27019 --quiet <<EOF
rs.initiate(
  {
    _id: "shard2",
    members: [
      { _id: 0, host: "shard2:27019" }
    ]
  }
);
EOF

echo "Ожидание готовности реплик..."
sleep 10

echo "Добавление шардов в кластер и включение шардирования для somedb.helloDoc..."
podman compose exec -T mongos_router mongosh --port 27020 --quiet <<EOF
sh.addShard("shard1/shard1:27018");
sh.addShard("shard2/shard2:27019");
sh.enableSharding("somedb");
sh.shardCollection("somedb.helloDoc", { "name": "hashed" });
EOF

echo "Шардирование настроено."
