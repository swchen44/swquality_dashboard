import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime
from utils.quality_metrics import calculate_quality_score, get_style
from utils.project_config import load_project_config

def load_preflight_wut_data(project_name):
    """載入並返回指定專案的 preflight_wut 測試結果"""
    file_path = f'data/{project_name}/preflight_wut_result.csv'
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            return df
        except Exception as e:
            st.error(f"載入 preflight_wut 數據失敗: {str(e)}")
            return None
    return None

def show_project_page():
    # 從session_state獲取專案名稱
    project = st.session_state.get("selected_project", "")
    if not project:
        st.error("未選擇專案，將返回主頁面")
        st.switch_page("pages/main.py")
    
    # 側邊欄設定
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
    st.title(f'{project} 專案儀表板')
    
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
    
    # 建立標籤頁
    tab1, tab2, tab3 = st.tabs(["品質指標趨勢", "模組覆蓋率", "Preflight WUT 分析"])
    
    with tab1:
        if len(filtered_df) > 1:
            fig = px.line(
                filtered_df,
                x='Date',
                y=['Pass_Rate(%)', 'Code_Coverage'],
                title='品質指標趨勢'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # 載入模組覆蓋率數據
        coverage_file = f'data/{project}/module_coverage.csv'
        if os.path.exists(coverage_file):
            coverage_df = pd.read_csv(coverage_file)
            coverage_df['date'] = pd.to_datetime(coverage_df['date'])
            
            # 過濾日期範圍
            mask = (
                (coverage_df['date'] >= pd.to_datetime(start_date)) & 
                (coverage_df['date'] <= pd.to_datetime(end_date))
            )
            filtered_coverage = coverage_df[mask]
            
            # 建立折線圖
            fig1 = px.line(
                filtered_coverage,
                x='date',
                y='coverage_percentage',
                color='module_name',
                title='模組覆蓋率趨勢',
                labels={
                    'date': '日期',
                    'coverage_percentage': '覆蓋率 (%)',
                    'module_name': '模組名稱'
                }
            )
            
            # 更新圖表樣式
            fig1.update_layout(
                xaxis_title='日期',
                yaxis_title='覆蓋率 (%)',
                legend_title='模組',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig1, use_container_width=True)
            
            # 計算並顯示統計摘要
            with st.expander("覆蓋率統計摘要"):
                # 按模組計算平均覆蓋率
                avg_coverage = filtered_coverage.groupby('module_name')['coverage_percentage'].agg([
                    ('平均覆蓋率', 'mean'),
                    ('最低覆蓋率', 'min'),
                    ('最高覆蓋率', 'max')
                ]).round(2)
                
                # 使用 plotly 繪製箱形圖
                fig2 = px.box(
                    filtered_coverage,
                    x='module_name',
                    y='coverage_percentage',
                    title='模組覆蓋率分布',
                    labels={
                        'module_name': '模組名稱',
                        'coverage_percentage': '覆蓋率 (%)'
                    }
                )
                
                # 顯示統計表格和箱形圖
                st.dataframe(avg_coverage, use_container_width=True)
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("此專案無模組覆蓋率數據")
    
    with tab3:
        # 載入 preflight_wut 數據
        preflight_data = load_preflight_wut_data(project)
        if preflight_data is not None:
            # 過濾日期範圍
            mask = (
                (preflight_data['date'] >= pd.to_datetime(start_date)) & 
                (preflight_data['date'] <= pd.to_datetime(end_date))
            )
            filtered_preflight = preflight_data[mask]
            
            # 計算每日各類型的數量
            daily_counts = filtered_preflight.groupby(['date', 'type']).size().unstack(fill_value=0)
            
            # 確保所有類型都存在
            for col in ['build_fail', 'wut_fail', 'pass']:
                if col not in daily_counts.columns:
                    daily_counts[col] = 0
            
            # 生成堆疊長條圖
            fig = px.bar(
                daily_counts,
                title=f'{project} Preflight WUT 測試結果分析',
                labels={'value': '數量', 'date': '日期', 'type': '狀態'},
                color_discrete_map={
                    'build_fail': '#FF5252',  # 紅色
                    'wut_fail': '#FFD740',    # 黃色
                    'pass': '#4CAF50'         # 綠色
                },
                barmode='stack'
            )
            
            # 更新圖表樣式
            fig.update_layout(
                xaxis_title='日期',
                yaxis_title='測試次數',
                legend_title='測試結果'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 顯示統計摘要
            with st.expander("查看統計摘要"):
                total_tests = len(filtered_preflight)
                pass_rate = (daily_counts['pass'].sum() / total_tests * 100) if total_tests > 0 else 0
                
                st.markdown(f"""
                    ### 測試統計
                    - 總測試次數: {total_tests}
                    - 通過次數: {daily_counts['pass'].sum()}
                    - Build 失敗次數: {daily_counts['build_fail'].sum()}
                    - WUT 失敗次數: {daily_counts['wut_fail'].sum()}
                    - 通過率: {pass_rate:.2f}%
                """)
        else:
            st.info("此專案無 Preflight WUT 測試數據")
    
    tab1_day, tab2_day = st.tabs(["單日模組覆蓋率", "單日模組覆蓋率分析"])
    
    with tab1_day:
        # 讀取覆蓋率數據
        coverage_file = f'data/{project}/module_coverage.csv'
        if os.path.exists(coverage_file):
            coverage_df = pd.read_csv(coverage_file)
            coverage_df['date'] = pd.to_datetime(coverage_df['date'])
            
            # 使用側邊欄選擇的結束日期
            selected_date = end_date
            day_data = coverage_df[coverage_df['date'] == selected_date].copy()
            
            if len(day_data) > 0:
                # 計算未覆蓋的行數
                day_data['uncovered_lines'] = day_data['total_line_number'] - day_data['covered_line_number']
                
                # 依據覆蓋率排序（由高到低）
                day_data = day_data.sort_values('coverage_percentage', ascending=False)
                
                # 創建堆疊直條圖
                fig = go.Figure()
                
                # 新增覆蓋的行數
                fig.add_trace(go.Bar(
                    name='已覆蓋行數',
                    x=day_data['module_name'],
                    y=day_data['covered_line_number'],
                    marker_color='#2ecc71',  # 綠色
                    text=day_data['covered_line_number'],
                    textposition='inside',
                ))
                
                # 新增未覆蓋的行數
                fig.add_trace(go.Bar(
                    name='未覆蓋行數',
                    x=day_data['module_name'],
                    y=day_data['uncovered_lines'],
                    marker_color='#e74c3c',  # 紅色
                    text=day_data['uncovered_lines'],
                    textposition='inside',
                ))
                
                # 更新圖表布局
                fig.update_layout(
                    title=f'模組覆蓋率分析 ({selected_date.strftime("%Y-%m-%d")})',
                    xaxis_title='模組名稱',
                    yaxis_title='程式行數',
                    barmode='stack',
                    hovermode='x unified',
                    showlegend=True
                )
                
                # 添加覆蓋率文字標籤
                annotations = []
                for i, row in day_data.iterrows():
                    annotations.append(dict(
                        x=row['module_name'],
                        y=row['total_line_number'],
                        text=f'{row["coverage_percentage"]:.1f}%',
                        showarrow=False,
                        yanchor='bottom',
                        yshift=10,
                        font=dict(
                            size=14,
                            color='black'
                        )
                    ))
                fig.update_layout(annotations=annotations)
                
                # 顯示圖表
                st.plotly_chart(fig, use_container_width=True)
                
                # 顯示數據表格
                with st.expander("查看詳細數據"):
                    summary_df = day_data[['module_name', 'covered_line_number', 'total_line_number', 'coverage_percentage']].copy()
                    summary_df.columns = ['模組名稱', '已覆蓋行數', '總行數', '覆蓋率(%)']
                    summary_df['覆蓋率(%)'] = summary_df['覆蓋率(%)'].round(2)
                    st.dataframe(summary_df, use_container_width=True)
            else:
                st.warning(f"在 {selected_date.strftime('%Y-%m-%d')} 沒有找到覆蓋率數據")
        else:
            st.info("此專案無模組覆蓋率數據")
    
    with tab2_day:
        # 讀取覆蓋率數據
        coverage_file = f'data/{project}/module_coverage.csv'
        if os.path.exists(coverage_file):
            coverage_df = pd.read_csv(coverage_file)
            coverage_df['date'] = pd.to_datetime(coverage_df['date'])
            
            # 使用側邊欄選擇的結束日期
            selected_date = end_date
            day_data = coverage_df[coverage_df['date'] == selected_date].copy()
            
            if len(day_data) > 0:
                # 創建泡泡圖
                fig = go.Figure()
                
                # 添加泡泡
                fig.add_trace(go.Scatter(
                    x=day_data['coverage_percentage'],
                    y=day_data['total_line_number'],
                    mode='markers+text',
                    marker=dict(
                        size=20,
                        color='#1f77b4',
                        opacity=0.7,
                        line=dict(
                            color='#ffffff',
                            width=1
                        )
                    ),
                    text=day_data['module_name'],
                    textposition='top center',
                    name='模組'
                ))
                
                # 更新圖表布局
                fig.update_layout(
                    title=f'模組覆蓋率分析 ({selected_date.strftime("%Y-%m-%d")})',
                    xaxis_title='覆蓋率 (%)',
                    yaxis_title='總行數',
                    showlegend=False,
                    hovermode='closest'
                )
                
                # 添加網格線
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
                
                # 顯示圖表
                st.plotly_chart(fig, use_container_width=True)
                
                # 顯示數據表格
                with st.expander("查看詳細數據"):
                    summary_df = day_data[['module_name', 'coverage_percentage', 'total_line_number']].copy()
                    summary_df.columns = ['模組名稱', '覆蓋率(%)', '總行數']
                    summary_df['覆蓋率(%)'] = summary_df['覆蓋率(%)'].round(2)
                    st.dataframe(summary_df.sort_values('覆蓋率(%)', ascending=False), use_container_width=True)
            else:
                st.warning(f"在 {selected_date.strftime('%Y-%m-%d')} 沒有找到覆蓋率數據")
        else:
            st.info("此專案無模組覆蓋率數據")

    # 返回主頁面按鈕
    if st.button('返回主頁面'):
        st.switch_page("pages/main.py")

if __name__ == '__main__':
    show_project_page()
