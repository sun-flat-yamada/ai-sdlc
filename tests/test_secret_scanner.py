"""
Unit Tests for ASDLC Secret Scanner
Ensures reliable detection of sensitive tokens, entropy calculation, and zero false positives on clean files.
Incorporates rules and placeholder hygiene from proud-noether standards.
"""
import unittest
from asdlc.security.secret_scanner import SecretScanner, SecretFinding

class TestSecretScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = SecretScanner()

    def test_01_detect_github_token(self):
        fake_token = "ghp_" + "1234567890abcdef1234567890abcdef1234"
        text = f"const token = '{fake_token}';"
        findings = self.scanner.scan_text(text, "api_client.ts")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "SEC-001-GITHUB-PAT")
        self.assertIn("****", findings[0].masked_snippet)

    def test_02_detect_openai_key(self):
        fake_key = "sk-" + "proj-" + "1234567890abcdef1234567890abcdef"
        text = f"export OPENAI_API_KEY=\"{fake_key}\""
        findings = self.scanner.scan_text(text, ".bashrc")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "SEC-002-OPENAI-KEY")

    def test_03_detect_private_key(self):
        fake_pk = "-----BEGIN " + "RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0..."
        findings = self.scanner.scan_text(fake_pk, "server.key")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "SEC-005-PRIVATE-KEY")

    def test_04_detect_hardcoded_generic_assignment(self):
        secret_line = "db_password" + " = 'SuperSecretP@ssw0rd12345!'"
        findings = self.scanner.scan_text(secret_line, "config.py")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "SEC-007-GENERIC-SECRET-ASSIGNMENT")

    def test_05_clean_text_no_findings(self):
        clean_code = """
        def get_auth_header(token: str) -> dict:
            return {"Authorization": f"Bearer {token}"}
        """
        findings = self.scanner.scan_text(clean_code, "clean.py")
        self.assertEqual(len(findings), 0)

    def test_06_entropy_calculation(self):
        # 高エントロピー（ランダム文字列）
        high_ent = self.scanner.calculate_entropy("4f9a8b1c2d3e4f5a6b7c8d9e0f1a2b3c")
        # 低エントロピー（繰り返し文字列）
        low_ent = self.scanner.calculate_entropy("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        self.assertGreater(high_ent, low_ent)
        self.assertGreater(high_ent, 3.5)

    def test_07_detect_github_fine_grained_pat(self):
        # 82文字の Fine-Grained PAT
        fake_pat = "github_pat_" + "A" * 82
        text = f"GITHUB_PAT = '{fake_pat}'"
        findings = self.scanner.scan_text(text, "ci_env.sh")


        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "SEC-001-GITHUB-FINE-GRAINED")

    def test_08_detect_anthropic_api_key(self):
        fake_ant = "sk-ant-api03-" + "abcdef1234567890abcdef1234567890abcdef"
        text = f"ANTHROPIC_KEY = '{fake_ant}'"
        findings = self.scanner.scan_text(text, "claude.py")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "SEC-002-ANTHROPIC-KEY")

    def test_09_detect_slack_webhook(self):
        fake_slack = "https://" + "hooks.slack.com/services/T11223344/B55667788/ABCDEF1234567890abcdef12"
        text = f"SLACK_WEBHOOK = '{fake_slack}'"
        findings = self.scanner.scan_text(text, "alerts.py")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "SEC-006-SLACK-WEBHOOK")


    def test_10_safe_placeholder_ignored(self):
        # proud-noether 準拠のセーフワードが含まれる行は誤検知除外
        placeholder_text = (
            "export API_KEY='your-enterprise-slug'\n"
            "const dummyToken = 'ghp_xxxx1234567890abcdef1234567890abcdef'; // DUMMY placeholder\n"
            "const exampleKey = 'sk-proj-0000000000000000000000000000'; // mock\n"
        )
        findings = self.scanner.scan_text(placeholder_text, "test_mock.py")
        self.assertEqual(len(findings), 0)

if __name__ == "__main__":
    unittest.main()
