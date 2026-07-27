"""Descriptor table integrity and projection (Slice 2 T1, ADR-0004/0005/0006)."""
import unittest

from collector import resources


class TableContract(unittest.TestCase):
    def test_default_branch_protection_is_first_in_table_order(self):
        self.assertEqual(
            resources.DESCRIPTORS[0]["name"], "default-branch-protection"
        )

    def test_default_branch_protection_request_contract(self):
        descriptor = resources.DESCRIPTORS[0]
        self.assertEqual(
            descriptor["path_template"],
            "/repos/{full_name}/branches/{default_branch}/protection",
        )
        self.assertEqual(descriptor["shape"], "object")
        self.assertEqual(descriptor["required_inputs"], ("default_branch",))
        self.assertEqual(descriptor["absence_message"], "Branch not protected")


def variant(**overrides):
    """The shipped protection descriptor with named fields replaced."""
    return {**resources.DEFAULT_BRANCH_PROTECTION, **overrides}


class TableIntegrity(unittest.TestCase):
    def test_shipped_table_passes_validation(self):
        resources.validate_table(resources.DESCRIPTORS)

    def test_duplicate_descriptor_names_are_rejected(self):
        table = (resources.DEFAULT_BRANCH_PROTECTION,
                 resources.DEFAULT_BRANCH_PROTECTION)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            resources.validate_table(table)

    def test_empty_table_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            resources.validate_table(())

    def test_malformed_descriptor_name_is_rejected(self):
        for bad in ("", "Has Spaces", "UPPER", "trailing."):
            with self.assertRaisesRegex(ValueError, "name"):
                resources.validate_table((variant(name=bad),))

    def test_unknown_shape_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "shape"):
            resources.validate_table((variant(shape="scalar"),))

    def test_path_placeholder_without_required_input_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "placeholder"):
            resources.validate_table((variant(required_inputs=()),))

    def test_required_input_missing_from_path_template_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "required input"):
            resources.validate_table(
                (variant(required_inputs=("default_branch", "unused")),)
            )

    def test_empty_projection_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "projection"):
            resources.validate_table((variant(projection=()),))

    def test_duplicate_projection_field_names_are_rejected(self):
        projection = (("branch", ("input", "default_branch")),
                      ("branch", ("input", "default_branch")))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            resources.validate_table((variant(projection=projection),))

    def test_unknown_projection_source_kind_is_rejected(self):
        projection = (("branch", ("telepathy", "default_branch")),)
        with self.assertRaisesRegex(ValueError, "source"):
            resources.validate_table((variant(projection=projection),))


# GitHub-documented protection body shape, standard-repo fixture values
# (one required approving review; strict checks with a single context).
FULL_PROTECTION_BODY = {
    "url": "https://api.github.com/repos/GHScannerLab/standard-repo/branches/main/protection",
    "required_status_checks": {
        "strict": True,
        "contexts": ["ci"],
        "checks": [{"context": "ci", "app_id": None}],
    },
    "required_pull_request_reviews": {
        "dismiss_stale_reviews": False,
        "require_code_owner_reviews": True,
        "required_approving_review_count": 1,
        "require_last_push_approval": False,
    },
    "required_signatures": {"enabled": False},
    "enforce_admins": {"enabled": True},
    "required_linear_history": {"enabled": False},
    "allow_force_pushes": {"enabled": False},
    "allow_deletions": {"enabled": False},
    "required_conversation_resolution": {"enabled": True},
    "lock_branch": {"enabled": False},
    "allow_fork_syncing": {"enabled": False},
}


def project_protection(body, inputs=None):
    return resources.project(resources.DEFAULT_BRANCH_PROTECTION, body, inputs)


