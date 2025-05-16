import os
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

if len(sys.argv) < 2:
    print("Usage: python parse_trx.py <path-to-trx-file>")
    sys.exit(1)

trx_file = sys.argv[1]

if not os.path.isfile(trx_file):
    print(f"❌ Error: File not found: {trx_file}")
    sys.exit(1)

NS = {'t': 'http://microsoft.com/schemas/VisualStudio/TeamTest/2010'}

# --- First Pass: Collect TestId to Suite mapping ---
testId_to_suite = {}

for event, elem in ET.iterparse(trx_file, events=("end",)):
    if elem.tag == f'{{{NS}}}UnitTest':
        test_id = elem.attrib.get('id')
        tm = elem.find(f'{{{NS}}}TestMethod')
        class_name = tm.attrib.get('className') if tm is not None else "Unknown"
        testId_to_suite[test_id] = class_name
        elem.clear()  # free memory

# --- Second Pass: Aggregate results and write detailed output ---
suites = defaultdict(lambda: {'Passed': 0, 'Failed': 0, 'Skipped': 0, 'Duration': 0.0})

SUMMARY_FILE = os.environ.get("GITHUB_STEP_SUMMARY", "summary.md")
with open(SUMMARY_FILE, "a") as f:
    f.write("## 🧪 TRX Test Summary\n\n")
    f.write("| Test Suite | Passed | Failed | Skipped | Duration (s) |\n")
    f.write("|------------|--------|--------|---------|---------------|\n")

    detailed_lines = []
    # Parse again for results (since iterparse is single-pass)
    for event, elem in ET.iterparse(trx_file, events=("end",)):
        if elem.tag == f'{{{NS}}}UnitTestResult':
            test_name = elem.attrib.get('testName')
            outcome = elem.attrib.get('outcome')
            test_id = elem.attrib.get('testId')
            suite = testId_to_suite.get(test_id, "Unknown")
            duration = elem.attrib.get('duration')
            suites[suite][outcome] += 1
            suites[suite]['Duration'] += duration
            detailed_lines.append(f"| {suite} | {test_name} | {outcome} | {duration:.2f} |\n")
            elem.clear()  # free memory

    for suite, data in suites.items():
        f.write(f"| {suite} | {data['Passed']} | {data['Failed']} | {data['Skipped']} | {data['Duration']:.2f} |\n")

    f.write("\n---\n### Detailed Results:\n\n")
    f.write("| Suite | Test Name | Outcome | Duration (s) |\n")
    f.write("|-------|-----------|---------|--------------|\n")
    for line in detailed_lines:
        f.write(line)

