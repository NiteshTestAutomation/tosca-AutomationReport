import json
import os
import glob
from datetime import datetime

# ----------------------------
# CONFIGURATION
# ----------------------------
INPUT_FOLDER = r"C:\Reports\8March"     # Folder containing Tosca JSON files
OUTPUT_FOLDER = r"C:\AutomationReports"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, f"Tosca_Merged_JSON_Report_{timestamp}.html")

# ----------------------------
# Project details
# ----------------------------
project_name = "Internet Banking",
environment_name = "UAT",
executed_user = "nmbadge@alinma.com",
automation_type = "API"


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
    "09 POST user-accounts-transfer/Transfer": "Perform transfer"
    # Add other mappings as needed
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

                for line in body_lines[1:]:
                    step_name = line.get("Name", "").strip()
                    if step_name == "":
                        continue

                    details = line.get("Detail", "").strip()
                    exec_time = line.get("StartTime", "").strip()
                    duration = line.get("Duration", "").strip()
                    loginfo = line.get("Loginfo", "").strip()

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
                    total_steps_passed += sum(1 for s in steps if s["status"]=="Passed")
                    total_steps_failed += sum(1 for s in steps if s["status"]=="Failed")

                    # TestCase status
                    tc_status = "Failed" if any(s["status"]=="Failed" for s in steps) else "Passed"
                    if tc_status == "Failed":
                        total_tc_failed +=1
                    else:
                        total_tc_passed +=1

                    testcases.append({
                        "name": tc_name,
                        "steps": steps,
                        "status": tc_status,
                        "source": os.path.basename(file)
                    })

# ----------------------------
# BUILD HTML REPORT WITH SUMMARY
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
.summary {{ text-align:center; margin:15px; font-size:14px; }}
</style>
</head>
<body>
<h1>Alinma QA Automation Execution Report</h1>
<div class="summary">
<div style="max-width: 900px; margin: 50px auto; font-family: Arial, sans-serif; border: 1px solid #ddd; border-radius: 12px; box-shadow: 0 6px 18px rgba(0,0,0,0.1); background-color: #fff; padding: 30px 40px;">

    <!-- Project, Environment & Time -->
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="margin: 0; color: #333;">{project_name}</h2>
        <p style="margin: 5px 0; font-size: 16px; color: #555;">
            <b>Environment:</b> {environment_name} &nbsp;|&nbsp; 
            <b>Automation Type:</b> {automation_type} &nbsp;|&nbsp; 
            <b>Executed By:</b> {executed_user}
        </p>
        <p style="margin: 5px 0; font-size: 14px; color: #888;">
            <b>Execution Time:</b> {datetime.now()}
        </p>
    </div>

    <!-- Horizontal Test Summary -->
    <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 25px; margin-top: 20px;">
        <div style="text-align: center; padding: 10px 20px; border-radius: 8px; background-color: #e6f0ff;">
            <b style="color: #007bff;">Total TestCases</b><br>
            <span style="color: #007bff; font-weight: bold;">{len(testcases)}</span>
        </div>
        <div style="text-align: center; padding: 10px 20px; border-radius: 8px; background-color: #e6ffe6;">
            <b style="color: green;">Passed TestCases</b><br>
            <span style="color: green; font-weight: bold;">{total_tc_passed}</span>
        </div>
        <div style="text-align: center; padding: 10px 20px; border-radius: 8px; background-color: #ffe6e6;">
            <b style="color: red;">Failed TestCases</b><br>
            <span style="color: red; font-weight: bold;">{total_tc_failed}</span>
        </div>
        <div style="text-align: center; padding: 10px 20px; border-radius: 8px; background-color: #e6f0ff;">
            <b style="color: #007bff;">Total Steps</b><br>
            <span style="color: #007bff; font-weight: bold;">{total_steps}</span>
        </div>
        <div style="text-align: center; padding: 10px 20px; border-radius: 8px; background-color: #e6ffe6;">
            <b style="color: green;">Steps Passed</b><br>
            <span style="color: green; font-weight: bold;">{total_steps_passed}</span>
        </div>
        <div style="text-align: center; padding: 10px 20px; border-radius: 8px; background-color: #ffe6e6;">
            <b style="color: red;">Steps Failed</b><br>
            <span style="color: red; font-weight: bold;">{total_steps_failed}</span>
        </div>
    </div>

</div>
</div>
"""

# ----------------------------
# ADD TESTCASES TABLES
# ----------------------------
for tc in testcases:
    steps = tc["steps"]
    tc_class = "fail" if tc["status"]=="Failed" else "pass"
    html_content += f"<h2>{tc['name']} - <span class='{tc_class}'>{tc['status']}</span> (Source: {tc['source']})</h2>"

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

print("\nMerged JSON HTML report with summary generated successfully!")
print("Saved at:", OUTPUT_FILE)