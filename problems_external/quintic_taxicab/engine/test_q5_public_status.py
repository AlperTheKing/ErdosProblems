from __future__ import annotations

import json
import shutil
import sys
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path


ENGINE = Path(__file__).resolve().parent
sys.path.insert(0, str(ENGINE))
import q5_public_status as status_lib


FIXED = datetime(2026, 7, 21, 7, 0, 0, tzinfo=timezone.utc)
COMMIT = "a" * 40
ARXIV = b"""<html><body>
arXiv:2512.11072 Valery Asiryan
Genus-One Fibrations and the Jacobian of Linear Slices in the Quintic Equal-Sum Problem
Comments: We do not address the global open problem of non-trivial solutions
to a^5+b^5=c^5+d^5 without linear constraints
</body></html>"""
OEIS_OPEN = b"""<html><body>
A046881 Smallest number that is sum of 2 positive distinct n-th powers in 2 different ways.
%S 5,65,1729,635318657
%O 1,1
</body></html>"""
OEIS_DEFINED_5 = b"""<html><body>
A046881 Smallest number that is sum of 2 positive distinct n-th powers in 2 different ways.
%S 5,65,1729,635318657,999999
%O 1,1
</body></html>"""
FORMAL_REF = json.dumps(
    {
        "ref": "refs/heads/main",
        "object": {"type": "commit", "sha": COMMIT, "url": "https://api.github.test/commit"},
    },
    separators=(",", ":"),
).encode("ascii")
FORMAL_OPEN = b"""import FormalConjectures.Util.ProblemImports

@[category research open, AMS 11]
theorem taxicab_for_5_2_2 : answer(sorry) \xe2\x86\x94 \xe2\x88\x83 x : \xe2\x84\x95, IsTaxicabFor 5 2 2 x := by
  sorry
"""
FORMAL_CLOSED = b"""import FormalConjectures.Util.ProblemImports

@[category research open, AMS 11]
theorem taxicab_for_5_2_2 : True := by
  trivial
"""


class FixtureFetcher:
    def __init__(self, *, oeis: bytes = OEIS_OPEN, formal: bytes = FORMAL_OPEN) -> None:
        self.oeis = oeis
        self.formal = formal
        self.urls: list[str] = []

    def __call__(self, url: str) -> status_lib.FetchResponse:
        self.urls.append(url)
        if url == status_lib.ARXIV_URL:
            body = ARXIV
            content_type = "text/html; charset=utf-8"
        elif url == status_lib.OEIS_URL:
            body = self.oeis
            content_type = "text/html; charset=utf-8"
        elif url == status_lib.FORMAL_REF_URL:
            body = FORMAL_REF
            content_type = "application/json"
        elif url == status_lib.FORMAL_RAW_TEMPLATE.format(commit=COMMIT):
            body = self.formal
            content_type = "text/plain; charset=utf-8"
        else:
            raise AssertionError(f"unexpected URL: {url}")
        return status_lib.FetchResponse(
            body=body,
            final_url=url,
            status=200,
            headers={
                "content-type": content_type,
                "etag": '"fixture"',
                "last-modified": "Tue, 21 Jul 2026 07:00:00 GMT",
            },
        )


class PublicStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = ENGINE / f"q5-public-status-test-{uuid.uuid4().hex}"
        self.root.mkdir()
        self.output = self.root / "public_status_gate.json"

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_collect_and_audit_exact_offline_capture(self) -> None:
        fetcher = FixtureFetcher()
        gate = status_lib.collect(self.output, fetcher=fetcher, clock=lambda: FIXED)
        self.assertTrue(gate["all_open"])
        self.assertEqual(gate["formal_main_commit_sha"], COMMIT)
        self.assertEqual(
            fetcher.urls[-1], status_lib.FORMAL_RAW_TEMPLATE.format(commit=COMMIT)
        )
        audited = status_lib.audit_gate(
            self.output, now=FIXED + timedelta(minutes=4), require_fresh=True
        )
        self.assertEqual(audited, gate)
        for source, expected in zip(
            gate["sources"], (ARXIV, OEIS_OPEN, FORMAL_REF, FORMAL_OPEN)
        ):
            self.assertEqual(Path(source["content_path"]).read_bytes(), expected)

    def test_oeis_fifth_term_emits_non_open_gate(self) -> None:
        gate = status_lib.collect(
            self.output,
            fetcher=FixtureFetcher(oeis=OEIS_DEFINED_5),
            clock=lambda: FIXED,
        )
        self.assertFalse(gate["oeis_no_n5_value"])
        self.assertFalse(gate["all_open"])
        self.assertEqual(gate["sources"][1]["observed_status"], "HAS_N5_VALUE")
        status_lib.audit_gate(self.output)

    def test_formal_proof_emits_non_open_gate(self) -> None:
        gate = status_lib.collect(
            self.output,
            fetcher=FixtureFetcher(formal=FORMAL_CLOSED),
            clock=lambda: FIXED,
        )
        self.assertFalse(gate["formal_conjecture_open"])
        self.assertFalse(gate["all_open"])
        self.assertEqual(gate["sources"][3]["observed_status"], "NOT_RESEARCH_OPEN")

    def test_unrelated_later_sorry_does_not_open_target(self) -> None:
        source = b"""@[category research open]
theorem taxicab_for_5_2_2 : True := by
  trivial

@[category research open]
theorem unrelated_open_problem : True := by
  answer(sorry)
"""
        observed, evidence = status_lib._classify_formal_raw(source)
        self.assertEqual(observed, "NOT_RESEARCH_OPEN")
        self.assertFalse(evidence["answer_sorry"])

    def test_commented_and_string_sorries_do_not_open_target(self) -> None:
        source = b"""/-
@[category research open]
theorem taxicab_for_5_2_2 : answer(sorry) \xe2\x86\x94 \xe2\x88\x83 x : \xe2\x84\x95, IsTaxicabFor 5 2 2 x := by
  sorry
-/
@[category research open]
theorem taxicab_for_5_2_2 : True := by
  let marker := "answer(sorry)"
  -- answer(sorry)
  trivial
"""
        observed, evidence = status_lib._classify_formal_raw(source)
        self.assertEqual(observed, "NOT_RESEARCH_OPEN")
        self.assertFalse(evidence["answer_sorry"])

    def test_duplicate_live_target_declarations_fail_closed(self) -> None:
        source = FORMAL_OPEN + b"\n" + FORMAL_OPEN
        with self.assertRaisesRegex(status_lib.PublicStatusError, "multiple live"):
            status_lib._classify_formal_raw(source)

    def test_indented_or_lemma_duplicate_target_fails_closed(self) -> None:
        variants = (
            FORMAL_OPEN + b"\n  theorem taxicab_for_5_2_2 : True := by\n    trivial\n",
            FORMAL_OPEN + b"\nlemma taxicab_for_5_2_2 : True := by\n  trivial\n",
        )
        for source in variants:
            with self.subTest(source=source):
                with self.assertRaisesRegex(status_lib.PublicStatusError, "multiple live"):
                    status_lib._classify_formal_raw(source)

    def test_unannotated_target_after_unrelated_open_theorem_is_not_open(self) -> None:
        source = b"""@[category research open]
theorem unrelated : True := by
  answer(sorry)

theorem taxicab_for_5_2_2 : answer(sorry) \xe2\x86\x94 \xe2\x88\x83 x : \xe2\x84\x95, IsTaxicabFor 5 2 2 x := by
  sorry
"""
        observed, evidence = status_lib._classify_formal_raw(source)
        self.assertEqual(observed, "NOT_RESEARCH_OPEN")
        self.assertFalse(evidence["answer_sorry"])

    def test_multiline_exact_target_header_is_open(self) -> None:
        source = b"""@[category research open, AMS 11]
theorem taxicab_for_5_2_2 :
    answer(sorry) \xe2\x86\x94
      \xe2\x88\x83 x : \xe2\x84\x95, IsTaxicabFor 5 2 2 x := by
  sorry
"""
        observed, evidence = status_lib._classify_formal_raw(source)
        self.assertEqual(observed, "RESEARCH_OPEN_ANSWER_SORRY")
        self.assertTrue(evidence["answer_sorry"])

    def test_failure_preserves_previous_gate_and_cleans_staging(self) -> None:
        previous = b"previous-valid-gate\n"
        self.output.write_bytes(previous)

        def failing(url: str) -> status_lib.FetchResponse:
            if url == status_lib.ARXIV_URL:
                return FixtureFetcher()(url)
            raise status_lib.PublicStatusError("fixture network failure")

        with self.assertRaises(status_lib.PublicStatusError):
            status_lib.collect(self.output, fetcher=failing, clock=lambda: FIXED)
        self.assertEqual(self.output.read_bytes(), previous)
        capture_parent = self.root / status_lib.CAPTURE_PARENT_NAME
        if capture_parent.exists():
            self.assertEqual(list(capture_parent.iterdir()), [])

    def test_mutated_response_and_extra_inventory_fail_audit(self) -> None:
        gate = status_lib.collect(
            self.output, fetcher=FixtureFetcher(), clock=lambda: FIXED
        )
        first = Path(gate["sources"][0]["content_path"])
        first.write_bytes(first.read_bytes() + b"drift")
        with self.assertRaisesRegex(status_lib.PublicStatusError, "captured bytes drift"):
            status_lib.audit_gate(self.output)

        shutil.rmtree(Path(gate["capture_dir"]))
        gate = status_lib.collect(
            self.output, fetcher=FixtureFetcher(), clock=lambda: FIXED
        )
        (Path(gate["capture_dir"]) / "unexpected.txt").write_text("x", encoding="ascii")
        with self.assertRaisesRegex(status_lib.PublicStatusError, "inventory"):
            status_lib.audit_gate(self.output)

    def test_strict_gate_schema_and_freshness(self) -> None:
        gate = status_lib.collect(
            self.output, fetcher=FixtureFetcher(), clock=lambda: FIXED
        )
        gate["extra"] = True
        self.output.write_text(json.dumps(gate), encoding="ascii")
        with self.assertRaisesRegex(status_lib.PublicStatusError, "keys differ"):
            status_lib.audit_gate(self.output)

        self.output.unlink()
        status_lib.collect(self.output, fetcher=FixtureFetcher(), clock=lambda: FIXED)
        with self.assertRaisesRegex(status_lib.PublicStatusError, "not fresh"):
            status_lib.audit_gate(
                self.output, now=FIXED + timedelta(minutes=5, microseconds=1), require_fresh=True
            )


    def test_arxiv_markup_spacing_does_not_control_classification(self) -> None:
        rendered = b"""<html><body>
        arXiv:2512.11072 <span>Valery Asiryan</span>
        <h1>Genus-One Fibrations and the Jacobian of Linear Slices in the
        Quintic Equal-Sum Problem</h1>
        <p>We do not address the global open problem of non-trivial solutions
        to <math>a <sup>5</sup> + b <sup>5</sup> = c <sup>5</sup> + d <sup>5</sup></math>.</p>
        </body></html>"""
        observed, _evidence = status_lib._classify_arxiv(rendered)
        self.assertEqual(observed, "OPEN")

    def test_wrong_host_redirect_fails_before_gate_replacement(self) -> None:
        previous = b"previous-valid-gate\n"
        self.output.write_bytes(previous)
        base = FixtureFetcher()

        def redirected(url: str) -> status_lib.FetchResponse:
            response = base(url)
            if url != status_lib.ARXIV_URL:
                return response
            return status_lib.FetchResponse(
                body=response.body,
                final_url="https://example.invalid/abs/2512.11072",
                status=response.status,
                headers=response.headers,
            )

        with self.assertRaisesRegex(status_lib.PublicStatusError, "non-canonical final URL"):
            status_lib.collect(self.output, fetcher=redirected, clock=lambda: FIXED)
        self.assertEqual(self.output.read_bytes(), previous)

if __name__ == "__main__":
    unittest.main()
