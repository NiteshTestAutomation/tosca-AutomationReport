import json
from datetime import datetime

# Load Tosca JSON report
with open("ExecutionReport.json", "r") as file:
    data = json.load(file)

execution_entries = data.get("ExecutionEntries", [])

passed = 0
failed = 0

rows = ""

for test in execution_entries:
    name = test.get("Name")
    result = test.get("Result")
    duration = test.get("Duration")

    if result.lower() == "passed":
        passed += 1
        color = "green"
    else:
        failed += 1
        color = "red"

    rows += f"""
    <tr>
        <td>{name}</td>
        <td style='color:{color}'>{result}</td>
        <td>{duration} sec</td>
    </tr>
    """

# Create HTML report
html_content = f"""
<html>
<head>
<title>Tosca Execution Report</title>
</head>
<body>
<h2>Tosca Automation Report</h2>
<p>Date: {datetime.now()}</p>
<p>Total: {len(execution_entries)}</p>
<p style='color:green'>Passed: {passed}</p>
<p style='color:red'>Failed: {failed}</p>

<table border="1" cellpadding="5">
<tr>
<th>Test Case</th>
<th>Status</th>
<th>Duration</th>
</tr>
{rows}
</table>

</body>
</html>
"""

with open("Custom_Report.html", "w") as report:
    report.write(html_content)

print("Custom report generated successfully!")