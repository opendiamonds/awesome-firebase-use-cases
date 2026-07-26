-- =============================================================================
-- Cloud-360 Full Schema + RBAC Seed
-- Branch: luojingting/feat/role-permission-redesign（＋後續 A3 DDL 增量）
--
-- 單一腳本涵蓋：
--   A) 核心：users / user_diagrams / diagram_shares（架構圖儲存與分享）
--   B) A4：user_diagram_chats（聊天持久化）+ users.last_opened_diagram_id
--   E) A3：architecture_reviews（評核結果）+ wa_lenses（Offline Lens 現行標準）
--   C) RBAC：role_permissions + 預設矩陣（308 列）
--   D) 預設管理員：admin / admin123（Platform_Admin）
--
-- 執行（新環境可只跑這支）：
--   psql "$DATABASE_URL" -f schema_rbac.sql
--
-- 注意：
--   - 表使用 IF NOT EXISTS，可重複執行
--   - role_permissions 會 DELETE 後重播預設（Admin UI 調過請先備份）
--   - 不覆寫既有 admin 密碼
--   - 矩陣來源：aidlc-docs/construction/plans/role-permission-design.md
--   - A3：評核內容在 architecture_reviews；可編輯 Lens 在 wa_lenses.body_json
-- =============================================================================

BEGIN;

-- ###########################################################################
-- A) Core: users + architecture diagrams + shares
-- ###########################################################################

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR NOT NULL,
  password_hash VARCHAR NOT NULL,
  role VARCHAR NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  last_opened_diagram_id INTEGER
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username);
CREATE INDEX IF NOT EXISTS ix_users_id ON users (id);

CREATE TABLE IF NOT EXISTS user_diagrams (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users (id),
  title VARCHAR NOT NULL DEFAULT '未命名架構圖',
  xml_data TEXT NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_user_diagrams_id ON user_diagrams (id);

-- 延後加 FK，避免 users ↔ user_diagrams 循環建立問題
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'fk_users_last_opened_diagram'
  ) THEN
    ALTER TABLE users
      ADD CONSTRAINT fk_users_last_opened_diagram
      FOREIGN KEY (last_opened_diagram_id)
      REFERENCES user_diagrams (id)
      ON DELETE SET NULL;
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS diagram_shares (
  user_id INTEGER NOT NULL REFERENCES users (id),
  diagram_id INTEGER NOT NULL REFERENCES user_diagrams (id),
  PRIMARY KEY (user_id, diagram_id)
);

COMMENT ON TABLE user_diagrams IS 'A2: per-user architecture diagram drafts (draw.io XML)';
COMMENT ON TABLE diagram_shares IS 'A2: many-to-many share ACL for diagrams';

-- ###########################################################################
-- B) A4: chat persistence per user × diagram
-- ###########################################################################

CREATE TABLE IF NOT EXISTS user_diagram_chats (
  user_id INTEGER NOT NULL REFERENCES users (id),
  diagram_id INTEGER NOT NULL REFERENCES user_diagrams (id) ON DELETE CASCADE,
  messages_json TEXT NOT NULL DEFAULT '[]',
  updated_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (user_id, diagram_id)
);

COMMENT ON TABLE user_diagram_chats IS 'A4: chat messages keyed by user × diagram';

-- ###########################################################################
-- E) A3: Well-Architected review persistence
--    對應 backend/models.py ArchitectureReview、database._ensure_a3_schema()
-- ###########################################################################

