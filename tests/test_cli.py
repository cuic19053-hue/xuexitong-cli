import unittest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from xuexitong_cli.crypto import calculate_enc
from xuexitong_cli.session import XuexitongSession

class TestXuexitongCLI(unittest.TestCase):
    def test_calculate_enc(self):
        enc = calculate_enc("123", "456", "obj_1", 30.0, 120.0)
        self.assertTrue(isinstance(enc, str))
        self.assertEqual(len(enc), 32)

    def test_session_lifecycle(self):
        import tempfile
        from pathlib import Path
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        
        try:
            s = XuexitongSession(temp_path)
            s.session.cookies.set("UID", "test_user_123")
            s.save()

            s2 = XuexitongSession(temp_path)
            self.assertEqual(s2.session.cookies.get("UID"), "test_user_123")
        finally:
            Path(temp_path).unlink(missing_ok=True)

if __name__ == "__main__":
    unittest.main()
