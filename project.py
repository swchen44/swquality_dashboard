import streamlit as st
import pandas as pd
from utils.project_config import load_project_config

def show_project_details(project_name):
    st.set_page_config(
        page_title=f"{project_name} 專案詳情",
        layout="wide"
    )
    
    st.title(f"{project_name} 專案詳情")
    
    # 載入專案配置
    config = load_project_config(project_name)
    
    if config and 'description' in config:
        st.markdown("## 專案說明")
        st.markdown(config['description'])
    
    # TODO: 後續添加 module coverage 顯示功能

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        show_project_details(sys.argv[1])
    else:
        st.error("請指定專案名稱")
