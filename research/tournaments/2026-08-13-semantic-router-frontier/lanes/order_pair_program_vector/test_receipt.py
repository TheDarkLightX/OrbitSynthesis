"""Exercise the real bounded audit CLI against receipt substitution attacks."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ReceiptBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.command = [sys.executable]
        if sys.flags.optimize:
            cls.command.append("-O")
        cls.command.extend([str(Path(__file__).with_name(
            "audit_order_pair_program_vector.py")), "--semantic-width", "2",
            "--lower-bound-width", "2", "--arithmetic-width", "5"])
        run = subprocess.run(cls.command, capture_output=True, text=True,
                             timeout=30, check=True)
        cls.original = json.loads(run.stdout)

    def replay(self, text, accepted):
        with tempfile.TemporaryDirectory(prefix="order-pair-receipt-") as temp:
            path = Path(temp) / "expected.json"
            path.write_text(text, encoding="utf-8")
            run = subprocess.run([*self.command, "--expected-receipt", str(path)],
                                 capture_output=True, text=True, timeout=30)
        self.assertEqual(run.returncode == 0, accepted, run.stderr)
        if accepted:
            self.assertEqual(json.loads(run.stdout), self.original)
        else:
            self.assertIn("ValueError", run.stderr)

    def test_original_and_reformatted_receipt(self):
        for text in (json.dumps(self.original),
                     json.dumps(self.original, indent=4, sort_keys=True)):
            with self.subTest(text=text[:20]):
                self.replay(text, True)

    def test_numeric_types_stale_values_digest_and_extra_fields(self):
        for path, value in [
            (("checks", "semantic_projection_cases"),
             float(self.original["checks"]["semantic_projection_cases"])),
            (("materialized", 0, "width"), True),
            (("checks", "semantic_projection_cases"), 0),
            (("semantic_sha256",), "0" * 64),
            (("extra",), 1),
        ]:
            changed = copy.deepcopy(self.original)
            target = changed
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            with self.subTest(path=path, value=value):
                self.replay(json.dumps(changed), False)

    def test_duplicate_fields_and_non_finite_constants(self):
        normal = json.dumps(self.original)
        for text in (
            normal[:-1] + ',"schema":' + json.dumps(self.original["schema"]) + '}',
            normal.replace('"semantic_projection_cases":',
                '"semantic_projection_cases": 0, "semantic_projection_cases":', 1),
            normal[:-1] + ',"extra":NaN}',
            normal[:-1] + ',"extra":Infinity}',
            normal[:-1] + ',"extra":-Infinity}',
        ):
            self.replay(text, False)


if __name__ == "__main__":
    unittest.main()
