from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from googleapiclient.discovery import build
from helpers.gmail_handler import send_email
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

sender = os.getenv('GMAIL_SENDER', 'legal-dispute@resumedone.io')


class EmailSchema(BaseModel):
    subject: str
    body: str
    to: str
    at_record_id: Optional[str] = None


@app.get("/")
def read_root():
    return {"Status": "online"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.post("/send_email")
async def email_endpoint(background_tasks: BackgroundTasks, email: EmailSchema):
    # Add the send_email task to the background tasks
    #(to, subject, message_text, sender=_sender, at_record_id=None)
    background_tasks.add_task(send_email, email.to, email.subject, email.body, email.at_record_id, sender)
    return {"status": "email scheduled"}
