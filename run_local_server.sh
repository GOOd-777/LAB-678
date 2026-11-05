#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Ошибка: python3 не найден."
  echo "Установите Python 3: https://www.python.org/downloads/"
  exit 1
fi

try_free_port() {
  local port="$1"
  local pids attempt
  for attempt in 1 2 3; do
    pids=$(lsof -ti ":$port" 2>/dev/null || true)
    if [ -z "$pids" ]; then
      return 0
    fi
    echo "Порт $port занят — останавливаю старый процесс (попытка $attempt)..."
    echo "$pids" | xargs kill -9 2>/dev/null || true
    sleep 0.6
  done
  pids=$(lsof -ti ":$port" 2>/dev/null || true)
  [ -z "$pids" ]
}

PORT=""
for candidate in 8080 8081 8082 8083 8084; do
  if try_free_port "$candidate"; then
    PORT="$candidate"
    break
  fi
done

if [ -z "$PORT" ]; then
  echo "Ошибка: не удалось занять порты 8080–8084."
  echo "Закройте другие серверы или выполните: ./stop-server.sh"
  exit 1
fi

echo "Запуск Motion Playground (совместный режим)..."
echo "  Адрес: http://127.0.0.1:$PORT"
if [ "$PORT" != "8080" ]; then
  echo "  (порт 8080 был занят, используется $PORT)"
fi
echo "  Остановка: Ctrl+C  |  ./stop-server.sh"
echo ""

export PORT
exec python3 room_server.py
