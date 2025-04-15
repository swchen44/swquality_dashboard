# Streamlit 多頁面應用入口
import streamlit as st
import logging
import logging.handlers
import os

# 基本配置
st.set_page_config(
    page_title="Software Quality Dashboard",
    page_icon="📊",
    layout="wide"
)

# 日誌配置
def setup_logging():
    """配置日誌系統"""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    os.makedirs('logs', exist_ok=True)
    
    file_handler = logging.handlers.TimedRotatingFileHandler(
        'logs/app.log', when='midnight', backupCount=7, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logging.info("日誌系統初始化完成")

# 主入口
def main():
    setup_logging()
    from pages.main import show_main_page
    show_main_page()

if __name__ == '__main__':
    main()
