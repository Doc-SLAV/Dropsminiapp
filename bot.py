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
    headers = get_headers()
    body = json.dumps({"webAppData": payload})
    print(f"Logging in...")
    
    response = requests.post(f"{BASE_API_URL}/auth/login", headers=headers, data=body)
    if response.status_code == 200:
        try:
            token = response.json()["jwt"]["access"]["token"]
            print(f"Login successful.")
            return token
        except KeyError:
            print(f"Login failed: Incorrect response structure.")
            raise Exception("Login failed: Incorrect response structure.")
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        raise Exception(f"Login failed: {response.status_code} - {response.text}")

def get_user_info(token):
    headers = get_headers(token)
    print(f"Fetching user information...")
    
    response = requests.get(f"{BASE_API_URL}/user/current", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"Account: {data['tgUsername']}, Balance: {data['balance']}")
        return data
    else:
        print(f"Failed to fetch user information: {response.status_code} - {response.text}")
        raise Exception(f"Failed to fetch user information: {response.status_code} - {response.text}")

def daily_bonus(token):
    headers = get_headers(token)
    print(f"Claiming daily bonus...")
    
    response = requests.post(f"{BASE_API_URL}/bonus/dailyBonus", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data["result"]:
            print(f"Daily bonus claimed. Streaks: {data['streaks']}")
    else:
        print(f"Failed to claim daily bonus: {response.status_code} - {response.text}")
        raise Exception(f"Failed to claim daily bonus: {response.status_code} - {response.text}")

def check_tasks(token):
    headers = get_headers(token)
    print("Checking available tasks...")
    
    response = requests.get(f"{BASE_API_URL}/quest", headers=headers)
    if response.status_code == 200:
        tasks = response.json()
        any_claimed = False

        for task in tasks:
            for quest in task['quests']:
                print(f"Checking quest: {quest['name']} - Status: {quest['status']}")
                if quest.get("claimAllowed"):
                    task_id = quest["id"]
                    if quest["status"] == "claimed":
                        print(f"Task {task_id} is already claimed. Skipping verification.")
                        continue

                    if verify_task(token, task_id):
                        claim_task(token, task_id)
                        any_claimed = True

        return any_claimed  # Return whether any tasks were claimed
    else:
        print(f"Failed to check tasks: {response.status_code} - {response.text}")
        raise Exception(f"Failed to check tasks: {response.status_code} - {response.text}")

def verify_task(token, task_id):
    headers = get_headers(token)
    print(f"Verifying task ID: {task_id}")
    response = requests.post(f"{BASE_API_URL}/quest/{task_id}/verify", headers=headers)
    data = response.json()

    if response.status_code == 200 and data.get("success", False):
        print(f"Task {task_id} verified successfully.")
        return True
    else:
        print(f"ERROR: Failed to verify task {task_id}. Response: {response.status_code} - {response.text}")
        return False

def claim_task(token, task_id):
    headers = get_headers(token)
    print(f"Claiming task ID: {task_id}")
    
    response = requests.put(f"{BASE_API_URL}/quest/{task_id}/claim", headers=headers)
    if response.status_code == 200:
        print(f"Task {task_id} claimed successfully.")
        if not verify_task(token, task_id):
            print(f"WARNING: Task {task_id} claimed but could not be verified.")
    else:
        print(f"ERROR: Failed to claim task {task_id}. Response: {response.json()}")
        
def claim_referral(token):
    headers = get_headers(token)
    print("Claiming referral...")

    response = requests.post(f"{BASE_API_URL}/refLink/claim", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("success", False):
            print("Referral claimed successfully!")
        else:
            print("Failed to claim referral:", data.get("message", "Unknown error."))
    else:
        print(f"Failed to claim referral: {response.status_code} - {response.text}")
        raise Exception(f"Failed to claim referral: {response.status_code} - {response.text}")
      

def dynamic_countdown(sleep_time):
    while sleep_time > 0:
        hours, remainder = divmod(sleep_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"Waiting until 00:01 UTC... {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
        time.sleep(1)
        sleep_time -= 1

def wait_until_midnight():
    now = datetime.utcnow()
    next_run = now.replace(hour=0, minute=1, second=0, microsecond=0)
    if now >= next_run:
        next_run += timedelta(days=1)
    sleep_time = (next_run - now).total_seconds()
    dynamic_countdown(int(sleep_time))

def process_query(query):
    try:
        print("Processing query...")
        token = get_token_and_login(query)
        get_user_info(token)
        daily_bonus(token)
        if check_tasks(token):  # Modify this function to return whether tasks are available
            claim_referral(token)  # Only claim if there are tasks
    except Exception as e:
        print(f"Error occurred: {e}")

def process_queries():
    while True:
        with open('sesi.txt', 'r') as file:
            queries = [query.strip() for query in file.readlines()]

        for query in queries:
            process_query(query)  # Process each query sequentially

        wait_until_midnight()  # Wait until 00:01 UTC before restarting

if __name__ == "__main__":
    process_queries()
