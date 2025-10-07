import pandas as pd

# Create realistic NO-GO test data with critical issues
test_data = {
    'test_id': [
        'TEST_0001', 'TEST_0002', 'TEST_0003', 'TEST_0004', 'TEST_0005',
        'TEST_0006', 'TEST_0007', 'TEST_0008', 'TEST_0009', 'TEST_0010',
        'TEST_0011', 'TEST_0012', 'TEST_0013', 'TEST_0014', 'TEST_0015'
    ],
    'test_name': [
        'Payment Gateway Integration',
        'User Authentication Security',
        'Database Transaction Rollback',
        'API Rate Limiting',
        'Data Encryption Validation',
        'Session Management',
        'File Upload Security',
        'SQL Injection Prevention',
        'Cross-Site Scripting Protection',
        'Performance Under Load',
        'Data Backup Verification',
        'Password Policy Enforcement',
        'Two-Factor Authentication',
        'Audit Log Generation',
        'System Recovery Testing'
    ],
    'status': [
        'fail', 'fail', 'fail', 'pass', 'fail',
        'blocked', 'fail', 'fail', 'pass', 'fail',
        'blocked', 'fail', 'pass', 'fail', 'blocked'
    ],
    'priority': [
        'critical', 'critical', 'high', 'medium', 'critical',
        'critical', 'high', 'critical', 'medium', 'high',
        'critical', 'high', 'medium', 'critical', 'critical'
    ],
    'execution_time': [
        120, 90, 150, 45, 180,
        0, 75, 110, 60, 200,
        0, 95, 55, 130, 0
    ],
    'environment': [
        'production', 'production', 'staging', 'staging', 'production',
        'production', 'staging', 'production', 'staging', 'production',
        'production', 'staging', 'staging', 'production', 'production'
    ],
    'assignee': [
        'Security Team', 'Security Team', 'Database Team', 'API Team', 'Security Team',
        'DevOps Team', 'Security Team', 'Security Team', 'Frontend Team', 'Performance Team',
        'DevOps Team', 'Security Team', 'Security Team', 'Audit Team', 'Infrastructure Team'
    ],
    'comments': [
        'Payment processing fails with timeout errors',
        'Authentication bypass vulnerability discovered',
        'Transaction rollback mechanism not working',
        'Rate limiting correctly implemented',
        'Encryption algorithm shows weakness',
        'Environment unavailable for testing',
        'File upload allows malicious content',
        'SQL injection vulnerability found',
        'XSS protection working correctly',
        'System crashes under 1000 concurrent users',
        'Backup system completely down',
        'Password policy not enforced for admin users',
        '2FA working as expected',
        'Critical security events not logged',
        'Recovery process fails completely'
    ],
    'defect_severity': [
        'Critical', 'Critical', 'Medium', '', 'Medium',
        'Blocked', 'Medium', 'Minor', '', '',
        '', '', '', '', ''
    ],
    'defect_type': [
        'Functional', 'Security', 'Functional', '', 'UI',
        'Infrastructure', 'Performance', 'Cosmetic', '', '',
        '', '', '', '', ''
    ],
    'impact': [
        'High', 'High', 'Medium', '', 'Low',
        'High', 'Medium', 'Low', '', '',
        '', '', '', '', ''
    ],
    'likelihood': [
        'Very Likely', 'Very Likely', 'Likely', '', 'Very Likely',
        'Very Likely', 'Likely', 'Very Likely', '', 'Very Likely',
        'Very Likely', 'Possible', '', 'Very Likely', 'Very Likely'
    ],
    'detection_phase': [
        'Production', 'Security Testing', 'System Testing', '', 'Security Testing',
        'Production', 'Security Testing', 'Security Testing', '', 'Performance Testing',
        'Production', 'System Testing', '', 'Production', 'Production'
    ],
    'root_cause': [
        'Third Party', 'Design Flaw', 'Code Logic Error', '', 'Design Flaw',
        'Environment', 'Configuration Issue', 'Code Logic Error', '', 'Code Logic Error',
        'Environment', 'Requirements Gap', '', 'Configuration Issue', 'Environment'
    ],
    'defect_status': [
        'Open', 'Open', 'Open', '', 'In Progress',
        'Blocked', 'Open', 'Open', '', '',
        '', '', '', '', ''
    ],
    'defect_id': [
        'CRIT_001', 'CRIT_002', 'MED_001', '', 'MED_002',
        'BLOCK_001', 'MED_003', 'MIN_001', '', '',
        '', '', '', '', ''
    ],
    'business_impact': [
        'Revenue loss - customers cannot complete purchases',
        'Security breach risk - unauthorized access possible',
        'Feature limitation - reduced functionality',
        '',
        'User experience issue - interface problems',
        'Testing blocked - cannot verify critical functionality',
        'Slow response time - performance degradation',
        'Visual inconsistency - minor display issue',
        '',
        '',
        '',
        '',
        '',
        '',
        ''
    ]
}

# Create DataFrame
df = pd.DataFrame(test_data)

# Save to Excel
df.to_excel('no_go_release_blocked.xlsx', index=False)

print("❌ Created NO-GO Release (BLOCKED) test data:")
print(f"📊 Total Tests: {len(df)}")
print(f"📈 Test Results:")
print(df['status'].value_counts())

# Check defects
defect_data = df[df['defect_severity'].notna() & (df['defect_severity'] != '')]
if len(defect_data) > 0:
    print(f"\n🐛 Defects Found: {len(defect_data)}")
    print(f"Severity: {defect_data['defect_severity'].value_counts().to_dict()}")
    print(f"Status: {defect_data['defect_status'].value_counts().to_dict()}")

# Calculate release readiness
total_tests = len(df)
passed_tests = len(df[df['status'] == 'pass'])
failed_tests = len(df[df['status'] == 'fail'])
blocked_tests = len(df[df['status'] == 'blocked'])
pass_rate = (passed_tests / total_tests) * 100

print(f"\n🚦 Release Readiness Assessment:")
print(f"Pass Rate: {pass_rate:.1f}% ({passed_tests}/{total_tests})")
print(f"Failed Tests: {failed_tests}")
print(f"Blocked Tests: {blocked_tests}")

# Count open critical/high severity defects
open_critical = len(defect_data[
    (defect_data['defect_severity'].isin(['Critical', 'Blocked'])) & 
    (defect_data['defect_status'].isin(['Open', 'In Progress']))
])
print(f"Open Critical/Blocked Defects: {open_critical}")

print("🔴 RECOMMENDATION: NO-GO - Release BLOCKED due to:")
print("   • Multiple critical security vulnerabilities")
print("   • System stability issues")
print("   • Infrastructure failures")
print("   • High failure rate in critical functionality")