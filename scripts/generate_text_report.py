import os
import re
from datetime import datetime

INPUT_FILE = r"C:\Reports\export.txt"
OUTPUT_FOLDER = r"C:\AutomationReports"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, f"Tosca_Hierarchical_Report_{timestamp}.html")

steps = []
current_step = None

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in lines:
    line = line.rstrip()

    # Detect step number like 01_POST, 02_GET etc.
    match = re.search(r'(\d+_[A-Z]+)', line)
    if match:
        if current_step:
            steps.append(current_step)

        step_code = match.group(1)

        # Extract duration
        duration_match = re.search(r'(\d+\.\d+:\d+\.\d+)', line)
        duration = duration_match.group(1) if duration_match else ""

        current_step = {
            "name": step_code,
            "details": "",
            "duration": duration,
            "status": "Passed"
        }

        # Detect failure message
        if "error" in line.lower():
            current_step["status"] = "Failed"

    elif current_step:
        # Collect multiline names or messages
        clean_line = line.strip()
        if clean_line:
            current_step["details"] += clean_line + " "

            if "error" in clean_line.lower():
                current_step["status"] = "Failed"

# Append last step
if current_step:
    steps.append(current_step)

# Summary
total = len(steps)
failed = sum(1 for s in steps if s["status"] == "Failed")
passed = total - failed

# Build HTML rows
rows = ""
for step in steps:
    status_class = "pass" if step["status"] == "Passed" else "fail"

    rows += f"""
    <tr>
        <td>{step['name']}</td>
        <td>{step['details']}</td>
        <td>{step['duration']}</td>
        <td class="{status_class}">{step['status']}</td>
    </tr>
    """

html_content = f"""
<html>
<head>
<title>Tosca Hierarchical Report</title>
<style>
body {{ font-family: Arial; background:#f4f6f9; }}
h1 {{ text-align:center; }}
.pass {{ color:green; font-weight:bold; }}
.fail {{ color:red; font-weight:bold; }}
table {{ width:95%; margin:auto; border-collapse:collapse; }}
th, td {{ border:1px solid #ccc; padding:8px; }}
th {{ background:#007bff; color:white; }}
.summary {{ text-align:center; margin:20px; }}
</style>
</head>

<body>

<h1>Tosca API Execution Report</h1>

<div class="summary">
<p><b>Date:</b> {datetime.now()}</p>
<p><b>Total Steps:</b> {total}</p>
<p class="pass">Passed: {passed}</p>
<p class="fail">Failed: {failed}</p>
</div>

<table>
<tr>
<th>Step Code</th>
<th>Details</th>
<th>Duration</th>
<th>Status</th>
</tr>

{rows}

</table>

</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Report generated successfully!")
print("Saved at:", OUTPUT_FILE)