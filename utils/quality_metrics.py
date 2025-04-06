import pandas as pd
from utils.project_config import load_project_config

def calculate_quality_score(project_name, metrics):
    """計算專案品質評分"""
    config = load_project_config(project_name)
    if not config:
        return None
    
    total_score = 0
    for metric, props in config['metrics'].items():
        value = metrics.get(metric, 0)
        threshold = props['threshold']
        weight = config['weights'].get(metric, 0)
        
        if props['higher_better']:
            normalized = min(value / threshold, 1.5)  # 最高不超過閾值1.5倍
        else:
            normalized = min(threshold / max(value, 1), 1.5)  # 避免除以0
            
        total_score += normalized * weight
    
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
