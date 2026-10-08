"""Mutation tests for evidence receipts bound to immutable Git objects."""

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "create_evidence_receipt.py"
VALIDATOR = ROOT / "scripts" / "validate_evidence_receipts.py"
SCHEMA = ROOT / ".quirk" / "schemas" / "evidence-receipt.schema.json"
GOVERNANCE_WORKFLOW = ROOT / ".github" / "workflows" / "governance-contracts.yml"
REUSABLE_WORKFLOW = ROOT / ".github" / "workflows" / "reusable-evidence-binding.yml"
CHECKOUT_PIN = "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"
PYTHON_PIN = "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97"
LEGACY_CHECKOUT_PIN = "actions/checkout@08eba0b27e820071cde6df949e0beb9ba4906955"
LEGACY_PYTHON_PIN = "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065"

sys.path.insert(0, str(ROOT / "scripts"))
import validate_evidence_receipts  # noqa: E402


def run(*args, cwd, check=True, env_extra=None):
    env = None
    if env_extra:
        env = {**os.environ, **env_extra}
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)
    if check and result.returncode:
        raise AssertionError(result.stderr or result.stdout)
    return result


def git(root, *args, check=True):
    return run("git", *args, cwd=root, check=check)


def git_commit(root, message):
    git(root, "add", "-A")
    git(root, "commit", "-m", message)
    return git(root, "rev-parse", "HEAD").stdout.strip()


def workflow_run_body(text, step_name):
    """Return the shell body of a named workflow step, dedented.

    Line-scanned rather than parsed: `scripts/` and `tests/` import nothing
    outside the standard library, so there is no YAML parser here. The scan
    starts at the step's `- name:` line, finds its `run: |`, and takes the block
    indented further than that key.
    """
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == "- name: " + step_name)
    run_at = next(i for i in range(start, len(lines)) if lines[i].strip() == "run: |")
    key_indent = len(lines[run_at]) - len(lines[run_at].lstrip())
    body = []
    for line in lines[run_at + 1:]:
        if line.strip() and len(line) - len(line.lstrip()) <= key_indent:
            break
        body.append(line[key_indent + 2:] if line.strip() else "")
    return "\n".join(body) + "\n"


def receipt_digest(receipt):
    value = copy.deepcopy(receipt)
    value.pop("receipt_sha256", None)
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


