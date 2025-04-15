import streamlit as st
import pandas as pd
import os
import glob
import plotly.express as px
from datetime import datetime
from utils.quality_metrics import calculate_quality_score, get_style
from utils.project_config import load_project_config

@st.cache_data  
def load_preflight_wut_data(project_name):
    """載入並返回指定項目的preflight_wut測試結果"""
    file_path = f'data/{project_name}/preflight_wut_result.csv'
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            return df
        except Exception as e:
            st.error(f"載入preflight_wut數據失敗: {str(e)}")
            raise
    return None

@st.cache_data
def load_module_coverage(project_name):
    """載入並返回指定項目的模組覆蓋率數據"""
    file_path = f'data/{project_name}/module_coverage.csv'
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            return df
        except Exception as e:
            st.error(f"載入module coverage數據失敗: {str(e)}")
            raise
    return None

@st.cache_data
def load_all_projects():
    """載入所有專案數據"""
    project_files = glob.glob('data/project*/sample_qa_dashboard.csv')
    all_data = []
    for file in project_files:
        project_name = file.split('/')[1]
        df = pd.read_csv(file)
        df['Project'] = project_name
        all_data.append(df)
    return pd.concat(all_data)

def show_main_page():
    """顯示主頁面內容"""
    # 載入資料
    df = load_all_projects()
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 側邊欄設定
    st.sidebar.title('篩選控制')
    projects = df['Project'].unique()
    selected_projects = st.sidebar.multiselect('選擇專案', projects, default=projects[:3])
    
    # 日期範圍選擇
    min_date = df['Date'].min().to_pydatetime()
    max_date = df['Date'].max().to_pydatetime()
    date_range = st.sidebar.date_input('日期範圍', value=(min_date, max_date), min_value=min_date, max_value=max_date)
    
    # 過濾資料
    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    else:
        start_date, end_date = min_date, max_date
        
    filtered_df = df[
        (df['Project'].isin(selected_projects)) &
        (df['Date'] >= start_date) &
        (df['Date'] <= end_date)
    ]
    
    # 主頁面內容
    st.title('軟體品質儀表板')
    
    # 專案品質卡片
    if len(selected_projects) > 0:
        latest_data = filtered_df.sort_values('Date').groupby('Project').last().reset_index()
        
        for _, row in latest_data.iterrows():
            project = row['Project']
            config = load_project_config(project)
            
            with st.expander(f"{project} - 品質評分", expanded=True):
                cols = st.columns(4)
                metrics = [
                    ('Test_Executed', '測試執行數', '{:.0f}'),
                    ('Test_Passed', '測試通過數', '{:.0f}'),
                    ('Pass_Rate(%)', '通過率', '{:.1f}%'),
                    ('Code_Coverage', '代碼覆蓋率', '{:.1f}%')
                ]
                
                for i, (col, title, fmt) in enumerate(metrics):
                    with cols[i % 4]:
                        value = row[col]
                        style = get_style(value, config['metrics'].get(col, {}).get('threshold', 0), 
                                        config['metrics'].get(col, {}).get('higher_better', True))
                        st.markdown(f"""
                            <div style="border:1px solid #ddd; border-radius:8px; padding:10px; margin:5px; background-color:#f9f9f9;">
                                <div style="font-weight:bold;">{title}</div>
                                <div style='{style}; font-size:20px;'>{fmt.format(value)}</div>
                            </div>
                        """, unsafe_allow_html=True)
                
                # 添加點擊查看詳情按鈕
                if st.button(
                    "查看詳情", 
                    key=f"detail_{project}",
                    use_container_width=True
                ):
                    st.session_state["selected_project"] = project
                    st.switch_page("pages/card_detail.py")

    # 其他圖表內容...
    # (保留原有圖表邏輯，此處簡化顯示)

if __name__ == '__main__':
    show_main_page()
