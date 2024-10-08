import requests
import json
import time
from datetime import datetime, timedelta

BASE_API_URL = "https://api.miniapp.dropstab.com/api"
BASE_HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\", \"Microsoft Edge WebView2\";v=\"129\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "Referer": "https://mdkefjwsfepf.dropstab.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

def get_headers(token=None):
    headers = BASE_HEADERS.copy()
    if token:
        headers["authorization"] = f"Bearer {token}"
    return headers

def get_token_and_login(payload):
    time.sleep(5)
    headers = get_headers()
    body = json.dumps({"webAppData": payload})
    print("Sedang melakukan login...")
    response = requests.post(f"{BASE_API_URL}/auth/login", headers=headers, data=body)
    
    try:
        token = response.json()["jwt"]["access"]["token"]
        print("Login berhasil.")
        return token
    except KeyError:
        raise Exception("Login gagal atau struktur respons tidak sesuai.")

def get_user_info(token):
    time.sleep(5)
    headers = get_headers(token)
    print("Mengambil informasi user...")
    response = requests.get(f"{BASE_API_URL}/user/current", headers=headers)
    data = response.json()
    print(f"Akun: {data['tgUsername']}, Saldo: {data['balance']}")
    return data

def daily_bonus(token):
    time.sleep(5)
    headers = get_headers(token)
    print("Mengambil daily bonus...")
    response = requests.post(f"{BASE_API_URL}/bonus/dailyBonus", headers=headers)
    data = response.json()
    
    if data["result"]:
        print(f"Daily login berhasil. Streaks: {data['streaks']}")

def check_tasks(token):
    time.sleep(5)
    headers = get_headers(token)
    print("Memeriksa tasks yang tersedia...")
    response = requests.get(f"{BASE_API_URL}/quest/active", headers=headers)
    
    tasks = response.json()
    any_claimed = False  # Variabel untuk melacak apakah ada tugas yang diklaim
    for task in tasks:
        for quest in task['quests']:
            if quest["claimAllowed"]:
                claim_task(token, quest["id"])
                any_claimed = True  # Ada tugas yang diklaim

    if not any_claimed:
        print("Tidak ada tasks yang bisa diklaim, melanjutkan ke proses selanjutnya...")

def claim_task(token, task_id):
    time.sleep(5)
    headers = get_headers(token)
    print(f"Mengklaim task ID: {task_id}")
    requests.put(f"{BASE_API_URL}/quest/{task_id}/claim", headers=headers)

def dynamic_countdown(sleep_time):
    while sleep_time > 0:
        hours, remainder = divmod(sleep_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"\rMenunggu hingga jam 00:01 UTC untuk memulai ulang... {int(hours):02}:{int(minutes):02}:{int(seconds):02}", end="")
        time.sleep(1)
        sleep_time -= 1
    print()  # Newline after countdown finishes

def wait_until_midnight():
    now = datetime.utcnow()
    next_run = now.replace(hour=0, minute=1, second=0, microsecond=0)
    if now >= next_run:
        next_run += timedelta(days=1)
    sleep_time = (next_run - now).total_seconds()
    dynamic_countdown(int(sleep_time))

def process_queries():
    while True:
        with open('sesi.txt', 'r') as file:
            queries = file.readlines()

        for query in queries:
            try:
                print("Memproses query...")
                token = get_token_and_login(query.strip())  # Menghapus whitespace yang tidak perlu
                user_info = get_user_info(token)  # Ambil informasi user setelah login
                daily_bonus(token)
                check_tasks(token)  # Cek dan klaim tasks
            except Exception as e:
                print(f"Terjadi kesalahan: {e}")

        wait_until_midnight()  # Tunggu sampai jam 00:01 sebelum mulai ulang

process_queries()
