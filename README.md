# 軟體品質儀表板 (Software Quality Dashboard)

## 專案簡介
Streamlit 開發的軟體品質監控系統，幫助 QA、PM 與開發團隊追蹤測試與缺陷指標。資料來源為本地 CSV 檔案，支援多專案比較分析。

## 功能亮點
- 📊 即時品質評分 (A-E 五級制)
- 📈 多專案趨勢比較
- 🔍 互動式篩選控制
- 🎨 亮色/暗色主題切換
- 📥 資料匯出功能

## 使用技術
- **前端框架**: Streamlit
- **視覺化**: Plotly, Matplotlib
- **資料處理**: Pandas, NumPy
- **部署**: Docker (可選)

## 專案結構
```
swquality_dashboard/
├── app.py                # 主程式
├── data/                 # 專案資料
│   └── project[1-10]/    
│       ├── config.json   # 專案設定
│       └── sample_qa_dashboard.csv
├── utils/
│   ├── data_generator.py # 測試資料生成
│   ├── project_config.py # 配置載入
│   └── quality_metrics.py # 評分計算
└── README.md
```

## 快速啟動
```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動應用
streamlit run app.py
```

## 測試資料
專案已包含 10 個測試專案，每個專案包含：
- 自動生成的 QA 指標數據
- 完整專案配置 (含說明文件)
- 預設品質閾值設定

範例專案說明格式：
```markdown
## Project1 專案說明
- **技術棧**: Python, AWS
- [需求文件](https://example.com)
- 里程碑: 2025/06/30 上線
```

## 可擴充整合
- 🔌 JIRA 缺陷追蹤 (需 API 金鑰)
- 📊 GitLab/GitHub 整合
- 🛠️ 自訂指標計算模組

## 如何貢獻
1. Fork 本專案
2. 建立新分支 (`git checkout -b feature/your-feature`)
3. 提交修改 (`git commit -m 'Add some feature'`)
4. 推送分支 (`git push origin feature/your-feature`)
5. 建立 Pull Request

## 授權
[MIT License](LICENSE)
