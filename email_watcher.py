import time
import threading
import imaplib
import email
from email.header import decode_header
import traceback
import winsound
import os
import asyncio
import edge_tts
import speech_recognition as sr
import tempfile
from playsound3 import playsound
import socket
from datetime import datetime
import re

# ------------- CONFIG -------------
GMAIL_USER = "awabbhammad8@gmail.com"
GMAIL_PASS = "etbg xuql hcxo ohro"
CHECK_INTERVAL = 20  # seconds
LAST_UID_FILE = "last_seen_uid.txt"
IMAP_HOST = "imap.gmail.com"
# ----------------------------------

OTP_REGEX = re.compile(r"\b(?:OTP|One[- ]?Time[- ]?Password|verification code|code)[:\s]*([0-9]{4,8})\b", re.IGNORECASE)
GENERIC_DIGIT_REGEX = re.compile(r"\b([0-9]{4,8})\b")  # fallback if explicit words missing

# -----------------------
# Utility: IP + date
# -----------------------
def get_local_ip():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        # handle localhost fallback
        if ip.startswith("127.") or ip == "0.0.0.0":
            # attempt another method
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
            except:
                pass
            finally:
                s.close()
        return ip
    except:
        return "Unknown"

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -----------------------
# TTS helpers (safe)
# -----------------------
async def _create_tts_file(text):
    # create unique temp file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        path = f.name
    try:
        tts = edge_tts.Communicate(text, voice="en-US-AriaNeural")
        # save writes to path
        await tts.save(path)
        return path
    except Exception as e:
        # cleanup on error
        try:
            if os.path.exists(path):
                os.remove(path)
        except:
            pass
        raise

def speak(text, block=True):
    """Generate TTS and play it. block=True waits until finished playing."""
    try:
        mp3_path = asyncio.run(_create_tts_file(text))
    except Exception as e:
        print("TTS generation failed:", e)
        return

    try:
        # play (playsound blocks until finished)
        playsound(mp3_path)
    except Exception as e:
        print("Playing TTS failed:", e)
    finally:
        # remove temp file
        try:
            os.remove(mp3_path)
        except:
            pass

# -----------------------
# Other helpers
# -----------------------
def play_notification_sound():
    try:
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    except:
        try:
            winsound.Beep(1000, 300)
        except:
            pass

def decode_text(field):
    if not field:
        return ""
    decoded_parts = decode_header(field)
    parts = []
    for part, charset in decoded_parts:
        try:
            if isinstance(part, bytes):
                parts.append(part.decode(charset or "utf-8", errors="ignore"))
            else:
                parts.append(str(part))
        except:
            parts.append(str(part))
    return " ".join(parts)

def read_last_uid():
    if os.path.exists(LAST_UID_FILE):
        try:
            with open(LAST_UID_FILE, "r") as f:
                val = f.read().strip()
                return val if val else None
        except:
            return None
    return None

def save_last_uid(uid):
    try:
        with open(LAST_UID_FILE, "w") as f:
            # ensure string
            f.write(uid.decode() if isinstance(uid, bytes) else str(uid))
    except Exception as e:
        print("Could not save last uid:", e)

def extract_otp(text):
    if not text:
        return None
    # first try explicit OTP wording
    m = OTP_REGEX.search(text)
    if m:
        return m.group(1)
    # fallback: find likely 4-8 digit standalone
    m2 = GENERIC_DIGIT_REGEX.search(text)
    if m2:
        return m2.group(1)
    return None

