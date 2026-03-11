import json
import os
import re
import glob
from datetime import datetime

# ----------------------------
# CONFIGURATION
# ----------------------------
INPUT_FOLDER = r"C:\Reports\11March"
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
# FIND JSON FILES
# ----------------------------
INPUT_FILES = glob.glob(os.path.join(INPUT_FOLDER, "*.json"))
if not INPUT_FILES:
    print("No JSON files found in folder:", INPUT_FOLDER)
    exit()

print(f"Found {len(INPUT_FILES)} JSON files")

# ----------------------------
# PARSE JSON AND MERGE TEST CASES
# ----------------------------
testcases = []
total_steps = 0
total_steps_passed = 0
total_steps_failed = 0
total_tc_passed = 0
total_tc_failed = 0

def sum_durations(steps):
    total_ms = 0
    for step in steps:
        duration = step.get("duration", "").strip()
        if duration:
            try:
                mins_secs, ms = duration.split(".")
                mins, secs = mins_secs.split(":")
                total_ms += (int(mins) * 60 + int(secs)) * 1000 + int(ms)
            except:
                pass
    minutes = total_ms // 60000
    seconds = (total_ms % 60000) // 1000
    milliseconds = total_ms % 1000
    return f"{minutes:02}:{seconds:02}.{milliseconds:03}", total_ms/1000  # return duration in sec too

for file in INPUT_FILES:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        pages = data.get("Document", {}).get("Pages", [])
        for page in pages:
            tables = page.get("Tables", [])
            for table in tables:
                if table.get("ID") != "TreeStructure":
                    continue
                body_lines = table.get("BodyLines", [])
                tc_name = body_lines[0].get("unnamed_0", "Unknown TestCase")
                steps = []
                tc_buffers = {}
                for line in body_lines[1:]:
                    step_name = line.get("Name", "").strip()
                    if step_name == "":
                        continue
                    combined_text = (line.get("ActionMode", "") + " " + line.get("Loginfo", "")).strip()
                    if "Buffer with name" in combined_text:
                        match = re.search(
                            r'Buffer with name:\s*"([^"]+)"\s*has been set to value:\s*"([^"]+)"',
                            combined_text
                        )
                        if match:
                            buffer_name = match.group(1)
                            buffer_value = match.group(2)
                            tc_buffers[buffer_name] = buffer_value
                    if step_name not in step_details_map:
                        continue
                    details = line.get("Detail", "").strip()
                    exec_time = line.get("StartTime", "").strip()
                    duration = line.get("Duration", "").strip()
                    status = "Failed" if any(k in combined_text.lower() for k in fail_keywords) else "Passed"
                    custom_desc = step_details_map.get(step_name, "")
                    details = f"{details} ({custom_desc})" if details else custom_desc
                    steps.append({
                        "step": step_name,
                        "details": details,
                        "exec_time": exec_time,
                        "duration": duration,
                        "status": status,
                        "source": os.path.basename(file)
                    })
                if steps:
                    total_steps += len(steps)
                    tc_total_duration_str, tc_total_duration_sec = sum_durations(steps)
                    total_steps_passed += sum(1 for s in steps if s["status"] == "Passed")
                    total_steps_failed += sum(1 for s in steps if s["status"] == "Failed")
                    tc_status = "Failed" if any(s["status"]=="Failed" for s in steps) else "Passed"
                    if tc_status == "Failed":
                        total_tc_failed += 1
                    else:
                        total_tc_passed += 1
                    testcases.append({
                        "name": tc_name,
                        "steps": steps,
                        "status": tc_status,
                        "source": os.path.basename(file),
                        "buffers": tc_buffers,
                        "total_duration": tc_total_duration_str,
                        "total_duration_sec": tc_total_duration_sec
                    })

# ----------------------------
# BUILD HTML REPORT
# ----------------------------
project_name = "Internet Banking - API"
environment_name = "UAT"
executed_user = "Nitesh Badge"
module_name = "Transfer"
testing_type = "Smoke Suite"

html_content = f"""
<html>
<head>
<title>Tosca Execution Report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
.card {{ max-width: 900px; margin: 10px auto; border: 1px solid #ddd; border-radius: 12px; background-color: #fff; padding: 15px 20px; }}
.summary-box {{ display: flex; justify-content: center; flex-wrap: wrap; gap: 25px; margin-top: 20px; }}
.summary-item {{ text-align: center; padding: 10px 20px; border-radius: 8px; min-width: 120px; }}
.total {{ background-color: #e6f0ff; color: #007bff; font-weight: bold; }}
.passed {{ background-color: #e6ffe6; color: green; font-weight: bold; }}
.failed {{ background-color: #ffe6e6; color: red; font-weight: bold; }}
.tc-container {{ width: 95%; margin: 0 auto 20px auto; }}
.collapsible {{ background-color: #007bff; color: white; cursor: pointer; padding: 10px 12px; width: 100%; border: none; text-align: left; font-size: 14px; border-radius: 6px; }}
.collapsible:hover {{ background-color: #0056b3; }}
.content {{ display: none; overflow: hidden; margin-top: 5px; }}
.chart-container-flex {{ display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin: 20px auto; }}
.chart-box {{ width: 350px; background: #fff; border-radius: 8px; padding: 10px; box-shadow: 0px 0px 8px rgba(0,0,0,0.1); }}
</style>
</head>
<body>

<h1>QA API Automation Execution Report</h1>

<div class="card">
<div style="text-align: center; margin-bottom: 20px;">
 <h2 style="margin-top: 5px; margin-bottom: 10px;">{project_name} Execution Summary</h2>
 <p><b>Module Name:</b> {module_name} &nbsp;|&nbsp; 
    <b>Environment:</b> {environment_name} &nbsp;|&nbsp;    
    <b>Test Execution:</b> {testing_type} &nbsp;|&nbsp; 
    <b>Executed By:</b> {executed_user}</p>
</div>

<div class="summary-box">
<div class="summary-item total">Total API TestCases<br>{len(testcases)}</div>
<div class="summary-item passed">Passed TestCases<br>{total_tc_passed}</div>
<div class="summary-item failed">Failed TestCases<br>{total_tc_failed}</div>
</div>
</div>

<!-- Charts -->
<div class="chart-container-flex">
  <div class="chart-box">
    <h4 style="text-align:center;">TestCase Status</h4>
    <canvas id="tcChart" width="200" height="200"></canvas>
  </div>
  <div class="chart-box">
    <h4 style="text-align:center;">TestCase Duration (sec)</h4>
    <canvas id="tcDurationChart" width="200" height="200"></canvas>
  </div>
</div>
"""

