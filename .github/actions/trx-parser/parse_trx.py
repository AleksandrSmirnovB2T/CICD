#!/usr/bin/env python3
import sys
import os
import xml.etree.ElementTree as ET

if len(sys.argv) < 2:
    print("Usage: parse_trx.py <path-to-trx-file>")
    sys.exit(1)

trx_file = sys.argv[1]

NS = {'t': 'http://microsoft.com/schemas/VisualStudio/TeamTest/2010'}
tree = ET.parse(trx_file)
root = tree.getroot()

results = root.find('t:Results', NS)
if results is None:
    print("No <Results> found in TRX file.")
    sys.exit(1)

unit_tests = results.findall('t:UnitTestResult', NS)
total = len(unit_tests)
passed = sum(1 for u in unit_tests if u.attrib.get('outcome') == 'Passed')
failed = sum(1 for u in unit_tests if u.attrib.get('outcome') == 'Failed')
skipped = sum(1 for u in unit_tests if u.attrib.get('outcome') == 'NotExecuted')

print(f"Total tests:   {total}")
print(f"✅ Passed:     {passed}")
print(f"❌ Failed:     {failed}")
print(f"⚠️  Skipped:    {skipped}\n")

failed_tests = [
    u.attrib.get('testName') for u in unit_tests
    if u.attrib.get('outcome') == 'Failed'
]

# Output to GitHub step summary
summary = os.environ.get("GITHUB_STEP_SUMMARY")
if summary:
    with open(summary, "a") as f:
        f.write("### 🧪 Test Summary\n")
        f.write(f"- Total: **{total}**\n")
        f.write(f"- ✅ Passed: {passed}\n")
        f.write(f"- ❌ Failed: {failed}\n")
        f.write(f"- ⚠️ Skipped: {skipped}\n\n")
        if failed_tests:
            f.write("#### ❌ Failed Tests\n")
            for name in failed_tests:
                f.write(f"- {name}\n")
