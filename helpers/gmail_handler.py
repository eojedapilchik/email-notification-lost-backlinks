from __future__ import print_function
import os.path
import base64
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

_sender = os.getenv('GMAIL_SENDER')
script_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(script_dir)


def authenticate_google_account():
    service = None
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print('authenticate_google_account: No valid credentials found.')
            credentials_path = os.path.join(parent_dir, 'credentials.json')
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path,
                SCOPES)
            creds = flow.run_local_server(port=0)
            print(f"A new window to authorize app is required. Please check your browser.")

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
    except HttpError as error:
        print(f'An error occurred trying gmail service: {error}')
    return service


def send_email(to, subject, message_text, at_record_id=None, cc=None, sender=_sender):
    if not message_text or not to or not subject:
        raise ValueError("Cannot send email without message, to, and subject")
    service = authenticate_google_account()
    # Get the current date and time
    current_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    message = create_message(sender, to, cc, subject, message_text)
    message_sent = send_message(service, 'me', message)
    message_sent['date'] = current_date
    if at_record_id is not None:
        pass
        # TODO: update airtable if at_record_id is not None
    return message_sent


def create_message(sender, to, cc, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    if cc:
        message['cc'] = cc
    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}


def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except HttpError as error:
        print(f'An error occurred: {error}')


def list_messages_with_subject(service, user_id, subject):
    try:
        response = service.users().messages().list(userId=user_id,
                                                   q=subject).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=subject,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except HttpError as error:
        print(f'An error occurred: {error}')


def get_message(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        #print(f'Message snippet: {message["snippet"]}')

        return message
    except HttpError as error:
        print(f'An error occurred: {error}')


def get_thread(service, user_id, thread_id):
    try:
        thread = service.users().threads().get(userId=user_id, id=thread_id).execute()
        messages = thread['messages']
        #print(f'Thread ID: {thread["id"]}')
        #print(f'Number of messages in this thread: {len(messages)}')
        #print(f'Snippet of the last message: {messages[-1]["snippet"]}')

        # The original email is the first email in the thread
        original_email = messages[0]
        #print(f'Original email Subject: {original_email["payload"]["headers"]}')
        #print(f'Original email Subject: {original_email["id"]}')
        return thread
    except HttpError as error:
        print(f'An error occurred: {error}')


def check_if_reply(service, user_id, msg_id):
    message = get_message(service, user_id, msg_id)
    thread_id = message['threadId']

    if thread_id:
        thread = get_thread(service, user_id, thread_id)
        # If the thread has more than one email, the message is a reply
        if len(thread['messages']) > 1:
            print(f'Message {msg_id} is a reply.')
            return True
        else:
            print(f'Message {msg_id} is not a reply.')
            return False
    else:
        print(f'Message {msg_id} is not a reply.')
        return False


def list_threads_last_24_hours(user_id):
    try:
        service = authenticate_google_account()
        # Calculate the timestamp for 24 hours ago
        after = datetime.now() - timedelta(hours=24)
        after = int(after.timestamp())

        # Query all threads from the last 24 hours
        response = service.users().threads().list(userId=user_id,
                                                  q=f'after:{after}').execute()

        threads = []
        if 'threads' in response:
            threads.extend(response['threads'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().threads().list(userId=user_id,
                                                      q=f'after:{after}',
                                                      pageToken=page_token).execute()
            threads.extend(response['threads'])

        return threads
    except HttpError as error:
        print(f'An error occurred: {error}')


def get_threads_with_replies(user_id="me"):

    service = authenticate_google_account()
    threads = list_threads_last_24_hours(user_id)
    threads_replied = []
    for thread in threads:
        thread_data = get_thread(service, user_id, thread['id'])
        messages = thread_data['messages']
        # print(f'Number of messages in this thread: {len(messages)}')
        if len(messages) >= 2:
            found_reply = False
            for msg in messages:
                message = get_message(service, user_id, msg['id'])
                for header in message['payload']['headers']:
                    if header['name'] == 'In-Reply-To':
                        # print(f'\n ** This email is a reply to: {header["value"]}\n')
                        threads_replied.append(thread['id'])
                        found_reply = True
                        break
                        # print(f'\n ** This email is a reply to: {header["value"]}\n')
                if found_reply:
                    break
    print(f'Number of threads replied: {len(threads_replied)}')
    return threads_replied


def main():
    service = authenticate_google_account()
    current_date = datetime.now().strftime("%Y %H:%M:%S")
    sender = "legal-dispute@resumedone.io"
    to = "eojedapilchik@gmail.com"
    subject = "Test email"
    message_text = "Hello, this is a test email sent at " + current_date + " from Python"

    # send an email
    # raw_message = create_message(sender, to, subject, message_text)
    # send_message(service, "me", raw_message)

    # get replies
    # messages = list_messages_with_subject(service, "me", subject)
    # for msg in messages:
    #     get_message(service, "me", msg['id'])

    get_threads_with_replies("me")


if __name__ == '__main__':
    main()
