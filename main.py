import os

from helpers.gmail_handler import send_email
from helpers.airtable_handler import AirtableHandler
from dotenv import load_dotenv

load_dotenv()


def main():
    get_today_emails_to_send()
    pass


def get_today_emails_to_send():
    email_table = os.getenv("EMAIL_QUEUE_TABLE")
    airtable_handler = AirtableHandler(email_table)
    emails = airtable_handler.get_records(filter_by_formula=" AND(OR( IS_BEFORE({Send Date}, TODAY()), "
                                                            "IS_SAME({Send Date}, TODAY())), {Status} = 'Scheduled')")
    if len(emails) > 0:
        for email in emails:
            at_email_id = email["id"]
            fields = email.get("fields")
            status = fields.get("fields").get("Status")
            if fields and status == "Scheduled":
                at_link_id = fields.get("Backlink")[0]
                sequence = fields.get("Sequence")
                to = fields.get("to")
                body = fields.get("body")
                subject = fields.get("subject")
                cc = fields.get("cc")

            print(email)


def parse_email(email):
    pass


if __name__ == "__main__":
    main()
