# NOT FOR SALE, FREE TO CLONE OR RENAME
# PAY IT FORDWARD!
import requests
import json
import time
import os
from datetime import datetime, timedelta
from colorama import Fore, Style, init

init(autoreset=True)

TELEGRAM_BOT_TOKEN = 'TELEGRAM_BOT_TOKEN' # 333217932:aoj3poeohdowa201eh10u
CHAT_ID = 'CHAT_ID' # -263218379

class Endpoints:
    AUTH_LOGIN = "/auth/login"
    USER_CURRENT = "/user/current"
    DAILY_BONUS = "/bonus/dailyBonus"
    TASKS = "/quest"
    VERIFY_TASK = "/quest/{task_id}/verify"
    CLAIM_TASK = "/quest/{task_id}/claim"
    CLAIM_REF = "/refLink/claim"

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

def retry_request(func, *args, retries=3, delay=5, **kwargs):
    """Retries a function if it raises an exception."""
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"{Fore.YELLOW}Error on attempt {attempt + 1}: {e}{Style.RESET_ALL}")
            if attempt < retries - 1:
                print(f"{Fore.YELLOW}Retrying in {delay} seconds...{Style.RESET_ALL}")
                time.sleep(delay)
            else:
                print(f"{Fore.RED}Max retries reached.{Style.RESET_ALL}")
                raise

def get_token_and_login(payload):
    time.sleep(5)
    headers = get_headers()
    body = json.dumps({"webAppData": payload})
    print(f"{Fore.CYAN}Attempting to login with payload...{Style.RESET_ALL}")
    try:
        response = requests.post(f"{BASE_API_URL}{Endpoints.AUTH_LOGIN}", headers=headers, data=body, timeout=10)
        response.raise_for_status()
        token = response.json().get("jwt", {}).get("access", {}).get("token", None)
        if token:
            print(f"{Fore.GREEN}Login successful.{Style.RESET_ALL}")
            return token
        else:
            raise ValueError("Failed to retrieve token from response.")
    except requests.RequestException as e:
        print(f"{Fore.RED}Request failed during login: {e}{Style.RESET_ALL}")
        raise
    except ValueError as e:
        print(f"{Fore.RED}Value error: {e}{Style.RESET_ALL}")
        raise

def get_user_info(token, send_message=True):
    time.sleep(5)
    headers = get_headers(token)
    print(f"{Fore.CYAN}Fetching user info...{Style.RESET_ALL}")
    try:
        response = requests.get(f"{BASE_API_URL}{Endpoints.USER_CURRENT}", headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"{Fore.GREEN}Account: {data['tgUsername']}, Balance: {data['balance']}{Style.RESET_ALL}")

        if send_message:
            balance_message = f"<b>Account:</b> {data['tgUsername']}\n<b>Balance:</b> {data['balance']}"
            send_telegram_message(balance_message)

        return data
    except requests.RequestException as e:
        print(f"{Fore.RED}Request failed while fetching user info: {e}{Style.RESET_ALL}")
        raise
    except KeyError as e:
        print(f"{Fore.RED}Key error in user info response: {e}{Style.RESET_ALL}")
        raise

