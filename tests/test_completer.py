"""
Unit tests for Slash Commands autocompletion in CTF-AI Solver Pro.
"""

import unittest
from prompt_toolkit.document import Document
from ctf_ai.completer import CTFCommandCompleter, COMMANDS_REGISTRY, SUB_ARGUMENTS


class TestCTFCommandCompleter(unittest.TestCase):

    def setUp(self):
        self.completer = CTFCommandCompleter()

    def _get_completions(self, text: str):
        doc = Document(text, cursor_position=len(text))
        return list(self.completer.get_completions(doc, None))

    def test_slash_prefix_suggests_all_commands(self):
        completions = self._get_completions("/")
        self.assertGreaterEqual(len(completions), 20)
        # All completions should start with /
        for c in completions:
            self.assertTrue(c.text.startswith("/"))
            self.assertTrue(bool(c.display_meta))

    def test_filtering_with_partial_input(self):
        completions = self._get_completions("/pl")
        texts = [c.text for c in completions]
        self.assertIn("/plan", texts)
        self.assertIn("/plan-study", texts)
        # Should not include unrelated commands
        self.assertNotIn("/challenge", texts)
        self.assertNotIn("/solve", texts)

    def test_plain_text_without_slash(self):
        completions = self._get_completions("sol")
        texts = [c.text for c in completions]
        self.assertIn("solve", texts)
        # Should NOT have slash prefix if user did not type slash
        self.assertFalse(any(t.startswith("/") for t in texts))

    def test_sub_argument_provider(self):
        completions = self._get_completions("/provider ")
        texts = [c.text for c in completions]
        self.assertIn("gemini", texts)
        self.assertIn("openai", texts)
        self.assertIn("claude", texts)

    def test_sub_argument_tool(self):
        completions = self._get_completions("/tool ")
        texts = [c.text for c in completions]
        self.assertIn("b64d", texts)
        self.assertIn("rot13", texts)
        self.assertIn("hashid", texts)
        self.assertIn("magic", texts)

    def test_sub_argument_filtering(self):
        completions = self._get_completions("/tool b6")
        texts = [c.text for c in completions]
        self.assertIn("b64d", texts)
        self.assertIn("b64e", texts)
        self.assertNotIn("rot13", texts)

    def test_sub_argument_mode(self):
        completions = self._get_completions("/mode ")
        texts = [c.text for c in completions]
        self.assertIn("ctf", texts)
        self.assertIn("mentor", texts)
        self.assertIn("diag", texts)

    def test_sub_argument_roadmap(self):
        completions = self._get_completions("/roadmap ")
        texts = [c.text for c in completions]
        self.assertIn("pentesting", texts)
        self.assertIn("blue_team", texts)
        self.assertIn("reversing", texts)


if __name__ == "__main__":
    unittest.main()