CREATE TABLE IF NOT EXISTS architecture_reviews (
  id SERIAL PRIMARY KEY,
  diagram_id INTEGER NOT NULL REFERENCES user_diagrams (id) ON DELETE CASCADE,
  created_by INTEGER NOT NULL REFERENCES users (id),
  provider VARCHAR(16) NOT NULL DEFAULT 'aws',
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  overall_score INTEGER,
  scores_json TEXT,
  findings_json TEXT DEFAULT '[]',
  suggestions_text TEXT,
  error_message TEXT,
  rule_pack_version VARCHAR(64),
  archived BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_architecture_reviews_diagram_id
  ON architecture_reviews (diagram_id);

CREATE INDEX IF NOT EXISTS ix_architecture_reviews_created_by
  ON architecture_reviews (created_by);

COMMENT ON TABLE architecture_reviews IS
  'A3: WA review rows — overall_score + scores_json (lens/heuristic) + findings_json + suggestions_text';
COMMENT ON COLUMN architecture_reviews.scores_json IS
  'JSON: source_of_truth, pillar_scores, risk_counts, lens, heuristic, findings_source, …';
COMMENT ON COLUMN architecture_reviews.findings_json IS
  'JSON array of findings (Lens HIGH/MEDIUM preferred; heuristic fallback on lens failure)';
COMMENT ON COLUMN architecture_reviews.status IS
  'pending | rules_complete | complete | rules_only | unsupported';

CREATE TABLE IF NOT EXISTS wa_lenses (
  id SERIAL PRIMARY KEY,
  lens_id VARCHAR(64) NOT NULL DEFAULT 'cloud360-core-mvp',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  body_json TEXT NOT NULL,
  updated_by INTEGER REFERENCES users (id),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_wa_lenses_lens_id ON wa_lenses (lens_id);
CREATE INDEX IF NOT EXISTS ix_wa_lenses_is_active ON wa_lenses (is_active);

COMMENT ON TABLE wa_lenses IS
  'A3: active Offline Custom Lens JSON edited by Security_Reviewer; reviews resolve DB-first then file fallback';
COMMENT ON COLUMN wa_lenses.body_json IS
  'Full Custom Lens JSON (schemaVersion 2021-11-01, five pillars)';

-- ###########################################################################
-- C) RBAC: role × story permissions (view / edit / review)
-- ###########################################################################

CREATE TABLE IF NOT EXISTS role_permissions (
  role        VARCHAR(64)  NOT NULL,
  story_id    VARCHAR(16)  NOT NULL,
  can_view    BOOLEAN      NOT NULL DEFAULT FALSE,
  can_edit    BOOLEAN      NOT NULL DEFAULT FALSE,
  can_review  BOOLEAN      NOT NULL DEFAULT FALSE,
  updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
  updated_by  VARCHAR(128),
  PRIMARY KEY (role, story_id)
);

CREATE INDEX IF NOT EXISTS idx_role_permissions_story
  ON role_permissions (story_id);

COMMENT ON TABLE role_permissions IS
  'RBAC: per-role per-story flags view/edit/review';

DELETE FROM role_permissions;

INSERT INTO role_permissions (role, story_id, can_view, can_edit, can_review) VALUES
  ('Project_Architect', 'A1', true, true, false),
  ('Developer', 'A1', true, true, false),
  ('Project_Editor', 'A1', true, true, false),
  ('Project_Admin', 'A1', true, false, false),
  ('FinOps_Analyst', 'A1', true, false, false),
  ('SRE', 'A1', true, false, false),
  ('Ops_Lead', 'A1', true, false, false),
  ('Platform_Engineer', 'A1', true, false, false),
  ('Security_Reviewer', 'A1', true, false, false),
  ('Platform_Admin', 'A1', true, false, false),
  ('Platform_Owner', 'A1', true, false, false),
  ('Project_Architect', 'A2', true, true, false),
  ('Developer', 'A2', true, true, false),
  ('Project_Editor', 'A2', true, true, false),
  ('Project_Admin', 'A2', true, false, false),
  ('FinOps_Analyst', 'A2', true, false, false),
  ('SRE', 'A2', true, false, false),
  ('Ops_Lead', 'A2', true, false, false),
  ('Platform_Engineer', 'A2', true, false, false),
  ('Security_Reviewer', 'A2', true, false, false),
  ('Platform_Admin', 'A2', true, false, false),
  ('Platform_Owner', 'A2', true, false, false),
  ('Project_Architect', 'A3', true, true, false),
  ('Developer', 'A3', true, false, false),
  ('Project_Editor', 'A3', true, true, false),
  ('Project_Admin', 'A3', true, false, false),
  ('FinOps_Analyst', 'A3', false, false, false),
  ('SRE', 'A3', true, false, false),
  ('Ops_Lead', 'A3', true, false, false),
  ('Platform_Engineer', 'A3', true, false, false),
  ('Security_Reviewer', 'A3', true, true, true),
  ('Platform_Admin', 'A3', true, false, false),
  ('Platform_Owner', 'A3', true, false, false),
  ('Project_Architect', 'A4', true, true, false),
  ('Developer', 'A4', true, true, false),
  ('Project_Editor', 'A4', true, true, false),
  ('Project_Admin', 'A4', true, false, false),
  ('FinOps_Analyst', 'A4', true, false, false),
  ('SRE', 'A4', true, false, false),
  ('Ops_Lead', 'A4', true, false, false),
  ('Platform_Engineer', 'A4', true, false, false),
  ('Security_Reviewer', 'A4', true, false, false),
  ('Platform_Admin', 'A4', true, false, false),
  ('Platform_Owner', 'A4', true, false, false),
  ('Project_Architect', 'B1', true, false, false),
  ('Developer', 'B1', true, false, false),
  ('Project_Editor', 'B1', true, false, false),
  ('Project_Admin', 'B1', true, true, false),
  ('FinOps_Analyst', 'B1', true, true, false),
  ('SRE', 'B1', true, false, false),
  ('Ops_Lead', 'B1', true, false, false),
  ('Platform_Engineer', 'B1', true, false, false),
  ('Security_Reviewer', 'B1', true, false, false),
  ('Platform_Admin', 'B1', true, false, false),
  ('Platform_Owner', 'B1', true, false, false),
  ('Project_Architect', 'B2', true, true, false),
  ('Developer', 'B2', true, false, false),
  ('Project_Editor', 'B2', true, false, false),
  ('Project_Admin', 'B2', true, false, false),
  ('FinOps_Analyst', 'B2', true, false, false),
  ('SRE', 'B2', true, false, false),
  ('Ops_Lead', 'B2', true, true, false),
  ('Platform_Engineer', 'B2', true, false, false),
  ('Security_Reviewer', 'B2', true, false, false),
  ('Platform_Admin', 'B2', true, false, false),
  ('Platform_Owner', 'B2', true, false, false),
  ('Project_Architect', 'B3', true, false, false),
  ('Developer', 'B3', true, false, false),
  ('Project_Editor', 'B3', true, false, false),
  ('Project_Admin', 'B3', true, true, false),
  ('FinOps_Analyst', 'B3', true, false, false),
  ('SRE', 'B3', true, false, false),
  ('Ops_Lead', 'B3', true, false, false),
  ('Platform_Engineer', 'B3', true, false, false),
  ('Security_Reviewer', 'B3', true, true, false),
  ('Platform_Admin', 'B3', true, false, false),
  ('Platform_Owner', 'B3', true, false, false),
  ('Project_Architect', 'C1', true, false, false),
  ('Developer', 'C1', false, false, false),
  ('Project_Editor', 'C1', true, false, false),
  ('Project_Admin', 'C1', true, false, false),
  ('FinOps_Analyst', 'C1', true, true, false),
  ('SRE', 'C1', true, false, false),
  ('Ops_Lead', 'C1', true, false, false),
  ('Platform_Engineer', 'C1', false, false, false),
  ('Security_Reviewer', 'C1', false, false, false),
  ('Platform_Admin', 'C1', true, false, false),
  ('Platform_Owner', 'C1', true, false, false),
  ('Project_Architect', 'C2', true, false, false),
  ('Developer', 'C2', false, false, false),
  ('Project_Editor', 'C2', true, false, false),
  ('Project_Admin', 'C2', true, false, false),
  ('FinOps_Analyst', 'C2', true, true, false),
  ('SRE', 'C2', true, true, false),
  ('Ops_Lead', 'C2', true, false, false),
  ('Platform_Engineer', 'C2', false, false, false),
  ('Security_Reviewer', 'C2', false, false, false),
  ('Platform_Admin', 'C2', true, false, false),
  ('Platform_Owner', 'C2', true, false, false),
  ('Project_Architect', 'C3', true, true, false),
  ('Developer', 'C3', false, false, false),
  ('Project_Editor', 'C3', true, false, false),
  ('Project_Admin', 'C3', true, false, false),
  ('FinOps_Analyst', 'C3', true, true, false),
  ('SRE', 'C3', true, false, false),
  ('Ops_Lead', 'C3', true, false, false),
  ('Platform_Engineer', 'C3', false, false, false),
  ('Security_Reviewer', 'C3', false, false, false),
  ('Platform_Admin', 'C3', true, false, false),
  ('Platform_Owner', 'C3', true, false, false),
  ('Project_Architect', 'D1', true, true, false),
  ('Developer', 'D1', true, true, false),
  ('Project_Editor', 'D1', true, false, false),
  ('Project_Admin', 'D1', true, false, false),
  ('FinOps_Analyst', 'D1', false, false, false),
  ('SRE', 'D1', true, false, false),
  ('Ops_Lead', 'D1', true, false, false),
  ('Platform_Engineer', 'D1', true, true, false),
  ('Security_Reviewer', 'D1', true, false, false),
  ('Platform_Admin', 'D1', true, false, false),
  ('Platform_Owner', 'D1', true, false, false),
  ('Project_Architect', 'D2', true, false, false),
  ('Developer', 'D2', true, false, false),
  ('Project_Editor', 'D2', true, false, false),
  ('Project_Admin', 'D2', true, false, false),
  ('FinOps_Analyst', 'D2', false, false, false),
  ('SRE', 'D2', true, false, false),
  ('Ops_Lead', 'D2', true, false, false),
  ('Platform_Engineer', 'D2', true, true, false),
  ('Security_Reviewer', 'D2', true, true, false),
  ('Platform_Admin', 'D2', true, false, false),
  ('Platform_Owner', 'D2', true, false, false),
  ('Project_Architect', 'D3', true, false, false),
  ('Developer', 'D3', true, true, false),
  ('Project_Editor', 'D3', true, false, false),
  ('Project_Admin', 'D3', true, false, false),
  ('FinOps_Analyst', 'D3', false, false, false),
  ('SRE', 'D3', true, false, false),
  ('Ops_Lead', 'D3', true, false, false),
  ('Platform_Engineer', 'D3', true, false, false),
  ('Security_Reviewer', 'D3', true, true, false),
  ('Platform_Admin', 'D3', true, false, false),
  ('Platform_Owner', 'D3', true, false, false),
  ('Project_Architect', 'E1', true, false, false),
  ('Developer', 'E1', false, false, false),
  ('Project_Editor', 'E1', true, true, false),
  ('Project_Admin', 'E1', true, false, false),
  ('FinOps_Analyst', 'E1', true, false, false),
  ('SRE', 'E1', true, false, false),
  ('Ops_Lead', 'E1', true, true, false),
  ('Platform_Engineer', 'E1', true, false, false),
  ('Security_Reviewer', 'E1', true, false, false),
  ('Platform_Admin', 'E1', true, false, false),
  ('Platform_Owner', 'E1', true, false, false),
  ('Project_Architect', 'E2', true, true, false),
  ('Developer', 'E2', true, false, false),
  ('Project_Editor', 'E2', true, false, false),
  ('Project_Admin', 'E2', true, true, false),
  ('FinOps_Analyst', 'E2', true, false, false),
  ('SRE', 'E2', true, false, false),
  ('Ops_Lead', 'E2', true, false, false),
  ('Platform_Engineer', 'E2', true, false, false),
  ('Security_Reviewer', 'E2', true, false, false),
  ('Platform_Admin', 'E2', true, false, false),
  ('Platform_Owner', 'E2', true, false, false),
  ('Project_Architect', 'E3', true, false, false),
  ('Developer', 'E3', false, false, false),
  ('Project_Editor', 'E3', true, false, false),
  ('Project_Admin', 'E3', true, false, false),
  ('FinOps_Analyst', 'E3', true, false, false),
  ('SRE', 'E3', true, true, false),
  ('Ops_Lead', 'E3', true, true, false),
  ('Platform_Engineer', 'E3', true, false, false),
  ('Security_Reviewer', 'E3', true, false, false),
  ('Platform_Admin', 'E3', true, false, false),
  ('Platform_Owner', 'E3', true, false, false),
  ('Project_Architect', 'F1', true, false, false),
  ('Developer', 'F1', false, false, false),
  ('Project_Editor', 'F1', true, false, false),
  ('Project_Admin', 'F1', true, false, false),
  ('FinOps_Analyst', 'F1', false, false, false),
  ('SRE', 'F1', true, true, false),
  ('Ops_Lead', 'F1', true, true, false),
  ('Platform_Engineer', 'F1', true, false, false),
  ('Security_Reviewer', 'F1', true, false, false),
  ('Platform_Admin', 'F1', true, false, false),
  ('Platform_Owner', 'F1', true, false, false),
  ('Project_Architect', 'F2', true, false, false),
  ('Developer', 'F2', false, false, false),
  ('Project_Editor', 'F2', true, false, false),
  ('Project_Admin', 'F2', true, false, false),
  ('FinOps_Analyst', 'F2', false, false, false),
  ('SRE', 'F2', true, true, false),
  ('Ops_Lead', 'F2', true, false, false),
  ('Platform_Engineer', 'F2', true, true, false),
  ('Security_Reviewer', 'F2', true, false, false),
  ('Platform_Admin', 'F2', true, false, false),
  ('Platform_Owner', 'F2', true, false, false),
  ('Project_Architect', 'F3', true, false, false),
  ('Developer', 'F3', false, false, false),
  ('Project_Editor', 'F3', false, false, false),
  ('Project_Admin', 'F3', true, false, false),
  ('FinOps_Analyst', 'F3', false, false, false),
  ('SRE', 'F3', true, true, false),
  ('Ops_Lead', 'F3', true, false, false),
  ('Platform_Engineer', 'F3', false, false, false),
  ('Security_Reviewer', 'F3', true, false, true),
  ('Platform_Admin', 'F3', true, false, false),
  ('Platform_Owner', 'F3', true, false, true),
  ('Project_Architect', 'G1', true, false, false),
  ('Developer', 'G1', true, false, false),
  ('Project_Editor', 'G1', true, false, false),
  ('Project_Admin', 'G1', true, false, false),
  ('FinOps_Analyst', 'G1', false, false, false),
  ('SRE', 'G1', true, false, false),
  ('Ops_Lead', 'G1', true, false, false),
  ('Platform_Engineer', 'G1', true, false, false),
  ('Security_Reviewer', 'G1', true, true, true),
  ('Platform_Admin', 'G1', true, false, false),
  ('Platform_Owner', 'G1', true, false, false),
  ('Project_Architect', 'G2', true, false, false),
  ('Developer', 'G2', true, true, false),
  ('Project_Editor', 'G2', true, false, false),
  ('Project_Admin', 'G2', true, false, false),
  ('FinOps_Analyst', 'G2', false, false, false),
  ('SRE', 'G2', true, false, false),
  ('Ops_Lead', 'G2', true, false, false),
  ('Platform_Engineer', 'G2', true, false, false),
  ('Security_Reviewer', 'G2', true, true, true),
  ('Platform_Admin', 'G2', true, false, false),
  ('Platform_Owner', 'G2', true, false, false),
  ('Project_Architect', 'G3', true, false, false),
  ('Developer', 'G3', true, false, false),
  ('Project_Editor', 'G3', true, false, false),
  ('Project_Admin', 'G3', true, false, false),
  ('FinOps_Analyst', 'G3', false, false, false),
  ('SRE', 'G3', true, false, false),
  ('Ops_Lead', 'G3', true, false, false),
  ('Platform_Engineer', 'G3', true, true, false),
  ('Security_Reviewer', 'G3', true, true, true),
  ('Platform_Admin', 'G3', true, false, false),
  ('Platform_Owner', 'G3', true, false, false),
  ('Project_Architect', 'H1', true, false, false),
  ('Developer', 'H1', true, false, false),
  ('Project_Editor', 'H1', true, false, false),
  ('Project_Admin', 'H1', true, false, false),
  ('FinOps_Analyst', 'H1', false, false, false),
  ('SRE', 'H1', true, false, false),
  ('Ops_Lead', 'H1', true, false, false),
  ('Platform_Engineer', 'H1', true, true, false),
  ('Security_Reviewer', 'H1', true, false, false),
  ('Platform_Admin', 'H1', true, true, true),
  ('Platform_Owner', 'H1', true, false, false),
  ('Project_Architect', 'H2', true, false, false),
  ('Developer', 'H2', true, false, false),
  ('Project_Editor', 'H2', true, false, false),
  ('Project_Admin', 'H2', true, false, false),
  ('FinOps_Analyst', 'H2', false, false, false),
  ('SRE', 'H2', true, true, false),
  ('Ops_Lead', 'H2', true, false, false),
  ('Platform_Engineer', 'H2', true, false, false),
  ('Security_Reviewer', 'H2', true, false, false),
  ('Platform_Admin', 'H2', true, true, true),
  ('Platform_Owner', 'H2', true, false, true),
  ('Project_Architect', 'H3', true, false, false),
  ('Developer', 'H3', true, false, false),
  ('Project_Editor', 'H3', true, false, false),
  ('Project_Admin', 'H3', true, false, false),
  ('FinOps_Analyst', 'H3', false, false, false),
  ('SRE', 'H3', true, false, false),
  ('Ops_Lead', 'H3', true, false, false),
  ('Platform_Engineer', 'H3', true, true, false),
  ('Security_Reviewer', 'H3', true, false, false),
  ('Platform_Admin', 'H3', true, true, true),
  ('Platform_Owner', 'H3', true, false, false),
  ('Project_Architect', 'J1', true, true, false),
  ('Developer', 'J1', true, true, false),
  ('Project_Editor', 'J1', true, true, false),
  ('Project_Admin', 'J1', true, true, false),
  ('FinOps_Analyst', 'J1', true, true, false),
  ('SRE', 'J1', true, true, false),
  ('Ops_Lead', 'J1', true, true, false),
  ('Platform_Engineer', 'J1', true, true, false),
  ('Security_Reviewer', 'J1', true, true, false),
  ('Platform_Admin', 'J1', true, true, true),
  ('Platform_Owner', 'J1', true, true, false),
  ('Project_Architect', 'J3a', false, false, false),
  ('Developer', 'J3a', false, false, false),
  ('Project_Editor', 'J3a', false, false, false),
  ('Project_Admin', 'J3a', true, true, true),
  ('FinOps_Analyst', 'J3a', false, false, false),
  ('SRE', 'J3a', false, false, false),
  ('Ops_Lead', 'J3a', false, false, false),
  ('Platform_Engineer', 'J3a', false, false, false),
  ('Security_Reviewer', 'J3a', false, false, false),
  ('Platform_Admin', 'J3a', true, true, true),
  ('Platform_Owner', 'J3a', true, false, false),
  ('Project_Architect', 'J3b', false, false, false),
  ('Developer', 'J3b', false, false, false),
  ('Project_Editor', 'J3b', false, false, false),
  ('Project_Admin', 'J3b', true, true, true),
  ('FinOps_Analyst', 'J3b', false, false, false),
  ('SRE', 'J3b', false, false, false),
  ('Ops_Lead', 'J3b', false, false, false),
  ('Platform_Engineer', 'J3b', false, false, false),
  ('Security_Reviewer', 'J3b', false, false, false),
  ('Platform_Admin', 'J3b', true, true, true),
  ('Platform_Owner', 'J3b', true, false, false)
;

-- ###########################################################################
-- D) Default admin account
--    username: admin
--    password: admin123   ※上線後請立即更換
-- ###########################################################################

INSERT INTO users (username, password_hash, role, is_active)
SELECT
  'admin',
  '$2b$12$3.9UUW/RwGhlhYd3qfBfcuFRALszLp6Wek7kDoVFSSgQNnuYn8pNG',
  'Platform_Admin',
  TRUE
WHERE NOT EXISTS (
  SELECT 1 FROM users WHERE username = 'admin'
);

UPDATE users
SET role = 'Platform_Admin',
    is_active = TRUE
WHERE username = 'admin';

COMMIT;

-- 驗證範例：
-- \dt
-- SELECT count(*) FROM role_permissions;           -- 308
-- SELECT username, role FROM users WHERE username = 'admin';
-- SELECT count(*) FROM user_diagrams;
-- SELECT count(*) FROM diagram_shares;
-- SELECT count(*) FROM user_diagram_chats;
-- SELECT count(*) FROM architecture_reviews;
-- SELECT id, diagram_id, status, overall_score, archived FROM architecture_reviews ORDER BY id DESC LIMIT 5;
-- SELECT id, lens_id, is_active, updated_at FROM wa_lenses ORDER BY id DESC LIMIT 5;
