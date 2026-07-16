import sys
from unittest.mock import MagicMock

# Mock psycopg2 to bypass ModuleNotFoundError when running tests on systems without postgresql drivers
sys.modules['psycopg2'] = MagicMock()

import unittest
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 將 backend 路徑引入
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(backend_dir / "services") not in sys.path:
    sys.path.insert(0, str(backend_dir / "services"))

from models import Base, RolePermission
from services.rbac import (
    normalize_role,
    is_canonical_role,
    user_can,
    user_can_arch,
    sync_arch_permission_flags,
    permissions_map_for_role,
    ensure_role_permissions_seeded,
)

class TestRBAC(unittest.TestCase):
    def setUp(self):
        # 使用 sqlite memory 資料庫
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        
        # Seed 資料
        ensure_role_permissions_seeded(self.db, force=True)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_normalize_role(self):
        self.assertEqual(normalize_role("Security_Admin"), "Security_Reviewer")
        self.assertEqual(normalize_role("Engineering_Manager"), "Project_Editor")
        self.assertEqual(normalize_role("Developer"), "Developer")

    def test_is_canonical_role(self):
        self.assertTrue(is_canonical_role("Project_Architect"))
        self.assertTrue(is_canonical_role("Security_Admin"))
        self.assertFalse(is_canonical_role("Non_Existent_Role"))

    def test_sync_arch_permission_flags(self):
        self.assertEqual(sync_arch_permission_flags(False, True, False), (True, True, False))
        self.assertEqual(sync_arch_permission_flags(False, False, True), (True, False, True))
        self.assertEqual(sync_arch_permission_flags(True, False, False), (True, False, False))

    def test_user_can(self):
        # 預設 seed 中，Project_Architect 應該可以編輯 A1 (架構圖生成)
        self.assertTrue(user_can(self.db, "Project_Architect", "A1", "edit"))
        self.assertTrue(user_can(self.db, "Project_Architect", "A1", "view"))
        
        # Developer 預設對 J3 (管理員面板) 沒有編輯權限
        self.assertFalse(user_can(self.db, "Developer", "J3", "edit"))

    def test_user_can_arch(self):
        self.assertTrue(user_can_arch(self.db, "Project_Architect", "edit"))
        self.assertTrue(user_can_arch(self.db, "Project_Architect", "view"))

    def test_permissions_map_for_role(self):
        perms = permissions_map_for_role(self.db, "Project_Architect")
        self.assertIn("A1", perms)
        self.assertEqual(perms["A2"], perms["A1"])
        self.assertEqual(perms["A4"], perms["A1"])

if __name__ == "__main__":
    unittest.main()
