"""The security-and-analysis descriptor at the pure projection seam (Slice 3 T1).

ADR-0009's dedicated-request realization: the shared Secret Scanning / Push
Protection evidence surface ships as one declarative descriptor in
resources.py alone — both status fields from T1 so T5 adds no descriptor
change — and every engine consumes it unchanged. These tests pin the request
contract and the projection behavior the ticket's rows govern: V41's offline
aspect (real values project verbatim onto the declared surface), V50 (absent
surface projects unknown, never a disablement claim), V51 (unrecognized
values pass through, never coerced).
"""
import unittest

from collector import resources

# GitHub-documented repository metadata shape (standard-repo fixture values);
# the extra metadata and control fields prove the projection observes only
# the declared surface.
REPO_METADATA_BODY = {
    "id": 5,
    "name": "standard-repo",
    "full_name": "GHScannerLab/standard-repo",
    "private": False,
    "visibility": "public",
    "fork": False,
    "archived": False,
    "default_branch": "main",
    "security_and_analysis": {
        "secret_scanning": {"status": "enabled"},
        "secret_scanning_push_protection": {"status": "disabled"},
        "dependabot_security_updates": {"status": "disabled"},
        "secret_scanning_non_provider_patterns": {"status": "disabled"},
        "secret_scanning_validity_checks": {"status": "disabled"},
    },
}


def projected(body):
    return resources.project(resources.SECURITY_AND_ANALYSIS, body)


def status_pair(document):
    surface = document["security_and_analysis"]
    return (surface["secret_scanning"]["status"],
            surface["secret_scanning_push_protection"]["status"])


class TableContract(unittest.TestCase):
    def test_security_and_analysis_is_third_in_table_order(self):
        self.assertEqual([d["name"] for d in resources.DESCRIPTORS],
                         ["default-branch-protection", "repository-rulesets",
                          "security-and-analysis"])

    def test_request_contract_is_the_dedicated_repository_get(self):
        # ADR-0009's dedicated-request decision (issue #27): the shared
        # surface is its own request, never a projection of the inventory.
        descriptor = resources.SECURITY_AND_ANALYSIS
        self.assertEqual(descriptor["path_template"], "/repos/{full_name}")
        self.assertEqual(descriptor["shape"], "object")
        self.assertEqual(descriptor["required_inputs"], ())

    def test_no_absence_anchor_metadata_has_no_absence_class(self):
        # A 404 must classify inaccessible · absence-rule-unmatched-404
        # (ADR-0006, V54's evidence half), which requires the anchor unset.
        self.assertIsNone(resources.SECURITY_AND_ANALYSIS["absence_message"])

    def test_shipped_table_with_three_descriptors_validates(self):
        resources.validate_table(resources.DESCRIPTORS)


class SecurityAnalysisProjection(unittest.TestCase):
    def test_v41_real_values_project_verbatim_and_extras_drop(self):
        self.assertEqual(projected(REPO_METADATA_BODY), {
            "visibility": "public",
            "security_and_analysis": {
                "secret_scanning": {"status": "enabled"},
                "secret_scanning_push_protection": {"status": "disabled"},
            },
        })

    def test_v50_absent_surface_projects_unknown_statuses(self):
        # Absence of the surface is undetermined data, never disablement
        # (ADR-0008); visibility still projects.
        body = {key: value for key, value in REPO_METADATA_BODY.items()
                if key != "security_and_analysis"}
        self.assertEqual(projected(body), {
            "visibility": "public",
            "security_and_analysis": {
                "secret_scanning": {"status": "unknown"},
                "secret_scanning_push_protection": {"status": "unknown"},
            },
        })

    def test_absent_control_subobject_leaves_the_sibling_intact(self):
        body = {**REPO_METADATA_BODY,
                "security_and_analysis": {
                    "secret_scanning": {"status": "enabled"}}}
        self.assertEqual(status_pair(projected(body)), ("enabled", "unknown"))

    def test_v51_unrecognized_values_project_verbatim_never_coerced(self):
        for value in ("paused", 5, "", False, 0, "ENABLED"):
            body = {**REPO_METADATA_BODY,
                    "security_and_analysis": {
                        "secret_scanning": {"status": value},
                        "secret_scanning_push_protection": {"status": value}}}
            self.assertEqual(status_pair(projected(body)), (value, value))

    def test_null_statuses_and_null_visibility_are_unknown(self):
        body = {**REPO_METADATA_BODY, "visibility": None,
                "security_and_analysis": {
                    "secret_scanning": {"status": None},
                    "secret_scanning_push_protection": None}}
        document = projected(body)
        self.assertEqual(document["visibility"], "unknown")
        self.assertEqual(status_pair(document), ("unknown", "unknown"))

    def test_non_dict_bodies_project_the_exact_shape_all_unknown(self):
        for body in (None, 7, "repo", [], True):
            self.assertEqual(projected(body), {
                "visibility": "unknown",
                "security_and_analysis": {
                    "secret_scanning": {"status": "unknown"},
                    "secret_scanning_push_protection": {"status": "unknown"},
                },
            })

    def test_non_dict_control_surfaces_project_unknown_never_coerced(self):
        for surface in ("enabled", 5, ["enabled"], True):
            body = {**REPO_METADATA_BODY, "security_and_analysis": surface}
            self.assertEqual(status_pair(projected(body)),
                             ("unknown", "unknown"))


if __name__ == "__main__":
    unittest.main()