def send_telegram_message(message):
    """Send a message to the specified Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"{Fore.GREEN}Telegram message sent successfully.{Style.RESET_ALL}")
    except requests.RequestException as e:
        print(f"{Fore.RED}Failed to send message to Telegram: {e}{Style.RESET_ALL}")

def daily_bonus(token):
    time.sleep(5)
    headers = get_headers(token)
    print(f"{Fore.CYAN}Attempting to collect daily bonus...{Style.RESET_ALL}")
    try:
        response = requests.post(f"{BASE_API_URL}{Endpoints.DAILY_BONUS}", headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("result", False):
            print(f"{Fore.GREEN}Daily login successful. Streaks: {data['streaks']}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Daily bonus already claimed or not available.{Style.RESET_ALL}")
    except requests.RequestException as e:
        print(f"{Fore.RED}Request failed while claiming daily bonus: {e}{Style.RESET_ALL}")
    except KeyError as e:
        print(f"{Fore.RED}Key error in daily bonus response: {e}{Style.RESET_ALL}")

def fetch_and_check_tasks(token):
    time.sleep(5)
    headers = get_headers(token)
    print(f"{Fore.CYAN}Fetching and checking tasks from the external source...{Style.RESET_ALL}")

    try:
        response = requests.get(f"{BASE_API_URL}{Endpoints.TASKS}", headers=headers)
        response.raise_for_status()
        tasks_data = response.json()
        task_categories_count = len(tasks_data)
        print(f"{Fore.GREEN}Fetched {task_categories_count} task categories.{Style.RESET_ALL}")

        any_claimed_or_clicked = False

        for task_category in tasks_data:
            task_count = len(task_category['quests'])
            print(f"{Fore.CYAN}Processing {task_count} tasks in category: {task_category['name']}{Style.RESET_ALL}")

            for task in task_category['quests']:
                print(f"{Fore.BLUE}Task: {task['name']}, Status: {task['status']}, Claim Allowed: {task.get('claimAllowed', 'Not Specified')}{Style.RESET_ALL}")

                if task.get("claimAllowed") is True:
                    claim_task(token, task["id"])
                    any_claimed_or_clicked = True

                elif task.get("claimAllowed") is False and task_category['name'] == "Daily":
                    verify_daily_task(token, task["id"])
                    any_claimed_or_clicked = True

        if not any_claimed_or_clicked:
            print(f"{Fore.YELLOW}No tasks available to claim or click.{Style.RESET_ALL}")
            return False
        return True

    except requests.RequestException as e:
        print(f"{Fore.RED}Request failed while fetching tasks: {e}{Style.RESET_ALL}")
        return False
    except KeyError as e:
        print(f"{Fore.RED}Key error in task fetching response: {e}{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
        return False

def claim_task(token, task_id):
    headers = get_headers(token)
    try:
        print(f"{Fore.CYAN}Attempting to claim task with ID: {task_id}{Style.RESET_ALL}")
        response = requests.put(f"{BASE_API_URL}{Endpoints.CLAIM_TASK.format(task_id=task_id)}", headers=headers)
        response.raise_for_status()
        data = response.json()
        print(f"{Fore.GREEN}Claim response data: {data}{Style.RESET_ALL}") 
    except requests.RequestException as e:
        print(f"{Fore.RED}Request failed while claiming task ID {task_id}: {e}{Style.RESET_ALL}")

def verify_daily_task(token, task_id):
    headers = get_headers(token)
    try:
        print(f"{Fore.CYAN}Verifying daily task with ID: {task_id}{Style.RESET_ALL}")
        response = requests.put(f"{BASE_API_URL}{Endpoints.VERIFY_TASK.format(task_id=task_id)}", headers=headers)
        response.raise_for_status()
        data = response.json()
        print(f"{Fore.GREEN}Verify response data: {data}{Style.RESET_ALL}")
    except requests.RequestException as e:
        print(f"{Fore.RED}Request failed while verifying daily task ID {task_id}: {e}{Style.RESET_ALL}")

def claim_referral(token):
    headers = get_headers(token)
    try:
        print(f"{Fore.CYAN}Attempting to claim referral link...{Style.RESET_ALL}")
        response = requests.post(f"{BASE_API_URL}{Endpoints.CLAIM_REF}", headers=headers)
        response.raise_for_status()
        data = response.json()
        print(f"{Fore.GREEN}Claim referral response data: {data}{Style.RESET_ALL}") 
    except requests.RequestException as e:
        print(f"{Fore.RED}Request failed while claiming referral link: {e}{Style.RESET_ALL}")

def dynamic_countdown(sleep_time):
    while sleep_time > 0:
        hours, remainder = divmod(sleep_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"\r{Fore.YELLOW}Waiting until 00:01 UTC to restart... {int(hours):02}:{int(minutes):02}:{int(seconds):02}{Style.RESET_ALL}", end="")
        time.sleep(1)
        sleep_time -= 1
    print() 

def wait_until_midnight():
    now = datetime.utcnow()
    next_run = now.replace(hour=0, minute=1, second=0, microsecond=0)
    if now >= next_run:
        next_run += timedelta(days=1)
    sleep_time = (next_run - now).total_seconds()
    dynamic_countdown(int(sleep_time))

def process_queries():
    if not os.path.exists('sesi.txt'):
        print(f"{Fore.RED}Error: sesi.txt file not found.{Style.RESET_ALL}")
        return

    all_balances = []

    while True:
        with open('sesi.txt', 'r') as file:
            queries = file.readlines()

        for query in queries:
            try:
                token = retry_request(get_token_and_login, query.strip())
                user_info = retry_request(get_user_info, token, send_message=False)
                old_balance = user_info['balance']

                daily_bonus(token)
                claim_referral(token)

                tasks_available = retry_request(fetch_and_check_tasks, token)
                if not tasks_available:
                    print(f"{Fore.YELLOW}No tasks available to claim for account {user_info['tgUsername']}. Moving to next account.{Style.RESET_ALL}")
                    continue

                updated_user_info = retry_request(get_user_info, token)
                new_balance = updated_user_info['balance']

                if new_balance != old_balance:
                    account_balance_message = f"<b>Account:</b> {updated_user_info['tgUsername']}\n<b>Balance:</b> {new_balance}"
                    all_balances.append(account_balance_message)
                else:
                    print(f"{Fore.YELLOW}No change in balance for account {updated_user_info['tgUsername']}. Skipping message.{Style.RESET_ALL}")

            except Exception as e:
                print(f"{Fore.RED}Error processing query: {e}{Style.RESET_ALL}")

        if all_balances:
            final_balance_message = "Here are the balances for all accounts after solving tasks:\n" + "\n".join(all_balances)
            send_telegram_message(final_balance_message)
        else:
            print(f"{Fore.YELLOW}No balances changed, no summary message sent.{Style.RESET_ALL}")

        print(f"{Fore.YELLOW}Waiting for 1 hour before processing accounts again...{Style.RESET_ALL}")
        time.sleep(3600)

        wait_until_midnight()

if __name__ == "__main__":
    process_queries()
