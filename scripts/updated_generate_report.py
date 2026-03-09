import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

RESULT_XML = r"C:\ToscaReports\result.xml"
HISTORY_FILE = "history/trend.json"

# -----------------------
# Parse Tosca XML
# -----------------------
tree = ET.parse(RESULT_XML)
root = tree.getroot()

tests = []

for tc in root.findall(".//TestCase"):
    tests.append({
        "name": tc.get("name"),
        "result": tc.get("result"),
        "duration": tc.get("duration")
    })

passed = len([t for t in tests if t["result"] == "Passed"])
failed = len([t for t in tests if t["result"] == "Failed"])
total = len(tests)

# -----------------------
# Trend History
# -----------------------
history = []

if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE) as f:
        history = json.load(f)

history.append({
    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "passed": passed,
    "failed": failed
})

with open(HISTORY_FILE, "w") as f:
    json.dump(history, f, indent=2)

# -----------------------
# Generate HTML
# -----------------------
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("report_template.html")

html = template.render(
    tests=tests,
    passed=passed,
    failed=failed,
    total=total,
    history=history,
    date=datetime.now()
)

with open("Tosca_Report.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Advanced report generated")