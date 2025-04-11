# Software Quality Dashboard 架構說明

## 主要功能
- 軟體品質監控儀表板
- 追蹤多專案的品質指標
- 提供測試覆蓋率、缺陷統計和preflight測試結果分析

## 核心模組
1. **主程式 (app.py)**
   - 初始化設定 (logging, 頁面配置)
   - 資料載入與處理
   - 使用者介面 (Streamlit)
   - 圖表生成 (Plotly)

2. **資料處理函式**
   - load_preflight_wut_data(): 載入preflight測試結果
   - load_module_coverage(): 載入模組覆蓋率數據
   - load_all_projects(): 載入所有專案數據

3. **工具函式 (utils/)**
   - quality_metrics.py: 計算品質分數
   - project_config.py: 載入專案配置

## 資料流程
1. 從CSV檔案載入專案數據
2. 應用使用者篩選條件
3. 計算各種品質指標
4. 使用Plotly生成互動式圖表
5. 透過Streamlit顯示儀表板

## 關鍵技術
- Streamlit: Web儀表板框架
- Pandas: 資料處理與分析
- Plotly: 互動式圖表
- Logging: 系統日誌記錄
