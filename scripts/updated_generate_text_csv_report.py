import csv
import os
from datetime import datetime
import re

# Input / Output
INPUT_FILE = r"C:\Reports\export1.csv"  # Your CSV/TXT file
OUTPUT_FOLDER = r"C:\AutomationReports"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, f"Tosca_TestCase_Report_{timestamp}.html")

# Custom step details mapping (like switch-case)
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

# Parse CSV
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

        # Details / Error from CSV
        details = row[4].strip() if len(row) > 4 else ""
        exec_time = row[6].strip() if len(row) > 6 else ""
        duration = row[7].strip() if len(row) > 7 else ""
        status = "Failed" if "error" in details.lower() else "Passed"

        # ✅ Add custom description using mapping
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

# Build HTML
html_rows = ""
for tc in testcases:
    tc_status = "Failed" if any(s["status"] == "Failed" for s in tc["steps"]) else "Passed"
    tc_class = "fail" if tc_status == "Failed" else "pass"
    html_rows += f"""
    <tr>
        <td colspan="5" style="background:#e0e0e0; font-weight:bold;" class="{tc_class}">{tc['name']} - {tc_status}</td>
    </tr>
    """
    for s in tc["steps"]:
        status_class = "pass" if s["status"] == "Passed" else "fail"
        html_rows += f"""
        <tr>
            <td>{s['step']}</td>
            <td>{s['details']}</td>
            <td>{s['exec_time']}</td>
            <td>{s['duration']}</td>
            <td class="{status_class}">{s['status']}</td>
        </tr>
        """

# Summary
total_steps = sum(len(tc["steps"]) for tc in testcases)
total_failed = sum(1 for tc in testcases for s in tc["steps"] if s["status"]=="Failed")
total_passed = total_steps - total_failed

# HTML Template
html_content = f"""
<html>
<head>
<title>Tosca TestCase Execution Report</title>
<style>
body {{ font-family: Arial; background:#f4f6f9; }}
h1 {{ text-align:center; }}
.pass {{ color:green; font-weight:bold; }}
.fail {{ color:red; font-weight:bold; }}
table {{ width:95%; margin:auto; border-collapse:collapse; }}
th, td {{ border:1px solid #ccc; padding:8px; text-align:left; }}
th {{ background:#007bff; color:white; }}
.summary {{ text-align:center; margin:20px; }}
</style>
</head>
<body>

<h1>Tosca TestCase Execution Report</h1>

<div class="summary">
<p><b>Date:</b> {datetime.now()}</p>
<p><b>Total Steps:</b> {total_steps}</p>
<p class="pass">Passed: {total_passed}</p>
<p class="fail">Failed: {total_failed}</p>
</div>

<table>
<tr>
<th>Step Code</th>
<th>Details</th>
<th>Execution Time</th>
<th>Duration</th>
<th>Status</th>
</tr>

{html_rows}
</table>

</body>
</html>
"""

# Save HTML
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print("HTML report generated successfully!")
print("Saved at:", OUTPUT_FILE)