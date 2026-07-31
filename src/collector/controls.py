"""Security Control definitions: declarative table + pure plane rules (ADR-0008/0009)."""
import re

from collector.resources import DESCRIPTORS

_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_DESCRIPTOR_NAMES = frozenset(entry["name"] for entry in DESCRIPTORS)

# Closed plane vocabularies for this slice's boolean-enablement controls:
# `unavailable` is excluded (grill condition 2), the configuration triple is
# unreachable, and `not-applicable` awaits affirmative inapplicability
# evidence (ADR-0009 deferrals).
OPERATIONAL_STATES = frozenset(
    {"enabled", "disabled", "inaccessible", "unknown"})
APPLICABILITY_STATES = frozenset({"applicable", "applicability-unknown"})

SECRET_SCANNING = {
    "name": "secret-scanning",
    "descriptor": "security-and-analysis",
    "status_path": ("security_and_analysis", "secret_scanning", "status"),
    "applicability": "visibility",
}

CONTROLS = (SECRET_SCANNING,)


def _valid_applicability(kind):
    """The closed applicability-kind vocabulary: "visibility", or
    ("chain", <control declared earlier in the table>) — table order is the
    single deterministic evaluation pass, so a chain target must precede its
    dependent (T5's definition-only additivity, ADR-0009)."""
    if kind == "visibility":
        return True
    return (isinstance(kind, tuple) and len(kind) == 2 and kind[0] == "chain"
            and isinstance(kind[1], str) and bool(kind[1]))


def validate_controls(table):
    """Reject a malformed control table loudly; a valid table returns None."""
    if not table:
        raise ValueError("control table is empty")
    names = set()
    for definition in table:
        name = definition.get("name")
        if not isinstance(name, str) or not _NAME.match(name):
            raise ValueError(f"malformed control name: {name!r}")
        if name in names:
            raise ValueError(f"duplicate control name: {name!r}")
        descriptor = definition.get("descriptor")
        if descriptor not in _DESCRIPTOR_NAMES:
            raise ValueError(
                f"{name}: unknown evidence descriptor {descriptor!r}")
        path = definition.get("status_path")
        if (not isinstance(path, tuple) or not path or not all(
                isinstance(key, str) and key for key in path)):
            raise ValueError(
                f"{name}: status_path must be a non-empty tuple of names")
        kind = definition.get("applicability")
        if not _valid_applicability(kind):
            raise ValueError(f"{name}: unknown applicability rule {kind!r}")
        if isinstance(kind, tuple) and kind[1] not in names:
            raise ValueError(f"{name}: chains on unknown control {kind[1]!r}")
        names.add(name)


validate_controls(CONTROLS)
