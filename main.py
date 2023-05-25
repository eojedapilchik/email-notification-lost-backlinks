import os
import time
from datetime import datetime
from helpers.gmail_handler import send_email
from helpers.airtable_handler import AirtableHandler
from dotenv import load_dotenv

load_dotenv()


def main():
    get_today_emails_to_send()


def get_today_emails_to_send():
    date_now = datetime.now().strftime("%d-%m-%y %H:%M:%S")
    email_table = os.getenv("EMAIL_QUEUE_TABLE")
    airtable_handler = AirtableHandler(email_table)
    emails = airtable_handler.get_records(filter_by_formula=" AND(OR( IS_BEFORE({Send Date}, TODAY()), "
                                                            "IS_SAME({Send Date}, TODAY())), {Status} = 'Scheduled')")
    if len(emails) > 0:
        emails_generated = parse_emails(emails)
        update_airtable(emails_generated)
    else:
        print(f"[!] {date_now} No emails to send today")


def parse_emails(emails):
    emails_generated = []
    for email in emails:
        at_email_id = email["id"]
        fields = email.get("fields")
        status = fields.get("Status")
        if fields and status == "Scheduled":
            at_record_id = fields.get("Backlink")[0]
            sequence = fields.get("Sequence")
            to = fields.get("to")
            body = fields.get("body")
            subject = fields.get("subject")
            cc = fields.get("cc")
            email_sent = send_email(to, subject, body, cc)
            emails_generated.append({"at_id": at_email_id, "google_email_id": email_sent["id"],
                                     "sequence": sequence, "at_link_id": at_record_id,
                                     "date_sent": email_sent["date"]})

    return emails_generated


def update_airtable(emails_generated):
    airtable_records_to_update = []
    airtable_handler = AirtableHandler(os.getenv("EMAIL_QUEUE_TABLE"))
    if len(emails_generated) > 0:
        for email in emails_generated:
            at_email_id = email["at_id"]
            fields = {
                "fldeoNVjJpbMNBv8d": "Sent",  # Status
                "fldhxyaaBv4IdKz40": email["google_email_id"],  # Google Email ID
                "fldcj8lw0RIQhFuy5": email["date_sent"],  # Date Sent
            }
            airtable_records_to_update.append({"id": at_email_id, "fields": fields})
            time.sleep(10)
    if len(airtable_records_to_update) > 0:
        airtable_handler.update_records(airtable_records_to_update)
        print(f"[!] {datetime.now().strftime('%d-%m-%y %H:%M:%S')} Emails sent: {len(airtable_records_to_update)}")


if __name__ == "__main__":
    main()
