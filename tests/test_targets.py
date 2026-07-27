"""Canonical target discovery contract (Slice 2 T4, ADR-0005; rows V31-V33)."""
import json
import unittest

from collector import resources, targets

PROTECTION = resources.DEFAULT_BRANCH_PROTECTION


def item(repo_id, full_name, **fields):
    return {"id": repo_id, "full_name": full_name,
            "name": full_name.split("/")[-1] if isinstance(full_name, str) else None,
            **fields}


def page(body, status=200, body_text=None, **envelope):
    text = body_text if body_text is not None else json.dumps(body)
    return {"envelope": {"status": status, **envelope}, "body_text": text}


class Discovery(unittest.TestCase):
    def test_eligible_items_become_targets_ascending_by_id(self):
        pages = [
            page([item(9, "o/nine", default_branch="main"),
                  item(4, "o/four", default_branch="main")]),
            page([item(7, "o/seven", default_branch="trunk")]),
        ]
        discovered = targets.discover_targets(pages)
        self.assertEqual([t["id"] for t in discovered], [4, 7, 9])
        self.assertEqual(discovered[0]["full_name"], "o/four")
        self.assertEqual(discovered[0]["name"], "four")

    def test_duplicate_id_first_eligible_occurrence_wins(self):
        # V31: pagination drift repeats one repository across pages.
        pages = [
            page([item(42, "o/first", default_branch="main")]),
            page([item(42, "o/second", default_branch="dev")]),
        ]
        discovered = targets.discover_targets(pages)
        self.assertEqual(len(discovered), 1)
        self.assertEqual(discovered[0]["full_name"], "o/first")

    def test_earlier_malformed_occurrence_never_suppresses_later_eligible(self):
        # ADR-0005: eligibility is evaluated before deduplication.
        pages = [
            page([item(42, "not-owner-name")]),
            page([item(42, "o/good", default_branch="main")]),
        ]
        discovered = targets.discover_targets(pages)
        self.assertEqual([t["full_name"] for t in discovered], ["o/good"])

    def test_malformed_ids_are_never_targets(self):
        # V32: boolean, string, missing, zero, negative — no repair.
        bad = [item(True, "o/bool"), item("42", "o/string"),
               {"full_name": "o/missing", "name": "missing"},
               item(0, "o/zero"), item(-5, "o/negative"), item(None, "o/none")]
        self.assertEqual(targets.discover_targets([page(bad)]), ())

    def test_malformed_identities_are_never_targets(self):
        # V32: structurally valid owner/name identity required — no repair.
        bad = [item(1, None), item(2, ""), item(3, "noslash"),
               item(4, "a/b/c"), item(5, "/name"), item(6, "owner/"),
               item(7, 42), {"id": 8, "name": "no-full-name"}]
        self.assertEqual(targets.discover_targets([page(bad)]), ())

    def test_items_on_shape_invalid_or_failed_pages_are_not_targets(self):
        eligible = item(4, "o/four", default_branch="main")
        pages = [
            page({"repos": [eligible]}),
            page(None, body_text="{not-json"),
            page([item(5, "o/five")], status=404),
            page([item(6, "o/six")], status=500),
            page([eligible]),
        ]
        discovered = targets.discover_targets(pages)
        self.assertEqual([t["id"] for t in discovered], [4])

    def test_incomplete_page_items_still_contribute(self):
        # Partial evidence is evidence: a cap-breached page remains shape-valid.
        capped = page([item(4, "o/four")], incomplete=True)
        self.assertEqual([t["id"] for t in targets.discover_targets([capped])], [4])

    def test_missing_records_contribute_nothing(self):
        self.assertEqual(targets.discover_targets([None]), ())


class DescriptorInputs(unittest.TestCase):
    def test_present_input_is_returned_with_no_missing_names(self):
        (target,) = targets.discover_targets(
            [page([item(4, "o/four", default_branch="main")])]
        )
        values, missing = targets.descriptor_inputs(target, PROTECTION)
        self.assertEqual(values, {"default_branch": "main"})
        self.assertEqual(missing, ())

    def test_missing_default_branch_keeps_target_discovered(self):
        # V33: the repository remains in the discovered set; the descriptor
        # gets no fabricated input.
        (target,) = targets.discover_targets([page([item(4, "o/four")])])
        self.assertEqual(target["id"], 4)
        values, missing = targets.descriptor_inputs(target, PROTECTION)
        self.assertEqual(values, {})
        self.assertEqual(missing, ("default_branch",))

    def test_unusable_input_values_are_missing_never_repaired(self):
        for value in (None, "", 7, ["main"]):
            with self.subTest(value=value):
                (target,) = targets.discover_targets(
                    [page([item(4, "o/four", default_branch=value)])]
                )
                values, missing = targets.descriptor_inputs(target, PROTECTION)
                self.assertEqual(values, {})
                self.assertEqual(missing, ("default_branch",))


