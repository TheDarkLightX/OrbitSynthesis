"""Reject source substitution at the actual current-manuscript binding gate."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from audit_fixed_q_preprint import ROOT, REVIEW_SUBJECT, check_review_binding


class ReviewedSubject(unittest.TestCase):
    def test_reviewed_subject_and_changed_manuscript(self):
        subject = REVIEW_SUBJECT
        manifest = json.loads((ROOT / subject).read_text())
        with tempfile.TemporaryDirectory(prefix="preprint-subject-control-") as temp:
            root = Path(temp)
            for name in [*manifest["sha256"], subject]:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            original = check_review_binding(root)
            self.assertEqual(original["checked_files"], len(manifest["sha256"]))
            manuscript = root / "paper/FIXED_Q_TERM_COMPLEXITY_DRAFT.md"
            manuscript.write_bytes(manuscript.read_bytes() + b"\nChanged theorem.\n")
            with self.assertRaisesRegex(RuntimeError, "reviewed subject changed"):
                check_review_binding(root)
            manuscript.unlink()
            with self.assertRaises(FileNotFoundError):
                check_review_binding(root)


if __name__ == "__main__":
    unittest.main()
