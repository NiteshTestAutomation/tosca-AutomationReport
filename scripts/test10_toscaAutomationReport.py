import json
import os
import re
import glob
from datetime import datetime

# ----------------------------
# CONFIGURATION
# ----------------------------
INPUT_FOLDER = r"C:\Reports\10March"  # Folder containing Tosca JSON files
OUTPUT_FOLDER = r"C:\AutomationReports"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, f"Tosca_Execution_Report_{timestamp}.html")

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
    "09 POST local-transfer/Transfer Request": "Perform transfer",
    "09 POST user-accounts-transfer/Transfer": "Perform transfer",
    "06_POST Account Validate": "Validate transfer request",
    "07_POST Prepare Amount Transfer": "Prepare transfer request",
    "09_POST Transfer Amount": "Perform transfer",
    "06_POST user-accounts-transfer/Validate": "Validate transfer request",
    "07_POST user-accounts-transfer/Prepare": "Prepare transfer request",
    "08_POST user-accounts-transfer/Transfer": "Perform transfer",
    "06_POST_charity-transfer/Validate": "Validate transfer request",
    "07_POST_charity-transfer/Prepare": "Prepare transfer request",
    "09_POST_charity-transfer/Transfer": "Perform transfer",
    "06_POST local-transfer/Validate Request": "Validate transfer request",
    "07_POST local-transfer/Prepare Request": "Prepare transfer request",
    "09_POST local-transfer/Transfer Request": "Perform transfer",
    "06_GET Currencies": "Get Currency",
    "07_POST alinma-express/convert-Currency": "Convert Currency",
    "08_POST alinma-express/validate": "Validate transfer request",
    "09_POST alinma-express/prepare": "Prepare transfer request",
    "10_Get Otp": "Get OTP",
    "11_POST alinma-express/transfer": "Perform transfer",
    "06_POST Convert Currency": "Convert Currency",
    "07_GET Currency": "Get Currency",
    "08_POST swift-transfer/Validate": "Validate transfer request",
    "09_POST swift-transfer/Prepare": "Prepare transfer request",
    "11_POST swift-transfer/Transfer": "Perform transfer",
    "06_POST westernUnion/convert-currency": "Convert Currency",
    "07_POST westernUnion/validate": "Validate transfer request",
    "08_POST westernUnion/prepare": "Prepare transfer request",
    "09_Get Otp": "Get OTP",
    "10_POST westernUnion/Transfer": "Perform transfer"
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
# MERGE JSON REPORTS
# ----------------------------
testcases = []
total_steps = 0
total_steps_passed = 0
total_steps_failed = 0
total_tc_passed = 0
total_tc_failed = 0

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

                # TestCase name = first line
                tc_name = body_lines[0].get("unnamed_0", "Unknown TestCase")
                steps = []
                tc_buffers = {}  # <-- store all buffers for this test case

                for line in body_lines[1:]:
                    step_name = line.get("Name", "").strip()
                    if step_name == "":
                        continue

                    # Capture buffers from loginfo
                    loginfo = line.get("Loginfo", "").strip()
                    if "Buffer with name" in loginfo:
                        match = re.search(
                            r'Buffer with name:\s*"([^"]+)"\s*has been set to value:\s*"([^"]+)"',
                            loginfo
                        )
                        if match:
                            buffer_name = match.group(1)
                            buffer_value = match.group(2)
                            tc_buffers[buffer_name] = buffer_value

                    # Skip steps not in mapping
                    if step_name not in step_details_map:
                        continue

                    details = line.get("Detail", "").strip()
                    exec_time = line.get("StartTime", "").strip()
                    duration = line.get("Duration", "").strip()

                    # Step status based on Detail or Loginfo
                    combined_text = (details + " " + loginfo).lower()
                    status = "Failed" if any(k in combined_text for k in fail_keywords) else "Passed"

                    # Optional description mapping
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
                    # Update step counters
                    total_steps += len(steps)
                    total_steps_passed += sum(1 for s in steps if s["status"] == "Passed")
                    total_steps_failed += sum(1 for s in steps if s["status"] == "Failed")

                    # TestCase status
                    tc_status = "Failed" if any(s["status"] == "Failed" for s in steps) else "Passed"
                    if tc_status == "Failed":
                        total_tc_failed += 1
                    else:
                        total_tc_passed += 1

                    testcases.append({
                        "name": tc_name,
                        "steps": steps,
                        "status": tc_status,
                        "source": os.path.basename(file),
                        "buffers": tc_buffers  # <-- store buffers here
                    })

