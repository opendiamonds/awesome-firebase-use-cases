# 👨‍💻 開發者 SDLC 模板（Dev）

給開發者使用的 Firebase 工具，加速軟體開發生命週期中的各種流程。

---

## 📋 收錄範本

| 模板 | 說明 | Firebase 核心 | AI 整合 |
|------|------|--------------|---------|
| ci-cd-starter | Firebase CI/CD Starter：GitHub Actions 自動部署 | Hosting + Functions + GitHub Actions | Gemini Code Review |
| test-report | 自動化測試報告：Crashlytics + AI 異常趨勢分析 | Crashlytics + Analytics + Functions | Gemini Crash 分析 |
| api-doc-gen | API 文件生成器：Function code → OpenAPI doc | Functions + Firestore | Gemini 文件生成 |
| security-audit | 安全稽核自動化：異常行為偵測，即時告警 | App Check + Functions + FCM | Gemini 威脅偵測 |
| perf-monitor | 效能監控儀表板：AI 異常偵測，自動 Root Cause | Analytics + BigQuery + Functions | Gemini 效能分析 |
| env-manager | 多環境部署管理：Dev/Staging/Prod 一鍵切換 | Hosting + Functions + Environment Config | Gemini 部署建議 |
| lib-publisher | Library 發布管理：npm 發布 + CHANGELOG 生成 | Storage + Functions + npm | Gemini 版本相容性檢查 |
| changelog-bot | 自動 CHANGELOG：Commit 記錄 → 格式化的更新日誌 | GitHub API + Functions | Gemini CHANGELOG 生成 |

---

## 🚀 貢獻新規模板

新增開發者模板的方式：

1. 在本資料夾建立新子資料夾：`[template-name]/`
2. 放入完整的 Firebase 程式碼
3. **必須包含詳細的 `README.md`（見主目錄文件規範）**
4. PR 標題格式：`[dev] 新增 [template-name]`

---

## 📖 文件撰寫規範

每個開發者模板的 README.md 必須包含：

- [ ] 場景介紹（這個 Template 解決什麼痛點）
- [ ] 前置需求（Firebase 專案、GitHub repo、相關工具）
- [ ] 安裝步驟（Step-by-step）
- [ ] 功能說明（截圖 + 操作方式）
- [ ] GitHub Actions / CI/CD 設定方式
- [ ] AI 整合方式（Gemini API 設定）
- [ ] 客製化指南
- [ ] 部署教學
