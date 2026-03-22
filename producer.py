import redis
import json

# Подключаемся к складу (Редису на порту 6379)
r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

# Формируем заказ
task = {
    "action": "open_adspower",
    "profile_id": "12345",
    "target_url": "https://example.com"
}

# Кидаем заказ на ленту с названием "task_queue"
r.lpush("task_queue", json.dumps(task))
print(f"[PRODUCER] Задача отправлена в очередь: {task}")