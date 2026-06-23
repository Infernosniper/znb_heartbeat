import os
import sys
import smtplib
import urllib.request
import urllib.error
from email.mime.text import MIMEText
from datetime import datetime, timezone

SITE_URL = os.environ["SITE_URL"]
ALERT_EMAIL = os.environ["ALERT_EMAIL"]
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
TIMEOUT = int(os.environ.get("TIMEOUT_SECONDS", "30"))


def check_site():
    try:
        req = urllib.request.Request(SITE_URL, method="GET")
        req.add_header("User-Agent", "UptimeMonitor/1.0")
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
        status = resp.getcode()
        if status >= 400:
            return False, f"HTTP {status}"
        return True, f"HTTP {status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return False, f"Connection failed: {e.reason}"
    except Exception as e:
        return False, str(e)


def send_alert(error_detail):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    subject = f"ALERT: {SITE_URL} is DOWN"
    body = f"{SITE_URL} is unreachable.\n\nTime: {now}\nError: {error_detail}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_EMAIL

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [ALERT_EMAIL], msg.as_string())

    print(f"Alert sent to {ALERT_EMAIL}")


if __name__ == "__main__":
    ok, detail = check_site()
    now = datetime.now(timezone.utc).strftime("%H:%M UTC")
    if ok:
        print(f"[{now}] {SITE_URL} is UP ({detail})")
    else:
        print(f"[{now}] {SITE_URL} is DOWN ({detail}) — sending alert")
        send_alert(detail)
        sys.exit(1)
