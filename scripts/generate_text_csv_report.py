import csv
import os
from datetime import datetime

# Input / Output
INPUT_FILE = r"C:\Reports\export1.csv"  # Your CSV/TXT file
OUTPUT_FOLDER = r"C:\AutomationReports"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, f"Tosca_CSV_Report_{timestamp}.html")

# Read CSV
steps = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if not row or len(row) < 2:
            continue

        # Step Code is in column 1
        step_code = row[1].strip()
        if not step_code:
            continue

        # Details / Error Message in column 5
        details = row[4].strip() if len(row) > 4 else ""

        # Execution timestamp in column 6 or 7
        exec_time = row[6].strip() if len(row) > 6 else ""

        # Duration in column 7 or 8
        duration = row[7].strip() if len(row) > 7 else ""

        # Status: failed if details mention "error"
        status = "Failed" if "error" in details.lower() else "Passed"

        steps.append({
            "step": step_code,
            "details": details,
            "exec_time": exec_time,
            "duration": duration,
            "status": status
        })

# Summary
total = len(steps)
failed = sum(1 for s in steps if s["status"] == "Failed")
passed = total - failed

# Build HTML rows
rows = ""
for s in steps:
    status_class = "pass" if s["status"] == "Passed" else "fail"
    rows += f"""
    <tr>
        <td>{s['step']}</td>
        <td>{s['details']}</td>
        <td>{s['exec_time']}</td>
        <td>{s['duration']}</td>
        <td class="{status_class}">{s['status']}</td>
    </tr>
    """

# HTML Template
html_content = f"""
<html>
<head>
<title>Tosca CSV Execution Report</title>
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

<h1>Tosca CSV Execution Report</h1>

<div class="summary">
<p><b>Date:</b> {datetime.now()}</p>
<p><b>Total Steps:</b> {total}</p>
<p class="pass">Passed: {passed}</p>
<p class="fail">Failed: {failed}</p>
</div>

<table>
<tr>
<th>Step Code</th>
<th>Details / Error</th>
<th>Execution Time</th>
<th>Duration</th>
<th>Status</th>
</tr>

{rows}
</table>

</body>
</html>
"""

# Save HTML
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print("HTML report generated successfully!")
print("Saved at:", OUTPUT_FILE)