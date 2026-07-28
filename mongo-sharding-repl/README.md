# mongo-sharding-repl

Стенд приложения `pymongo-api` с шардированной MongoDB и репликацией: сервер конфигурации (`configSrv`), два шарда, каждый из которых — replica set из трёх узлов (`shard1-1`, `shard1-2`, `shard1-3` и `shard2-1`, `shard2-2`, `shard2-3`), и роутер (`mongos_router`). Приложение подключается к MongoDB через роутер.

## Как запустить

Запускаем все сервисы:

```shell
podman compose up -d
```

Дожидаемся, пока все контейнеры станут `healthy` (проверить можно командой `podman compose ps`).

## Настройка репликации и шардирования

Скрипт инициализирует сервер конфигурации, replica set каждого шарда (по 3 узла), добавляет шарды в кластер и включает шардирование коллекции `somedb.helloDoc` (hashed по полю `name`):

```shell
./scripts/init-sharding-repl.sh
```

## Наполнение БД тестовыми данными

Скрипт вставляет 1000 документов в коллекцию `helloDoc` базы `somedb` через роутер:

```shell
./scripts/mongo-init.sh
```

## Как проверить

### Через приложение

Откройте в браузере http://localhost:8080 — в JSON-ответе будут:

- `mongo_topology_type: "Sharded"`;
- `shards` — список шардов, у каждого перечислены все три узла replica set;
- `collections.helloDoc.documents_count` — общее количество документов (1000).

Документация API: http://localhost:8080/docs

### Через mongosh

Общее количество документов (через роутер):

```shell
podman compose exec -T mongos_router mongosh --port 27020 --quiet <<EOF
use somedb
db.helloDoc.countDocuments()
EOF
```

Количество документов на шардах (запрос к PRIMARY каждого replica set):

```shell
podman compose exec -T shard1-1 mongosh --port 27018 --quiet <<EOF
use somedb
db.helloDoc.countDocuments()
EOF

podman compose exec -T shard2-1 mongosh --port 27019 --quiet <<EOF
use somedb
db.helloDoc.countDocuments()
EOF
```

Статус репликации (в выводе должно быть 3 члена: 1 PRIMARY и 2 SECONDARY):

```shell
podman compose exec -T shard1-1 mongosh --port 27018 --quiet <<EOF
rs.status().members.forEach(m => print(m.name, m.stateStr))
EOF

podman compose exec -T shard2-1 mongosh --port 27019 --quiet <<EOF
rs.status().members.forEach(m => print(m.name, m.stateStr))
EOF
```

Проверка, что данные реплицируются на SECONDARY (чтение с secondary-узла):

```shell
podman compose exec -T shard1-2 mongosh --port 27018 --quiet <<EOF
db.getMongo().setReadPref("secondary")
use somedb
db.helloDoc.countDocuments()
EOF
```

Сумма документов на двух шардах должна равняться общему количеству (1000).
