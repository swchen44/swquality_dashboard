import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
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
            
            # 繪製區間趨勢圖
            with st.expander("覆蓋率區間趨勢"):
                # 計算每日的覆蓋率統計
                daily_stats = filtered_coverage.groupby('date').agg({
                    'coverage_percentage': ['mean', 'min', 'max']
                }).reset_index()
                daily_stats.columns = ['date', 'mean', 'min', 'max']
                
                # 創建區間趨勢圖
                fig3 = go.Figure()
                
                # 添加區間
                fig3.add_trace(go.Scatter(
                    x=daily_stats['date'],
                    y=daily_stats['max'],
                    fill=None,
                    mode='lines',
                    line_color='rgba(0,100,80,0.2)',
                    name='最高覆蓋率'
                ))
                
                fig3.add_trace(go.Scatter(
                    x=daily_stats['date'],
                    y=daily_stats['min'],
                    fill='tonexty',
                    mode='lines',
                    line_color='rgba(0,100,80,0.2)',
                    name='最低覆蓋率'
                ))
                
                # 添加平均線
                fig3.add_trace(go.Scatter(
                    x=daily_stats['date'],
                    y=daily_stats['mean'],
                    mode='lines',
                    line_color='rgb(0,100,80)',
                    name='平均覆蓋率'
                ))
                
                # 更新布局
                fig3.update_layout(
                    title='每日覆蓋率區間趨勢',
                    xaxis_title='日期',
                    yaxis_title='覆蓋率 (%)',
                    hovermode='x unified',
                    showlegend=True
                )
                
                st.plotly_chart(fig3, use_container_width=True)
            
            with st.expander("覆蓋率熱力圖"):
                # 重新組織數據為矩陣形式
                pivot_data = filtered_coverage.pivot(
                    index='date',
                    columns='module_name',
                    values='coverage_percentage'
                )
                
                # 創建熱力圖
                fig4 = go.Figure(data=go.Heatmap(
                    z=pivot_data.values,
                    x=pivot_data.columns,
                    y=pivot_data.index,
                    colorscale='RdYlGn',  # 紅黃綠配色
                    zmin=0,
                    zmax=100
                ))
                
                # 更新布局
                fig4.update_layout(
                    title='模組覆蓋率熱力圖',
                    xaxis_title='模組名稱',
                    yaxis_title='日期',
                    height=600
                )
                
                st.plotly_chart(fig4, use_container_width=True)
            
            with st.expander("週期性分析"):
                # 添加時間維度選擇
                col1, col2 = st.columns(2)
                with col1:
                    time_unit = st.selectbox(
                        "選擇時間維度",
                        ["週", "月"],
                        key="time_unit"
                    )
                with col2:
                    value_type = st.selectbox(
                        "選擇數值類型",
                        ["平均值", "期末值"],
                        key="value_type"
                    )
                
                # 根據選擇的時間維度進行數據重組
                filtered_coverage_period = filtered_coverage.copy()
                if time_unit == "週":
                    filtered_coverage_period['period'] = filtered_coverage_period['date'].dt.strftime('%Y-W%U')
                else:
                    filtered_coverage_period['period'] = filtered_coverage_period['date'].dt.strftime('%Y-%m')
                
                # 根據選擇的數值類型計算數據
                if value_type == "平均值":
                    period_data = filtered_coverage_period.groupby(['period', 'module_name'])['coverage_percentage'].mean().reset_index()
                else:
                    # 計算每個週期的最後一天數據
                    period_last_date = filtered_coverage_period.groupby(['period', 'module_name']).agg({
                        'date': 'max',
                        'coverage_percentage': 'last'
                    }).reset_index()
                    period_data = period_last_date[['period', 'module_name', 'coverage_percentage']]
                
                # 設定 y 軸標籤
                y_axis_label = '覆蓋率 (%)'
                
                # 創建週期性趨勢圖
                fig_period = px.line(
                    period_data,
                    x='period',
                    y='coverage_percentage',
                    color='module_name',
                    title=f'模組覆蓋率{time_unit}度趨勢 ({value_type})',
                    labels={
                        'period': f'{time_unit}份',
                        'coverage_percentage': y_axis_label,
                        'module_name': '模組名稱'
                    }
                )
                
                # 更新布局
                fig_period.update_layout(
                    xaxis_title=f'{time_unit}份',
                    yaxis_title=y_axis_label,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_period, use_container_width=True)
                
                # 顯示週期性統計摘要
                value_description = "平均" if value_type == "平均值" else "期末"
                period_stats = period_data.groupby('module_name').agg({
                    'coverage_percentage': ['mean', 'std', 'min', 'max']
                }).round(2)
                period_stats.columns = [f'{value_description}覆蓋率平均', '標準差', '最低覆蓋率', '最高覆蓋率']
                st.dataframe(period_stats)
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
            
            # 創建子標籤頁
            wut_tab1, wut_tab2, wut_tab3, wut_tab4 = st.tabs([
                "每日分析", 
                "累積趨勢分析",
                "失敗原因分析",
                "時間分布分析"
            ])
            
            with wut_tab1:
                # 計算每日各類型的數量
                daily_counts = filtered_preflight.groupby(['date', 'type']).size().unstack(fill_value=0)
                
                # 確保所有類型都存在
                for col in ['build_fail', 'wut_fail', 'pass']:
                    if col not in daily_counts.columns:
                        daily_counts[col] = 0
                
                # 生成堆疊長條圖
                fig = px.bar(
                    daily_counts,
                    title=f'{project} Preflight WUT 每日測試結果',
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
                    legend_title='測試結果',
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with wut_tab2:
                # 創建時間維度選擇器
                time_unit = st.selectbox(
                    "選擇時間維度",
                    ["日", "週", "月"],
                    key="wut_time_unit"
                )
                
                # 根據選擇的時間維度進行數據重組
                if time_unit == "週":
                    filtered_preflight['period'] = filtered_preflight['date'].dt.strftime('%Y-W%U')
                elif time_unit == "月":
                    filtered_preflight['period'] = filtered_preflight['date'].dt.strftime('%Y-%m')
                else:
                    filtered_preflight['period'] = filtered_preflight['date'].dt.strftime('%Y-%m-%d')
                
                # 計算累積數據
                cumulative_data = filtered_preflight.groupby(['period', 'type']).size().unstack(fill_value=0).cumsum()
                
                # 確保所有類型都存在
                for col in ['build_fail', 'wut_fail', 'pass']:
                    if col not in cumulative_data.columns:
                        cumulative_data[col] = 0
                
                # 創建累積面積圖
                fig_cum = go.Figure()
                
                # 添加各類型的累積面積
                fig_cum.add_trace(go.Scatter(
                    x=cumulative_data.index,
                    y=cumulative_data['pass'],
                    name='通過',
                    fill='tonexty',
                    mode='lines',
                    line=dict(color='#4CAF50')
                ))
                
                fig_cum.add_trace(go.Scatter(
                    x=cumulative_data.index,
                    y=cumulative_data['wut_fail'] + cumulative_data['pass'],
                    name='WUT失敗',
                    fill='tonexty',
                    mode='lines',
                    line=dict(color='#FFD740')
                ))
                
                fig_cum.add_trace(go.Scatter(
                    x=cumulative_data.index,
                    y=cumulative_data['build_fail'] + cumulative_data['wut_fail'] + cumulative_data['pass'],
                    name='建置失敗',
                    fill='tonexty',
                    mode='lines',
                    line=dict(color='#FF5252')
                ))
                
                # 更新布局
                fig_cum.update_layout(
                    title=f'Preflight WUT {time_unit}度累積趨勢',
                    xaxis_title=f'{time_unit}份',
                    yaxis_title='累積測試次數',
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_cum, use_container_width=True)
                
                # 計算成功率趨勢
                period_total = filtered_preflight.groupby('period').size()
                period_success = filtered_preflight[filtered_preflight['type'] == 'pass'].groupby('period').size()
                success_rate = (period_success / period_total * 100).fillna(0)
                
                # 創建成功率趨勢圖
                fig_rate = go.Figure()
                
                fig_rate.add_trace(go.Scatter(
                    x=success_rate.index,
                    y=success_rate.values,
                    mode='lines+markers',
                    name='成功率',
                    line=dict(color='#2196F3'),
                    marker=dict(size=8)
                ))
                
                # 添加目標線（80%）
                fig_rate.add_shape(
                    type="line",
                    x0=success_rate.index[0],
                    x1=success_rate.index[-1],
                    y0=80,
                    y1=80,
                    line=dict(
                        color="red",
                        width=2,
                        dash="dash",
                    )
                )
                
                # 更新布局
                fig_rate.update_layout(
                    title=f'Preflight WUT {time_unit}度成功率趨勢',
                    xaxis_title=f'{time_unit}份',
                    yaxis_title='成功率 (%)',
                    yaxis=dict(range=[0, 100]),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_rate, use_container_width=True)
                
                # 計算失敗率趨勢
                total_by_period = filtered_preflight.groupby('period').size()
                build_fail_by_period = filtered_preflight[filtered_preflight['type'] == 'build_fail'].groupby('period').size()
                wut_fail_by_period = filtered_preflight[filtered_preflight['type'] == 'wut_fail'].groupby('period').size()
                
                build_fail_rate = (build_fail_by_period / total_by_period * 100).fillna(0)
                wut_fail_rate = (wut_fail_by_period / total_by_period * 100).fillna(0)
                
                # 創建失敗率趨勢圖
                fig_fail_rate = go.Figure()
                
                # 添加建置失敗率曲線
                fig_fail_rate.add_trace(go.Scatter(
                    x=build_fail_rate.index,
                    y=build_fail_rate.values,
                    mode='lines+markers',
                    name='建置失敗率',
                    line=dict(color='#FF5252'),
                    marker=dict(size=8)
                ))
                
                # 添加WUT失敗率曲線
                fig_fail_rate.add_trace(go.Scatter(
                    x=wut_fail_rate.index,
                    y=wut_fail_rate.values,
                    mode='lines+markers',
                    name='WUT失敗率',
                    line=dict(color='#FFD740'),
                    marker=dict(size=8)
                ))
                
                # 更新布局
                fig_fail_rate.update_layout(
                    title=f'Preflight WUT {time_unit}度失敗率趨勢',
                    xaxis_title=f'{time_unit}份',
                    yaxis_title='失敗率 (%)',
                    yaxis=dict(range=[0, 100]),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_fail_rate, use_container_width=True)
            
            with wut_tab3:
                # 創建失敗原因分析圖表
                fail_data = filtered_preflight[filtered_preflight['type'] != 'pass'].copy()
                
                if len(fail_data) > 0:
                    # 計算每種失敗類型的數量
                    fail_counts = fail_data['type'].value_counts()
                    
                    # 創建圓餅圖
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=fail_counts.index,
                        values=fail_counts.values,
                        hole=.3,
                        marker_colors=['#FF5252', '#FFD740']
                    )])
                    
                    fig_pie.update_layout(
                        title='失敗原因分布',
                        showlegend=True
                    )
                    
                    # 顯示圓餅圖
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                    # 計算每日失敗比例趨勢
                    daily_fails = fail_data.groupby(['date', 'type']).size().unstack(fill_value=0)
                    daily_fails_pct = daily_fails.div(daily_fails.sum(axis=1), axis=0) * 100
                    
                    # 創建堆疊面積圖
                    fig_trend = go.Figure()
                    
                    for fail_type in daily_fails_pct.columns:
                        fig_trend.add_trace(go.Scatter(
                            x=daily_fails_pct.index,
                            y=daily_fails_pct[fail_type],
                            name=fail_type,
                            stackgroup='one',
                            line=dict(width=0.5),
                            hovertemplate='%{y:.1f}%'
                        ))
                    
                    fig_trend.update_layout(
                        title='每日失敗原因分布趨勢',
                        xaxis_title='日期',
                        yaxis_title='比例 (%)',
                        hovermode='x unified',
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig_trend, use_container_width=True)
                    
                else:
                    st.info("在選定的時間範圍內沒有失敗記錄")
            
            with wut_tab4:
                # 添加時間維度選擇
                time_dimension = st.selectbox(
                    "選擇時間維度",
                    ["小時分布", "星期分布"],
                    key="time_dimension"
                )
                
                if time_dimension == "小時分布":
                    # 提取小時資訊
                    filtered_preflight['hour'] = filtered_preflight['date'].dt.hour
                    time_data = filtered_preflight.groupby(['hour', 'type']).size().unstack(fill_value=0)
                    
                    # 創建熱力圖數據
                    hours = list(range(24))
                    types = ['pass', 'build_fail', 'wut_fail']
                    heatmap_data = np.zeros((24, len(types)))
                    
                    for i, hour in enumerate(hours):
                        if hour in time_data.index:
                            for j, type_name in enumerate(types):
                                if type_name in time_data.columns:
                                    heatmap_data[i, j] = time_data.loc[hour, type_name]
                    
                    # 創建熱力圖
                    fig_heatmap = go.Figure(data=go.Heatmap(
                        z=heatmap_data,
                        x=types,
                        y=[f"{h:02d}:00" for h in hours],
                        colorscale='YlOrRd',
                        hoverongaps=False
                    ))
                    
                    fig_heatmap.update_layout(
                        title='每小時測試結果分布',
                        xaxis_title='測試結果',
                        yaxis_title='時間',
                        height=800
                    )
                    
                else:  # 星期分布
                    # 提取星期資訊
                    filtered_preflight['weekday'] = filtered_preflight['date'].dt.day_name()
                    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    weekday_map = {
                        'Monday': '週一',
                        'Tuesday': '週二',
                        'Wednesday': '週三',
                        'Thursday': '週四',
                        'Friday': '週五',
                        'Saturday': '週六',
                        'Sunday': '週日'
                    }
                    filtered_preflight['weekday_zh'] = filtered_preflight['weekday'].map(weekday_map)
                    
                    # 計算每個星期幾的數據
                    weekday_data = filtered_preflight.groupby(['weekday_zh', 'type']).size().unstack(fill_value=0)
                    weekday_data = weekday_data.reindex([weekday_map[day] for day in weekday_order])
                    
                    # 創建熱力圖
                    fig_heatmap = go.Figure(data=go.Heatmap(
                        z=weekday_data.values,
                        x=['通過', '建置失敗', 'WUT失敗'],
                        y=weekday_data.index,
                        colorscale='YlOrRd',
                        hoverongaps=False
                    ))
                    
                    fig_heatmap.update_layout(
                        title='每週測試結果分布',
                        xaxis_title='測試結果',
                        yaxis_title='星期',
                        height=400
                    )
                
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # 添加統計摘要
                with st.expander("查看時間分布統計"):
                    if time_dimension == "小時分布":
                        hour_stats = filtered_preflight.groupby('hour').size()
                        peak_hour = hour_stats.idxmax()
                        quiet_hour = hour_stats.idxmin()
                        
                        st.markdown(f"""
                            ### 時間分布統計
                            - 最活躍時段：{peak_hour:02d}:00 ({hour_stats[peak_hour]} 次測試)
                            - 最不活躍時段：{quiet_hour:02d}:00 ({hour_stats[quiet_hour]} 次測試)
                            - 平均每小時測試次數：{hour_stats.mean():.1f}
                        """)
                    else:
                        weekday_stats = filtered_preflight.groupby('weekday_zh').size()
                        peak_day = weekday_stats.idxmax()
                        quiet_day = weekday_stats.idxmin()
                        
                        st.markdown(f"""
                            - 最活躍星期：{peak_day} ({weekday_stats[peak_day]} 次測試)
                            - 最不活躍星期：{quiet_day} ({weekday_stats[quiet_day]} 次測試)
                            - 平均每天測試次數：{weekday_stats.mean():.1f}
                        """)
            
            # 顯示統計摘要
            with st.expander("查看整體統計摘要"):
                total_tests = len(filtered_preflight)
                pass_count = len(filtered_preflight[filtered_preflight['type'] == 'pass'])
                build_fail_count = len(filtered_preflight[filtered_preflight['type'] == 'build_fail'])
                wut_fail_count = len(filtered_preflight[filtered_preflight['type'] == 'wut_fail'])
                pass_rate = (pass_count / total_tests * 100) if total_tests > 0 else 0
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "總測試次數",
                        f"{total_tests:,}",
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        "通過次數",
                        f"{pass_count:,}",
                        delta=f"{pass_rate:.1f}%"
                    )
                
                with col3:
                    st.metric(
                        "建置失敗",
                        f"{build_fail_count:,}",
                        delta=f"{(build_fail_count/total_tests*100):.1f}%" if total_tests > 0 else "0%"
                    )
                
                with col4:
                    st.metric(
                        "WUT失敗",
                        f"{wut_fail_count:,}",
                        delta=f"{(wut_fail_count/total_tests*100):.1f}%" if total_tests > 0 else "0%"
                    )
    
    # 返回主頁面按鈕
    if st.button('返回主頁面'):
        st.switch_page("pages/main.py")

if __name__ == '__main__':
    show_project_page()
