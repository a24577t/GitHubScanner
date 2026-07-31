"""Scripted fan-out fixtures shared by the collection-seam tests.

One home for the descriptor endpoint paths, fixture response bodies, and the
org script the fan-out tests compose (Slice 2 T5/T8; Slice 3 T1 split at the
fixtures/tests responsibility boundary). Behavioral tests stay in their seam
files.
"""
from fake_github import response
from test_collect import META_OK, ORG_OK, RUN_ID, USER_OK

PROTECTION_BODY = {
    "enforce_admins": {"enabled": True},
    "required_pull_request_reviews": {"required_approving_review_count": 1},
}
ABSENCE_BODY = {"message": "Branch not protected"}


def protection_path(i, branch="main"):
    return f"/repos/acme/repo-{i}/branches/{branch}/protection"


def rulesets_path(i):
    return f"/repos/acme/repo-{i}/rulesets"


def rulesets_empty(*ids):
    """Scripted empty rulesets listings (the fixture default: V07)."""
    return {rulesets_path(i): [response(200, [])] for i in ids}


def security_path(i):
    return f"/repos/acme/repo-{i}"


def security_body(i):
    return {
        "id": i, "name": f"repo-{i}", "full_name": f"acme/repo-{i}",
        "visibility": "public",
        "security_and_analysis": {
            "secret_scanning": {"status": "disabled"},
            "secret_scanning_push_protection": {"status": "disabled"},
        },
    }


def security_ok(*ids):
    """Scripted dedicated repository GETs (the fixture default: disabled)."""
    return {security_path(i): [response(200, security_body(i))] for i in ids}


def org_script(repos, **endpoints):
    return {
        "/user": [USER_OK], "/meta": [META_OK], "/orgs/acme": [ORG_OK],
        "/orgs/acme/repos": [response(200, repos)],
        **endpoints,
    }


def raw_files(out):
    raw = out / "evidence" / "raw" / RUN_ID
    return sorted(str(p.relative_to(raw)).replace("\\", "/")
                  for p in raw.rglob("*") if p.is_file())
