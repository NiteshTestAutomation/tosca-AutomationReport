import csv
import os
from datetime import datetime
import re

# Input / Output
INPUT_FILE = r"C:\Reports\export1.csv"  # Your CSV/TXT file
OUTPUT_FOLDER = r"C:\AutomationReports"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, f"Tosca_TestCaseOutsideTable_{timestamp}.html")

# ------------------------
# Custom step details mapping
# ------------------------
step_details_map = {
    "01_POST_LoginAuth": "Authenticate user via API",
    "02_GET_Encrypt_UserName": "Encrypt username",
    "03_GET_Encrypt_Password": "Encrypt password",
    "04_POST_Login": "Perform login",
    "05_GET AccountIndex": "Get Account index",
    "06_POST Account Validate": "Validate account",
    "07_POST Prepare Amount Transfer": "Prepare amount transfer",
    "08_Get Otp": "Get OTP",
    "09_POST Transfer Amount": "Perform transfer"
}

# ------------------------
# Parse CSV
# ------------------------
testcases = []
current_tc = None

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if not row or len(row) < 2:
            continue

        step_code = row[1].strip()

        # TestCase line: in < ... >
        if step_code.startswith("<") and step_code.endswith(">"):
            tc_name = step_code.strip("<>").strip()
            current_tc = {"name": tc_name, "steps": []}
            testcases.append(current_tc)
            continue

        # Ignore lines without number prefix
        if not re.match(r'^\d+', step_code):
            continue

        # Step details
        details = row[4].strip() if len(row) > 4 else ""
        exec_time = row[6].strip() if len(row) > 6 else ""
        duration = row[7].strip() if len(row) > 7 else ""
        status = "Failed" if "error" in details.lower() else "Passed"

        # Add custom description
        custom_detail = step_details_map.get(step_code, "")
        if custom_detail:
            details = details + " (" + custom_detail + ")" if details else custom_detail

        if current_tc:
            current_tc["steps"].append({
                "step": step_code,
                "details": details,
                "exec_time": exec_time,
                "duration": duration,
                "status": status
            })

# ------------------------
# Build HTML
# ------------------------
html_content = f"""
<html>
<head>
<title>Transfer API Test Execution Report</title>
<style>
body {{ font-family: Arial; background:#f4f6f9; font-size:12px; }}
h1 {{ text-align:center; font-size:16px; }}
h2 {{ font-size:14px; margin-top:20px; color:#333; }}
.pass {{ color:green; font-weight:bold; }}
.fail {{ color:red; font-weight:bold; }}
table {{ width:95%; margin:auto; border-collapse:collapse; font-size:12px; table-layout:auto; }}
th, td {{ border:1px solid #ccc; padding:6px; line-height:1.2; text-align:left; }}
th {{ background:#007bff; color:white; }}
.summary {{ text-align:center; margin:10px; font-size:12px; }}
</style>
</head>
<body>

<h1>Transfer API Tosca TestCase Execution Report</h1>
<div class="summary">
<p><b>Date:</b> {datetime.now()}</p>
</div>
"""

# Add TestCases
for tc in testcases:
    tc_status = "Failed" if any(s["status"] == "Failed" for s in tc["steps"]) else "Passed"
    tc_class = "fail" if tc_status == "Failed" else "pass"

    # TestCase header outside the table
    html_content += f"<h2>{tc['name']} - <span class='{tc_class}'>{tc_status}</span></h2>\n"

    # Steps table for this TestCase
    html_content += """
    <table>
    <tr>
        <th>Step Code</th>
        <th>Details / Description</th>
        <th>Execution Time</th>
        <th>Duration</th>
        <th>Status</th>
    </tr>
    """

    for s in tc["steps"]:
        status_class = "pass" if s["status"] == "Passed" else "fail"
        html_content += f"""
        <tr>
            <td>{s['step']}</td>
            <td>{s['details']}</td>
            <td>{s['exec_time']}</td>
            <td>{s['duration']}</td>
            <td class="{status_class}">{s['status']}</td>
        </tr>
        """

    html_content += "</table>\n"

# Close HTML
html_content += "</body></html>"

# Save HTML
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print("HTML report generated successfully with TestCase names outside the table!")
print("Saved at:", OUTPUT_FILE)