# ----------------------------
# BUILD HTML REPORT WITH SUMMARY
# ----------------------------
project_name = 'Internet Banking - API'
environment_name = "UAT"
executed_user = "Nitesh Badge"
module_name = "Transfer"
testing_type = "Smoke Suite"

html_content = f"""
<html>
<head>
<title>Tosca Execution Report</title>
<style>
body {{ font-family: Arial, sans-serif; background: #f4f6f9; font-size: 13px; margin: 0; padding: 0; }}
h1 {{ text-align: center; margin-top: 20px; }}
h2 {{ margin-top: 25px; color: #333; }}
.pass {{ color: green; font-weight: bold; }}
.fail {{ color: red; font-weight: bold; }}
table {{ width: 95%; margin: 10px auto 30px auto; border-collapse: collapse; background-color: #fff; }}
th, td {{ border: 1px solid #ccc; padding: 6px 8px; text-align: left; font-size: 13px; }}
th {{ background-color: #007bff; color: white; }}
tr:nth-child(even) {{ background-color: #f9f9f9; }}
tr:hover {{ background-color: #f1f1f1; }}
.summary {{ text-align: center; margin: 15px; font-size: 14px; }}
.card {{ max-width: 900px; margin: 20px auto 40px auto; border: 1px solid #ddd; border-radius: 12px; background-color: #fff; padding: 30px 40px; }}
.summary-box {{ display: flex; justify-content: center; flex-wrap: wrap; gap: 25px; margin-top: 20px; }}
.summary-item {{ text-align: center; padding: 10px 20px; border-radius: 8px; min-width: 120px; }}
.total {{ background-color: #e6f0ff; color: #007bff; font-weight: bold; }}
.passed {{ background-color: #e6ffe6; color: green; font-weight: bold; }}
.failed {{ background-color: #ffe6e6; color: red; font-weight: bold; }}
</style>
</head>
<body>
<h1>Alinma QA Automation Execution Report</h1>

<div class="card">
    <div style="text-align: center; margin-bottom: 20px;">
        <h2>{project_name} Execution Summary</h2>
        <p><b>Module Name:</b> {module_name} &nbsp;|&nbsp; 
           <b>Environment:</b> {environment_name} &nbsp;|&nbsp;    
           <b>Test Execution:</b> {testing_type} &nbsp;|&nbsp; 
           <b>Executed By:</b> {executed_user}</p>
    </div>

    <div class="summary-box">
        <div class="summary-item total">Total TestCases<br>{len(testcases)}</div>
        <div class="summary-item passed">Passed TestCases<br>{total_tc_passed}</div>
        <div class="summary-item failed">Failed TestCases<br>{total_tc_failed}</div>
        <div class="summary-item total">Total Steps<br>{total_steps}</div>
        <div class="summary-item passed">Steps Passed<br>{total_steps_passed}</div>
        <div class="summary-item failed">Steps Failed<br>{total_steps_failed}</div>
    </div>
</div>
"""

# ----------------------------
# ADD TESTCASES AND BUFFERS
# ----------------------------
for tc in testcases:
    steps = tc["steps"]
    tc_class = "fail" if tc["status"]=="Failed" else "pass"

    # # Buffer table
    # buffers = tc.get("buffers", {})
    # buffer_html = ""
    # if buffers:
    #     buffer_html += "<table><tr><th>Buffer Name</th><th>Value</th></tr>"
    #     for name, value in buffers.items():
    #         buffer_html += f"<tr><td>{name}</td><td>{value}</td></tr>"
    #     buffer_html += "</table>"

    # html_content += f"<h2>{tc['name']} - <span class='{tc_class}'>{tc['status']}</span> (Source: {tc['source']})</h2>"
    # html_content += buffer_html

    # Get sessionReference from buffers if available
    session_value = tc.get("buffers", {}).get("b_sessionReference", "N/A")

    # Add session value directly in heading
    html_content += f"<h2>{tc['name']} - <span class='{tc_class}'>{tc['status']}</span> (Session Id: {session_value})</h2>"

    # Steps table
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
        status_class = "pass" if step["status"]=="Passed" else "fail"
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

print("\nMerged JSON HTML report with summary & buffers generated successfully!")
print("Saved at:", OUTPUT_FILE)