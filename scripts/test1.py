import re
import os
from datetime import datetime

INPUT_FILES = [
    r"C:\Reports\export1.csv",
    r"C:\Reports\export2.csv",
    r"C:\Reports\export3.csv",
    r"C:\Reports\export4.csv",
    r"C:\Reports\export5.csv",
    r"C:\Reports\export6.csv",
    r"C:\Reports\export7.csv"
]
OUTPUT_FOLDER = r"C:\AutomationReports"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, f"Tosca_Merged_Report_{timestamp}.html")
# ✅ MUST BE OUTSIDE LOOP
testcases = []

# -----------------------------------
# READ ALL FILES
# -----------------------------------
for INPUT_FILE in INPUT_FILES:

    current_tc = None

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            # ----------------------
            # Detect TestCase
            # ----------------------
            if "<" in line and ">" in line:
                match = re.search(r'<(.*?)>', line)
                if match:
                    tc_name = match.group(1).strip()

                    current_tc = {
                        "name": tc_name,
                        "steps": []
                    }

                    testcases.append(current_tc)

                continue

            # Ignore description line
            if line.startswith("Transfer API"):
                continue

            # ----------------------
            # Detect Steps
            # ----------------------
            if re.match(r'^\d+', line) and current_tc:
                parts = re.split(r'\s{2,}', line)

                step_name = parts[0]
                exec_time = parts[1] if len(parts) > 1 else ""
                duration = parts[2] if len(parts) > 2 else ""

                current_tc["steps"].append({
                    "step": step_name,
                    "exec_time": exec_time,
                    "duration": duration,
                    "status": "Passed"
                })

# -----------------------------------
# DEBUG CHECK
# -----------------------------------
print("Total TestCases Detected:", len(testcases))

html_content = f"""
<html>
<head>
<title>Tosca Merged Execution Report</title>
<style>
body {{ font-family: Arial; background:#f4f6f9; font-size:13px; }}
h1 {{ text-align:center; }}
h2 {{ margin-top:25px; color:#333; }}
.pass {{ color:green; font-weight:bold; }}
.fail {{ color:red; font-weight:bold; }}
table {{ width:95%; margin:auto; border-collapse:collapse; table-layout:auto; }}
th, td {{ border:1px solid #ccc; padding:6px; text-align:left; }}
th {{ background:#007bff; color:white; }}
.summary {{ text-align:center; margin:15px; }}
</style>
</head>
<body>

<h1>Tosca Merged TestCase Execution Report</h1>

<div class="summary">
<p><b>Date:</b> {datetime.now()}</p>
<p><b>Total TestCases:</b> {len(testcases)}</p>
</div>
"""

# Add TestCases
for tc in testcases:
    if not tc["steps"]:
        continue

    tc_status = "Failed" if any(s["status"] == "Failed" for s in tc["steps"]) else "Passed"
    tc_class = "fail" if tc_status == "Failed" else "pass"

    html_content += f"<h2>{tc['name']} - <span class='{tc_class}'>{tc_status}</span></h2>\n"

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

print("\nMerged HTML report generated successfully!")
print("Saved at:", OUTPUT_FILE)


