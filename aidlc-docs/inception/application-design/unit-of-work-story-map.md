# Unit of Work — Story Map

> Maps Cloud-360 user stories to development units.  
> Focus: **A1 / A2 / A4 / A5 / J** (developed). Other stories listed as unassigned.

## 中文版

### 1. 已開發 Story → Unit

| Story | 標題 | Unit ID | Unit 名稱 | Construction 追溯 | 開發狀態 |
|---|---|---|---|---|---|
| **J1** | 統一登入入口與安全憑證驗證 | `U-J` | Identity & RBAC | `plans/role-permission-*.md`、`j/code/` | ✅ Core（❌ MFA／重設密碼） |
| **J2** | 基於角色細項權限的頁面可見性控制 | `U-J` | Identity & RBAC | 同上 | ✅ Core |
| **J3** | 管理員使用者管理（指派／啟停用／刪除／核准） | `U-J` | Identity & RBAC | 同上 | ✅ 指派／啟停用；❌ 核准申請、刪除 |
| **J4** | 細粒度角色-故事權限矩陣編輯與預設還原 | `U-J` | Identity & RBAC | 同上 | ✅ Core |
| **J5** | 自助註冊、角色介紹與授權申請（無預設角色） | `U-J` | Identity & RBAC | 同上 | ❌ 未做（現況 register→Developer） |
| **A1** | 自然語言轉架構與草圖產出 | `U-A1` | Architecture Design Generation | `a1/` + `plans/a1-*.md` | ✅ Code；待 E2E |
| **A2** | AI + draw.io 畫布協同編輯 | `U-A2` | Canvas Collaborative Editing | （目錄待補） | 🔄 核心完成；AC 部分缺 |
| **A4** | 重整後仍記得對話與上次開啟的架構圖 | `U-A4` | Chat & Last-Opened Persistence | `a4/` + `plans/a4-*.md` | ✅ Code；待 E2E |
| **A5** | 跨使用者架構圖分享與即時協同連線 | `U-A5` | Diagram Sharing & Real-time Collab | （目錄待補） | 🔄 分享＋WS XML；游標缺 |

### 2. Unit → Stories（反向）

| Unit ID | Stories | 一句話 |
|---|---|---|
| `U-J` | J1, J2, J3, J4, J5 | 身分、角色、細項矩陣、Admin UI、註冊授權閘門 |
| `U-A1` | A1 | NL → XML 產圖 |
| `U-A2` | A2 | 畫布編輯、存檔、多圖、局部 AI |
| `U-A4` | A4 | 聊天持久化、last-opened、bootstrap |
| `U-A5` | A5 | 分享、WebSocket 共編、連線狀態 |

### 3. 產品權限欄 vs 開發 Unit（重要）

RBAC Admin 矩陣（產品語意）把 **A1／A2／A4 合併為「架構圖生成」**，儲存時三者同步；**A5** 的分享／共編能力仍掛在架構圖 ACL 與 can_edit／view／review 行為上。

| 產品矩陣欄 | 對應開發 Units | 說明 |
|---|---|---|
| 架構圖生成（A1＝A2＝A4） | `U-A1` + `U-A2` + `U-A4` | 權限旗標共用；程式與 AIDLC unit 文件仍分開 |
| （共編／分享行為） | `U-A5` | 分享與 WS；細項不另開 A5 欄時仍受架構圖 V／E／R 約束 |
| 使用者設定／細項設定（J） | `U-J` | 矩陣 UI 僅 J3a／J3b；不含 J1／J5 |

### 4. A2／A5 AC 與 Unit 歸屬（避免重複認列）

| AC／場景（摘自 aidlc-state） | 歸屬 Unit |
|---|---|
| AI 局部編輯、連線保留、存 DB、多檔切換 | `U-A2` |
| 進入工作區還原上次圖＋聊天 | `U-A4`（銜接 U-A2 diagram） |
| 分享給其他使用者 | `U-A5` |
| 多人即時共編（XML 同步）、協作狀態列 | `U-A5` |
| 多人游標可見 | `U-A5`（未做） |
| AI 修改歷史＋一鍵 Undo | `U-A2`（未做） |
| 框選節點群組後送 AI | `U-A2`（部分） |

### 5. 尚未指派 Unit 的 Stories

以下尚無 Construction unit（本 map 標記 `—`）：

| Stories | Pillar |
|---|---|
| A3 | A — Well-Architected |
| B1, B2, B3 | B — 跨雲選型 |
| C1, C2, C3 | C — FinOps |
| D1, D2, D3 | D — IaC |
| E1, E2, E3 | E — 維運優化 |
| F1, F2, F3 | F — 多雲維運 |
| G1, G2, G3 | G — 安全態勢 |
| H1, H2, H3 | H — MCP／Skill |

擴充時：新增 `U-*` 於 `unit-of-work.md`，更新本表與 `unit-of-work-dependency.md`。

### 6. 覆蓋檢查

- [x] A1, A2, A4, A5, J1–J5 皆已指派且僅指派一個開發 unit  
- [x] 無已開發 story 遺漏  
- [x] 產品權限合併（A1＝A2＝A4）已在 §3 註記，避免與 unit 邊界混淆  

---

## English Version

### 1. Developed story → unit

| Story | Unit ID | Status |
|---|---|---|
| J1–J4 | `U-J` | Core done |
| J5 | `U-J` | Not done (register still assigns Developer) |
| A1 | `U-A1` | Code done; E2E pending |
| A2 | `U-A2` | Core done; AC gaps |
| A4 | `U-A4` | Code done; E2E pending |
| A5 | `U-A5` | Share + WS XML done; cursors pending |

### 2. Unit → stories

| Unit ID | Stories |
|---|---|
| `U-J` | J1, J2, J3, J4, J5 |
| `U-A1` | A1 |
| `U-A2` | A2 |
| `U-A4` | A4 |
| `U-A5` | A5 |

### 3. Product permission column vs development units

Admin matrix merges **A1 = A2 = A4** as “Architecture generation”; development units remain separate (`U-A1`, `U-A2`, `U-A4`). Sharing/realtime behaviour is `U-A5`, gated by architecture V/E/R.

### 4. AC ownership

| Scenario | Unit |
|---|---|
| Partial AI edit, save, multi-diagram | `U-A2` |
| Restore last diagram + chat | `U-A4` |
| Share, WS XML sync, collab badge | `U-A5` |
| Multi-user cursors (missing) | `U-A5` |
| AI undo history (missing) | `U-A2` |

### 5. Unassigned

A3, B1–B3, C1–C3, D1–D3, E1–E3, F1–F3, G1–G3, H1–H3 → no unit yet.

### 6. Coverage

- [x] A1, A2, A4, A5, J1–J5 each map to exactly one development unit
- [x] No developed story left unmapped  
- [x] Permission merge A1=A2=A4 documented in §3  
