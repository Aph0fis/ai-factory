import os
import time
import json
import redis
import requests

def get_default_gateway():
    """Читаем физическую таблицу маршрутов Пода, чтобы найти реальный шлюз"""
    try:
        with open('/proc/net/route', 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) > 2 and parts[1] == '00000000':
                    hex_ip = parts[2]
                    return ".".join([str(int(hex_ip[i:i+2], 16)) for i in (6, 4, 2, 0)])
    except:
        pass
    return None

def discover_host_ip():
    """Автоматический поиск прокси-моста с подробным логированием"""
    print("[*] [v18] Запуск радара: Ищу прокси-мост socat...")
    
    gw = get_default_gateway()
    
    # Собираем все возможные варианты
    candidates = [
        os.getenv('WINDOWS_IP', ''),  # 1. Приоритет переменной (если задана)
        gw,                           # 2. Динамический шлюз из ядра Linux
        'host.docker.internal',       # 3. Дефолтный DNS Докера для хоста
        'host.minikube.internal',     # 4. Дефолтный DNS Minikube
        '192.168.49.1',               # 5. Классический шлюз Minikube
        '172.17.0.1',                 # 6. Классический шлюз Docker
        '172.18.240.1'                # 7. Прямой IP Windows (если прокси сдох)
    ]
    
    # Убираем пустые значения и дубликаты, сохраняя порядок
    seen = set()
    clean_candidates = []
    for ip in candidates:
        if ip and ip not in seen:
            seen.add(ip)
            clean_candidates.append(ip)

    for ip in clean_candidates:
        url = f"http://{ip}:50325/status"
        try:
            print(f"[.] Сканирую: {ip} ...")
            # Увеличил таймаут до 2 секунд, чтобы не пропустить медленный ответ
            resp = requests.get(url, timeout=2.0)
            if resp.status_code == 200:
                print(f"[v] БИНГО! Мост найден по адресу: {ip}")
                return ip
        except Exception:
            pass
            
    print("[!] РАДАР СЛЕП. Ни один маршрут не ответил. Прокси (socat) точно запущен?")
    return '127.0.0.1'

# Инициализация
HOST_IP = discover_host_ip()
ADSPOWER_API = f"http://{HOST_IP}:50325"

redis_host = os.getenv('REDIS_HOST', 'localhost')

try:
    r = redis.Redis(host=redis_host, port=6379, decode_responses=True)
    r.ping()
    print(f"[*] [v18] Подключено к Redis: {redis_host}")
except redis.exceptions.ConnectionError:
    print(f"[!] ОШИБКА: Redis недоступен")
    exit(1)

def open_adspower_profile(profile_id):
    url = f"{ADSPOWER_API}/api/v1/browser/start?user_id={profile_id}"
    try:
        print(f"[*] [v18] ОТПРАВКА ({HOST_IP}): {url}")
        response = requests.get(url, timeout=(3, 15))
        
        if response.status_code == 200:
            print(f"[v] УСПЕХ: AdsPower ответил -> {response.json()}")
        else:
            print(f"[x] Ошибка HTTP от AdsPower: {response.status_code}")
            
    except requests.exceptions.ConnectTimeout:
        print(f"[!] ТАЙМАУТ: Связь с {HOST_IP} потеряна.")
    except requests.exceptions.ConnectionError as e:
        print(f"[!] ОТКАЗ: Соединение сброшено на {HOST_IP}.")
    except Exception as e:
        print(f"[!] Неизвестный сбой: {e}")

def main():
    print(f"[*] Агент v18 запущен. Рабочая цель: {HOST_IP}")
    last_heartbeat = 0
    
    while True:
        try:
            if time.time() - last_heartbeat > 10:
                print(f"[.] Агент v18 дежурит. Жду задачи...")
                last_heartbeat = time.time()

            task_raw = r.lpop('tasks')
            if task_raw:
                task = json.loads(task_raw)
                print(f"[+] Взял профиль: {task.get('profile_id')}")
                open_adspower_profile(task.get('profile_id'))
                time.sleep(1)
            else:
                time.sleep(2)
        except Exception as e:
            print(f"[!] Ошибка цикла: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()