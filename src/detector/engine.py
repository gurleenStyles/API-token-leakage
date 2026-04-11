from .rules import detect_known_secrets
from .entropy import investigate_entropy

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
                    "secret": m["value"]
                })
        
        # 2. Extract values from config objects
        for config in self.configs:
            for key, val in config.items():
                if isinstance(val, str):
                    self.strings.append(val)
                    key_lower = key.lower()
                    if any(term in key_lower for term in ['key', 'secret', 'token', 'pass', 'auth', 'cred']):
                        self.findings.append({
                            "detector": "config_key_heuristic",
                            "type": "Probable Config Secret",
                            "secret": val,
                            "context": key
                        })

        # 3. Entropy heuristics on all strings
        for s in set(self.strings):
            is_high, ent_value = investigate_entropy(s)
            if is_high:
                self.findings.append({
                    "detector": "entropy",
                    "type": "High Entropy String",
                    "secret": s,
                    "entropy": round(ent_value, 2)
                })
                
        # Deduplicate findings based on secret value
        unique_secrets = {}
        for f in self.findings:
            if f["secret"] not in unique_secrets:
                unique_secrets[f["secret"]] = f
                
        return list(unique_secrets.values())
