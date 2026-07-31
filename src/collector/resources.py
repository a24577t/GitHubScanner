"""Repository resource descriptors: declarative observation table (ADR-0004/0005/0006)."""
import re

_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_PLACEHOLDER = re.compile(r"\{([^{}]+)\}")
# Slice 1 taxonomy shape vocabulary; "object_array" identifies a paginated listing drain.
_SHAPES = frozenset({"object", "object_array"})
_SOURCE_KINDS = frozenset(
    {"input", "field", "enabled", "count", "object", "length", "items"})

PROTECTION_PROJECTION = (
    ("branch", ("input", "default_branch")),
    ("enforce_admins", ("enabled", "enforce_admins")),
    ("required_pull_request_reviews", ("object", "required_pull_request_reviews", (
        ("required_approving_review_count",
         ("field", "required_approving_review_count")),
        ("require_code_owner_reviews", ("field", "require_code_owner_reviews")),
        ("dismiss_stale_reviews", ("field", "dismiss_stale_reviews")),
    ))),
    ("required_status_checks", ("object", "required_status_checks", (
        ("strict", ("field", "strict")),
        ("contexts_count", ("count", "contexts")),
    ))),
    ("required_linear_history", ("enabled", "required_linear_history")),
    ("required_conversation_resolution",
     ("enabled", "required_conversation_resolution")),
    ("required_signatures", ("enabled", "required_signatures")),
    ("allow_force_pushes", ("enabled", "allow_force_pushes")),
    ("allow_deletions", ("enabled", "allow_deletions")),
)

DEFAULT_BRANCH_PROTECTION = {
    "name": "default-branch-protection",
    "path_template": "/repos/{full_name}/branches/{default_branch}/protection",
    "shape": "object",
    "required_inputs": ("default_branch",),
    # Absence anchor (ADR-0006): 404 + shape-valid JSON + this exact message;
    # re-pinned by each validation run.
    "absence_message": "Branch not protected",
    "projection": PROTECTION_PROJECTION,
}

RULESET_SUMMARY = (
    ("id", ("field", "id")),
    ("name", ("field", "name")),
    ("target", ("field", "target")),
    ("enforcement", ("field", "enforcement")),
    ("created_at", ("field", "created_at")),
)

REPOSITORY_RULESETS = {
    "name": "repository-rulesets",
    # Observes the repository's own rulesets inventory - summary information
    # only. Organization-owned rulesets are a different resource, excluded by
    # descriptor coherence (includes_parents=false; exact parameter behavior
    # pinned by the validation run). Emptiness is a value, never absence.
    "path_template": "/repos/{full_name}/rulesets?includes_parents=false",
    "shape": "object_array",
    "required_inputs": (),
    "absence_message": None,
    "projection": (("count", ("length",)),
                   ("rulesets", ("items", "id", RULESET_SUMMARY))),
}

SECURITY_ANALYSIS_PROJECTION = (
    ("visibility", ("field", "visibility")),
    ("security_and_analysis", ("object", "security_and_analysis", (
        ("secret_scanning", ("object", "secret_scanning", (
            ("status", ("field", "status")),
        ))),
        ("secret_scanning_push_protection",
         ("object", "secret_scanning_push_protection", (
             ("status", ("field", "status")),
         ))),
    ))),
)

SECURITY_AND_ANALYSIS = {
    "name": "security-and-analysis",
    # Observes only the repository metadata object's visibility and
    # security_and_analysis surface via ADR-0009's dedicated request (issue
    # #27 decision) - no claim about other metadata, organization security
    # configuration, or scanning activity. Both controls' status fields ship
    # together so the T5 push-protection control adds no descriptor change.
    # No absence anchor: a discovered repository's metadata object has no
    # affirmative-absence class; a 404 derives inaccessible ·
    # absence-rule-unmatched-404 (ADR-0006). Absence of the surface in a
    # collected body is undetermined data, never disablement (ADR-0008).
    "path_template": "/repos/{full_name}",
    "shape": "object",
    "required_inputs": (),
    "absence_message": None,
    "projection": SECURITY_ANALYSIS_PROJECTION,
}

DESCRIPTORS = (DEFAULT_BRANCH_PROTECTION, REPOSITORY_RULESETS,
               SECURITY_AND_ANALYSIS)


