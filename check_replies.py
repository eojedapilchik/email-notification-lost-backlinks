import requests
import json
import os
from dotenv import load_dotenv
from helpers.gmail_handler import get_threads_with_replies
from datetime import datetime

load_dotenv()


def main():
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    at_webhook = os.getenv("AT_WEBHOOK_EMAILS")
    threads_replied = get_threads_with_replies()
    if len(threads_replied) > 0:
        response = post_threads_replied(threads_replied, at_webhook)
        if response.status_code == 200:
            print(f" {current_datetime} The request to AT was successful! \nThreads replied: {threads_replied}")
        else:
            print(f"There was an error with the request. Status code: {response.status_code}")


def post_threads_replied(threads_replied, url):
    current_datetime = datetime.now()
    data = json.dumps({"email_ids": threads_replied, "datetime": current_datetime.isoformat()})
    response = requests.post(url, data=data, headers={'Content-Type': 'application/json'})

    return response


if __name__ == '__main__':
    main()
