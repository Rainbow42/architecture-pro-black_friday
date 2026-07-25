# mongo-sharding

Стенд приложения `pymongo-api` с шардированной MongoDB: сервер конфигурации (`configSrv`), два шарда (`shard1`, `shard2`) и роутер (`mongos_router`). Приложение подключается к MongoDB через роутер.

## Как запустить

Запускаем все сервисы:

```shell
podman compose up -d
```

Дожидаемся, пока все контейнеры станут `healthy` (проверить можно командой `podman compose ps`).

## Инициализация шардирования

Скрипт инициализирует сервер конфигурации, оба шарда, добавляет их в кластер и включает шардирование коллекции `somedb.helloDoc` (hashed по полю `name`):

```shell
./scripts/init-sharding.sh
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
- `shards` — список шардов;
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

Количество документов на shard1:

```shell
podman compose exec -T shard1 mongosh --port 27018 --quiet <<EOF
use somedb
db.helloDoc.countDocuments()
EOF
```

Количество документов на shard2:

```shell
podman compose exec -T shard2 mongosh --port 27019 --quiet <<EOF
use somedb
db.helloDoc.countDocuments()
EOF
```

Сумма документов на двух шардах должна равняться общему количеству (1000).