def _validate_projection(name, entries, seen):
    for field, source in entries:
        if not isinstance(field, str) or not field:
            raise ValueError(f"{name}: projection field name must be a non-empty string")
        if field in seen:
            raise ValueError(f"{name}: duplicate projection field {field!r}")
        seen.add(field)
        kind = source[0]
        if kind not in _SOURCE_KINDS:
            raise ValueError(f"{name}: unknown projection source kind {kind!r}")
        if kind == "object":
            _validate_projection(name, source[2], set())
        if kind == "items":
            if not isinstance(source[1], str) or not source[1]:
                raise ValueError(f"{name}: items sort key must be a non-empty string")
            if not source[2]:
                raise ValueError(f"{name}: items projection must be a non-empty sequence")
            _validate_projection(name, source[2], set())


def validate_table(table):
    """Reject a malformed descriptor table loudly; a valid table returns None."""
    if not table:
        raise ValueError("descriptor table is empty")
    names = set()
    for descriptor in table:
        name = descriptor.get("name")
        if not isinstance(name, str) or not _NAME.match(name):
            raise ValueError(f"malformed descriptor name: {name!r}")
        if name in names:
            raise ValueError(f"duplicate descriptor name: {name!r}")
        names.add(name)
        if descriptor.get("shape") not in _SHAPES:
            raise ValueError(f"{name}: unknown shape {descriptor.get('shape')!r}")
        template = descriptor.get("path_template")
        if not isinstance(template, str) or not template.startswith("/"):
            raise ValueError(f"{name}: path_template must be a string starting with '/'")
        inputs = descriptor.get("required_inputs")
        if not isinstance(inputs, tuple) or not all(
            isinstance(item, str) and item for item in inputs
        ):
            raise ValueError(f"{name}: required_inputs must be a tuple of names")
        placeholders = set(_PLACEHOLDER.findall(template)) - {"full_name"}
        for placeholder in sorted(placeholders - set(inputs)):
            raise ValueError(
                f"{name}: path placeholder {{{placeholder}}} is neither "
                "full_name nor a required input"
            )
        for unused in sorted(set(inputs) - placeholders):
            raise ValueError(
                f"{name}: required input {unused!r} does not appear in the path template"
            )
        absence = descriptor.get("absence_message")
        if absence is not None and (not isinstance(absence, str) or not absence):
            raise ValueError(f"{name}: absence_message must be None or a non-empty string")
        projection = descriptor.get("projection")
        if not projection:
            raise ValueError(f"{name}: projection must be a non-empty sequence")
        _validate_projection(name, projection, set())


validate_table(DESCRIPTORS)


UNKNOWN = "unknown"


def _item_key(item, key_field):
    """Deterministic item ordering: integer keys ascending, then everything
    else by string form (the repositories.json sort precedent); ties keep
    source order via sort stability."""
    key = item.get(key_field) if isinstance(item, dict) else None
    if isinstance(key, int):
        return (False, key)
    return (True, str(key))


def _value(source, mapping, inputs):
    """Undetermined values are 'unknown'; False and 0 are values, never unknown."""
    kind = source[0]
    if kind == "input":
        value = inputs.get(source[1]) if isinstance(inputs, dict) else None
        return UNKNOWN if value is None else value
    if kind == "length":
        return len(mapping) if isinstance(mapping, list) else UNKNOWN
    if kind == "items":
        if not isinstance(mapping, list):
            return UNKNOWN
        return [
            {field: _value(entry, item, inputs) for field, entry in source[2]}
            for item in sorted(mapping,
                               key=lambda item: _item_key(item, source[1]))
        ]
    value = mapping.get(source[1]) if isinstance(mapping, dict) else None
    if kind == "field":
        return UNKNOWN if value is None else value
    if kind == "enabled":
        enabled = value.get("enabled") if isinstance(value, dict) else None
        return UNKNOWN if enabled is None else enabled
    if kind == "count":
        return len(value) if isinstance(value, list) else UNKNOWN
    return {field: _value(entry, value, inputs) for field, entry in source[2]}


def project(descriptor, body, inputs=None):
    """Project a response body onto the descriptor's exact field set."""
    return {
        field: _value(source, body, inputs)
        for field, source in descriptor["projection"]
    }
