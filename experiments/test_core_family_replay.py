"""Adversarial replay-boundary checks using the actual constructor output."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import research_kernel_discriminator_core_family as replay

ROOT = Path(__file__).resolve().parents[1]


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fresh = subprocess.check_output([sys.executable,
            str(ROOT / 'experiments/discriminator_core_family_realizability.py'),
            '--exact-max-carrier', '6'], text=True)
        cls.report = json.loads(cls.fresh)

    def test_original_and_semantically_equal_formatting(self):
        self.assertEqual(replay.validate_summary(self.fresh.encode(), self.fresh), self.report)
        self.assertEqual(replay.validate_summary(json.dumps(self.report, indent=4).encode(), self.fresh), self.report)

    def test_type_confusion_stale_counts_digest_and_duplicate_fields(self):
        for key, value in [('family_mismatch_count', False), ('exact_max_carrier', 6.0),
                           ('exact_family_count', float(self.report['exact_family_count'])),
                           ('foreign_core_mismatch_count', 1), ('semantic_sha256', '0' * 64)]:
            changed = copy.deepcopy(self.report); changed[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                replay.validate_summary(json.dumps(changed).encode(), self.fresh)
        duplicate = self.fresh.rstrip()[:-1] + ',"exact_max_carrier":6}'
        with self.assertRaises(ValueError):
            replay.validate_summary(duplicate.encode(), self.fresh)

    def test_path_replacement_cannot_substitute_artifact_hash(self):
        original = Path.read_bytes
        summary = ROOT / 'runs/zag_discriminator_core_family/summary.json'
        reads = 0
        captured = self.fresh.encode()
        altered = copy.deepcopy(self.report); altered['family_mismatch_count'] = 1
        def read(path):
            nonlocal reads
            if path == summary:
                reads += 1
                return captured if reads == 1 else json.dumps(altered).encode()
            return original(path)
        written = {}
        def write(path, text, *args, **kwargs):
            written[path.name] = text; return len(text)
        with patch.object(Path, 'read_bytes', read), patch.object(Path, 'write_text', write), \
                patch.object(Path, 'mkdir'), patch.object(sys, 'argv', ['replay', '--repo-root', str(ROOT), '--out-root', '/unused']), \
                patch.object(subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, stdout=self.fresh)), \
                patch('builtins.print'):
            replay.main()
        report = json.loads(written['report.json'])
        self.assertEqual(reads, 1)
        self.assertEqual(report['artifacts'][str(summary.relative_to(ROOT))], 'sha256:' + hashlib.sha256(captured).hexdigest())


if __name__ == '__main__':
    unittest.main()
