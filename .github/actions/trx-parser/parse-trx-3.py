import os
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime

def parse_trx(trx_file):
    """Parse TRX file and generate test summary with optimized memory usage"""
    
    # Validate input file
    if not os.path.isfile(trx_file):
        print(f"❌ Error: File not found: {trx_file}")
        sys.exit(1)
    
    # XML namespace for TRX files
    NS = {'t': 'http://microsoft.com/schemas/VisualStudio/TeamTest/2010'}
    
    # Use defaultdict to track test suite statistics
    suites = defaultdict(lambda: {'Passed': 0, 'Failed': 0, 'Skipped': 0, 'Duration': 0.0})
    
    # Summary file path
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY", "summary.md")
    
    # Initialize summary file
    with open(summary_file, "a") as f:
        f.write("## TRX Test Summary\n\n")
    
    # Process the XML file in a single pass
    context = ET.iterparse(trx_file, events=("end",))
    
    # Process UnitTests first to build the testId_to_suite mapping
    print("Building test ID to suite mapping...")
    testId_to_suite = {}
    for _, elem in context:
        if elem.tag.endswith('UnitTest'):
            test_id = elem.attrib.get('id')
            tm = elem.find('.//*[@className]')  # Find any element with className attribute
            class_name = tm.attrib.get('className') if tm is not None else "Unknown"
            testId_to_suite[test_id] = class_name
            elem.clear()  # Free memory
    
    # Process UnitTestResults to collect statistics
    print("Processing test results...")
    detailed_results = []
    
    for _, elem in ET.iterparse(trx_file, events=("end",)):
        if elem.tag.endswith('UnitTestResult'):
            test_name = elem.attrib.get('testName', 'Unknown')
            outcome = elem.attrib.get('outcome', 'Unknown')
            test_id = elem.attrib.get('testId', 'Unknown')
            
            # Get suite name from mapping
            suite = testId_to_suite.get(test_id, "Unknown")
            
            # Parse duration (safely)
            duration_str = elem.attrib.get('duration', '0:00:00.000')
            try:
                # Convert duration format to seconds
                time_obj = datetime.strptime(duration_str[0:15], "%H:%M:%S.%f")
    
                # Convert to total milliseconds
                hours = time_obj.hour
                minutes = time_obj.minute
                seconds = time_obj.second
                microseconds = time_obj.microsecond
                duration = (hours * 3600 + minutes * 60 + seconds) * 1000 + microseconds / 1000
            except (ValueError, IndexError):
                duration = 0.0
            
            # Update suite statistics
            suites[suite][outcome] += 1
            suites[suite]['Duration'] += duration
            
            # Store detailed result (memory-efficient: just store what we need)
            detailed_results.append((suite, test_name, outcome, duration))
            
            # Clear element to free memory
            elem.clear()
    
    # Write summary and detailed results to file
    write_results(summary_file, suites, detailed_results)
    
    print(f"✅ Summary written to {summary_file}")

def write_results(summary_file, suites, detailed_results):
    """Write test results to summary file"""
    with open(summary_file, "a") as f:
        # Suite summary table
        f.write("| Test Suite | Passed | Failed | Skipped | Duration (s) |\n")
        f.write("|------------|--------|--------|---------|---------------|\n")
        
        for suite, data in suites.items():
            f.write(f"| {suite} | {data['Passed']} | {data['Failed']} | {data['Skipped']} | {data['Duration']:.2f} |\n")
        
        # Detailed results table
        f.write("\n---\n### Detailed Results:\n\n")
        f.write("| Suite | Test Name | Outcome | Duration (s) |\n")
        f.write("|-------|-----------|---------|--------------|\n")
        
        for suite, test_name, outcome, duration in detailed_results:
            f.write(f"| {suite} | {test_name} | {outcome} | {duration:.2f} |\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_trx.py <path-to-trx-file>")
        sys.exit(1)
    
    parse_trx(sys.argv[1])