class Addressing(unittest.TestCase):
    def test_safe_annotation_is_appended_verbatim(self):
        for name in ("repo-1", "a", "A_b.C-9", "a" * 100, "CON", "nul"):
            with self.subTest(name=name):
                self.assertEqual(targets.directory_key(42, name), f"42-{name}")

    def test_unsafe_annotations_yield_id_only_directory(self):
        # V36: reserved-character, trailing-dot, oversized, non-string names —
        # omitted, never normalized, escaped, replaced, truncated, or repaired.
        for name in ("repo.", "a" * 101, "", "a b", "a/b", "a:b", "a*b",
                     "a?b", "naïve", "répo", None, 7, ["x"]):
            with self.subTest(name=name):
                self.assertEqual(targets.directory_key(42, name), "42")

    def test_annotation_never_affects_eligibility_or_identity(self):
        # An annotation-unsafe name leaves the target eligible, its identity
        # intact, and only the storage address reduced to the ID.
        unsafe = {"id": 4, "full_name": "o/repo.", "name": "repo.",
                  "default_branch": "main"}
        (target,) = targets.discover_targets([page([unsafe])])
        self.assertEqual(target["full_name"], "o/repo.")
        self.assertEqual(targets.directory_key(target["id"], target["name"]), "4")
        values, missing = targets.descriptor_inputs(target, PROTECTION)
        self.assertEqual((values, missing), ({"default_branch": "main"}, ()))


class DirectoryClaims(unittest.TestCase):
    def test_directory_names_claim_their_leading_repository_id(self):
        for dirname, expected in (("42", 42), ("42-name", 42),
                                  ("9034-2nd-repo", 9034), ("7-a.b_c", 7)):
            with self.subTest(dirname=dirname):
                self.assertEqual(targets.claimed_repository_id(dirname), expected)

    def test_unrecognized_directory_names_claim_nothing(self):
        for dirname in ("junk", "042-x", "42-", "-42", "0", "4 2", "42x", ""):
            with self.subTest(dirname=dirname):
                self.assertIsNone(targets.claimed_repository_id(dirname))


def conflicts(*claims):
    return targets.structural_conflicts(claims)


class StructuralValidation(unittest.TestCase):
    def test_clean_claims_report_no_conflicts(self):
        report = conflicts(("4", (4, 4)), ("9-name", (9,)), ("7", ()))
        self.assertEqual(report, {
            "duplicate_ids": (),
            "mismatched_directories": (),
            "unrecognized_directories": (),
            "conflicted_directories": (),
        })

    def test_duplicate_id_directories_are_a_structural_conflict(self):
        # V34: more than one directory claiming one repository ID — no
        # winner is selected and nothing deduplicates silently.
        report = conflicts(("42", (42,)), ("42-name", (42,)), ("7", (7,)))
        self.assertEqual(report["duplicate_ids"], (42,))
        self.assertEqual(report["conflicted_directories"], ("42", "42-name"))

    def test_path_envelope_id_disagreement_is_a_structural_conflict(self):
        # V35: path text never overrides envelope content; the directory's
        # evidence never surfaces as an apparently valid observation.
        report = conflicts(("42", (42, 43)), ("7", (7,)))
        self.assertEqual(report["mismatched_directories"], ("42",))
        self.assertEqual(report["conflicted_directories"], ("42",))

    def test_missing_envelope_identity_cannot_corroborate_the_path(self):
        report = conflicts(("42", (None,)))
        self.assertEqual(report["mismatched_directories"], ("42",))

    def test_unrecognized_directories_are_surfaced_never_ignored(self):
        report = conflicts(("junk", (42,)), ("4", (4,)))
        self.assertEqual(report["unrecognized_directories"], ("junk",))
        self.assertEqual(report["conflicted_directories"], ())

    def test_report_is_deterministic_and_sorted(self):
        report = conflicts(("9-b", (9,)), ("9-a", (9,)), ("42", (1,)))
        self.assertEqual(report["duplicate_ids"], (9,))
        self.assertEqual(report["mismatched_directories"], ("42",))
        self.assertEqual(report["conflicted_directories"], ("42", "9-a", "9-b"))


if __name__ == "__main__":
    unittest.main()
