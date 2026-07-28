# sharding-repl-cache

Стенд приложения `pymongo-api` с шардированной MongoDB, репликацией и кешированием: сервер конфигурации (`configSrv`), два шарда — replica set по три узла каждый (`shard1-1..3`, `shard2-1..3`), роутер (`mongos_router`) и Redis (`redis`) для кеширования запросов приложения к MongoDB. Приложение подключается к MongoDB через роутер, кеш включается переменной окружения `REDIS_URL`.

## Как запустить

1. Запускаем все сервисы:

```shell
podman compose up -d
```

Дожидаемся, пока все контейнеры станут `healthy` (проверить можно командой `podman compose ps`).

2. Инициализируем шардирование и репликацию (сервер конфигурации, replica set обоих шардов по 3 узла, добавление шардов в кластер, включение шардирования коллекции `somedb.helloDoc`):

```shell
./scripts/init-sharding-repl.sh
```

3. Наполняем БД тестовыми данными (1000 документов в коллекции `helloDoc` базы `somedb`):

```shell
./scripts/mongo-init.sh
```

## Как проверить

Откройте в браузере http://localhost:8080 — в JSON-ответе будут:

- `mongo_topology_type: "Sharded"`;
- `shards` — список шардов, у каждого перечислены все три узла replica set;
- `collections.helloDoc.documents_count` — общее количество документов (1000);
- `cache_enabled: true` — кеширование включено.

Документация API: http://localhost:8080/docs

### Проверка количества документов и реплик

Скрипт выводит общее количество документов через роутер, количество документов на каждом шарде и состав каждого replica set (1 PRIMARY + 2 SECONDARY):

```shell
./scripts/check-cluster.sh
```

### Проверка кеширования

Эндпоинт `/helloDoc/users` кешируется. Первый запрос выполняется больше секунды, повторные — из кеша, менее 100 мс:

```shell
./scripts/check-cache.sh
```
