import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="API Token Leakage Dashboard")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Simple UI to view recent scan reports."""
    files = [f for f in os.listdir('.') if f.endswith('.json')]
    
    html_content = f"""
    <html>
        <head>
            <title>Leakage Detector Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }}
                h1 {{ color: #333; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #007bff; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .High {{ color: red; font-weight: bold; }}
                .Critical {{ color: darkred; font-weight: bold; text-decoration: underline; }}
                .Medium {{ color: orange; }}
            </style>
        </head>
        <body>
            <h1>API Token Leakage Reports</h1>
            <p>Available JSON reports in current directory: {', '.join(files) if files else 'None'}</p>
            <ul>
    """
    for f in files:
        html_content += f"<li><a href='/report/{f}'>View {f}</a></li>"
        
    html_content += """
            </ul>
        </body>
    </html>
    """
    return html_content

@app.get("/report/{filename}", response_class=HTMLResponse)
async def view_report(filename: str):
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Report not found")
        
    with open(filename, 'r') as f:
        data = json.load(f)
        
    html_content = f"""
    <html>
        <head>
            <title>Report - {data.get('target', 'Unknown')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #007bff; color: white; }}
                .High {{ color: red; font-weight: bold; }}
                .Critical {{ color: darkred; font-weight: bold; text-decoration: underline; }}
                .Medium {{ color: orange; }}
                .back-btn {{ padding: 10px 15px; background: #333; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <a href="/" class="back-btn">Back to Dashboard</a>
            <h2>Scan Report for: <a href="{data.get('target', '#')}">{data.get('target', 'Unknown')}</a></h2>
            <p>Total Secrets Found: {data.get('total_findings', 0)}</p>
            <table>
                <tr>
                    <th>Type</th>
                    <th>Secret Fragment</th>
                    <th>Validation</th>
                    <th>Severity</th>
                    <th>GitHub Exposed</th>
                </tr>
    """
    
    for item in data.get('findings', []):
        secret = item.get("secret", "")
        secret_preview = secret[:10] + "..." + secret[-5:] if len(secret) > 15 else secret
        sev = item.get("severity", "Info")
        
        html_content += f"""
                <tr>
                    <td>{item.get('type')}</td>
                    <td><code>{secret_preview}</code></td>
                    <td>{item.get('validation')}</td>
                    <td class="{sev}">{sev}</td>
                    <td>{item.get('github_exposed', 'N/A')}</td>
                </tr>
        """
        
    html_content += """
            </table>
        </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    print("Starting Dashboard on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