class GitReceiptFixture:
    def __init__(self, root):
        self.root = Path(root)
        git(self.root, "init", "-b", "main")
        git(self.root, "config", "user.name", "Evidence Test")
        git(self.root, "config", "user.email", "evidence@example.invalid")
        (self.root / "keep.txt").write_text("base\n", encoding="utf-8")
        (self.root / "delete.txt").write_text("delete me\n", encoding="utf-8")
        self.base = git_commit(self.root, "base")
        (self.root / "keep.txt").write_text("subject\n", encoding="utf-8")
        (self.root / "present.txt").write_text("proof bytes\n", encoding="utf-8")
        (self.root / "delete.txt").unlink()
        self.subject = git_commit(self.root, "subject")
        self.receipts = self.root / ".quirk" / "evidence"
        self.receipts.mkdir(parents=True)
        self.receipt_path = self.receipts / "qreceipt.test.json"

    def generate(
        self,
        evidence_paths=("delete.txt", "keep.txt", "present.txt"),
        extra=(),
        base=None,
        commands=("python -m unittest discover -s tests -v",),
    ):
        command = [
            sys.executable,
            str(GENERATOR),
            "--repository",
            "owner/repository",
            "--base",
            base or self.base,
            "--commit",
            self.subject,
            "--receipt-id",
            "qreceipt.test",
            "--claim-id",
            "qclaim.test",
            "--claim",
            "The subject changes are byte-bound to this receipt.",
            "--verified-at",
            "2026-08-21T12:00:00Z",
            "--root",
            str(self.root),
            "--output",
            str(self.receipt_path),
        ]
        for path in evidence_paths:
            command.extend(("--evidence-path", path))
        for entry in commands:
            command.extend(("--verification-command", entry))
        command.extend(extra)
        return run(*command, cwd=self.root, check=False)

    def load(self):
        return json.loads(self.receipt_path.read_text(encoding="utf-8"))

    def write(self, value, recompute=True):
        if recompute:
            value["receipt_sha256"] = receipt_digest(value)
        self.receipt_path.parent.mkdir(parents=True, exist_ok=True)
        self.receipt_path.write_text(
            json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    def validate(self, *extra):
        return run(
            sys.executable,
            str(VALIDATOR),
            "--repository",
            "owner/repository",
            "--root",
            str(self.root),
            "--receipts",
            str(self.receipts),
            *extra,
            cwd=self.root,
            check=False,
        )


class EvidenceReceiptTest(unittest.TestCase):
    def fixture(self, directory):
        return GitReceiptFixture(directory)

    def test_generator_creates_valid_two_commit_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            generated = fixture.generate()
            self.assertEqual(generated.returncode, 0, generated.stderr)
            receipt = fixture.load()
            self.assertEqual(receipt["subject"]["base_commit"], fixture.base)
            self.assertEqual(receipt["subject"]["commit"], fixture.subject)
            self.assertEqual(
                receipt["subject"]["changed_paths"],
                ["delete.txt", "keep.txt", "present.txt"],
            )
            self.assertEqual(receipt["artifacts"][0]["state"], "deleted")
            self.assertIsNone(receipt["artifacts"][0]["git_blob"])
            self.assertTrue(receipt["artifacts"][1]["sha256"].startswith("sha256:"))
            self.assertEqual(receipt["claims"][0]["claim_type"], "evidence")
            self.assertEqual(receipt["claims"][0]["authority_effect"], "none")
            fixture.receipt_commit = git_commit(fixture.root, "receipt")
            result = fixture.validate()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("1 receipt", result.stdout)

    def test_a_correction_is_a_separate_instrument_not_an_annotation(self):
        """`correction` is legal only on a non-verified receipt, and required there.

        The validator forbids a correction on a `verified` receipt and demands one
        on `unverified` or `retracted`, so a receipt cannot both attest bytes and
        correct an earlier claim. The generator emitted only verified receipts
        with `correction` hardcoded null, which left the instrument unreachable
        and every correction so far as prose inside a claim statement, where no
        validator or query can find it.
        """
        whole = (
            "--correction-reason", "the earlier claim called a near-lapse a lapse",
            "--corrects-claim", "qclaim.earlier.aaaaaaaaaaaa",
            "--correction-observation", "the document was re-read before its review date",
        )
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            result = fixture.generate(extra=("--status", "retracted") + whole)
            self.assertEqual(result.returncode, 0, result.stderr)
            receipt = fixture.load()
            self.assertEqual(receipt["status"], "retracted")
            self.assertEqual(receipt["correction"]["external_claim_refs"], ["qclaim.earlier.aaaaaaaaaaaa"])
            self.assertEqual(len(receipt["correction"]["observations"]), 1)
            fixture.receipt_commit = git_commit(fixture.root, "receipt")
            self.assertEqual(fixture.validate().returncode, 0, "a retracted correction must validate")

        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            # A verified receipt may not carry one, which is why prose was used before.
            result = fixture.generate(extra=whole)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("cannot carry a correction", result.stderr)
            # A non-verified receipt may not omit one, nor any of its three parts.
            result = fixture.generate(extra=("--status", "retracted"))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("requires a correction", result.stderr)
            for drop in (0, 2, 4):
                partial = tuple(v for i, v in enumerate(whole) if i not in (drop, drop + 1))
                result = fixture.generate(extra=("--status", "unverified") + partial)
                self.assertNotEqual(result.returncode, 0, f"accepted a correction missing {whole[drop]}")
                self.assertIn("requires a correction", result.stderr)
            result = fixture.generate(extra=("--status", "retracted") + whole
                                      + ("--corrects-claim", "qclaim.earlier.aaaaaaaaaaaa"))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must not repeat", result.stderr)

    def test_a_correction_needs_no_evidence_path_and_no_command(self):
        """A correction has a zero-diff subject, so the two verified-only flags must be optional.

        `--status` alone did not make the instrument reachable. `--evidence-path`
        and `--verification-command` stayed mandatory in argparse, and a
        correction has neither: it withdraws a claim rather than attesting bytes,
        so there is no diff to point at and no command that passed against one.
        The validator has always allowed both to be empty on a non-verified
        receipt and required both on a verified one, so the only thing that
        forced the one existing correction to be written by hand was this
        generator. A hand-written receipt is the failure mode receipts exist to
        prevent, which is why this is a test and not a convenience.
        """
        whole = (
            "--status", "retracted",
            "--correction-reason", "the earlier claim called a near-lapse a lapse",
            "--corrects-claim", "qclaim.earlier.aaaaaaaaaaaa",
            "--correction-observation", "the document was re-read before its review date",
        )
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            result = fixture.generate(
                evidence_paths=(), commands=(), base=fixture.subject, extra=whole
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            receipt = fixture.load()
            self.assertEqual(receipt["subject"]["changed_paths"], [])
            self.assertEqual(receipt["artifacts"], [])
            self.assertEqual(receipt["verification"]["commands"], [])
            self.assertEqual(receipt["claims"][0]["evidence_paths"], [])
            # A withdrawal is not an attestation, and the bounded claim types say so.
            self.assertEqual(receipt["claims"][0]["claim_type"], "correction")
            fixture.receipt_commit = git_commit(fixture.root, "receipt")
            self.assertEqual(
                fixture.validate().returncode, 0, "a zero-diff correction must validate"
            )

        # A verified receipt still requires both, and the error names the flag.
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            result = fixture.generate(evidence_paths=())
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--evidence-path is required", result.stderr)
            result = fixture.generate(commands=())
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--verification-command is required", result.stderr)

    def test_an_unverified_receipt_records_a_failed_command_as_failed(self):
        """A receipt that exists to record a failure must not record it as a pass.

        Writing `result: pass` and `exit_code: 0` for every command was harmless
        while this generator emitted only `verified` receipts, where the
        validator requires all-pass anyway. `--status unverified` exists for the
        case where a proof could not be reproduced, so the one receipt whose job
        is to carry a failure would have carried it as a pass — structurally
        valid, and false. The schema has always allowed `fail` with a non-zero
        exit on a non-verified receipt; only this generator forced them green.
        """
        correction = (
            "--correction-reason", "the cited proof does not reproduce",
            "--corrects-claim", "qclaim.earlier.aaaaaaaaaaaa",
            "--correction-observation", "the command exits 1 at this commit",
        )
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            result = fixture.generate(
                evidence_paths=(),
                commands=(),
                base=fixture.subject,
                extra=("--status", "unverified") + correction
                + ("--failed-verification", "python -m unittest discover -s tests", "1"),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            commands = fixture.load()["verification"]["commands"]
            self.assertEqual(
                commands,
                [{
                    "command": "python -m unittest discover -s tests",
                    "result": "fail",
                    "exit_code": 1,
                }],
            )
            fixture.receipt_commit = git_commit(fixture.root, "receipt")
            self.assertEqual(fixture.validate().returncode, 0, "a recorded failure must validate")

        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            # A verified receipt may not carry one: the validator requires all-pass there.
            result = fixture.generate(extra=("--failed-verification", "false", "1"))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("cannot record a failed command", result.stderr)
            # `pass iff exit code 0` is the validator's rule, so exit 0 is not a failure.
            result = fixture.generate(
                evidence_paths=(), commands=(), base=fixture.subject,
                extra=("--status", "unverified") + correction
                + ("--failed-verification", "true", "0"),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must not be 0", result.stderr)
            result = fixture.generate(
                evidence_paths=(), commands=(), base=fixture.subject,
                extra=("--status", "unverified") + correction
                + ("--failed-verification", "true", "oops"),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must be an integer", result.stderr)

    def test_a_verified_receipt_records_correction_as_none(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            self.assertEqual(fixture.generate().returncode, 0)
            receipt = fixture.load()
            self.assertEqual(receipt["status"], "verified")
            self.assertIsNone(receipt["correction"])

    def test_generator_refuses_claim_path_outside_subject_diff(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            result = fixture.generate(("not-in-diff.txt",))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("subject diff", result.stderr)

    def test_generator_records_but_never_executes_verification_command(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            marker = fixture.root / "must-not-exist"
            command = [
                sys.executable, str(GENERATOR), "--repository", "owner/repository",
                "--base", fixture.base, "--commit", fixture.subject,
                "--receipt-id", "qreceipt.no-exec", "--claim-id", "qclaim.no-exec",
                "--claim", "The command is metadata only.",
                "--evidence-path", "keep.txt",
                "--verification-command", "touch " + str(marker),
                "--verified-at", "2026-08-21T12:00:00Z",
                "--root", str(fixture.root), "--output", str(fixture.receipt_path),
            ]
            generated = run(*command, cwd=fixture.root, check=False)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            self.assertFalse(marker.exists())

    def test_validator_accepts_present_and_deleted_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            self.assertEqual(fixture.generate().returncode, 0)
            git_commit(fixture.root, "receipt")
            self.assertEqual(fixture.validate().returncode, 0)

    def test_digest_blob_path_and_order_mutations_fail(self):
        mutations = {
            "wrong digest": lambda r: r["artifacts"][1].__setitem__("sha256", "sha256:" + "0" * 64),
            "wrong blob": lambda r: r["artifacts"][1].__setitem__("git_blob", "0" * 40),
            "substituted path": lambda r: r["subject"]["changed_paths"].__setitem__(1, "other.txt"),
            "unsorted path": lambda r: r["subject"]["changed_paths"].reverse(),
            "duplicate path": lambda r: r["subject"]["changed_paths"].append("keep.txt"),
            "claim outside diff": lambda r: r["claims"][0]["evidence_paths"].append("outside.txt"),
            "artifact order": lambda r: r["artifacts"].reverse(),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                fixture = self.fixture(directory)
                self.assertEqual(fixture.generate().returncode, 0)
                receipt = fixture.load()
                mutate(receipt)
                fixture.write(receipt)
                git_commit(fixture.root, "mutated receipt")
                result = fixture.validate()
                self.assertNotEqual(result.returncode, 0, label)

    def test_changed_receipt_digest_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            self.assertEqual(fixture.generate().returncode, 0)
            receipt = fixture.load()
            receipt["claims"][0]["statement"] = "Changed without updating digest."
            fixture.write(receipt, recompute=False)
            git_commit(fixture.root, "forged receipt")
            result = fixture.validate()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt_sha256", result.stderr)

    def test_missing_or_failed_command_and_structural_authority_effect_fail(self):
        mutations = {
            "missing command": lambda r: r["verification"].__setitem__("commands", []),
            "failed command": lambda r: r["verification"]["commands"][0].update(result="fail", exit_code=1),
            "admission effect": lambda r: r["authority"].__setitem__("admission_effect", "canonical"),
            "claim authority effect": lambda r: r["claims"][0].__setitem__("authority_effect", "admission"),
            "unknown claim type": lambda r: r["claims"][0].__setitem__("claim_type", "authority"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                fixture = self.fixture(directory)
                self.assertEqual(fixture.generate().returncode, 0)
                receipt = fixture.load()
                mutate(receipt)
                fixture.write(receipt)
                git_commit(fixture.root, "mutated receipt")
                result = fixture.validate()
                self.assertNotEqual(result.returncode, 0, label)

    def test_truthful_negated_authority_sentence_is_informational_and_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            self.assertEqual(fixture.generate().returncode, 0)
            receipt = fixture.load()
            receipt["claims"][0]["statement"] = "This receipt does not grant canon admission."
            fixture.write(receipt)
            git_commit(fixture.root, "negated authority statement")
            result = fixture.validate()
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_duplicate_claim_and_receipt_ids_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            self.assertEqual(fixture.generate().returncode, 0)
            receipt = fixture.load()
            receipt["claims"].append(copy.deepcopy(receipt["claims"][0]))
            fixture.write(receipt)
            git_commit(fixture.root, "duplicate claim")
            self.assertNotEqual(fixture.validate().returncode, 0)

        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            self.assertEqual(fixture.generate().returncode, 0)
            duplicate = fixture.receipts / "duplicate.json"
            duplicate.write_text(fixture.receipt_path.read_text(encoding="utf-8"), encoding="utf-8")
            git_commit(fixture.root, "duplicate receipt")
            self.assertNotEqual(fixture.validate().returncode, 0)

    def test_non_ancestor_base_or_subject_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            self.assertEqual(fixture.generate().returncode, 0)
            receipt = fixture.load()
            git(fixture.root, "checkout", "-b", "alternate", fixture.base)
            (fixture.root / "alternate.txt").write_text("alternate\n", encoding="utf-8")
            alternate = git_commit(fixture.root, "alternate")
            git(fixture.root, "checkout", "main")
            receipt["subject"]["commit"] = alternate
            receipt["subject"]["changed_paths"] = ["alternate.txt"]
            receipt["claims"][0]["evidence_paths"] = ["alternate.txt"]
            blob = git(fixture.root, "rev-parse", alternate + ":alternate.txt").stdout.strip()
            digest = hashlib.sha256(b"alternate\n").hexdigest()
            receipt["artifacts"] = [{
                "path": "alternate.txt", "state": "present", "git_blob": blob,
                "sha256": "sha256:" + digest,
            }]
            fixture.write(receipt)
            git_commit(fixture.root, "non-ancestor receipt")
            result = fixture.validate()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ancestor", result.stderr)

        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            self.assertEqual(fixture.generate().returncode, 0)
            receipt = fixture.load()
            git(fixture.root, "checkout", "-b", "alternate-base", fixture.base)
            (fixture.root / "alternate-base.txt").write_text("alternate\n", encoding="utf-8")
            alternate_base = git_commit(fixture.root, "alternate base")
            git(fixture.root, "checkout", "main")
            receipt["subject"]["base_commit"] = alternate_base
            fixture.write(receipt)
            git_commit(fixture.root, "non-ancestor base receipt")
            result = fixture.validate()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("base commit must be an ancestor", result.stderr)

    def test_unverified_zero_diff_correction_passes_but_does_not_cover(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            correction = {
                "schema_version": "evidence-receipt.v1",
                "receipt_id": "qreceipt.correction",
                "repository": "owner/repository",
                "status": "unverified",
                "subject": {"base_commit": fixture.subject, "commit": fixture.subject, "changed_paths": []},
                "claims": [{
                    "claim_id": "qclaim.external-no-delta",
                    "claim_type": "correction",
                    "authority_effect": "none",
                    "statement": "The cited external claim has no visible implementation delta.",
                    "evidence_paths": [],
                }],
                "artifacts": [],
                "verification": {"commands": [], "verified_at": "2026-08-21T12:00:00Z"},
                "authority": {"admission_effect": "none", "authority_ref": None},
                "correction": {
                    "reason": "The referenced comparison has zero changed files.",
                    "external_claim_refs": ["https://example.invalid/pull/42"],
                    "observations": ["The base-to-head comparison contains no paths."],
                },
            }
            fixture.write(correction)
            head = git_commit(fixture.root, "correction receipt")
            accepted = fixture.validate()
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            coverage = fixture.validate(
                "--range-base", fixture.base,
                "--range-head", head,
                "--require-covered-diff",
            )
            self.assertNotEqual(coverage.returncode, 0)
            self.assertIn("uncovered", coverage.stderr)

    def test_correction_requires_reason_observation_and_external_reference(self):
        fields = ("reason", "external_claim_refs", "observations")
        for field in fields:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                fixture = self.fixture(directory)
                correction = {
                    "schema_version": "evidence-receipt.v1",
                    "receipt_id": "qreceipt.correction",
                    "repository": "owner/repository",
                    "status": "retracted",
                    "subject": {"base_commit": fixture.subject, "commit": fixture.subject, "changed_paths": []},
                    "claims": [{
                        "claim_id": "qclaim.retracted",
                        "claim_type": "correction",
                        "authority_effect": "none",
                        "statement": "The earlier claim is withdrawn.",
                        "evidence_paths": [],
                    }],
                    "artifacts": [],
                    "verification": {"commands": [], "verified_at": "2026-08-21T12:00:00Z"},
                    "authority": {"admission_effect": "none", "authority_ref": None},
                    "correction": {
                        "reason": "The evidence is not reproducible.",
                        "external_claim_refs": ["qclaim.external"],
                        "observations": ["No matching artifact was found."],
                    },
                }
                correction["correction"][field] = [] if field != "reason" else ""
                fixture.write(correction)
                git_commit(fixture.root, "invalid correction")
                self.assertNotEqual(fixture.validate().returncode, 0)

    def test_command_result_and_exit_code_are_consistent_for_corrections(self):
        mutations = (("pass", 1), ("fail", 0))
        for result_name, exit_code in mutations:
            with self.subTest(result=result_name, exit_code=exit_code), tempfile.TemporaryDirectory() as directory:
                fixture = self.fixture(directory)
                correction = {
                    "schema_version": "evidence-receipt.v1",
                    "receipt_id": "qreceipt.correction-command",
                    "repository": "owner/repository",
                    "status": "unverified",
                    "subject": {"base_commit": fixture.subject, "commit": fixture.subject, "changed_paths": []},
                    "claims": [{
                        "claim_id": "qclaim.correction-command",
                        "claim_type": "correction",
                        "authority_effect": "none",
                        "statement": "The command outcome is recorded consistently.",
                        "evidence_paths": [],
                    }],
                    "artifacts": [],
                    "verification": {
                        "commands": [{"command": "false", "result": result_name, "exit_code": exit_code}],
                        "verified_at": "2026-08-21T12:00:00Z",
                    },
                    "authority": {"admission_effect": "none", "authority_ref": None},
                    "correction": {
                        "reason": "The command outcome is unverified.",
                        "external_claim_refs": ["qclaim.external"],
                        "observations": ["The result and exit code disagree."],
                    },
                }
                fixture.write(correction)
                git_commit(fixture.root, "inconsistent correction command")
                self.assertNotEqual(fixture.validate().returncode, 0)

    def test_exact_coverage_passes_receipt_json_is_excluded_and_later_change_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            self.assertEqual(fixture.generate().returncode, 0)
            receipt_head = git_commit(fixture.root, "receipt")
            covered = fixture.validate(
                "--range-base", fixture.base,
                "--range-head", receipt_head,
                "--require-covered-diff",
            )
            self.assertEqual(covered.returncode, 0, covered.stderr)
            (fixture.root / "later.txt").write_text("not receipted\n", encoding="utf-8")
            later_head = git_commit(fixture.root, "later")
            uncovered = fixture.validate(
                "--range-base", fixture.base,
                "--range-head", later_head,
                "--require-covered-diff",
            )
            self.assertNotEqual(uncovered.returncode, 0)
            self.assertIn("later.txt", uncovered.stderr)

    def test_later_same_path_change_is_stale_until_a_later_receipt_covers_it(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            self.assertEqual(fixture.generate().returncode, 0)
            first_receipt_head = git_commit(fixture.root, "first receipt")
            (fixture.root / "keep.txt").write_text("later same path\n", encoding="utf-8")
            later_subject = git_commit(fixture.root, "later same-path change")
            stale = fixture.validate(
                "--range-base", fixture.base,
                "--range-head", later_subject,
                "--require-covered-diff",
            )
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("stale", stale.stderr)

            second_receipt = fixture.receipts / "qreceipt.keep-latest.json"
            generated = run(
                sys.executable, str(GENERATOR),
                "--repository", "owner/repository",
                "--base", first_receipt_head,
                "--commit", later_subject,
                "--receipt-id", "qreceipt.keep-latest",
                "--claim-id", "qclaim.keep-latest",
                "--claim", "The latest keep.txt bytes are bound.",
                "--evidence-path", "keep.txt",
                "--verification-command", "python -m unittest discover -s tests -v",
                "--verified-at", "2026-08-21T12:00:00Z",
                "--root", str(fixture.root),
                "--output", str(second_receipt),
                cwd=fixture.root,
                check=False,
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            latest_head = git_commit(fixture.root, "latest receipt")
            covered = fixture.validate(
                "--range-base", fixture.base,
                "--range-head", latest_head,
                "--require-covered-diff",
            )
            self.assertEqual(covered.returncode, 0, covered.stderr)

    def test_merged_side_branch_that_restores_the_bytes_is_still_stale(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            self.assertEqual(fixture.generate().returncode, 0)
            git_commit(fixture.root, "receipt")
            git(fixture.root, "checkout", "-q", "-b", "side", fixture.base)
            (fixture.root / "keep.txt").write_text("tampered\n", encoding="utf-8")
            git_commit(fixture.root, "side change")
            (fixture.root / "keep.txt").write_text("subject\n", encoding="utf-8")
            git_commit(fixture.root, "side restores subject bytes")
            git(fixture.root, "checkout", "-q", "main")
            git(fixture.root, "merge", "-q", "--no-ff", "-m", "merge side", "side")
            merged = git(fixture.root, "rev-parse", "HEAD").stdout.strip()
            result = fixture.validate(
                "--range-base", fixture.base,
                "--range-head", merged,
                "--require-covered-diff",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("stale", result.stderr)
            self.assertIn("keep.txt", result.stderr)

    def test_subject_equal_to_range_base_does_not_qualify(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            self.assertEqual(fixture.generate().returncode, 0)
            receipt_head = git_commit(fixture.root, "receipt bound to the range base")
            covered = fixture.validate(
                "--range-base", fixture.subject,
                "--range-head", receipt_head,
                "--require-covered-diff",
            )
            self.assertEqual(covered.returncode, 0, covered.stderr)
            (fixture.root / "later.txt").write_text("not receipted\n", encoding="utf-8")
            later_head = git_commit(fixture.root, "later")
            uncovered = fixture.validate(
                "--range-base", fixture.subject,
                "--range-head", later_head,
                "--require-covered-diff",
            )
            self.assertNotEqual(uncovered.returncode, 0)
            self.assertIn("uncovered paths: later.txt", uncovered.stderr)

    def test_deleted_receipt_json_is_not_a_substantive_path(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            self.assertEqual(fixture.generate().returncode, 0)
            receipt_head = git_commit(fixture.root, "receipt")
            fixture.receipt_path.unlink()
            retired_head = git_commit(fixture.root, "retire receipt")
            covered = fixture.validate(
                "--range-base", receipt_head,
                "--range-head", retired_head,
                "--require-covered-diff",
            )
            self.assertEqual(covered.returncode, 0, covered.stderr)
            (fixture.root / "keep.txt").unlink()
            (fixture.root / "notes.json").write_text("{}\n", encoding="utf-8")
            outside_head = git_commit(fixture.root, "delete a non-receipt path")
            uncovered = fixture.validate(
                "--range-base", receipt_head,
                "--range-head", outside_head,
                "--require-covered-diff",
            )
            self.assertNotEqual(uncovered.returncode, 0)
            self.assertIn("keep.txt", uncovered.stderr)
            self.assertIn("notes.json", uncovered.stderr)

    def test_deleted_receipt_is_exempt_when_the_root_is_the_receipt_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            fixture.receipt_path = fixture.root / "qreceipt.test.json"
            self.assertEqual(fixture.generate().returncode, 0)
            receipt_head = git_commit(fixture.root, "receipt at the root")
            fixture.receipt_path.unlink()
            retired_head = git_commit(fixture.root, "retire root receipt")
            covered = run(
                sys.executable, str(VALIDATOR),
                "--repository", "owner/repository",
                "--root", str(fixture.root),
                "--receipts", ".",
                "--range-base", receipt_head,
                "--range-head", retired_head,
                "--require-covered-diff",
                cwd=fixture.root,
                check=False,
            )
            self.assertEqual(covered.returncode, 0, covered.stderr)

    def test_git_pathspec_magic_filename_cannot_evade_freshness(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git(root, "init", "-b", "main")
            git(root, "config", "user.name", "Evidence Test")
            git(root, "config", "user.email", "evidence@example.invalid")
            (root / "base.txt").write_text("base\n", encoding="utf-8")
            base = git_commit(root, "base")
            magic_path = ":(literal)proof.txt"
            (root / magic_path).write_text("subject\n", encoding="utf-8")
            subject = git_commit(root, "magic-path subject")
            receipts = root / ".quirk" / "evidence"
            first_receipt = receipts / "qreceipt.magic-first.json"
            generated = run(
                sys.executable, str(GENERATOR),
                "--repository", "owner/repository",
                "--base", base,
                "--commit", subject,
                "--receipt-id", "qreceipt.magic-first",
                "--claim-id", "qclaim.magic-first",
                "--claim", "The pathspec-magic filename is byte-bound.",
                "--evidence-path", magic_path,
                "--verification-command", "python -m unittest discover -s tests -v",
                "--verified-at", "2026-08-21T12:00:00Z",
                "--root", str(root),
                "--output", str(first_receipt),
                cwd=root,
                check=False,
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            first_receipt_head = git_commit(root, "first magic-path receipt")
            (root / magic_path).write_text("later\n", encoding="utf-8")
            later_subject = git_commit(root, "later magic-path change")
            stale = run(
                sys.executable, str(VALIDATOR),
                "--repository", "owner/repository",
                "--root", str(root),
                "--receipts", str(receipts),
                "--range-base", base,
                "--range-head", later_subject,
                "--require-covered-diff",
                cwd=root,
                check=False,
            )
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("stale", stale.stderr)

            second_receipt = receipts / "qreceipt.magic-latest.json"
            generated = run(
                sys.executable, str(GENERATOR),
                "--repository", "owner/repository",
                "--base", first_receipt_head,
                "--commit", later_subject,
                "--receipt-id", "qreceipt.magic-latest",
                "--claim-id", "qclaim.magic-latest",
                "--claim", "The latest pathspec-magic filename is byte-bound.",
                "--evidence-path", magic_path,
                "--verification-command", "python -m unittest discover -s tests -v",
                "--verified-at", "2026-08-21T12:00:00Z",
                "--root", str(root),
                "--output", str(second_receipt),
                cwd=root,
                check=False,
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            latest_head = git_commit(root, "latest magic-path receipt")
            covered = run(
                sys.executable, str(VALIDATOR),
                "--repository", "owner/repository",
                "--root", str(root),
                "--receipts", str(receipts),
                "--range-base", base,
                "--range-head", latest_head,
                "--require-covered-diff",
                cwd=root,
                check=False,
            )
            self.assertEqual(covered.returncode, 0, covered.stderr)

    def test_non_ascii_repository_path_round_trips_through_nul_diff(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git(root, "init", "-b", "main")
            git(root, "config", "user.name", "Evidence Test")
            git(root, "config", "user.email", "evidence@example.invalid")
            (root / "base.txt").write_text("base\n", encoding="utf-8")
            base = git_commit(root, "base")
            unicode_path = "café/資料.txt"
            (root / "café").mkdir()
            (root / unicode_path).write_text("proof\n", encoding="utf-8")
            subject = git_commit(root, "unicode subject")
            output = root / ".quirk" / "evidence" / "qreceipt.unicode.json"
            generated = run(
                sys.executable, str(GENERATOR),
                "--repository", "owner/repository",
                "--base", base,
                "--commit", subject,
                "--receipt-id", "qreceipt.unicode",
                "--claim-id", "qclaim.unicode",
                "--claim", "The UTF-8 path and bytes are bound.",
                "--evidence-path", unicode_path,
                "--verification-command", "python -m unittest discover -s tests -v",
                "--verified-at", "2026-08-21T12:00:00Z",
                "--root", str(root),
                "--output", str(output),
                cwd=root,
                check=False,
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            receipt = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(receipt["subject"]["changed_paths"], [unicode_path])
            git_commit(root, "unicode receipt")
            validated = run(
                sys.executable, str(VALIDATOR),
                "--repository", "owner/repository",
                "--root", str(root),
                "--receipts", str(output.parent),
                cwd=root,
                check=False,
            )
            self.assertEqual(validated.returncode, 0, validated.stderr)

    def test_nul_diff_parser_rejects_malformed_non_utf8_and_unsafe_paths(self):
        self.assertEqual(
            validate_evidence_receipts.parse_name_status("A\0café/資料.txt\0".encode()),
            [("café/資料.txt", "present")],
        )
        malformed_outputs = (
            b"A\0missing-terminal-nul",
            b"A\0",
            b"A\0bad-utf8-\xff\0",
            b"A\0unsafe\npath.txt\0",
        )
        for output in malformed_outputs:
            with self.subTest(output=output):
                with self.assertRaises(validate_evidence_receipts.ReceiptError):
                    validate_evidence_receipts.parse_name_status(output)

    def test_unsafe_repository_paths_fail(self):
        unsafe_paths = ["../outside.txt", "/absolute.txt", "windows\\path.txt", "control\npath.txt"]
        for unsafe in unsafe_paths:
            with self.subTest(path=unsafe), tempfile.TemporaryDirectory() as directory:
                fixture = self.fixture(directory)
                self.assertEqual(fixture.generate().returncode, 0)
                receipt = fixture.load()
                receipt["subject"]["changed_paths"][0] = unsafe
                receipt["artifacts"][0]["path"] = unsafe
                receipt["claims"][0]["evidence_paths"][0] = unsafe
                fixture.write(receipt)
                git_commit(fixture.root, "unsafe receipt")
                self.assertNotEqual(fixture.validate().returncode, 0)

    def test_cli_requires_complete_coverage_flag_set(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            self.assertEqual(fixture.generate().returncode, 0)
            head = git_commit(fixture.root, "receipt")
            partial = fixture.validate("--range-base", fixture.base)
            self.assertNotEqual(partial.returncode, 0)
            complete = fixture.validate(
                "--range-base", fixture.base,
                "--range-head", head,
                "--require-covered-diff",
            )
            self.assertEqual(complete.returncode, 0, complete.stderr)

    def test_schema_is_closed_and_matches_exact_contract(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertFalse(schema["additionalProperties"])
        self.assertSetEqual(
            set(schema["required"]),
            {
                "schema_version", "receipt_id", "repository", "status", "subject",
                "claims", "artifacts", "verification", "authority", "correction",
                "receipt_sha256",
            },
        )
        for definition in schema["$defs"].values():
            if definition.get("type") == "object":
                self.assertFalse(definition["additionalProperties"])
        self.assertSetEqual(
            set(schema["$defs"]["claim"]["required"]),
            {"claim_id", "claim_type", "authority_effect", "statement", "evidence_paths"},
        )

    def test_a_correction_only_pull_request_emits_no_candidate_and_passes(self):
        """The candidate step must not fail a range whose only change is a receipt.

        Making the correction instrument reachable from the generator was not
        enough to make a correction landable on its own. The candidate step
        detects a receipt-only head, moves the subject back to its parent, finds
        no substantive path in the range, and then called the generator with no
        `--evidence-path` and the default `verified` status — which cannot
        succeed, so the `validate` job failed for a range the coverage step
        accepts. The only way to land a retraction was to attach it to an
        unrelated change, which is the opposite of a separate instrument.

        This runs the step's own shell body rather than asserting on its text,
        so a rewrite that drops the guard fails here even if the comment stays.
        """
        body = workflow_run_body(
            GOVERNANCE_WORKFLOW.read_text(encoding="utf-8"),
            "Emit exact-range receipt candidate for review",
        )
        self.assertIn("create_evidence_receipt.py", body)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git(root, "init", "-q", "-b", "main")
            git(root, "config", "user.email", "test@example.com")
            git(root, "config", "user.name", "test")
            (root / "subject.txt").write_text("base\n", encoding="utf-8")
            base = git_commit(root, "base")
            receipts = root / ".quirk" / "evidence"
            receipts.mkdir(parents=True)
            (receipts / "qreceipt.correction.json").write_text("{}\n", encoding="utf-8")
            head = git_commit(root, "correction receipt alone")
            result = run(
                "bash",
                "-c",
                body,
                cwd=root,
                check=False,
                env_extra={"RANGE_BASE": base, "RANGE_HEAD": head},
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertIn("No substantive path in range", result.stdout)
            # The guard must return before the generator runs, not after it fails.
            self.assertNotIn("EXACT-RANGE RECEIPT CANDIDATE", result.stdout)

    def test_workflows_are_stable_read_only_and_do_not_execute_claimant_commands(self):
        governance = GOVERNANCE_WORKFLOW.read_text(encoding="utf-8")
        reusable = REUSABLE_WORKFLOW.read_text(encoding="utf-8")
        for workflow in (governance, reusable):
            self.assertIn("runs-on: ubuntu-24.04", workflow)
            self.assertIn("contents: read", workflow)
            self.assertNotIn("pull_request_target", workflow)
            self.assertNotRegex(workflow, r"(?m)^\s*secrets:")
            self.assertNotRegex(workflow, r"(?m)^\s+paths(?:-ignore)?:")
            self.assertNotRegex(workflow, r"actions/(?:checkout|setup-python)@v[0-9]")
            self.assertIn(CHECKOUT_PIN, workflow)
            self.assertIn(PYTHON_PIN, workflow)
            self.assertNotIn(LEGACY_CHECKOUT_PIN, workflow)
            self.assertNotIn(LEGACY_PYTHON_PIN, workflow)
        self.assertIn("fetch-depth: 0", governance)
        self.assertIn("python -m unittest discover -s tests -v", governance)
        self.assertNotIn("python scripts/validate_topology.py", governance)
        self.assertIn("scripts/validate_governed_decisions.py", governance)
        self.assertIn("scripts/validate_evidence_receipts.py", governance)
        self.assertIn("${{ job.workflow_repository }}", reusable)
        self.assertIn("${{ job.workflow_sha }}", reusable)
        self.assertIn("if: github.event_name != 'pull_request'", reusable)
        self.assertIn("${{ github.repository }}", reusable)
        self.assertIn("${{ github.event.pull_request.base.sha }}", reusable)
        self.assertIn("${{ github.event.pull_request.head.sha }}", reusable)
        self.assertNotIn("inputs:", reusable)
        self.assertNotIn("${{ inputs", reusable)
        self.assertNotIn("verification-command", reusable)
        self.assertNotRegex(reusable, r"(?m)^\s+command:\s*$")
        # The original evidence gate still has one non-persisting checkout;
        # additive OS probes must not loosen that boundary or persist credentials.
        gate = governance.split("  validate:\n", 1)[1]
        self.assertEqual(gate.count("persist-credentials: false"), 1)
        self.assertEqual(governance.count("persist-credentials: false"),
                         governance.count("uses: actions/checkout@"))
        self.assertEqual(reusable.count("persist-credentials: false"), 2)


if __name__ == "__main__":
    unittest.main()
