import pandas as pd
from utils.project_config import load_project_config

def calculate_quality_score(project_name, metrics):
    """計算專案品質評分"""
    config = load_project_config(project_name)
    if not config or not isinstance(metrics, dict):
        return {'score': 0, 'grade': 'N/A'}
    
    total_score = 0
    valid_metrics = 0
    
    for metric, props in config['metrics'].items():
        if metric not in metrics or metrics[metric] is None:
            continue
            
        threshold = props.get('threshold', 100)
        weight = config['weights'].get(metric, 0)
        value = metrics[metric]
        
        try:
            if props.get('higher_better', True):
                normalized = min(float(value) / float(threshold), 1.5)
            else:
                normalized = min(float(threshold) / max(float(value), 1), 1.5)
                
            total_score += normalized * weight
            valid_metrics += 1
        except (ValueError, TypeError, ZeroDivisionError):
            continue
    
    if valid_metrics == 0:
        return {'score': 0, 'grade': 'N/A'}
    
    final_score = round(total_score * 100, 1)
    
    grade_scale = config.get('style_rules', {}).get('grade_scale', {
        'A': 90, 'B': 80, 'C': 70, 'D': 60, 'E': 0
    })
    
    for grade, min_score in grade_scale.items():
        if final_score >= min_score:
            return {'score': final_score, 'grade': grade}
    
    return {'score': final_score, 'grade': 'E'}

def get_style(value, threshold, higher_better):
    """獲取數值顯示樣式"""
    if higher_better:
        return "color: green" if value >= threshold else "color: red"
    else:
        return "color: green" if value <= threshold else "color: red"

def load_module_coverage(project_name):
    """載入並返回指定項目的模組覆蓋率數據
    
    此函數會從data/{project_name}/module_coverage.csv讀取模組覆蓋率數據，
    並將日期欄位轉換為datetime格式。
    
    Args:
        project_name (str): 項目名稱，對應data目錄下的子目錄
        
    Returns:
        pandas.DataFrame or None: 包含模組覆蓋率數據的DataFrame結構如下:
            - date: 測試日期 (datetime)
            - module_name: 模組名稱 
            - covered_line_number: 覆蓋行數
            - total_line_number: 總行數
            - coverage_percentage: 覆蓋率
            找不到文件時返回None
    """
    file_path = f'data/{project_name}/module_coverage.csv'
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            return df
        except Exception as e:
            logging.error(f"載入模組覆蓋率數據失敗: {str(e)}", exc_info=True)
            raise
    
    logging.warning(f"模組覆蓋率文件不存在: {file_path}")
    return None
