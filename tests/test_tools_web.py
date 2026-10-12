"""
Unit tests for Web tools and scope enforcer in CTF-AI Solver Pro.
"""

from pathlib import Path
import tempfile
import unittest

from ctf_ai.tools.web import (
    ScopeEnforcer,
    global_scope_enforcer,
    WebStaticSecretScannerTool,
    WebToolsDetectorTool,
)


class TestWebTools(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.scanner = WebStaticSecretScannerTool()
        self.detector = WebToolsDetectorTool()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_scope_enforcer(self):
        scope = ScopeEnforcer()
        # Default local targets
        self.assertTrue(scope.is_in_scope("localhost"))
        self.assertTrue(scope.is_in_scope("127.0.0.1:8080"))
        self.assertTrue(scope.is_in_scope("http://127.0.0.1:5000/api"))
        self.assertTrue(scope.is_in_scope("10.10.11.20"))  # Private CTF IP
        self.assertTrue(scope.is_in_scope("192.168.1.100"))

        # External arbitrary target should be false by default
        self.assertFalse(scope.is_in_scope("evil-external-site.com"))

        # Explicitly authorized target
        scope.add_allowed_target("challenge.ctf-platform.org")
        self.assertTrue(scope.is_in_scope("http://challenge.ctf-platform.org/login"))

    def test_web_static_secret_scanner_text(self):
        html_content = """
        <html>
        <head><title>CTF Challenge</title></head>
        <body>
            <!-- Remember to remove test token before release: api_key = "abcdef1234567890abcdef" -->
            <script>
                const awsKey = "AKIA1234567890ABCDEF";
                fetch("/api/v1/user/flag");
                fetch("/admin/dashboard");
            </script>
        </body>
        </html>
        """
        res = self.scanner.run(content_or_file=html_content)
        self.assertTrue(res.success)
        # Check secrets detected
        detected_types = [s["type"] for s in res.data["secrets_detected"]]
        self.assertIn("AWS Access Key ID", detected_types)
        # Check endpoints discovered
        endpoints = res.data["endpoints_found"]
        self.assertIn("/api/v1/user/flag", endpoints)
        self.assertIn("/admin/dashboard", endpoints)
        # Check comments captured
        self.assertTrue(any("api_key" in c for c in res.data["comments_sample"]))

    def test_web_static_secret_scanner_file(self):
        file_path = Path(self.tmp_dir.name) / "bundle.js"
        file_path.write_text("let token = 'ghp_123456789012345678901234567890123456';", encoding="utf-8")

        res = self.scanner.run(content_or_file=str(file_path))
        self.assertTrue(res.success)
        detected_types = [s["type"] for s in res.data["secrets_detected"]]
        self.assertIn("GitHub Personal Access Token", detected_types)

    def test_web_tools_detector(self):
        res = self.detector.run()
        self.assertTrue(res.success)
        self.assertIn("curl", res.data)


if __name__ == "__main__":
    unittest.main()
