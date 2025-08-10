import os
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from clickpoints.includes.Database import _probe_const_gop


class TestGOPDetection(unittest.TestCase):
    def test_probe_const_gop(self):
        try:
            subprocess.check_call(
                "ffmpeg -y -f lavfi -i testsrc=size=16x16:rate=30 -frames:v 30 -g 10 gop_test.mp4",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            self.skipTest("ffmpeg not installed")
        fps, gop_len, _ = _probe_const_gop("gop_test.mp4")
        self.assertEqual(gop_len, 10)
        os.remove("gop_test.mp4")


if __name__ == "__main__":
    unittest.main()
