import speech_recognition as sr
import smtplib
import os
import time
from bs4 import BeautifulSoup
import email
import imaplib
from gtts import gTTS
import pyglet

def play_text(text):
    tts = gTTS(text=text, lang='en')
    ttsname = "temp.mp3"
    tts.save(ttsname)
    music = pyglet.media.load(ttsname, streaming=False)
    music.play()
    time.sleep(music.duration)
    os.remove(ttsname)

def get_login_user():
    login_user = os.getlogin()
    print(f"You are logging in from: {login_user}")
    return login_user

def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        print("Processing...")
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    return ""

def send_email(msg):
    try:
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login('affanshaikhsurabofficial@gmail.com', 'Affanaffan@youtube')  # Replace with actual email and password
        mail.sendmail('affanshaikhsurabofficial@gmail.com', 'needfitagency@gmail.com', msg)  # Replace with actual recipient email
        mail.close()
        print("Congrats! Your mail has been sent.")
        play_text("Congrats! Your mail has been sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_inbox():
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        mail.login('your_email@gmail.com', 'your_password')  # Replace with actual email and password
        mail.select('Inbox')

        result, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()
        print(f"Number of mails in your inbox: {len(mail_ids)}")
        play_text(f"Total mails are: {len(mail_ids)}")

        result, data = mail.search(None, 'UNSEEN')
        unseen_ids = data[0].split()
        print(f"Number of unseen mails: {len(unseen_ids)}")
        play_text(f"Your unseen mail count is: {len(unseen_ids)}")

        if mail_ids:
            result, email_data = mail.fetch(mail_ids[-1], '(RFC822)')
            raw_email = email_data[0][1].decode("utf-8")
            email_message = email.message_from_string(raw_email)

            from_ = email_message['From']
            subject = email_message['Subject']
            print(f"From: {from_}")
            print(f"Subject: {subject}")
            play_text(f"From: {from_} and your subject is: {subject}")

            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8")
                        print(f"Body: {body}")
                        play_text(f"Body: {body}")
                        break
            else:
                body = email_message.get_payload(decode=True).decode("utf-8")
                print(f"Body: {body}")
                play_text(f"Body: {body}")

        mail.close()
        mail.logout()
    except Exception as e:
        print(f"Failed to check inbox: {e}")

def main():
    play_text("Project: Voice based Email for blind")

    login_user = get_login_user()

    play_text("Option 1. Compose a mail.")
    play_text("Option 2. Check your inbox.")
    play_text("Your choice")

    choice = recognize_speech()
    print(f"You said: {choice}")

    if 'one' in choice.lower() or '1' in choice:
        play_text("Your message")
        message = recognize_speech()
        print(f"You said: {message}")
        send_email(message)
    elif 'two' in choice.lower() or '2' in choice:
        check_inbox()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
