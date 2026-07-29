"""Per-resource derivation at the derive seam (Slice 2 T6; crafted raw trees)."""
import json
import tempfile
import unittest
from pathlib import Path

from collector.derive import derive_observed
from collector.serialize import write_canonical

RUN = "20260101T000000Z"

PROTECTION_BODY = {
    "enforce_admins": {"enabled": True},
    "required_pull_request_reviews": {"required_approving_review_count": 1},
    "allow_deletions": {"enabled": False},
}


def repo_item(i, **overrides):
    item = {
        "id": i, "name": f"repo-{i}", "full_name": f"acme/repo-{i}",
        "visibility": "public", "fork": False, "archived": False,
        "created_at": "2021-01-01T00:00:00Z", "default_branch": "main",
    }
    item.update(overrides)
    return item


def record(status, body, headers=None, captured="2026-01-01T00:00:00Z", **extra):
    envelope = {
        "attempts": 1, "captured_at": captured, "method": "GET",
        "response_headers": headers or {}, "run_id": RUN, "status": status,
        "url": "https://api.example/x", "waits_seconds": [],
    }
    envelope.update(extra)
    body_text = body if isinstance(body, str) else json.dumps(body)
    return {"envelope": envelope, "body_text": body_text}


def page_record(items, number=1, incomplete=False):
    extra = {"page": number,
             "item_count": len(items) if isinstance(items, list) else 0}
    if incomplete:
        extra["incomplete"] = True
    return record(200, items, **extra)


def write_tree(root, pages, resources=()):
    """Craft a raw tree; ``resources`` holds (dirname, filename, record)."""
    raw = root / "evidence" / "raw" / RUN
    write_canonical(raw / "user.json", record(200, {"login": "op", "id": 7}))
    write_canonical(raw / "meta.json",
                    record(200, {"installed_version": "3.17.0"},
                           endpoint_optional=True))
    write_canonical(raw / "org.json",
                    record(200, {"login": "acme", "id": 42,
                                 "created_at": "2020-01-02T03:04:05Z"}))
    for number, page in enumerate(pages, start=1):
        write_canonical(raw / f"repos.page-{number}.json", page)
    for dirname, filename, resource_record in resources:
        write_canonical(raw / "repos" / dirname / filename, resource_record)


def protection_doc(out):
    derive_observed(out, run_id=RUN)
    path = out / "observed" / "default-branch-protection.json"
    return json.loads(path.read_text(encoding="utf-8"))


def protection(dirname, status, body, **kw):
    return (dirname, "default-branch-protection.json", record(status, body, **kw))


class DocumentShape(unittest.TestCase):
    def test_top_level_keys_run_id_and_latest_only_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [protection("1-repo-1", 200, PROTECTION_BODY)])
            doc = protection_doc(out)
            self.assertEqual(sorted(doc),
                             ["coverage", "repositories", "run_id", "state"])
            self.assertEqual(doc["run_id"], RUN)
            self.assertEqual(doc["coverage"]["basis"],
                             "eligible-discovered-repositories")
            self.assertEqual(doc["coverage"]["eligible_target_count"], 1)
            self.assertEqual(doc["coverage"]["inventory_state"], "collected")

    def test_collected_entry_projects_descriptor_field_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [protection("1-repo-1", 200, PROTECTION_BODY)])
            [entry] = protection_doc(out)["repositories"]
            self.assertEqual(entry["id"], 1)
            self.assertEqual(entry["full_name"], "acme/repo-1")
            self.assertEqual((entry["state"], entry["reason"]),
                             ("collected", "collected"))
            self.assertEqual(entry["branch"], "main")
            self.assertEqual(entry["enforce_admins"], True)
            self.assertEqual(entry["allow_deletions"], False)
            reviews = entry["required_pull_request_reviews"]
            self.assertEqual(reviews["required_approving_review_count"], 1)
            self.assertEqual(reviews["require_code_owner_reviews"], "unknown")
            self.assertEqual(reviews["dismiss_stale_reviews"], "unknown")
            checks = entry["required_status_checks"]
            self.assertEqual(checks["strict"], "unknown")
            self.assertEqual(checks["contexts_count"], "unknown")
            self.assertEqual(entry["required_signatures"], "unknown")
            self.assertEqual(entry["allow_force_pushes"], "unknown")


