import streamlit as st
import pandas as pd
import os
import logging
from utils.project_config import load_project_config
from utils.quality_metrics import load_module_coverage

def show_project_details(project_name):
    st.set_page_config(
        page_title=f"{project_name} 專案詳情",
        layout="wide"
    )
    
    st.title(f"{project_name} 專案詳情")
    
    # 載入專案配置
    config = load_project_config(project_name)
    
    if config:
        if 'description' in config and config['description']:
            st.markdown("## 專案說明")
            st.markdown(config['description'])
        
        # 顯示模組覆蓋率
        st.markdown("## 模組覆蓋率")
        module_df = load_module_coverage(project_name)
        if module_df is not None:
            # 計算總覆蓋率
            totals = module_df.groupby('date').agg({
                'covered_line_number': 'sum',
                'total_line_number': 'sum'
            }).reset_index()
            totals['total_coverage'] = (totals['covered_line_number'] / totals['total_line_number'] * 100).round(2)
            
            # 顯示最新覆蓋率
            latest = totals.sort_values('date').iloc[-1]
            st.metric("最新總覆蓋率", f"{latest['total_coverage']}%")
            
            # 顯示模組覆蓋率表格
            latest_modules = module_df.sort_values('date').groupby('module_name').last().reset_index()
            st.dataframe(
                latest_modules[['module_name', 'coverage_percentage']].sort_values('coverage_percentage', ascending=False),
                column_config={
                    "module_name": "模組名稱",
                    "coverage_percentage": st.column_config.NumberColumn(
                        "覆蓋率(%)",
                        format="%.1f%%"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.warning("找不到模組覆蓋率資料")
    else:
        st.error("找不到專案配置")

def main():
    # 從查詢參數取得專案名稱
    project_name = st.query_params.get("project")
    if project_name:
        show_project_details(project_name)
    else:
        st.error("請從儀表板選擇專案")

if __name__ == '__main__':
    main()
