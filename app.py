# 必須放在最前面的Streamlit配置
import streamlit as st
st.set_page_config(
    page_title="Software Quality Dashboard",
    page_icon="📊",
    layout="wide"
)

import logging
import logging.handlers
from datetime import datetime

# 配置日志系统
def setup_logging():
    """配置应用程序日志系统
    
    设置:
    - 日志级别: DEBUG
    - 输出到文件: logs/app.log (每天轮换，保留7天)
    - 输出到控制台
    - 日志格式: 时间 - 级别 - 文件名:行号 - 消息
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # 创建logs目录
    os.makedirs('logs', exist_ok=True)
    
    # 文件handler (每天轮换)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        'logs/app.log', when='midnight', backupCount=7, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 控制台handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logging.info("日志系统初始化完成")

# 
# Software Quality Dashboard Application

# 目的:
#     本應用程序提供了一個完整的軟體品質監控儀表板，用於追蹤和分析多個專案的品質指標，
#     包括測試覆蓋率、缺陷統計和preflight測試結果等。

# 功能:
#     - 展示專案品質概覽卡片
#     - 提供測試通過率、缺陷趨勢和代碼覆蓋率趨勢圖
#     - 顯示模組級別的覆蓋率詳細資訊
#     - 整合preflight測試結果分析
#     - 支援多專案數據比較和篩選

# 運作原理:
#     1. 從CSV檔案載入專案數據
#     2. 應用用戶選擇的篩選條件
#     3. 計算各種品質指標
#     4. 使用Plotly生成互動式圖表
#     #5. 使用Streamlit建立web儀表板

# 使用範例:
#     $ streamlit run app.py

# API文件:
#     參見各函數和方法的docstrings
# 

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
    """載入並返回指定項目的preflight_wut測試結果
    
    Args:
        project_name (str): 項目名稱，對應data目錄下的子目錄
        
    Returns:
        pandas.DataFrame or None: 包含preflight_wut測試結果的DataFrame
            找不到文件時返回None
    """
    file_path = f'data/{project_name}/preflight_wut_result.csv'
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            return df
        except Exception as e:
            logging.error(f"載入preflight_wut數據失敗: {str(e)}", exc_info=True)
            raise
    
    logging.warning(f"preflight_wut文件不存在: {file_path}")
    return None

@st.cache_data
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
            
    Example:
        >>> df = load_module_coverage("project1")
        >>> print(df.head())
    """
    file_path = f'data/{project_name}/module_coverage.csv'
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            logging.info(f"成功載入preflight_wut數據，行數: {len(df)}")
            return df
        except Exception as e:
            logging.error(f"載入preflight_wut數據失敗: {str(e)}", exc_info=True)
            raise
    
    logging.warning(f"preflight_wut文件不存在: {file_path}")
    return None

# 載入所有專案資料
@st.cache_data
def load_all_projects():
    project_files = glob.glob('data/project*/sample_qa_dashboard.csv')
    all_data = []
    
    for file in project_files:
        project_name = file.split('/')[1]  # 取得專案名稱
        df = pd.read_csv(file)
        df['Project'] = project_name
        all_data.append(df)
    
    return pd.concat(all_data)

