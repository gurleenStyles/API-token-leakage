from .rules import detect_known_secrets
from .entropy import investigate_entropy

# Severity levels pre-assigned by secret type
SEVERITY_MAP = {
    "AWS Access Key":            "Critical",
    "AWS Secret Key":            "Critical",
    "GitHub Token":              "Critical",
    "Stripe Secret Key":         "Critical",
    "Stripe Restricted Key":     "Critical",
    "Generic Private Key":       "Critical",
    "Google API Key":            "High",
    "Slack Token":               "High",
    "SendGrid API Key":          "High",
    "Twilio API Key":            "High",
    "MailChimp API Key":         "Medium",
    "JSON Web Token":            "Medium",
    "High Entropy String":       "Low",
    "Probable Config Secret":    "Low",
}

class SecretDetector:
    def __init__(self, strings, configs):
        self.strings = strings
        self.configs = configs
        self.findings = []
        
    def analyze(self):
        """Run all detection logic on the extracted strings and configs."""
        # 1. Regex rules
        for s in self.strings:
            matches = detect_known_secrets(s)
            for m in matches:
                self.findings.append({
                    "detector": "regex",
                    "type": m["type"],
                    "secret": m["value"],
                    "severity": SEVERITY_MAP.get(m["type"], "Info")
                })
        
        # 2. Extract values from config objects
        # Use a separate list to avoid mutating self.strings and running config values through entropy twice
        extra_strings = []
        for config in self.configs:
            for key, val in config.items():
                if isinstance(val, str):
                    extra_strings.append(val)
                    key_lower = key.lower()
                    if any(term in key_lower for term in ['key', 'secret', 'token', 'pass', 'auth', 'cred']):
                        self.findings.append({
                            "detector": "config_key_heuristic",
                            "type": "Probable Config Secret",
                            "secret": val,
                            "context": key,
                            "severity": SEVERITY_MAP.get("Probable Config Secret", "Info")
                        })

        # 3. Entropy heuristics on all strings
        # Combine original strings with config values for entropy analysis only
        for s in set(self.strings + extra_strings):
            # Skip strings shorter than 20 characters — real tokens/keys are almost always longer
            if len(s) < 20:
                continue
            # Skip noisy non-secret strings to reduce false positives
            if ' ' in s:
                continue
            if s.startswith('http://') or s.startswith('https://'):
                continue
            if '/' in s:
                continue
            if any(s.endswith(ext) for ext in ['.com', '.js', '.css', '.html', '.json']):
                continue
            is_high, ent_value = investigate_entropy(s)
            if is_high:
                self.findings.append({
                    "detector": "entropy",
                    "type": "High Entropy String",
                    "secret": s,
                    "entropy": round(ent_value, 2),
                    "severity": SEVERITY_MAP.get("High Entropy String", "Info")
                })
                
        # Deduplicate findings based on secret value
        # Regex findings always win over entropy / config_key_heuristic for the same secret
        unique_secrets = {}
        for f in self.findings:
            if f["secret"] not in unique_secrets:
                unique_secrets[f["secret"]] = f
            elif f["detector"] == "regex":
                # Overwrite with the more specific regex finding
                unique_secrets[f["secret"]] = f
                
        return list(unique_secrets.values())
