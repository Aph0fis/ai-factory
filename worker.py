import redis
import json
import time

# Подключаемся к тому же складу
r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
print("[WORKER] Запущен. Жду задачи...")

while True:
    # brpop - скрипт намертво замирает у ленты и ждет, пока не появится задача
    queue_name, task_data = r.brpop("task_queue", timeout=0)
    task = json.loads(task_data)
    
    print(f"\n[WORKER] Получил приказ: {task['action']}")
    print(f"[WORKER] Цель: {task['target_url']}, Профиль: {task['profile_id']}")
    
    print("[WORKER] Выполняю...")
    time.sleep(2) # Имитируем бурную деятельность (позже тут будет код AdsPower)
    print("[WORKER] Задача завершена! Жду следующую...\n")