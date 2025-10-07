import pandas as pd
import random
from datetime import datetime

# Helper functions for generating realistic defect data
def generate_defect_severity(status):
    """Generate defect severity based on test status"""
    if status == 'fail':
        # Failed tests have defects with realistic distribution
        severities = ['Critical', 'Medium', 'Minor', 'Blocked']
        weights = [0.05, 0.20, 0.60, 0.05]  # Most defects are minor
        if random.random() < 0.70:  # 70% of failed tests have associated defects
            return random.choices(severities, weights=weights)[0]
    elif status == 'blocked':
        # Blocked tests always have blocked defects
        return 'Blocked'
    return ''  # Passing tests don't have defects

def generate_defect_category():
    """Generate defect category"""
    categories = ['UI', 'Backend', 'Database', 'Integration', 'Performance', 'Security', 'Logic', 'API']
    return random.choice(categories)

def generate_defect_description_for_severity(severity):
    """Generate realistic defect descriptions based on severity"""
    descriptions = {
        'Critical': [
            'System crash during user authentication',
            'Data corruption in payment processing module',
            'Security vulnerability allowing unauthorized access',
            'Complete feature breakdown in main workflow',
            'Database connection failure causing data loss'
        ],
        'Medium': [
            'Incorrect calculation in financial reports',
            'Performance degradation in search functionality',
            'UI elements not displaying correctly on mobile',
            'Email notifications delayed by more than 1 hour',
            'API response time exceeds acceptable limits'
        ],
        'Minor': [
            'Spelling error in user interface labels',
            'Minor formatting issue in PDF reports',
            'Tooltip text displays incorrect information',
            'Color inconsistency in application theme',
            'Non-critical validation message unclear'
        ],
        'Blocked': [
            'Test environment unavailable for execution',
            'Dependent external service not responding',
            'Required test data not accessible',
            'Authentication service temporarily down',
            'Database locked by another process'
        ]
    }
    
    if severity and severity in descriptions:
        return random.choice(descriptions[severity])
    return ''

def generate_defect_priority_for_severity(severity):
    """Generate defect priority based on severity"""
    priority_mapping = {
        'Critical': 'P0',
        'Blocked': 'P0', 
        'Medium': 'P1',
        'Minor': 'P2'
    }
    
    return priority_mapping.get(severity, '')

def generate_defect_status(severity):
    """Generate defect lifecycle status"""
    if not severity:
        return ''
    
    statuses = ['Open', 'In Progress', 'Resolved', 'Closed', 'Rejected', 'Reopened']
    
    # Different status distributions based on severity
    if severity == 'Critical':
        weights = [0.10, 0.30, 0.40, 0.15, 0.03, 0.02]  # Critical defects get resolved quickly
    elif severity == 'Blocked':
        weights = [0.20, 0.40, 0.25, 0.10, 0.03, 0.02]  # Blocked defects take time
    elif severity == 'Medium':
        weights = [0.25, 0.25, 0.30, 0.15, 0.03, 0.02]  # Balanced distribution
    else:  # Minor
        weights = [0.40, 0.20, 0.20, 0.10, 0.05, 0.05]  # More minor defects remain open
    
    return random.choices(statuses, weights=weights)[0]

def generate_defect_assignee():
    """Generate defect assignee"""
    assignees = [
        'John Smith', 'Sarah Johnson', 'Mike Chen', 'Anna Garcia', 
        'David Wilson', 'Lisa Brown', 'Tom Anderson', 'Maria Lopez',
        'Alex Kim', 'Emma Davis', 'Ryan Taylor', 'Sophie Miller'
    ]
    return random.choice(assignees)

def generate_defect_resolution_reason(status):
    """Generate resolution reason based on status"""
    resolution_reasons = {
        'Resolved': [
            'Fixed in code', 'Configuration updated', 'Database corrected',
            'Third-party issue resolved', 'User error clarified'
        ],
        'Closed': [
            'Fixed and verified', 'Working as designed', 'Cannot reproduce',
            'Environment specific', 'Duplicate of another defect'
        ],
        'Rejected': [
            'Not a defect', 'Feature request', 'Out of scope',
            'Invalid test case', 'Environmental issue'
        ]
    }
    
    if status in resolution_reasons:
        return random.choice(resolution_reasons[status])
    return ''

def generate_defect_age_days(status):
    """Generate defect age in days based on status"""
    if status in ['Open', 'In Progress', 'Reopened']:
        return random.randint(1, 30)  # Active defects
    elif status in ['Resolved']:
        return random.randint(5, 45)  # Recently resolved
    elif status in ['Closed']:
        return random.randint(10, 90)  # Older, closed defects
    elif status == 'Rejected':
        return random.randint(1, 15)  # Quickly rejected
    return random.randint(1, 60)

