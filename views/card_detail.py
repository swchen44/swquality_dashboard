import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from utils.quality_metrics import calculate_quality_score, get_style
from utils.project_config import load_project_config

@st.cache_data  
def load_preflight_wut_data(project_name):
    file_path = f'data/{project_name}/preflight_wut_result.csv'
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        return df
    return None

@st.cache_data
def load_module_coverage(project_name):
    file_path = f'data/{project_name}/module_coverage.csv'
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        return df
    return None

def show_card_detail():
    # 從session_state獲取專案名稱
    project = st.session_state.get("selected_project", "")
    if not project:
        st.error("未選擇專案，將返回主頁面")
        st.switch_page("pages/main.py")
    
    # 側邊欄設定 (與主頁面相同)
    st.sidebar.title('篩選控制')
    
    # 載入專案數據
    df = pd.read_csv(f'data/{project}/sample_qa_dashboard.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 日期範圍選擇
    min_date = df['Date'].min().to_pydatetime()
    max_date = df['Date'].max().to_pydatetime()
    date_range = st.sidebar.date_input(
        '日期範圍',
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # 過濾資料
    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    else:
        start_date, end_date = min_date, max_date
        
    filtered_df = df[
        (df['Date'] >= start_date) &
        (df['Date'] <= end_date)
    ]
    
    # 頁面內容
    st.title(f'{project} 詳細資訊')
    
    # 顯示專案配置
    config = load_project_config(project)
    if 'description' in config:
        st.markdown(f"**專案描述:** {config['description']}")
    
    # 顯示最新數據
    if len(filtered_df) > 0:
        latest_data = filtered_df.sort_values('Date').iloc[-1]
        
        cols = st.columns(3)
        metrics = [
            ('Test_Executed', '測試執行數', '{:.0f}'),
            ('Test_Passed', '測試通過數', '{:.0f}'), 
            ('Pass_Rate(%)', '通過率', '{:.1f}%'),
            ('Open_Bugs', '開放缺陷數', '{:.0f}'),
            ('Critical_Bugs', '嚴重缺陷', '{:.0f}'),
            ('Code_Coverage', '代碼覆蓋率', '{:.1f}%')
        ]
        
        for i, (col, title, fmt) in enumerate(metrics):
            with cols[i % 3]:
                value = latest_data[col]
                style = get_style(value, config['metrics'].get(col, {}).get('threshold', 0),
                                config['metrics'].get(col, {}).get('higher_better', True))
                st.markdown(f"""
                    <div style="border:1px solid #ddd; border-radius:8px; padding:10px; margin:5px; background-color:#f9f9f9;">
                        <div style="font-weight:bold;">{title}</div>
                        <div style='{style}; font-size:20px;'>{fmt.format(value)}</div>
                    </div>
                """, unsafe_allow_html=True)
    
    # 顯示趨勢圖表
    st.subheader('趨勢分析')
    if len(filtered_df) > 1:
        fig = px.line(
            filtered_df,
            x='Date',
            y=['Pass_Rate(%)', 'Code_Coverage'],
            title='品質指標趨勢'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 返回主頁面按鈕
    if st.button('返回主頁面'):
        st.switch_page("pages/main.py")

if __name__ == '__main__':
    show_card_detail()