# -----------------------
# Core watcher
# -----------------------
def check_new_emails_periodic(notify_callback=None):
    """
    1) Every CHECK_INTERVAL seconds announce count of unseen emails (voice).
    2) If there are *new* UIDs since last_seen, play sound + call notify_callback with subject and sender.
    """
    print(f"[{now_str()}] Email watcher starting for {GMAIL_USER}")
    print(f"Local IP: {get_local_ip()}")
    last_uid = read_last_uid()
    # convert to bytes for comparison when needed
    if last_uid:
        try:
            last_uid_bytes = last_uid.encode()
        except:
            last_uid_bytes = None
    else:
        last_uid_bytes = None

    while True:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_HOST)
            mail.login(GMAIL_USER, GMAIL_PASS)
            mail.select("inbox")

            result, data = mail.search(None, "UNSEEN")
            if result != "OK":
                print("IMAP search failed:", result, data)
                mail.logout()
                time.sleep(CHECK_INTERVAL)
                continue

            mail_ids = data[0].split()  # list of bytes uids
            unseen_count = len(mail_ids)
            # Announce count every interval (as requested)
            try:
                # voice the count (in English or change to Urdu if you'd like)
                if unseen_count == 0:
                    speak(f"You have zero unread emails.")
                elif unseen_count == 1:
                    speak(f"You have one unread email.")
                else:
                    speak(f"You have {unseen_count} unread emails.")
            except Exception as e:
                print("Voice count failed:", e)

            # determine whether there are UIDs greater than last_uid_bytes
            new_uids = []
            if mail_ids:
                if last_uid_bytes is None:
                    # if never seen before, consider the latest only as new (to avoid blasting old ones)
                    new_uids = [mail_ids[-1]]  # latest only
                else:
                    for u in mail_ids:
                        # compare as integers to be safer
                        try:
                            if int(u) > int(last_uid_bytes):
                                new_uids.append(u)
                        except:
                            if u > last_uid_bytes:
                                new_uids.append(u)

            if new_uids:
                # We'll work with only the latest UID for announcement (as requested)
                latest_uid = new_uids[-1]
                print(f"[{now_str()}] New UID(s) detected: {new_uids} -> announcing latest {latest_uid.decode() if isinstance(latest_uid, bytes) else latest_uid}")
                # play sound
                play_notification_sound()

                # safe fetch of latest message (RFC822)
                try:
                    result, msg_data = mail.fetch(latest_uid, "(RFC822)")
                    if result != "OK" or not msg_data or not msg_data[0]:
                        print("Failed to fetch message for UID", latest_uid)
                    else:
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)

                        subject = decode_text(msg["Subject"])
                        sender = decode_text(msg.get("From"))

                        # get text/plain payload if possible, else html
                        body = ""
                        html_body = ""
                        attachments_found = []
                        
                        downloads_dir = os.path.join(os.getcwd(), "downloads")
                        if not os.path.exists(downloads_dir):
                            os.makedirs(downloads_dir)

                        if msg.is_multipart():
                            for part in msg.walk():
                                ctype = part.get_content_type()
                                cdisp = str(part.get("Content-Disposition"))
                                
                                if ctype == "text/plain" and "attachment" not in cdisp:
                                    try:
                                        payload = part.get_payload(decode=True)
                                        charset = part.get_content_charset() or "utf-8"
                                        body = payload.decode(charset, errors="ignore")
                                    except:
                                        pass
                                elif ctype == "text/html" and "attachment" not in cdisp:
                                    try:
                                        payload = part.get_payload(decode=True)
                                        charset = part.get_content_charset() or "utf-8"
                                        html_body = payload.decode(charset, errors="ignore")
                                    except:
                                        pass
                                elif "attachment" in cdisp:
                                    try:
                                        filename = part.get_filename()
                                        if filename:
                                            filepath = os.path.join(downloads_dir, filename)
                                            with open(filepath, "wb") as f:
                                                f.write(part.get_payload(decode=True))
                                            attachments_found.append(filename)
                                            print(f"Saved attachment: {filepath}")
                                    except Exception as e:
                                        print(f"Error saving attachment: {e}")

                        else:
                            try:
                                payload = msg.get_payload(decode=True)
                                charset = msg.get_content_charset() or "utf-8"
                                if msg.get_content_type() == "text/html":
                                    html_body = payload.decode(charset, errors="ignore")
                                else:
                                    body = payload.decode(charset, errors="ignore")
                            except:
                                body = ""

                        # Prefer plain text, fallback to stripped HTML
                        final_body = body
                        if not final_body and html_body:
                            # Simple tag stripping
                            final_body = re.sub('<[^<]+?>', '', html_body)
                            final_body = re.sub(r'\s+', ' ', final_body).strip()
                        
                        if attachments_found:
                            final_body += f"\n\n(Attachments saved: {', '.join(attachments_found)})"

                        # Call notify_callback if provided
                        if notify_callback:
                            notify_callback(subject, sender, final_body)

                        # update last_uid to latest_uid and persist
                        save_last_uid(latest_uid)
                        last_uid_bytes = latest_uid

                        # Optionally mark as seen if desired — currently not marking automatically.
                        # If you want to mark read automatically uncomment next line:
                        # mail.store(latest_uid, '+FLAGS', '\\Seen')

                except imaplib.IMAP4.abort as e:
                    print("IMAP abort during fetch, will reconnect next cycle:", e)
                except Exception as e:
                    print("Error while fetching/processing latest email:", e)
                    traceback.print_exc()

            mail.logout()

        except Exception as e:
            print("Watcher loop error:", e)
            traceback.print_exc()

        # wait interval
        time.sleep(CHECK_INTERVAL)

def check_emails_once():
    """
    Fetch and return a list of unseen emails as [(subject, sender), ...]
    """
    emails = []
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST)
        mail.login(GMAIL_USER, GMAIL_PASS)
        mail.select("inbox")

        result, data = mail.search(None, "UNSEEN")
        if result == "OK":
            mail_ids = data[0].split()
            for uid in mail_ids[-10:]:  # Limit to last 10 to avoid overload
                try:
                    result, msg_data = mail.fetch(uid, "(RFC822)")
                    if result == "OK" and msg_data:
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        subject = decode_text(msg["Subject"])
                        sender = decode_text(msg.get("From"))
                        emails.append((subject, sender))
                except Exception as e:
                    print(f"Error fetching email {uid}: {e}")

        mail.logout()
    except Exception as e:
        print(f"Error checking emails: {e}")

    return emails

# -----------------------
# Start as thread/main
# -----------------------
if __name__ == "__main__":
    t = threading.Thread(target=check_new_emails_periodic, daemon=True)
    t.start()
    print("Email watcher thread started. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting watcher.")
