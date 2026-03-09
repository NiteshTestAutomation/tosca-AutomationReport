import json
import os
import glob
from datetime import datetime
import re

# ----------------------------
# CONFIGURATION
# ----------------------------
INPUT_FOLDER = r"C:\Reports\8March"
OUTPUT_FOLDER = r"C:\AutomationReports"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, f"Tosca_Merged_JSON_Report_{timestamp}.html")

# ----------------------------
# STEP DESCRIPTION MAPPING (optional)
# ----------------------------
step_details_map = {
    "01_POST_LoginAuth": "Authenticate user via API",
    "02_GET_Encrypt_UserName": "Encrypt username",
    "03_GET_Encrypt_Password": "Encrypt password",
    "04_POST_Login": "Perform login",
    "05_GET AccountIndex": "Get account index",
    "06 POST local-transfer/Validate Request": "Validate transfer request",
    "07 POST local-transfer/Prepare Request": "Prepare transfer request",
    "08_Get Otp": "Get OTP",
    "09 POST local-transfer/Transfer Request": "Perform transfer"
}

fail_keywords = ["error", "fail", "exception", "timeout"]

# ----------------------------
# FIND ALL JSON FILES
# ----------------------------
INPUT_FILES = glob.glob(os.path.join(INPUT_FOLDER, "*.json"))
if not INPUT_FILES:
    print("No JSON files found in folder:", INPUT_FOLDER)
    exit()

print(f"Found {len(INPUT_FILES)} JSON files")

# ----------------------------
# MERGE ALL JSON REPORTS
# ----------------------------
testcases = []

for file in INPUT_FILES:
    print("Reading:", file)
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

        pages = data.get("Document", {}).get("Pages", [])
        for page in pages:
            tables = page.get("Tables", [])
            for table in tables:
                if table.get("ID") != "TreeStructure":
                    continue
                body_lines = table.get("BodyLines", [])

                # Treat first line with unnamed_0 as TestCase name
                tc_name = body_lines[0].get("unnamed_0", "Unknown TestCase")
                steps = []

                for line in body_lines[1:]:
                    step_name = line.get("Name", "").strip()
                    if step_name == "":
                        continue

                    details = line.get("Detail", "").strip()
                    exec_time = line.get("StartTime", "").strip()
                    duration = line.get("Duration", "").strip()

                    # Determine status
                    status = "Failed" if any(k in details.lower() for k in fail_keywords) else "Passed"

                    # Optional mapping
                    if step_name in step_details_map:
                        custom = step_details_map[step_name]
                        details = f"{details} ({custom})" if details else custom

                    steps.append({
                        "step": step_name,
                        "details": details,
                        "exec_time": exec_time,
                        "duration": duration,
                        "status": status,
                        "source": os.path.basename(file)
                    })

                if steps:
                    testcases.append({
                        "name": tc_name,
                        "steps": steps,
                        "source": os.path.basename(file)
                    })

# ----------------------------
# BUILD HTML REPORT
# ----------------------------
html_content = f"""
<html>
<head>
<title>Tosca Merged JSON Execution Report</title>
<style>
body {{ font-family: Arial; background:#f4f6f9; font-size:13px; }}
h1 {{ text-align:center; }}
h2 {{ margin-top:25px; color:#333; }}
.pass {{ color:green; font-weight:bold; }}
.fail {{ color:red; font-weight:bold; }}
table {{ width:95%; margin:auto; border-collapse:collapse; }}
th, td {{ border:1px solid #ccc; padding:6px; text-align:left; }}
th {{ background:#007bff; color:white; }}
.summary {{ text-align:center; margin:15px; }}
</style>
</head>
<body>
<h1>Tosca Merged JSON TestCase Execution Report</h1>
<div class="summary">
<p><b>Date:</b> {datetime.now()}</p>
<p><b>Total TestCases:</b> {len(testcases)}</p>
</div>
"""

for tc in testcases:
    steps = tc["steps"]
    tc_status = "Failed" if any(s["status"] == "Failed" for s in steps) else "Passed"
    tc_class = "fail" if tc_status == "Failed" else "pass"

    html_content += f"<h2>{tc['name']} - <span class='{tc_class}'>{tc_status}</span> (Source: {tc['source']})</h2>"

    html_content += """
    <table>
    <tr>
        <th>Step Code</th>
        <th>Details</th>
        <th>Execution Time</th>
        <th>Duration</th>
        <th>Status</th>
    </tr>
    """

    for step in steps:
        status_class = "pass" if step["status"] == "Passed" else "fail"
        html_content += f"""
        <tr>
            <td>{step['step']}</td>
            <td>{step['details']}</td>
            <td>{step['exec_time']}</td>
            <td>{step['duration']}</td>
            <td class="{status_class}">{step['status']}</td>
        </tr>
        """

    html_content += "</table>"

html_content += "</body></html>"

# ----------------------------
# SAVE HTML REPORT
# ----------------------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print("\nMerged JSON HTML report generated successfully!")
print("Saved at:", OUTPUT_FILE)