import re
import glob

# Automatically read all txt files from folder
# INPUT_FILES = glob.glob("reports/*.txt")
INPUT_FILES = [
    r"C:\Reports\export1.csv",
    r"C:\Reports\export2.csv",
    r"C:\Reports\export3.csv",
    r"C:\Reports\export4.csv",
    r"C:\Reports\export5.csv",
    r"C:\Reports\export6.csv",
    r"C:\Reports\export7.csv"
]
INPUT_FOLDER = r"C:\Reports"
OUTPUT_FOLDER = r"C:\AutomationReports"
testcases = []   # MUST be outside loop

for file in INPUT_FILES:
    current_tc = None

    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            # -------------------------
            # Detect Testcase
            # -------------------------
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

            # -------------------------
            # Detect Steps
            # -------------------------
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

print("Total Testcases:", len(testcases))

html = """
<html>
<head>
<style>
body { font-family: Arial; }
h2 { margin-top: 30px; }

table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 20px;
}

th, td {
    border: 1px solid #ccc;
    padding: 6px;
    text-align: left;
}

th {
    background-color: #f2f2f2;
}
</style>
</head>
<body>

<h1>Tosca Automation Report</h1>
"""

# Loop all testcases
for tc in testcases:

    html += f"<h2>{tc['name']}</h2>"

    html += """
    <table>
    <tr>
        <th>Step</th>
        <th>Execution Time</th>
        <th>Duration</th>
    </tr>
    """

    for step in tc["steps"]:
        html += f"""
        <tr>
            <td>{step['step']}</td>
            <td>{step['exec_time']}</td>
            <td>{step['duration']}</td>
        </tr>
        """

    html += "</table>"

html += "</body></html>"

with open("Combined_Report.html", "w", encoding="utf-8") as f:
    f.write(html)

print("HTML Report Generated Successfully")