def generate_resolution_time_for_severity(severity):
    """Generate estimated resolution time based on severity"""
    resolution_times = {
        'Critical': ['1 day', '2 days', '3 days'],
        'Blocked': ['1 day', '2 days', '4 days'],
        'Medium': ['3 days', '5 days', '1 week'],
        'Minor': ['1 week', '2 weeks', '1 month']
    }
    
    if severity and severity in resolution_times:
        return random.choice(resolution_times[severity])
    return ''

# Generate sample test data
def generate_sample_data(num_tests=100):
    test_data = []
    priorities = ['low', 'medium', 'high', 'critical']
    statuses = ['pass', 'fail', 'blocked']
    
    for i in range(1, num_tests + 1):
        # Generate realistic test results
        priority = random.choices(priorities, weights=[30, 40, 20, 10])[0]
        
        # Higher priority tests have higher pass rates
        if priority == 'critical':
            status = random.choices(statuses, weights=[85, 10, 5])[0]
        elif priority == 'high':
            status = random.choices(statuses, weights=[88, 8, 4])[0]
        elif priority == 'medium':
            status = random.choices(statuses, weights=[90, 8, 2])[0]
        else:  # low priority
            status = random.choices(statuses, weights=[92, 7, 1])[0]
        
        # Generate defect information based on test status
        defect_severity = generate_defect_severity(status)
        defect_status = generate_defect_status(defect_severity)
        
        test_data.append({
            'test_id': f'TEST_{i:04d}',
            'test_name': f'Test Case {i}',
            'status': status,
            'priority': priority,
            'execution_time': random.randint(1, 300),
            'environment': random.choice(['staging', 'production']),
            'module': random.choice(['authentication', 'payment', 'user_mgmt', 'reporting', 'api']),
            # Enhanced defect data for comprehensive analysis
            'defect_severity': defect_severity,
            'defect_status': defect_status,
            'defect_category': generate_defect_category() if defect_severity else '',
            'defect_description': generate_defect_description_for_severity(defect_severity),
            'defect_priority': generate_defect_priority_for_severity(defect_severity),
            'estimated_resolution': generate_resolution_time_for_severity(defect_severity),
            'defect_assignee': generate_defect_assignee() if defect_severity else '',
            'defect_age_days': generate_defect_age_days(defect_status) if defect_severity else '',
            'resolution_reason': generate_defect_resolution_reason(defect_status),
            'defect_id': f'DEF_{random.randint(1000, 9999)}' if defect_severity else ''
        })
    
    return pd.DataFrame(test_data)

# Generate and save sample data
if __name__ == "__main__":
    # Generate sample data
    df = generate_sample_data(150)
    
    # Save to Excel
    df.to_excel('sample_test_results.xlsx', index=False)
    print("Sample test results generated: sample_test_results.xlsx")
    
    # Print summary
    print(f"\nSample Data Summary:")
    print(f"Total Tests: {len(df)}")
    print(f"Pass Rate: {(df['status'] == 'pass').mean():.2%}")
    print(f"Status Distribution:")
    print(df['status'].value_counts())
    print(f"\nPriority Distribution:")
    print(df['priority'].value_counts())
    
    # Defect lifecycle statistics
    defects_only = df[df['defect_severity'].notna() & (df['defect_severity'] != '')]
    if len(defects_only) > 0:
        print(f"\n🐛 Defect Lifecycle Analysis:")
        print(f"Total Defects: {len(defects_only)}")
        print(f"\nDefect Severity Distribution:")
        print(defects_only['defect_severity'].value_counts())
        print(f"\nDefect Status Distribution:")
        print(defects_only['defect_status'].value_counts())
        
        # Calculate ratios
        total_defects = len(defects_only)
        open_defects = len(defects_only[defects_only['defect_status'].isin(['Open', 'In Progress', 'Reopened'])])
        closed_defects = len(defects_only[defects_only['defect_status'].isin(['Resolved', 'Closed'])])
        rejected_defects = len(defects_only[defects_only['defect_status'] == 'Rejected'])
        
        print(f"\n📊 Defect Ratios:")
        print(f"Open Rate: {open_defects/total_defects:.1%} ({open_defects}/{total_defects})")
        print(f"Closure Rate: {closed_defects/total_defects:.1%} ({closed_defects}/{total_defects})")
        print(f"Rejection Rate: {rejected_defects/total_defects:.1%} ({rejected_defects}/{total_defects})")
        
        # Age analysis
        active_defects = defects_only[defects_only['defect_status'].isin(['Open', 'In Progress', 'Reopened'])]
        if len(active_defects) > 0:
            avg_age = active_defects['defect_age_days'].mean()
            print(f"Average Age of Active Defects: {avg_age:.1f} days")