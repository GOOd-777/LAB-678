#!/usr/bin/env bash
echo "Остановка серверов Motion Playground (порты 8080–8084)..."

found=0
for port in 8080 8081 8082 8083 8084; do
  pids=$(lsof -ti ":$port" 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo "  порт $port: останавливаю..."
    echo "$pids" | xargs kill -9 2>/dev/null || true
    found=1
  fi
done

if [ "$found" = "0" ]; then
  echo "Ничего не запущено."
else
  echo "Готово."
fi
