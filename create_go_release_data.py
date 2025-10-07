import pandas as pd

# Create realistic test data for GO release candidate
test_data = {
    'test_id': [
        'TEST_0001', 'TEST_0002', 'TEST_0003', 'TEST_0004', 'TEST_0005',
        'TEST_0006', 'TEST_0007', 'TEST_0008', 'TEST_0009', 'TEST_0010',
        'TEST_0011', 'TEST_0012', 'TEST_0013', 'TEST_0014', 'TEST_0015'
    ],
    'test_name': [
        'Commercial Vehicles - >36 =< 41 (4)',
        'Commercial Vehicles - >44 =< 75 (2)',
        'Private Cars - PC7 (10)',
        'Commercial Vehicles - LCV1 (1), Private Cars - PC4 (5)',
        'Private Cars - PC4 (9), Commercial Vehicles - LCV3 (8)',
        'Private Cars - PC1 (1), Motorcycles - >1200cc (3)',
        'Private Cars - PC2 (3)',
        'Commercial Vehicles - >12 =< 17 (2)',
        'Private Cars - PC1 (5)',
        'Private Cars - PC7 (2)(no claim scenario)',
        'Taxi Cars - TC1 Premium Calculation',
        'Motorcycles - 951-1200cc Engine Test',
        'Private Cars - PC5 Discount Validation',
        'Commercial Vehicles - Weight Category Test',
        'Multi-Vehicle Policy Integration Test'
    ],
    'status': [
        'pass', 'pass', 'pass', 'pass', 'pass',
        'pass', 'pass', 'pass', 'pass', 'pass',
        'pass', 'fail', 'pass', 'fail', 'pass'
    ],
    'priority': [
        'high', 'critical', 'medium', 'low', 'high',
        'medium', 'low', 'high', 'medium', 'low',
        'critical', 'medium', 'high', 'medium', 'low'
    ],
    'execution_time': [
        45, 120, 30, 15, 60,
        45, 120, 30, 15, 60,
        90, 75, 35, 50, 25
    ],
    'environment': [
        'uat', 'uat', 'uat', 'uat', 'uat',
        'uat', 'uat', 'uat', 'uat', 'uat',
        'uat', 'uat', 'uat', 'uat', 'uat'
    ],
    'assignee': [
        'John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown', 'Mike Davis',
        'John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown', 'Mike Davis',
        'Sarah Lee', 'Tom Chen', 'Lisa Wang', 'David Kim', 'Amy Liu'
    ],
    'comments': [
        'All assertions passed - premium calculated correctly',
        'Transaction completed successfully - all validations pass',
        'Validation successful - email field accepts valid formats',
        'Response time within limits - performance acceptable',
        'Database connection stable - data integrity maintained',
        'All assertions passed - multi-vehicle discount applied',
        'All assertions passed - basic coverage calculated',
        'All assertions passed - weight category determined correctly',
        'All assertions passed - no claim bonus applied',
        'All assertions passed - base premium calculated',
        'All assertions passed - taxi premium surcharge applied',
        'Engine capacity validation failed - incorrect category assignment',
        'All assertions passed - discount percentage calculated',
        'Weight validation failed - category boundary issue',
        'All assertions passed - policy integration successful'
    ],
    'defect_severity': [
        '', '', '', '', '',
        '', '', '', '', '',
        '', 'Minor', '', 'Minor', ''
    ],
    'defect_type': [
        '', '', '', '', '',
        '', '', '', '', '',
        '', 'Functional', '', 'Data', ''
    ],
    'impact': [
        '', '', '', '', '',
        '', '', '', '', '',
        '', 'Low', '', 'Low', ''
    ],
    'likelihood': [
        '', '', '', '', '',
        '', '', '', '', '',
        '', 'Unlikely', '', 'Possible', ''
    ],
    'detection_phase': [
        '', '', '', '', '',
        '', '', '', '', '',
        '', 'System Testing', '', 'UAT', ''
    ],
    'root_cause': [
        '', '', '', '', '',
        '', '', '', '', '',
        '', 'Code Logic Error', '', 'Configuration Issue', ''
    ],
    'defect_status': [
        '', '', '', '', '',
        '', '', '', '', '',
        '', 'Resolved', '', 'Closed', ''
    ],
    'defect_id': [
        '', '', '', '', '',
        '', '', '', '', '',
        '', 'DEF_001', '', 'DEF_002', ''
    ],
    'business_impact': [
        '', '', '', '', '',
        '', '', '', '', '',
        '', 'Minor impact on engine category display - does not affect premium calculation',
        '', 'Minor impact on weight display - premium calculation remains correct', ''
    ]
}

# Create DataFrame
df = pd.DataFrame(test_data)

# Save to Excel
df.to_excel('go_release_candidate_tests.xlsx', index=False)

print("✅ Created GO Release Candidate test data:")
print(f"📊 Total Tests: {len(df)}")
print(f"📈 Test Results:")
print(df['status'].value_counts())

# Check defects
defect_data = df[df['defect_severity'].notna() & (df['defect_severity'] != '')]
if len(defect_data) > 0:
    print(f"\n🐛 Defects Found: {len(defect_data)}")
    print(f"Severity: {defect_data['defect_severity'].value_counts().to_dict()}")
    print(f"Status: {defect_data['defect_status'].value_counts().to_dict()}")
else:
    print(f"\n✅ No open defects - Ready for GO release!")

# Calculate release readiness
total_tests = len(df)
passed_tests = len(df[df['status'] == 'pass'])
failed_tests = len(df[df['status'] == 'fail'])
pass_rate = (passed_tests / total_tests) * 100

print(f"\n🚦 Release Readiness Assessment:")
print(f"Pass Rate: {pass_rate:.1f}% ({passed_tests}/{total_tests})")
print(f"Failed Tests: {failed_tests}")
print(f"Open Defects: {len(defect_data[defect_data['defect_status'].isin(['Open', 'In Progress']) if len(defect_data) > 0 else []])}")

if pass_rate >= 90 and failed_tests <= 2:
    print("🟢 RECOMMENDATION: GO - Release candidate approved")
else:
    print("🟡 RECOMMENDATION: CONDITIONAL - Review required")