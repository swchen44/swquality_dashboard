import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_module_coverage_data(project_name):
    start_date = datetime(2024, 2, 1)
    end_date = datetime(2025, 12, 1)
    date_range = pd.date_range(start_date, end_date)
    
    # 為每個日期生成6個module的資料
    data = []
    for date in date_range:
        for module_num in range(1, 7):
            total_lines = np.random.randint(101, 1000)  # Minimum 101 to ensure covered_lines can be <= total_lines
            covered_lines = np.random.randint(100, total_lines + 1)  # +1 to include total_lines
            coverage = round((covered_lines / total_lines) * 100, 2)
            
            data.append({
                'date': date.strftime('%Y/%m/%d'),
                'module_name': f'm{module_num}',
                'covered_line_number': covered_lines,
                'total_line_number': total_lines,
                'coverage_percentage': coverage
            })
    
    df = pd.DataFrame(data)
    os.makedirs(f'data/{project_name}', exist_ok=True)
    df.to_csv(f'data/{project_name}/module_coverage.csv', index=False)
    return df

def generate_preflight_data(project_name):
    """生成preflight測試結果數據"""
    if project_name in ['project1', 'project3', 'project5']:
        return None
        
    start_date = datetime(2024, 2, 1)
    end_date = datetime(2024, 12, 1)
    date_range = pd.date_range(start_date, end_date)
    
    # 生成測試結果數據
    data = []
    for date in date_range:
        # 跳過週末(周六=5, 周日=6)
        if date.weekday() >= 5:
            continue
            
        # 每天1-10筆測試結果
        num_records = np.random.randint(1, 11)
        for _ in range(num_records):
            # 隨機生成測試結果
            rand = np.random.rand()
            if rand < 0.1:  # 10% build fail
                test_type = 'build_fail'
            elif rand < 0.3:  # 20% wut fail
                test_type = 'wut_fail'
            else:  # 70% pass
                test_type = 'pass'
                
            # 失败案例列表
            fail_cases = [
                'TimeoutError', 
                'AssertionError',
                'NetworkError',
                'ValidationError',
                'NullPointerException',
                'SyntaxError',
                'TypeMismatch',
                'MissingDependency',
                'ConfigurationError'
            ]
            
            record = {
                'date': date.strftime('%Y/%m/%d'),
                'type': test_type
            }
            
            if test_type == 'wut fail':
                record['wut_fail_case'] = np.random.choice(fail_cases)
                
            data.append(record)
    
    df = pd.DataFrame(data)
    os.makedirs(f'data/{project_name}', exist_ok=True)
    df.to_csv(f'data/{project_name}/preflight_wut_result.csv', index=False)
    return df

def generate_project_data(project_name, base_value):
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = pd.date_range(start_date, end_date)
    
    # 隨機跳過5-115天，確保至少有250天資料
    skip_days = np.random.randint(5, 115)
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1 + np.random.randint(0, 3))  # 隨機間隔1-3天
        
    # 確保至少有250天資料
    if len(dates) < 250:
        dates = dates[:250]
    
    # 生成測試數據
    test_executed = np.random.randint(base_value, base_value + 100, len(dates))
    test_passed = test_executed - np.random.randint(5, 30, len(dates))
    test_failed = test_executed - test_passed
    pass_rate = (test_passed / test_executed * 100).round(2)
    open_bugs = np.random.randint(5, 30, len(dates))
    critical_bugs = np.random.randint(0, 10, len(dates))
    code_coverage = np.linspace(
        base_value/2, 
        base_value/2 + 30, 
        len(dates)
    ).round(1)
    
    # 建立DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Test_Executed': test_executed,
        'Test_Passed': test_passed,
        'Test_Failed': test_failed,
        'Pass_Rate(%)': pass_rate,
        'Open_Bugs': open_bugs,
        'Critical_Bugs': critical_bugs,
        'Code_Coverage': code_coverage
    })
    
    # 儲存CSV
    os.makedirs(f'data/{project_name}', exist_ok=True)
    df.to_csv(f'data/{project_name}/sample_qa_dashboard.csv', index=False)
    
    # 生成module coverage資料
    generate_module_coverage_data(project_name)
    
    # 生成preflight測試結果
    generate_preflight_data(project_name)
    
    return df

# 生成10個專案資料
projects = {
    'project1': 80,
    'project2': 70,
    'project3': 60,
    'project4': 90,
    'project5': 50,
    'project6': 100,
    'project7': 40,
    'project8': 75,
    'project9': 85,
    'project10': 55
}

for name, base in projects.items():
    generate_project_data(name, base)