# 主程式
def main():
    # 載入資料
    df = load_all_projects()
    
    # 轉換日期格式
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 側邊欄設定
    st.sidebar.title('篩選控制')
    
    # 專案選擇
    projects = df['Project'].unique()
    selected_projects = st.sidebar.multiselect(
        '選擇專案', 
        projects, 
        default=projects[:3]
    )
    
    # 日期範圍選擇
    min_date = df['Date'].min().to_pydatetime()
    max_date = df['Date'].max().to_pydatetime()
    
    # 預設時間範圍選項
    time_period = st.sidebar.selectbox(
        '快速選擇時間範圍',
        ['自訂', '過去1個月', '過去2個月', '過去3個月', '過去6個月', '過去12個月'],
        index=0
    )
    
    # 計算預設範圍的日期
    if time_period != '自訂':
        months = int(time_period[2:-2])
        start_date = max_date - pd.DateOffset(months=months)
        date_range = (start_date, max_date)
    else:
        date_range = st.sidebar.date_input(
            '自訂日期範圍',
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    # 強制使用亮色主題
    theme = '亮色'
    
    # 過濾資料 - 處理日期範圍選擇不完整的情況
    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    else:
        start_date, end_date = min_date, max_date
        
    filtered_df = df[
        (df['Project'].isin(selected_projects)) &
        (df['Date'] >= start_date) &
        (df['Date'] <= end_date)
    ]
    
    # 載入preflight_wut數據
    all_preflight_wut = None
    if len(selected_projects) > 0:
        preflight_wut_data = []
        for project in selected_projects:
            pf_df = load_preflight_wut_data(project)
            if pf_df is not None:
                pf_df['Project'] = project
                preflight_wut_data.append(pf_df)
        
        if len(preflight_wut_data) > 0:
            all_preflight_wut = pd.concat(preflight_wut_data)
            # 過濾preflight_wut數據
            if len(date_range) == 2:
                all_preflight_wut = all_preflight_wut[
                    (all_preflight_wut['date'] >= start_date) & 
                    (all_preflight_wut['date'] <= end_date)
                ]
    
    # 主頁面標題
    st.title('軟體品質儀表板')
    st.markdown("---")

    # 定義tooltip字典
    title_dict = {
        '測試執行數': '已執行的測試案例總數',
        '測試通過數': '成功通過的測試案例數', 
        '通過率': '測試通過百分比',
        '開放缺陷數': '目前未解決的缺陷數量',
        '嚴重缺陷': '嚴重等級的缺陷數量',
        '代碼覆蓋率': '測試覆蓋的代碼百分比',
        'Preflight WUT Summary': 'Build Fail / WUT Fail / Pass / Total'
    }
    
    # 專案品質概覽區
    st.subheader('專案品質概覽')
    if len(selected_projects) > 0:
        latest_data = filtered_df.sort_values('Date').groupby('Project').last().reset_index()
        
        # 顯示所選專案清單
        st.markdown(f"**已選擇專案:** {', '.join(selected_projects)}")
        
        # 指標表格
        metrics = [
            ('Test_Executed', '測試執行數', '{:.0f}'),
            ('Test_Passed', '測試通過數', '{:.0f}'),
            ('Pass_Rate(%)', '通過率', '{:.1f}%'),
            ('Open_Bugs', '開放缺陷數', '{:.0f}'),
            ('Critical_Bugs', '嚴重缺陷', '{:.0f}'),
            ('Code_Coverage', '代碼覆蓋率', '{:.1f}%')
        ]
        
        # 添加preflight_wut組合指標
        if all_preflight_wut is not None:
            metrics.extend([
                ('preflight_combined', 'Preflight WUT Summary', '{}')
            ])
        
        # 顯示所有專案數據
        all_projects_data = []
        for project in selected_projects:
            project_df = latest_data[latest_data['Project'] == project]
            if len(project_df) == 0:
                # 如果沒有數據，使用空值
                project_data = {col: None for col in df.columns}
            else:
                project_data = project_df.iloc[0]
            # 計算品質評分
            metrics_dict = {col: project_data[col] for col, _, _ in metrics if col in project_data}

            quality = calculate_quality_score(project, metrics_dict)
            
            # 獲取專案配置
            config = load_project_config(project)
            
            # 收集專案數據
            row_data = {'專案名稱': project}
            for col, title, fmt in metrics:
                value = project_data.get(col)
                props = config['metrics'].get(col, {})
                
                # 處理preflight_wut組合數據
                if col == 'preflight_combined' and all_preflight_wut is not None:
                    pf_project = all_preflight_wut[all_preflight_wut['Project'] == project]
                    build_fail = len(pf_project[pf_project['type'] == 'build fail'])
                    wut_fail = len(pf_project[pf_project['type'] == 'wut fail'])
                    passed = len(pf_project[pf_project['type'] == 'pass'])
                    total = len(pf_project)
                    value = f"{build_fail}/{wut_fail}/{passed}/{total}"
                    style = "color: black"
                else:
                    style = get_style(value or 0, props.get('threshold',0), props.get('higher_better',True))
                
                formatted_value = "N/A" if value is None else fmt.format(value)
                row_data[title] = {
                    'value': formatted_value,
                    'style': style
                }
            row_data['品質評分'] = f"{quality['score']} ({quality['grade']})"
            all_projects_data.append(row_data)
        
        # 為每個專案顯示指標卡片
        for project in all_projects_data:
            with st.expander(f"{project['專案名稱']} - 品質評分: {project['品質評分']}", expanded=True):
                # 根據metrics數量動態調整列數 (每行最多4列)
                num_cols = min(len(metrics), 4)
                cols = st.columns(num_cols)
                for i, (_, title, _) in enumerate(metrics):
                    # 計算當前應顯示的列索引
                    col_idx = i % num_cols
                    # 當列索引歸零時創建新行
                    if col_idx == 0 and i > 0:
                        cols = st.columns(num_cols)
                    with cols[col_idx]:
                        st.markdown(
                            f"""
                            <div style="
                                border: 1px solid #ddd;
                                border-radius: 8px;
                                padding: 10px;
                                margin: 5px;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                background-color: #f9f9f9;
                            ">
                                <div style="font-weight: bold; margin-bottom: 5px;">
                                    {title}
                                    <span style="color: #666; font-size: 0.8em; margin-left: 5px;">(?)</span>
                                </div>
                                <div style='{project[title]["style"]}; font-size: 20px;'>
                                    {project[title]["value"]}
                                </div>
                                <div style="display: none;">{title_dict.get(title, '')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
        
            # 顯示專案說明和詳情連結
            if 'description' in config and config['description']:
                with st.expander("專案詳情"):
                    st.write(config['description'])
                    if len(selected_projects) == 1:
                        st.markdown(f"[查看完整專案詳情](/project.py?project={selected_projects[0]})", unsafe_allow_html=True)
        
    
    # 趨勢圖表區
    st.markdown("---")
    st.subheader('趨勢分析')
    
    if len(selected_projects) > 0:
        # 判斷是否為同一天
        is_single_day = len(filtered_df['Date'].unique()) == 1
        
        tab1, tab2, tab3 = st.tabs(["測試通過率", "缺陷趨勢", "代碼覆蓋率"])
        
        with tab1:
            if is_single_day:
                fig = px.bar(
                    filtered_df,
                    x='Project',
                    y='Pass_Rate(%)',
                    color='Project',
                    title=f"{filtered_df['Date'].iloc[0].strftime('%Y/%m/%d')} 測試通過率",
                    text='Pass_Rate(%)'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            else:
                fig = px.line(
                    filtered_df,
                    x='Date',
                    y='Pass_Rate(%)',
                    color='Project',
                    title='測試通過率趨勢'
                )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            if is_single_day:
                fig = px.bar(
                    filtered_df,
                    x='Project',
                    y=['Open_Bugs', 'Critical_Bugs'],
                    color='Project',
                    title=f"{filtered_df['Date'].iloc[0].strftime('%Y/%m/%d')} 缺陷數量",
                    barmode='group'
                )
            else:
                fig = px.line(
                    filtered_df,
                    x='Date',
                    y=['Open_Bugs', 'Critical_Bugs'],
                    color='Project',
                    title='缺陷趨勢'
                )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            if is_single_day:
                fig = px.bar(
                    filtered_df,
                    x='Project',
                    y='Code_Coverage',
                    color='Project',
                    title=f"{filtered_df['Date'].iloc[0].strftime('%Y/%m/%d')} 代碼覆蓋率",
                    text='Code_Coverage'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            else:
                fig = px.line(
                    filtered_df,
                    x='Date',
                    y='Code_Coverage',
                    color='Project',
                    title='代碼覆蓋率趨勢'
                )
            st.plotly_chart(fig, use_container_width=True)
    
    # 資料表格區
    st.markdown("---")
    st.subheader('詳細資料')
    st.dataframe(
        filtered_df.sort_values(['Project', 'Date']),
        use_container_width=True
    )
    
    # 模組覆蓋率趨勢 (僅顯示單一專案時)
    if len(selected_projects) == 1:
        st.markdown("---")
        st.subheader('模組覆蓋率趨勢')
        
        module_df = load_module_coverage(selected_projects[0])
        if module_df is not None:
            # 應用日期篩選
            filtered_module_df = module_df[
                (module_df['date'] >= start_date) & 
                (module_df['date'] <= end_date)
            ]
            
            # 計算總覆蓋率
            daily_totals = filtered_module_df.groupby('date').agg({
                'covered_line_number': 'sum',
                'total_line_number': 'sum'
            }).reset_index()
            daily_totals['total_coverage'] = (daily_totals['covered_line_number'] / daily_totals['total_line_number'] * 100).round(2)
            
            try:
                if len(filtered_module_df) == 0:
                    st.warning("選定日期範圍內無模組覆蓋率數據")
                    return
                
                # 判斷是否為同一天
                is_single_day = len(filtered_module_df['date'].unique()) == 1
                
                if is_single_day:
                    # 確保有數據
                    if len(daily_totals) == 0:
                        st.warning("無法計算總覆蓋率")
                        return
                        
                    # 單日數據 - 使用長條圖
                    fig = px.bar(
                        filtered_module_df,
                        x='module_name',
                        y='coverage_percentage',
                        color='module_name',
                        title=f"{filtered_module_df['date'].iloc[0].strftime('%Y/%m/%d')} 模組覆蓋率",
                        labels={'coverage_percentage': '覆蓋率(%)'},
                        text='coverage_percentage'
                    )
                    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
                    
                    # 添加總覆蓋率橫線
                    fig.add_hline(
                        y=daily_totals['total_coverage'].iloc[0],
                        line_dash="dot",
                        line_color="black",
                        annotation_text=f"總覆蓋率: {daily_totals['total_coverage'].iloc[0]:.2f}%",
                        annotation_position="top right"
                    )
                else:
                    # 多日數據 - 使用折線圖
                    fig = px.line(
                        filtered_module_df,
                        x='date',
                        y='coverage_percentage',
                        color='module_name',
                        title='各模組覆蓋率趨勢',
                        labels={'coverage_percentage': '覆蓋率(%)'}
                    )
                    
                    # 添加總覆蓋率線
                    fig.add_scatter(
                        x=daily_totals['date'],
                        y=daily_totals['total_coverage'],
                        mode='lines',
                        name='總覆蓋率',
                        line=dict(color='black', width=4, dash='dot')
                    )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"繪製圖表時發生錯誤: {str(e)}")
        else:
            st.warning("找不到模組覆蓋率資料")
    
    # 下載按鈕
    st.download_button(
        label="下載篩選後資料 (CSV)",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='filtered_quality_data.csv',
        mime='text/csv'
    )

if __name__ == '__main__':
    main()