# ----------------------------
# TESTCASE SUMMARY TABLE
# ----------------------------
html_content += """
<h2 style="text-align:center;">Test Case Summary</h2>
<table>
<tr>
<th>#</th>
<th>Test Case Name</th>
<th>Status</th>
<th>Session ID</th>
<th>Duration</th>
</tr>
"""
for i, tc in enumerate(testcases, start=1):
    session_value = " | ".join(tc["buffers"].values()) if tc.get("buffers") else ""
    status_class = "pass" if tc["status"] == "Passed" else "fail"
    html_content += f"""
    <tr>
        <td>{i}</td>
        <td><a href="javascript:void(0);" onclick="openTestCase({i})" style="text-decoration:none;color:#007bff;"><b>{tc['name']}</b></a></td>
        <td class="{status_class}">{tc['status']}</td>
        <td>{session_value}</td>
        <td>{tc['total_duration']}</td>
    </tr>
    """
html_content += "</table>"
# Add a heading before detailed collapsible sections
html_content += """
<h2 style="text-align:center; margin-top:30px;">Test Case Details</h2>
"""

# ----------------------------
# TEST CASE DETAILS (COLLAPSIBLE)
# ----------------------------
for i, tc in enumerate(testcases, start=1):
    buffer_html = " | ".join(tc["buffers"].values()) if tc.get("buffers") else ""
    tc_class = "fail" if tc["status"]=="Failed" else "pass"
    html_content += f"""
    <div id="tc{i}">
    <button id="btn{i}" class="collapsible">
    {tc['name']}  
    </button>
    <div class="content">
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
    html_content += "</table></div></div>"

# ----------------------------
# JAVASCRIPT FOR COLLAPSIBLE + CHARTS
# ----------------------------
def shorten_name(name, max_len=20):
    # keep only text after last dash
    short = name.split("-")[-1].strip()
    if len(short) > max_len:
        short = short[:17] + "…"
    return short

tc_names_js = ",".join([f'"{shorten_name(tc["name"])}"' for tc in testcases])

tc_durations_js = ",".join([str(tc["total_duration_sec"]) for tc in testcases])

html_content += f"""
<script>
var coll = document.getElementsByClassName("collapsible");
for (var i = 0; i < coll.length; i++) {{
  coll[i].addEventListener("click", function() {{
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {{
        content.style.display = "none";
    }} else {{
        content.style.display = "block";
    }}
  }});
}}

function openTestCase(i) {{
  var btn = document.getElementById("btn" + i);
  var content = btn.nextElementSibling;
  content.scrollIntoView({{behavior: "smooth", block: "start"}});
  if (content.style.display !== "block") {{
      btn.click();
  }}
}}

// TestCase Status Pie Chart
var ctx1 = document.getElementById('tcChart').getContext('2d');
var tcChart = new Chart(ctx1, {{
    type: 'pie',
    data: {{
        labels: ['Passed','Failed'],
        datasets: [{{
            label: 'TestCase Status',
            data: [{total_tc_passed},{total_tc_failed}],
            backgroundColor: ['#4caf50','#f44336']
        }}]
    }}
}});

// TestCase Duration Bar Chart
var ctx2 = document.getElementById('tcDurationChart').getContext('2d');
var tcDurationChart = new Chart(ctx2, {{
    type: 'bar',
    data: {{
        labels: [{tc_names_js}],
        datasets: [{{
            label: 'Duration (sec)',
            data: [{tc_durations_js}],
            backgroundColor: '#2196f3'
        }}]
    }},
    options: {{
        indexAxis: 'y',
        plugins: {{
            legend: {{ display: false }}
        }},
        scales: {{
            x: {{ beginAtZero: true }},
            y: {{ ticks: {{ autoSkip: false, maxRotation: 0, minRotation: 0 }} }}
        }}
    }}
}});
</script>
</body>
</html>
"""

# ----------------------------
# SAVE HTML REPORT
# ----------------------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print("\nMerged JSON HTML report with charts, sessions & buffers generated successfully!")
print("Saved at:", OUTPUT_FILE)