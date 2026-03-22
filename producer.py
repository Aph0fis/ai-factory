import redis
import json
import time

try:
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.ping()
    print("[*] Связь с Redis установлена!")
except redis.exceptions.ConnectionError:
    print("[!] Ошибка: Редис недоступен. Проверь kubectl port-forward.")
    exit(1)

# УБИРАЕМ ЦИКЛ. Тестируем только ОДИН конкретный профиль.
# Вставь сюда ТОЧНЫЙ ID профиля из таблицы AdsPower (столбец ID).
# Без всяких генераций и цифр на конце. Если ID "k18dat6h", то так и пиши.
REAL_PROFILE_ID = "k18dat6h" 

print(f"[*] Отправляем тестовую задачу для профиля: {REAL_PROFILE_ID}...")

task_data = {
    "task_id": 999,
    "action": "open_adspower_profile",
    "profile_id": REAL_PROFILE_ID
}

# Отправляем задачу в очередь
r.rpush('tasks', json.dumps(task_data))
print(f"[+] Успех! В очередь отправлена задача: {task_data['profile_id']}")
print("[*] Смотри в логи Кубернетиса и на свой экран.")