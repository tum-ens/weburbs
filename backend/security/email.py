import os

import requests


def send_resend_email(*, to: str, subject: str, text: str) -> None:
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise ValueError("RESEND_API_KEY is not set")

    from_email = os.environ.get("EMAIL_FROM", "noreply@urbs-energymodel.com")
    from_name = os.environ.get("EMAIL_FROM_NAME", "WebUrbs")
    from_header = f"{from_name} <{from_email}>"

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": from_header,
            "to": [to],
            "subject": subject,
            "text": text,
        },
        timeout=30,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Resend API error {response.status_code}: {response.text}")


def use_resend() -> bool:
    return bool(os.environ.get("RESEND_API_KEY"))
