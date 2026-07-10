-- Cloud-360 Database Schema (Full Deployment Script)
-- Includes A2 diagrams/shares and A4 chat persistence

CREATE TABLE users (
	id SERIAL NOT NULL, 
	username VARCHAR NOT NULL, 
	password_hash VARCHAR NOT NULL, 
	role VARCHAR NOT NULL, 
	is_active BOOLEAN, 
	last_opened_diagram_id INTEGER,
	PRIMARY KEY (id)
);

CREATE TABLE user_diagrams (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	title VARCHAR NOT NULL, 
	xml_data TEXT NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

-- 延後加 FK，避免 users / user_diagrams 循環建立問題
ALTER TABLE users
  ADD CONSTRAINT fk_users_last_opened_diagram
  FOREIGN KEY (last_opened_diagram_id) REFERENCES user_diagrams (id) ON DELETE SET NULL;

CREATE TABLE diagram_shares (
	user_id INTEGER NOT NULL, 
	diagram_id INTEGER NOT NULL, 
	PRIMARY KEY (user_id, diagram_id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(diagram_id) REFERENCES user_diagrams (id)
);

-- A4：使用者 × 架構圖 聊天紀錄
CREATE TABLE user_diagram_chats (
	user_id INTEGER NOT NULL,
	diagram_id INTEGER NOT NULL,
	messages_json TEXT NOT NULL DEFAULT '[]',
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
	PRIMARY KEY (user_id, diagram_id),
	FOREIGN KEY(user_id) REFERENCES users (id),
	FOREIGN KEY(diagram_id) REFERENCES user_diagrams (id) ON DELETE CASCADE
);