class EntryClassification(unittest.TestCase):
    def test_absence_denial_failure_shape_and_unmatched_404(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(
                out,
                [page_record([repo_item(i) for i in (1, 2, 3, 4, 5)])],
                [protection("1-repo-1", 404, {"message": "Branch not protected"}),
                 protection("2-repo-2", 403, {"message": "denied"}),
                 protection("3-repo-3", 500, {"message": "boom"}),
                 protection("4-repo-4", 200, "{not-json"),
                 protection("5-repo-5", 404, {"message": "Not Found"})],
            )
            doc = protection_doc(out)
            by_id = {entry["id"]: entry for entry in doc["repositories"]}
            self.assertEqual((by_id[1]["state"], by_id[1]["reason"]),
                             ("absent", "absence-message-matched"))
            self.assertEqual((by_id[2]["state"], by_id[2]["reason"]),
                             ("inaccessible", "authorization-denied"))
            self.assertEqual((by_id[3]["state"], by_id[3]["reason"]),
                             ("failed", "transport-failed"))
            self.assertEqual((by_id[4]["state"], by_id[4]["reason"]),
                             ("failed", "shape-invalid"))
            self.assertEqual((by_id[5]["state"], by_id[5]["reason"]),
                             ("inaccessible", "absence-rule-unmatched-404"))
            for entry in doc["repositories"]:
                # The required input came from inventory evidence, so the
                # branch stays determined; body-derived values are unknown.
                self.assertEqual(entry["branch"], "main")
                self.assertEqual(entry["enforce_admins"], "unknown")

    def test_missing_input_derives_unknown_without_consulting_artifacts(self):
        # V33 at the derive seam: no artifact exists and none is read.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1, default_branch=None),
                                          repo_item(2)])],
                       [protection("2-repo-2", 200, PROTECTION_BODY)])
            doc = protection_doc(out)
            by_id = {entry["id"]: entry for entry in doc["repositories"]}
            self.assertEqual((by_id[1]["state"], by_id[1]["reason"]),
                             ("unknown", "missing-required-input"))
            self.assertEqual(by_id[1]["branch"], "unknown")
            self.assertEqual((by_id[2]["state"], by_id[2]["reason"]),
                             ("collected", "collected"))

    def test_every_derived_entry_reason_is_in_the_closed_set(self):
        # The closed-set invariant swept at the emission seam, so vocabulary
        # drift between taxonomy.REASONS and derivation cannot go unnoticed.
        from collector.taxonomy import REASONS

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1, default_branch=None),
                                          repo_item(2), repo_item(3)])],
                       [protection("2-repo-2", 200, PROTECTION_BODY)])
            entries = protection_doc(out)["repositories"]
            self.assertEqual(len(entries), 3)
            for entry in entries:
                self.assertIn(entry["reason"], REASONS)

    def test_absent_artifact_with_input_present_is_raw_evidence_absent(self):
        # E1: the absent artifact is the durable trace of a recorded
        # collection failure; derivation reads it as unknown.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1), repo_item(2)])],
                       [protection("2-repo-2", 200, PROTECTION_BODY)])
            doc = protection_doc(out)
            by_id = {entry["id"]: entry for entry in doc["repositories"]}
            self.assertEqual((by_id[1]["state"], by_id[1]["reason"]),
                             ("unknown", "raw-evidence-absent"))
            self.assertEqual(by_id[1]["branch"], "main")


class OrderingAndRollup(unittest.TestCase):
    def test_entries_ascend_by_id_and_rollup_takes_first_non_collected(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(
                out,
                [page_record([repo_item(3), repo_item(1), repo_item(2)])],
                [protection("1-repo-1", 200, PROTECTION_BODY),
                 protection("2-repo-2", 500, {"message": "boom"}),
                 protection("3-repo-3", 200, PROTECTION_BODY)],
            )
            doc = protection_doc(out)
            self.assertEqual([entry["id"] for entry in doc["repositories"]],
                             [1, 2, 3])
            self.assertEqual(doc["state"], "failed")

    def test_all_collected_rolls_up_collected(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([repo_item(1)])],
                       [protection("1-repo-1", 200, PROTECTION_BODY)])
            self.assertEqual(protection_doc(out)["state"], "collected")

    def test_zero_eligible_targets_yield_empty_entries_and_unknown_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            write_tree(out, [page_record([{"id": True, "name": "b",
                                           "full_name": "acme/b"}])])
            doc = protection_doc(out)
            self.assertEqual(doc["repositories"], [])
            self.assertEqual(doc["state"], "unknown")
            self.assertEqual(doc["coverage"]["eligible_target_count"], 0)


if __name__ == "__main__":
    unittest.main()
