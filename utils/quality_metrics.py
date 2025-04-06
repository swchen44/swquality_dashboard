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
    
    # 如果有可用metrics則計算，否則返回N/A
    if valid_metrics == 0:
        return {'score': 0, 'grade': 'N/A'}
    
    # 轉換為百分制
    final_score = round(total_score * 100, 1)
    
    # 評定等級 (防禦性程式設計)
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
