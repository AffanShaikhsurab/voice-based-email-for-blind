import os
import time
import smtplib
import logging
import imaplib
import email
import speech_recognition as sr
from bs4 import BeautifulSoup
from gtts import gTTS
import pyglet
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Environment variables for security
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

def play_text(text):
    try:
        logging.info(f"Playing text: {text}")
        tts = gTTS(text=text, lang='en')
        ttsname = "temp.mp3"
        tts.save(ttsname)
        music = pyglet.media.load(ttsname, streaming=False)
        music.play()
        time.sleep(music.duration)
        os.remove(ttsname)
    except Exception as e:
        logging.error(f"Error in play_text: {e}")

def get_login_user():
    try:
        login_user = os.getlogin()
        logging.info(f"User logged in: {login_user}")
        play_text(f"You are logging in from: {login_user}")
        return login_user
    except Exception as e:
        logging.error(f"Error in get_login_user: {e}")
        play_text("Error retrieving login user.")

def recognize_speech(prompt_text):
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            play_text(prompt_text)
            logging.info(f"Listening for: {prompt_text}")
            audio = r.listen(source)
            logging.info("Processing audio...")
        result = r.recognize_google(audio)
        logging.info(f"Recognized speech: {result}")
        return result
    except sr.UnknownValueError:
        logging.error("Google Speech Recognition could not understand audio.")
        play_text("Sorry, I could not understand the audio. Please try again.")
    except sr.RequestError as e:
        logging.error(f"Request error from Google Speech Recognition service: {e}")
        play_text("Could not request results from the speech recognition service.")
    except Exception as e:
        logging.error(f"Error in recognize_speech: {e}")
        play_text("An error occurred while recognizing speech.")
    return ""

def send_email(subject, msg):
    try:
        logging.info("Sending email...")
        with smtplib.SMTP('smtp.gmail.com', 587) as mail:
            mail.ehlo()
            mail.starttls()
            mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            message = MIMEMultipart()
            message['From'] = EMAIL_ADDRESS
            message['To'] = RECIPIENT_EMAIL
            message['Subject'] = subject
            message.attach(MIMEText(msg, 'plain'))
            mail.send_message(message)
        logging.info("Email sent successfully.")
        play_text("Congrats! Your mail has been sent.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        play_text("Failed to send the email. Please try again later.")

def check_inbox():
    try:
        logging.info("Checking inbox...")
        with imaplib.IMAP4_SSL('imap.gmail.com', 993) as mail:
            mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            mail.select('inbox')

            result, data = mail.search(None, 'ALL')
            mail_ids = data[0].split()
            logging.info(f"Number of emails in the inbox: {len(mail_ids)}")
            play_text(f"Total mails are: {len(mail_ids)}")

            result, data = mail.search(None, 'UNSEEN')
            unseen_ids = data[0].split()
            logging.info(f"Number of unseen emails: {len(unseen_ids)}")
            play_text(f"Your unseen mail count is: {len(unseen_ids)}")

            if mail_ids:
                result, email_data = mail.fetch(mail_ids[-1], '(RFC822)')
                raw_email = email_data[0][1].decode("utf-8")
                email_message = email.message_from_string(raw_email)

                from_ = email_message['From']
                subject = email_message['Subject']
                logging.info(f"From: {from_}, Subject: {subject}")
                play_text(f"From: {from_} and the subject is: {subject}")

                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode("utf-8")
                            logging.info(f"Email body: {body}")
                            play_text(f"Body: {body}")
                            break
                else:
                    body = email_message.get_payload(decode=True).decode("utf-8")
                    logging.info(f"Email body: {body}")
                    play_text(f"Body: {body}")

        logging.info("Inbox checked successfully.")
    except Exception as e:
        logging.error(f"Failed to check inbox: {e}")
        play_text("Failed to check the inbox. Please try again later.")

def main():
    play_text("Project: Voice based Email for the blind")

    get_login_user()

    play_text("Option 1. Compose a mail.")
    play_text("Option 2. Check your inbox.")
    play_text("Your choice")

    choice = recognize_speech("Please say your choice.")

    if 'one' in choice.lower() or '1' in choice:
        subject = recognize_speech("Please state the subject of your email.")
        message = recognize_speech("Please state your message.")
        send_email(subject, message)
    elif 'two' in choice.lower() or '2' in choice:
        check_inbox()
    else:
        logging.error("Invalid choice made by user.")
        play_text("Invalid choice, please try again.")

if __name__ == "__main__":
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD or not RECIPIENT_EMAIL:
        logging.error("Email credentials are not set in environment variables.")
        play_text("Email credentials are not set. Please set the required environment variables and try again.")
    else:
        main()
