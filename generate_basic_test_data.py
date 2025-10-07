import pandas as pd
import random
from datetime import datetime, timedelta

def generate_basic_test_data():
    """Generate basic test data without defect columns as shown in user example"""
    
    test_cases = []
    
    # Generate test data similar to user's format
    modules = ['authentication', 'payment', 'user_management', 'reporting', 'api', 'ui']
    priorities = ['high', 'medium', 'low', 'critical']
    statuses = ['pass', 'fail', 'blocked', 'not_executed']
    environments = ['production', 'staging', 'development', 'testing']
    assignees = ['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson']
    
    for i in range(1, 51):  # Generate 50 test cases
        # Weight the status to have mostly passing tests
        status = random.choices(statuses, weights=[70, 20, 5, 5])[0]
        
        test_case = {
            'test_id': f'TEST_{i:04d}',
            'test_name': f'{random.choice(modules).title()} Test Case {i}',
            'status': status,
            'priority': random.choice(priorities),
            'execution_time': random.randint(15, 120),  # seconds
            'environment': random.choice(environments),
            'module': random.choice(modules),
            'assignee': random.choice(assignees),
            'comments': generate_comment(status)
        }
        
        test_cases.append(test_case)
    
    # Create DataFrame
    df = pd.DataFrame(test_cases)
    
    # Save to Excel
    df.to_excel('basic_test_results.xlsx', index=False)
    
    print(f"✅ Generated basic test data:")
    print(f"   📊 Test Cases: {len(df)}")
    print(f"   📁 Saved to: basic_test_results.xlsx")
    print(f"\\n📈 Test Results Summary:")
    print(df['status'].value_counts())
    print(f"\\n📋 Columns: {list(df.columns)}")
    print("\\n⚠️ Note: No defect-specific columns included - matches user's Excel format")
    
    return df

def generate_comment(status):
    """Generate realistic comments based on test status"""
    comments = {
        'pass': [
            'All assertions passed',
            'Test completed successfully',
            'No issues found',
            'Functionality working as expected',
            'All test steps executed without errors'
        ],
        'fail': [
            'Assertion failed on step 3',
            'Expected behavior not observed',
            'Functionality not working correctly',
            'Test failed due to system error',
            'Unable to complete test scenario'
        ],
        'blocked': [
            'Environment unavailable',
            'Dependency service down',
            'Missing test data',
            'Configuration issue preventing execution',
            'Blocked by previous test failure'
        ],
        'not_executed': [
            'Test skipped due to time constraints',
            'Not applicable for current build',
            'Deferred to next iteration',
            'Environment not ready',
            'Pending requirements clarification'
        ]
    }
    
    return random.choice(comments.get(status, ['No comment']))

if __name__ == "__main__":
    generate_basic_test_data()