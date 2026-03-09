import json
from datetime import datetime

# INPUT_FILE = "ExecutionReport.json"
# OUTPUT_FILE = "Tosca_Custom_Report.html"


INPUT_FILE = r"C:\Reports\export.json"

# with open(INPUT_FILE, "r", encoding="utf-8") as f:
#     data = json.load(f)
#



with open(INPUT_FILE, "r") as f:
    data = json.load(f)

OUTPUT_FILE = r"C:\AutomationReports\Tosca_Custom_Report.html"
execution_entries = data.get("ExecutionEntries", [])

total = len(execution_entries)
passed = 0
failed = 0
test_rows = ""

for test in execution_entries:
    name = test.get("Name")
    result = test.get("Result", "Unknown")
    duration = test.get("Duration", "0")

    status_class = "pass" if result.lower() == "passed" else "fail"

    if result.lower() == "passed":
        passed += 1
    else:
        failed += 1

    # Step details
    step_rows = ""
    for step in test.get("TestSteps", []):
        step_result = step.get("Result", "Unknown")
        step_class = "pass" if step_result.lower() == "passed" else "fail"
        error_msg = step.get("ErrorMessage", "")

        step_rows += f"""
        <tr>
            <td>{step.get("Name")}</td>
            <td class="{step_class}">{step_result}</td>
            <td>{error_msg}</td>
        </tr>
        """

    test_rows += f"""
    <tr class="{status_class}">
        <td>{name}</td>
        <td>{result}</td>
        <td>{duration} ms</td>
    </tr>
    <tr>
        <td colspan="3">
            <table class="inner-table">
                <tr>
                    <th>Step Name</th>
                    <th>Status</th>
                    <th>Error</th>
                </tr>
                {step_rows}
            </table>
        </td>
    </tr>
    """

html_content = f"""
<html>
<head>
<title>Tosca Execution Report</title>
<style>
body {{
    font-family: Arial;
    background-color: #f4f6f9;
}}

h1 {{
    text-align: center;
}}

.summary {{
    text-align: center;
    margin: 20px;
}}

.pass {{
    color: green;
    font-weight: bold;
}}

.fail {{
    color: red;
    font-weight: bold;
}}

table {{
    width: 90%;
    margin: auto;
    border-collapse: collapse;
    margin-bottom: 20px;
}}

th, td {{
    border: 1px solid #ccc;
    padding: 8px;
    text-align: left;
}}

th {{
    background-color: #007bff;
    color: white;
}}

.inner-table {{
    width: 100%;
    margin-top: 10px;
}}
</style>
</head>

<body>

<h1>Tosca Automation Execution Report</h1>

<div class="summary">
    <p><b>Date:</b> {datetime.now()}</p>
    <p><b>Total:</b> {total}</p>
    <p class="pass">Passed: {passed}</p>
    <p class="fail">Failed: {failed}</p>
</div>

<table>
<tr>
    <th>Test Case</th>
    <th>Status</th>
    <th>Duration</th>
</tr>

{test_rows}

</table>

</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print("HTML report generated successfully!")