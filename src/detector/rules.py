import re

KNOWN_SECRETS = {
    "Google API Key": r"AIza[0-9A-Za-z-_]{35}",
    "Stripe Secret Key": r"sk_live_[0-9a-zA-Z]{24}",
    "Stripe Restricted Key": r"rk_live_[0-9a-zA-Z]{24}",
    "AWS Access Key": r"(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
    "AWS Secret Key": r"(?i)aws_(?:secret_)?(?:access_)?key.{0,20}[=:].{0,5}['\"]([A-Za-z0-9/+=]{40})['\"]",
    "GitHub Token": r"(gh[pousr]_[A-Za-z0-9_]{36,255})",
    "Slack Token": r"xox[baprs]-[0-9]{12}-[0-9]{12}-[0-9a-zA-Z]{24}",
    "Twilio API Key": r"SK[0-9a-fA-F]{32}",
    "SendGrid API Key": r"SG\.[\w_]{16,32}\.[\w_]{16,64}",
    "MailChimp API Key": r"[0-9a-f]{32}-us[0-9]{1,2}",
    "JSON Web Token (JWT)": r"ey[A-Za-z0-9_-]{10,}\.ey[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
    "Generic Private Key": r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |)PRIVATE KEY-----",
}

def detect_known_secrets(text):
    """Scan text against known regex signatures and return matches."""
    matches = []
    for secret_name, pattern in KNOWN_SECRETS.items():
        found = re.findall(pattern, text)
        for val in found:
            matches.append({
                "type": secret_name,
                "value": val if isinstance(val, str) else text, # Handling groups
            })
    return matches
