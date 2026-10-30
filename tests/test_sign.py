import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from xuexitong_cli.session import XuexitongSession
from xuexitong_cli.sign import XuexitongSign

class TestXuexitongSign(unittest.TestCase):
    def test_sign_parser(self):
        signer = XuexitongSign(XuexitongSession())
        res1 = signer._parse_sign_response("success: 您已签到过了")
        self.assertTrue(res1["success"])

        res2 = signer._parse_sign_response("不在签到范围内")
        self.assertFalse(res2["success"])
        self.assertIn("范围", res2["message"])

        res3 = signer._parse_sign_response("验证码错误")
        self.assertFalse(res3["success"])
        self.assertIn("不匹配", res3["message"])

if __name__ == "__main__":
    unittest.main()
