"""
Unit tests for cryptographic tools in CTF-AI Solver Pro.
"""

import unittest
from ctf_ai.tools.crypto import (
    MultiDecoderTool,
    StatisticalAnalysisTool,
    RsaMathTool,
)


class TestCryptoTools(unittest.TestCase):

    def setUp(self):
        self.decoder = MultiDecoderTool()
        self.stats = StatisticalAnalysisTool()
        self.rsa = RsaMathTool()

    def test_multi_decoder_base64(self):
        # Q1RGe2hlbGxvX3dvcmxkfQ== -> CTF{hello_world}
        res = self.decoder.run(data="Q1RGe2hlbGxvX3dvcmxkfQ==")
        self.assertTrue(res.success)
        self.assertIn("base64", res.data)
        self.assertEqual(res.data["base64"], "CTF{hello_world}")

    def test_multi_decoder_hex(self):
        # 4354467b6865785f746573747d -> CTF{hex_test}
        res = self.decoder.run(data="4354467b6865785f746573747d")
        self.assertTrue(res.success)
        self.assertIn("hex", res.data)
        self.assertEqual(res.data["hex"], "CTF{hex_test}")

    def test_multi_decoder_rot13(self):
        # PGS{ebg13_grfg} -> CTF{rot13_test}
        res = self.decoder.run(data="PGS{ebg13_grfg}")
        self.assertTrue(res.success)
        self.assertIn("rot13", res.data)
        self.assertEqual(res.data["rot13"], "CTF{rot13_test}")

    def test_multi_decoder_url(self):
        res = self.decoder.run(data="CTF%7Burl_encoded%7D")
        self.assertTrue(res.success)
        self.assertIn("url", res.data)
        self.assertEqual(res.data["url"], "CTF{url_encoded}")

    def test_statistical_analysis_entropy(self):
        # Low entropy: repetitive string
        low_res = self.stats.run(text="AAAAAAAAAA")
        self.assertTrue(low_res.success)
        self.assertEqual(low_res.data["shannon_entropy"], 0.0)

        # High entropy: pseudo-random / diverse characters
        diverse_text = "".join(chr(i) for i in range(32, 127))
        high_res = self.stats.run(text=diverse_text)
        self.assertTrue(high_res.success)
        self.assertGreater(high_res.data["shannon_entropy"], 6.0)

    def test_statistical_analysis_ioc(self):
        # Index of coincidence for standard English text
        sample = "The quick brown fox jumps over the lazy dog repeatedly to test coincidence"
        res = self.stats.run(text=sample)
        self.assertTrue(res.success)
        self.assertIn("index_of_coincidence", res.data)
        self.assertIsInstance(res.data["index_of_coincidence"], float)

    def test_rsa_math_small_e_cube_root(self):
        # Test small e=3 where c = m^3 < n (cube root attack)
        message_int = 133742
        c = message_int ** 3
        # Large modulus so c < n
        n = 10 ** 50
        res = self.rsa.run(action="small_e_cube_root", c=c, n=n)
        self.assertTrue(res.success)
        self.assertEqual(res.data["recovered_m"], message_int)

    def test_rsa_math_fermat_factorization(self):
        # Choose two close primes
        p = 1000003
        q = 1000033
        n = p * q
        res = self.rsa.run(action="fermat_factorization", n=n)
        self.assertTrue(res.success)
        factors = sorted([res.data["p"], res.data["q"]])
        self.assertEqual(factors, [p, q])


if __name__ == "__main__":
    unittest.main()
