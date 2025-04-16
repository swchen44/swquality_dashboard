# 軟體品質儀表板 (Software Quality Dashboard)

## 專案簡介
基於 Streamlit 開發的軟體品質監控系統，協助團隊即時追蹤、分析並改善軟體品質指標。整合測試結果、覆蓋率和缺陷追蹤，提供全方位的品質監控視角。

## 主要特色
- 📊 即時品質評分系統 (A-E 五級制)
- 📈 多專案品質指標比較與趨勢分析
- 🔍 模組級別的代碼覆蓋率追蹤
- 🚦 Preflight 與 WUT 測試結果監控
- 🎯 客製化品質閾值和警報機制
- 📱 響應式設計，支援各種設備訪問
- 🌓 深色/淺色主題切換
- 📥 數據導出與報告生成

## 技術架構
- **前端框架**: Streamlit
- **數據處理**: Pandas, NumPy
- **視覺化**: Plotly, Matplotlib
- **測試框架**: Pytest
- **版本控制**: Git
- **部署選項**: Docker, Cloud Platform

## 快速開始

### 環境要求
- Python 3.8+
- pip 包管理器
- Git (選用)

### 安裝步驟
```bash
# 1. 克隆專案
git clone https://github.com/your-username/swquality_dashboard.git
cd swquality_dashboard

# 2. 建立虛擬環境 (推薦)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate   # Windows

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 啟動應用
streamlit run app.py
```

## 專案結構
```
swquality_dashboard/
├── app.py              # 應用程式入口
├── data/              # 專案資料目錄
│   └── project*/      # 各專案資料
│       ├── config.json           # 專案配置
│       ├── module_coverage.csv   # 模組覆蓋率數據
│       ├── preflight_wut_result.csv  # 測試結果
│       └── sample_qa_dashboard.csv   # 品質指標數據
├── utils/             # 工具函數
│   ├── data_generator.py    # 測試數據生成器
│   ├── project_config.py    # 專案配置管理
│   └── quality_metrics.py   # 品質計算模組
├── views/             # 頁面視圖
├── requirements.txt   # 依賴包清單
└── README.md         # 專案說明
```

## 配置說明
每個專案的 `config.json` 支援以下設定：
- 品質指標閾值
- 評分權重設定
- 專案描述文件
- 客製化頁面路由

## 開發指南
1. Fork 本專案到您的 GitHub 帳號
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 貢獻指南
- 遵循 Python PEP 8 編碼規範
- 添加適當的單元測試
- 更新相關文檔
- 保持向後相容性

## 版本發布
使用語義化版本 2.0.0 (Semantic Versioning)
- MAJOR 版本：不相容的 API 修改
- MINOR 版本：向下相容的功能性新增
- PATCH 版本：向下相容的問題修正

## 授權協議
本專案採用 [MIT License](LICENSE)
