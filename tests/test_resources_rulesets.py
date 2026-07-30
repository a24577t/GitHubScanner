"""Array-projection DSL and the repository-rulesets descriptor (Slice 2 T8).

ADR-0004's falsifiable claim governs this ticket: the second descriptor and
the array projection kinds it needs live in resources.py alone; every other
engine consumes them unchanged. These tests drive the DSL at the pure
projection seam; the shipped descriptor's contract joins in the same file.
"""
import unittest

from collector import resources

ITEM_SUMMARY = (
    ("id", ("field", "id")),
    ("name", ("field", "name")),
    ("target", ("field", "target")),
    ("enforcement", ("field", "enforcement")),
    ("created_at", ("field", "created_at")),
)

ARRAY_LISTING = {
    "name": "array-listing",
    "path_template": "/repos/{full_name}/array-listing",
    "shape": "object_array",
    "required_inputs": (),
    "absence_message": None,
    "projection": (("count", ("length",)),
                   ("entries", ("items", "id", ITEM_SUMMARY))),
}


def variant(**overrides):
    return {**ARRAY_LISTING, **overrides}


class ArrayDslValidation(unittest.TestCase):
    def test_length_and_items_kinds_are_table_legal(self):
        resources.validate_table(
            (resources.DEFAULT_BRANCH_PROTECTION, ARRAY_LISTING))

    def test_items_sort_key_must_be_a_non_empty_string(self):
        for bad_key in ("", None, 7):
            projection = (("entries", ("items", bad_key, ITEM_SUMMARY)),)
            with self.assertRaisesRegex(ValueError, "sort key"):
                resources.validate_table((variant(projection=projection),))

    def test_items_entries_must_be_non_empty(self):
        projection = (("entries", ("items", "id", ())),)
        with self.assertRaisesRegex(ValueError, "items projection"):
            resources.validate_table((variant(projection=projection),))

    def test_items_duplicate_entry_fields_are_rejected(self):
        projection = (("entries", ("items", "id",
                                   (("id", ("field", "id")),
                                    ("id", ("field", "id"))))),)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            resources.validate_table((variant(projection=projection),))

    def test_unknown_kind_inside_items_is_rejected(self):
        projection = (("entries", ("items", "id",
                                   (("id", ("telepathy", "id")),))),)
        with self.assertRaisesRegex(ValueError, "source"):
            resources.validate_table((variant(projection=projection),))


def project_listing(body):
    return resources.project(ARRAY_LISTING, body)


class ArrayDslProjection(unittest.TestCase):
    def test_list_body_projects_count_and_items_sorted_by_key(self):
        body = [
            {"id": 9, "name": "b", "target": "branch", "enforcement": "active",
             "created_at": "2026-01-02T00:00:00Z", "node_id": "X",
             "_links": {"self": {"href": "https://x"}}},
            {"id": 3, "name": "a", "target": "tag", "enforcement": "disabled",
             "created_at": "2026-01-01T00:00:00Z", "source_type": "Repository"},
        ]
        self.assertEqual(project_listing(body), {
            "count": 2,
            "entries": [
                {"id": 3, "name": "a", "target": "tag",
                 "enforcement": "disabled",
                 "created_at": "2026-01-01T00:00:00Z"},
                {"id": 9, "name": "b", "target": "branch",
                 "enforcement": "active",
                 "created_at": "2026-01-02T00:00:00Z"},
            ],
        })

    def test_empty_list_projects_count_zero_and_empty_items(self):
        # Emptiness is a value, never absence (V07 at the projection seam).
        self.assertEqual(project_listing([]), {"count": 0, "entries": []})

    def test_non_list_bodies_project_the_exact_shape_all_unknown(self):
        for body in (None, {}, {"id": 1}, "rulesets", 7):
            self.assertEqual(project_listing(body),
                             {"count": "unknown", "entries": "unknown"})

    def test_missing_item_fields_are_unknown_and_extras_dropped(self):
        projected = project_listing([{"id": 5, "surprise": True}])
        self.assertEqual(projected["entries"], [
            {"id": 5, "name": "unknown", "target": "unknown",
             "enforcement": "unknown", "created_at": "unknown"},
        ])

    def test_non_dict_items_project_all_unknown_after_keyed_items(self):
        projected = project_listing([7, {"id": 1, "name": "a"}])
        self.assertEqual([entry["id"] for entry in projected["entries"]],
                         [1, "unknown"])
        self.assertEqual(projected["count"], 2)

    def test_malformed_keys_sort_after_integers_deterministically(self):
        body = [{"id": "z"}, {"id": 2}, {}, {"id": 1}]
        projected = project_listing(body)
        self.assertEqual([entry["id"] for entry in projected["entries"]],
                         [1, 2, "unknown", "z"])

    def test_duplicate_keys_keep_source_order(self):
        body = [{"id": 4, "name": "first"}, {"id": 4, "name": "second"}]
        self.assertEqual(
            [entry["name"] for entry in project_listing(body)["entries"]],
            ["first", "second"])

    def test_false_and_zero_item_values_are_preserved_never_unknown(self):
        projected = project_listing([{"id": 0, "enforcement": False}])
        self.assertEqual(projected["entries"][0]["id"], 0)
        self.assertIs(projected["entries"][0]["enforcement"], False)


if __name__ == "__main__":
    unittest.main()
