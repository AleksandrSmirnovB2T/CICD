import os
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

if len(sys.argv) < 3:
    print("Usage: python parse_trx.py <path-to-trx-file> <output-html-file>")
    sys.exit(1)

trx_file = sys.argv[1]
output_html = sys.argv[2]

if not os.path.isfile(trx_file):
    print(f"❌ Error: File not found: {trx_file}")
    sys.exit(1)

NS = {'t': 'http://microsoft.com/schemas/VisualStudio/TeamTest/2010'}

tree = ET.parse(trx_file)
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
suites = defaultdict(lambda: {'Passed': [], 'Failed': [], 'Skipped': [], 'Durations': []})
detailed_tests = []

for result in results.findall('t:UnitTestResult', NS):
    test_name = result.attrib.get('testName')
    outcome = result.attrib.get('outcome')
    duration = result.attrib.get('duration', 'PT0S').replace("PT", "").replace("S", "")
    test_id = result.attrib.get('testId')
    suite = testId_to_suite.get(test_id, "Unknown")

    suites[suite][outcome].append(test_name)
    suites[suite]['Durations'].append(duration)

    detailed_tests.append({
        'Suite': suite,
        'Test': test_name,
        'Outcome': outcome,
        'Duration': duration
    })

# Generate HTML
html = ['<html><head><meta charset="UTF-8"><style>',
        'body { font-family: Arial; padding: 20px; }',
        'table { border-collapse: collapse; width: 100%; margin-bottom: 40px; }',
        'th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }',
        'th { background-color: #f2f2f2; }',
        '.passed { color: green; } .failed { color: red; } .skipped { color: orange; }',
        '</style></head><body>']

html.append("<h1>TRX Test Summary</h1>")
html.append("<table><tr><th>Test Suite</th><th>Passed</th><th>Failed</th><th>Skipped</th><th>Total Duration (s)</th></tr>")

for suite, data in suites.items():
    try:
        total_duration = sum(float(d) for d in data['Durations'] if d)
    except ValueError:
        total_duration = 0.0

    html.append(f"<tr><td>{suite}</td><td class='passed'>{len(data['Passed'])}</td>"
                f"<td class='failed'>{len(data['Failed'])}</td>"
                f"<td class='skipped'>{len(data['Skipped'])}</td>"
                f"<td>{total_duration:.2f}</td></tr>")

html.append("</table>")

# Detailed test cases
html.append("<h2>Detailed Test Results</h2>")
html.append("<table><tr><th>Test Suite</th><th>Test Name</th><th>Outcome</th><th>Duration (s)</th></tr>")

for t in detailed_tests:
    css_class = t['Outcome'].lower()
    html.append(f"<tr><td>{t['Suite']}</td><td>{t['Test']}</td><td class='{css_class}'>{t['Outcome']}</td><td>{t['Duration']}</td></tr>")

html.append("</table></body></html>")

with open(output_html, "w", encoding="utf-8") as f:
    f.write("\n".join(html))

print(f"✅ HTML report generated at: {output_html}")
