#!/bin/bash

###
# Проверка кеширования: три запроса к /helloDoc/users с замером времени.
# Первый запрос — из MongoDB (больше секунды), повторные — из кеша Redis (<100 мс)
###

for i in 1 2 3; do
  echo "Запрос $i:"
  curl -o /dev/null -s -w "  время: %{time_total}s\n" http://localhost:8080/helloDoc/users
done
