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

try:
    tree = ET.parse(trx_file)
except ET.ParseError as e:
    print(f"❌ Failed to parse XML: {e}")
    sys.exit(1)

root = tree.getroot()

results = root.find('t:Results', NS)
definitions = root.find('t:TestDefinitions', NS)

if results is None or definitions is None:
    print("❌ Missing Results or TestDefinitions.")
    sys.exit(1)

# Map testId to className (suite)
testId_to_suite = {}
for ut in definitions.findall('t:UnitTest', NS):
    test_id = ut.attrib.get('id')
    class_name = ut.find('t:TestMethod', NS).attrib.get('className')
    testId_to_suite[test_id] = class_name

# Collect test results
suites = defaultdict(lambda: {'Passed': 0, 'Failed': 0, 'Skipped': 0, 'Durations': []})
detailed_tests = []

for result in results.findall('t:UnitTestResult', NS):
    test_name = result.attrib.get('testName')
    outcome = result.attrib.get('outcome')
    duration = result.attrib.get('duration', 'PT0S').replace("PT", "").replace("S", "")
    test_id = result.attrib.get('testId')
    suite = testId_to_suite.get(test_id, "Unknown")

    suites[suite][outcome] += 1
    suites[suite]['Durations'].append(duration)

    detailed_tests.append({
        'Suite': suite,
        'Test': test_name,
        'Outcome': outcome,
        'Duration': duration
    })

SUMMARY_FILE = os.environ.get("GITHUB_STEP_SUMMARY", "summary.md")
with open(SUMMARY_FILE, "a") as f:
    f.write("## ✅ TRX Test Summary\n\n")
    f.write("| Test Suite | Passed | Failed | Skipped | Duration (s) |\n")
    f.write("|------------|--------|--------|---------|---------------|\n")

    for suite, data in suites.items():
        try:
            total_duration = sum(float(d) for d in data['Durations'] if d)
        except ValueError:
            total_duration = 0.0

        f.write(f"| {suite} | {data['Passed']} | {data['Failed']} | {data['Skipped']} | {total_duration:.2f} |\n")

    f.write("\n---\n")

    f.write("### Detailed Results:\n\n")
    f.write("| Suite | Test Name | Outcome | Duration (s) |\n")
    f.write("|-------|-----------|---------|--------------|\n")

    for t in detailed_tests:
        f.write(f"| {t['Suite']} | {t['Test']} | {t['Outcome']} | {t['Duration']} |\n")

