import csv
import os
import glob
from datetime import datetime
import re

# ----------------------------
# CONFIGURATION
# ----------------------------
INPUT_FOLDER = r"C:\Reports\8March"
OUTPUT_FOLDER = r"C:\AutomationReports"

# INPUT_FOLDER = r"C:\Reports"

# Detect all CSV files
input_files = glob.glob(os.path.join(INPUT_FOLDER, "*.csv"))

print("CSV files detected:")
for f in input_files:
    print(f)

testcases = []

step_pattern = r'^\d+_[A-Za-z0-9_]+'
fail_keywords = ["error", "fail", "exception", "timeout"]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, f"Tosca_Merged_Report_{timestamp}.html")

# ----------------------------
# STEP DESCRIPTION MAPPING
# ----------------------------
step_details_map = {
    "01_POST_LoginAuth": "Authenticate user via API",
    "02_GET_Encrypt_UserName": "Encrypt username",
    "03_GET_Encrypt_Password": "Encrypt password",
    "04_POST_Login": "Perform login",
    "05_GET": "Get account index",
    "06_POST": "Validate account",
    "07_POST": "Prepare amount transfer",
    "08_Get": "Get OTP",
    "09_POST": "Perform transfer"
}

# ----------------------------
# FIND ALL CSV FILES
# ----------------------------
INPUT_FILES = glob.glob(os.path.join(INPUT_FOLDER, "*.csv"))

print(f"Found {len(INPUT_FILES)} CSV files")

testcases = []

# Step detection pattern
step_pattern = r'^\d+_[A-Za-z0-9_]+'

# Failure keywords
fail_keywords = ["error", "fail", "exception", "timeout"]

# ----------------------------
# PARSE ALL FILES
# ----------------------------
for file in input_files:

    print("\nReading file:", file)

    current_tc = None

    with open(file, "r", encoding="utf-8") as f:

        reader = csv.reader(f)

        for row in reader:

            if not row or len(row) < 2:
                continue

            step_code = row[1].strip()

            # ----------------------------
            # Detect TestCase
            # ----------------------------
            if "<" in step_code and ">" in step_code:

                tc_name = step_code.replace("<", "").replace(">", "").strip()

                current_tc = {
                    "name": tc_name,
                    "steps": []
                }

                testcases.append(current_tc)

                print("Detected TestCase:", tc_name)

                continue

            if current_tc is None:
                continue

            if step_code == "":
                continue

            # ----------------------------
            # Detect Step Codes
            # ----------------------------
            if not re.match(step_pattern, step_code):
                continue

            # ----------------------------
            # Extract Step Details
            # ----------------------------
            details = row[4].strip() if len(row) > 4 else ""
            exec_time = row[6].strip() if len(row) > 6 else ""
            duration = row[7].strip() if len(row) > 7 else ""

            # ----------------------------
            # Failure Detection
            # ----------------------------
            status = "Passed"

            for k in fail_keywords:
                if k in details.lower():
                    status = "Failed"
                    break

            # ----------------------------
            # Step Mapping
            # ----------------------------
            step_key = step_code.strip()

            custom_detail = ""

            if step_key in step_details_map:
                custom_detail = step_details_map[step_key]

            if custom_detail:
                if details:
                    details = details + " (" + custom_detail + ")"
                else:
                    details = custom_detail

            # ----------------------------
            # Store Step
            # ----------------------------
            current_tc["steps"].append({
                "step": step_key,
                "details": details,
                "exec_time": exec_time,
                "duration": duration,
                "status": status
            })
# ----------------------------
# BUILD HTML REPORT
# ----------------------------
html_content = f"""
<html>
<head>
<title>Tosca Merged Execution Report</title>

<style>
body {{ font-family: Arial; background:#f4f6f9; }}

h1 {{ text-align:center }}

h2 {{ margin-top:25px }}

.pass {{ color:green; font-weight:bold }}
.fail {{ color:red; font-weight:bold }}

table {{
width:95%;
margin:auto;
border-collapse:collapse;
}}

th, td {{
border:1px solid #ccc;
padding:6px;
text-align:left;
}}

th {{
background:#007bff;
color:white;
}}

.summary {{
text-align:center;
margin:15px;
}}

</style>
</head>

<body>

<h1>Tosca Merged TestCase Execution Report</h1>

<div class="summary">

<p><b>Date:</b> {datetime.now()}</p>
<p><b>Total TestCases:</b> {len(testcases)}</p>

</div>
"""

# ----------------------------
# ADD TESTCASES
# ----------------------------
for tc in testcases:

    if not tc["steps"]:
        continue

    tc_status = "Failed" if any(s["status"] == "Failed" for s in tc["steps"]) else "Passed"

    tc_class = "fail" if tc_status == "Failed" else "pass"

    html_content += f"<h2>{tc['name']} - <span class='{tc_class}'>{tc_status}</span></h2>"

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

    for step in tc["steps"]:

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
# SAVE REPORT
# ----------------------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Merged HTML report generated")
print("Saved at:", OUTPUT_FILE)