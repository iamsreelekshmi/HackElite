#!/usr/bin/env python3
"""Test script to debug defect parsing issue"""

import pandas as pd
import sys

def test_parse_excel_file():
    """Test the Excel parsing function"""
    try:
        # Read the Excel file
        df = pd.read_excel('sample_test_results.xlsx', sheet_name=0)
        
        print("=== ORIGINAL DATA ===")
        print(f"Original columns: {df.columns.tolist()}")
        print(f"Total rows: {len(df)}")
        print(f"Defect severity sample: {df['defect_severity'].value_counts(dropna=False)}")
        
        # Expected columns (adjust based on your Excel format)
        required_cols = ['test_id', 'status', 'priority']
        
        # Normalize column names
        df.columns = df.columns.str.lower().str.strip()
        
        print("\n=== AFTER NORMALIZATION ===")
        print(f"Normalized columns: {df.columns.tolist()}")
        
        # Basic validation
        if not all(col in df.columns for col in required_cols):
            print(f"ERROR: Excel file must contain columns: {required_cols}")
            return None
        
        # Process the data
        total_tests = len(df)
        passed_tests = len(df[df['status'].str.lower() == 'pass'])
        failed_tests = len(df[df['status'].str.lower() == 'fail'])
        blocked_tests = len(df[df['status'].str.lower() == 'blocked'])
        
        # High priority tests
        high_priority_df = df[df['priority'].str.lower().isin(['high', 'critical'])]
        high_total = len(high_priority_df)
        high_passed = len(high_priority_df[high_priority_df['status'].str.lower() == 'pass'])
        
        # Calculate KPIs
        kpis = {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'blocked': blocked_tests,
            'pass_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'blocked_ratio': blocked_tests / total_tests if total_tests > 0 else 0,
            'high_total': high_total,
            'high_passed': high_passed,
            'high_pass_rate': high_passed / high_total if high_total > 0 else None
        }
        
        print("\n=== BASIC KPIs ===")
        for key, value in kpis.items():
            print(f"{key}: {value}")
        
        # Process defect data if defect_severity column exists (after normalization)
        print(f"\n=== DEFECT PROCESSING ===")
        print(f"Checking for 'defect_severity' in columns: {df.columns.tolist()}")
        print(f"'defect_severity' in df.columns: {'defect_severity' in df.columns}")
        
        if 'defect_severity' in df.columns:
            print("✅ defect_severity column found!")
            defect_data = df[df['defect_severity'].notna()]
            print(f"Rows with defect data: {len(defect_data)}")
            
            defect_counts = {
                'Critical': len(defect_data[defect_data['defect_severity'].str.lower() == 'critical']),
                'Medium': len(defect_data[defect_data['defect_severity'].str.lower() == 'medium']),
                'Minor': len(defect_data[defect_data['defect_severity'].str.lower() == 'minor']),
                'Blocked': len(defect_data[defect_data['defect_severity'].str.lower() == 'blocked'])
            }
            kpis['defect_counts'] = defect_counts
            print(f"Defect counts: {defect_counts}")
        else:
            print("❌ defect_severity column NOT found!")
            print(f"Available columns: {df.columns.tolist()}")
        
        print("\n=== FINAL KPIs ===")
        for key, value in kpis.items():
            print(f"{key}: {value}")
            
        return kpis
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("Testing defect parsing...")
    result = test_parse_excel_file()
    
    if result:
        print(f"\n=== SUCCESS ===")
        print(f"defect_counts in result: {'defect_counts' in result}")
        if 'defect_counts' in result:
            print(f"defect_counts value: {result['defect_counts']}")
    else:
        print("=== FAILED ===")