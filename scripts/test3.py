import csv
import os
import re
import html
from datetime import datetime

# ------------------------
# Configuration
# ------------------------

INPUT_FILES = [
    # r"C:\Reports\export1.csv",
    # r"C:\Reports\export2.csv",
    # r"C:\Reports\export8.csv",
    r"C:\Reports\export81.csv"
]

OUTPUT_FOLDER = r"C:\AutomationReports"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    f"Tosca_Merged_Report_{timestamp}.html"
)

# ------------------------
# Custom Step Descriptions
# ------------------------

step_details_map = {
    "01_POST_LoginAuth": "Authenticate user via API",
    "02_GET_Encrypt_UserName": "Encrypt username",
    "03_GET_Encrypt_Password": "Encrypt password",
    "04_POST_Login": "Perform login",
    "05_GET AccountIndex": "Get Account index",
    "06_POST Account Validate": "Validate account",
    "07_POST Prepare Amount Transfer": "Prepare amount transfer",
    "08_Get Otp": "Get OTP",
    "09_POST Transfer Amount": "Perform transfer"
}

# ------------------------
# Parse CSV Files
# ------------------------

def parse_csv_files(files):
    testcases = []
    total_steps = 0
    total_failed_steps = 0

    for file_path in files:
        if not os.path.exists(file_path):
            print(f"⚠ File not found: {file_path}")
            continue

        print(f"Processing: {file_path}")
        current_tc = None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)

                for row in reader:
                    if not row or len(row) < 2:
                        continue

                    step_code = row[1].strip()

                    # Detect TestCase
                    if step_code.startswith("<") and step_code.endswith(">"):
                        tc_name = step_code.strip("<>").strip()
                        current_tc = {"name": tc_name, "steps": []}
                        testcases.append(current_tc)
                        continue

                    # Ignore non-step rows
                    if not re.match(r'^\d+', step_code):
                        continue

                    details = row[4].strip() if len(row) > 4 else ""
                    exec_time = row[6].strip() if len(row) > 6 else ""
                    duration = row[7].strip() if len(row) > 7 else ""

                    status = "Failed" if "error" in details.lower() else "Passed"

                    if status == "Failed":
                        total_failed_steps += 1

                    total_steps += 1

                    # Add custom mapping
                    custom_detail = step_details_map.get(step_code, "")
                    if custom_detail:
                        details = (
                            details + f" ({custom_detail})"
                            if details else custom_detail
                        )

                    if current_tc:
                        current_tc["steps"].append({
                            "step": html.escape(step_code),
                            "details": html.escape(details),
                            "exec_time": html.escape(exec_time),
                            "duration": html.escape(duration),
                            "status": status
                        })

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    return testcases, total_steps, total_failed_steps


# ------------------------
# Generate HTML
# ------------------------

def generate_html(testcases, total_steps, total_failed_steps):

    total_tc = len(testcases)
    failed_tc = sum(
        1 for tc in testcases
        if any(s["status"] == "Failed" for s in tc["steps"])
    )
    passed_tc = total_tc - failed_tc

    html_content = f"""
    <html>
    <head>
    <title>Tosca Execution Report</title>
    <style>
    body {{ font-family: Arial; background:#f4f6f9; font-size:12px; }}
    h1 {{ text-align:center; font-size:18px; }}
    h2 {{ font-size:14px; margin-top:20px; }}
    .pass {{ color:green; font-weight:bold; }}
    .fail {{ color:red; font-weight:bold; }}
    table {{ width:95%; margin:auto; border-collapse:collapse; }}
    th, td {{ border:1px solid #ccc; padding:6px; }}
    th {{ background:#007bff; color:white; }}
    .summary {{ text-align:center; margin:15px; }}
    </style>
    </head>
    <body>

    <h1>Transfer API Tosca Execution Report</h1>

    <div class="summary">
        <p><b>Date:</b> {datetime.now()}</p>
        <p><b>Total TestCases:</b> {total_tc}</p>
        <p><b>Passed TestCases:</b> <span class="pass">{passed_tc}</span></p>
        <p><b>Failed TestCases:</b> <span class="fail">{failed_tc}</span></p>
        <p><b>Total Steps:</b> {total_steps}</p>
        <p><b>Failed Steps:</b> <span class="fail">{total_failed_steps}</span></p>
    </div>
    """

    for tc in testcases:
        tc_status = "Failed" if any(
            s["status"] == "Failed" for s in tc["steps"]
        ) else "Passed"

        tc_class = "fail" if tc_status == "Failed" else "pass"

        html_content += f"""
        <h2>{tc['name']} - 
        <span class="{tc_class}">{tc_status}</span></h2>

        <table>
        <tr>
            <th>Step Code</th>
            <th>Details</th>
            <th>Execution Time</th>
            <th>Duration</th>
            <th>Status</th>
        </tr>
        """

        for s in tc["steps"]:
            status_class = "pass" if s["status"] == "Passed" else "fail"

            html_content += f"""
            <tr>
                <td>{s['step']}</td>
                <td>{s['details']}</td>
                <td>{s['exec_time']}</td>
                <td>{s['duration']}</td>
                <td class="{status_class}">{s['status']}</td>
            </tr>
            """

        html_content += "</table>"

    html_content += "</body></html>"

    return html_content


# ------------------------
# Main Execution
# ------------------------

if __name__ == "__main__":

    testcases, total_steps, total_failed_steps = parse_csv_files(INPUT_FILES)

    html_report = generate_html(
        testcases,
        total_steps,
        total_failed_steps
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_report)

    print("\n✅ Merged HTML report generated successfully!")
    print("📂 Saved at:", OUTPUT_FILE)