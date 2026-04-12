# API Token Leakage Detector

A powerful security auditing tool built for bug bounty hunters and DevSecOps teams to discover, analyze, and validate hardcoded secrets (API keys, tokens, credentials) completely exposed within the front-end JavaScript bundles of modern web applications.

---

## 🛠️ How It Works (Project Breakdown)
Modern web applications (React, Vue, Angular) compile their code into JavaScript bundles sent directly to the client's browser. Developers often mistakenly hardcode sensitive keys into these bundles. 

This platform automates the discovery process in 5 distinct stages:

1. **🌐 Web Crawler:** Uses headless browsers to navigate to the target URL, wait for dynamic loads, and capture/download all associated `.js` bundle files.
2. **🔬 AST Syntax Analyzer:** Converts raw JavaScript into an Abstract Syntax Tree (AST) to efficiently and accurately extract all raw strings, variables, and configuration objects.
3. **🧠 Secret Detection Engine:** Scans extracted data utilizing specialized Regular Expressions (Regex) and Shannon Entropy Analysis (mathematical randomness checking) to pinpoint cryptographic keys. 
4. **🛡️ Validation Module:** Eliminates false positives by taking suspected "secrets" and live-testing them against their respective service endpoints (AWS, Stripe, etc.) to confirm if the token is actively working.
5. **🕵️ GitHub Exposure Check:** Cross-references validated keys using the GitHub API to check if the threat actor or developer has already leaked this exact key publicly on GitHub.
6. **📊 Reporting Module:** Outputs a visually distinct, color-coded terminal report of the final findings, with options to export the data.

---

## 🚀 Getting Started

### Prerequisites
Make sure you have Python installed on your machine. 

### Installation
1. Open your terminal in the project root directory.
2. Activate your virtual environment: 
   ```bash
   venv\Scripts\activate
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Install the Playwright Chromium browser binary (Required for crawling):
   ```bash
   playwright install chromium
   ```

### How to Run
The platform is operated via a Command Line Interface (CLI).

**Basic Scan:**
```bash
python src\cli.py scan https://example-website.com
```

**Advanced Scan (Export to JSON & Use Multi-threading):**
```bash
python src\cli.py scan https://example-website.com --output report.json --threads 4
```

---

## 📦 Technologies & Python Libraries Used
This project is built using modern and robust Python libraries:

* **`click`**: For building the advanced command-line terminal interface.
* **`rich`**: For rendering beautiful, color-coded terminal panels, text, and tables.
* **`playwright`**: For headless browser automation to render modern SPAs and capture asynchronous network requests.
* **`esprima`**: An ECMAScript parser used to parse downloaded JavaScript bundles into AST format for precise code inspection.
* **`requests` / `aiohttp`**: For speedy networking, downloading files, and making asynchronous HTTP validation requests to APIs.
* **`PyGithub`**: For authenticating and interacting directly with the GitHub API to check for public exposures. 
* **`beautifulsoup4` / `lxml`**: For parsing and navigating HTML documents.
* **`flask` / `fastapi`**: Included for future integrations to serve a front-end UI or dashboard.

---
**Disclaimer:** *This tool is for educational purposes, bug bounty programs, and internal auditing only. Ensure you have authorization to scan target platforms before running this software against them.*