class Projection(unittest.TestCase):
    project = staticmethod(project_protection)

    def test_full_body_projects_the_exact_spec_field_set(self):
        self.assertEqual(
            self.project(FULL_PROTECTION_BODY, {"default_branch": "main"}),
            {
                "branch": "main",
                "enforce_admins": True,
                "required_pull_request_reviews": {
                    "required_approving_review_count": 1,
                    "require_code_owner_reviews": True,
                    "dismiss_stale_reviews": False,
                },
                "required_status_checks": {"strict": True, "contexts_count": 1},
                "required_linear_history": False,
                "required_conversation_resolution": True,
                "required_signatures": False,
                "allow_force_pushes": False,
                "allow_deletions": False,
            },
        )


ALL_UNKNOWN = {
    "branch": "unknown",
    "enforce_admins": "unknown",
    "required_pull_request_reviews": {
        "required_approving_review_count": "unknown",
        "require_code_owner_reviews": "unknown",
        "dismiss_stale_reviews": "unknown",
    },
    "required_status_checks": {"strict": "unknown", "contexts_count": "unknown"},
    "required_linear_history": "unknown",
    "required_conversation_resolution": "unknown",
    "required_signatures": "unknown",
    "allow_force_pushes": "unknown",
    "allow_deletions": "unknown",
}


class ProjectionUnknowns(unittest.TestCase):
    project = staticmethod(project_protection)

    def test_empty_body_projects_the_exact_shape_all_unknown(self):
        self.assertEqual(self.project({}, {}), ALL_UNKNOWN)

    def test_non_dict_bodies_project_the_exact_shape_all_unknown(self):
        for body in (None, [FULL_PROTECTION_BODY], "protected", 7):
            self.assertEqual(self.project(body, {}), ALL_UNKNOWN)

    def test_missing_inputs_mapping_projects_branch_unknown(self):
        self.assertEqual(self.project({}, None), ALL_UNKNOWN)

    def test_partial_subobjects_keep_present_values_and_unknown_the_rest(self):
        body = {
            "required_pull_request_reviews": {"required_approving_review_count": 2},
            "required_status_checks": {"strict": False},
        }
        projected = self.project(body, {"default_branch": "trunk"})
        self.assertEqual(projected["branch"], "trunk")
        self.assertEqual(
            projected["required_pull_request_reviews"],
            {
                "required_approving_review_count": 2,
                "require_code_owner_reviews": "unknown",
                "dismiss_stale_reviews": "unknown",
            },
        )
        self.assertEqual(
            projected["required_status_checks"],
            {"strict": False, "contexts_count": "unknown"},
        )
        self.assertEqual(projected["enforce_admins"], "unknown")

    def test_enabled_wrapper_without_enabled_key_is_unknown(self):
        projected = self.project({"enforce_admins": {}}, {})
        self.assertEqual(projected["enforce_admins"], "unknown")

    def test_null_and_non_mapping_values_are_unknown(self):
        body = {
            "enforce_admins": None,
            "required_pull_request_reviews": {"required_approving_review_count": None},
            "required_status_checks": "everything",
        }
        projected = self.project(body, {})
        self.assertEqual(projected["enforce_admins"], "unknown")
        self.assertEqual(
            projected["required_pull_request_reviews"]
            ["required_approving_review_count"],
            "unknown",
        )
        self.assertEqual(
            projected["required_status_checks"],
            {"strict": "unknown", "contexts_count": "unknown"},
        )

    def test_non_list_contexts_is_unknown(self):
        body = {"required_status_checks": {"contexts": "ci"}}
        projected = self.project(body, {})
        self.assertEqual(projected["required_status_checks"]["contexts_count"],
                         "unknown")

    def test_false_and_zero_values_are_preserved_never_unknown(self):
        body = {
            "required_status_checks": {"strict": False, "contexts": []},
            "required_pull_request_reviews": {"required_approving_review_count": 0},
            "allow_force_pushes": {"enabled": False},
        }
        projected = self.project(body, {})
        self.assertEqual(
            projected["required_status_checks"],
            {"strict": False, "contexts_count": 0},
        )
        self.assertEqual(
            projected["required_pull_request_reviews"]
            ["required_approving_review_count"],
            0,
        )
        self.assertIs(projected["allow_force_pushes"], False)


if __name__ == "__main__":
    unittest.main()
