"""Canonical target discovery and evidence addressing (ADR-0005)."""
import re

from collector.taxonomy import body_of, shape_ok

# --- Canonical target discovery -------------------------------------------
# One rule, shared verbatim by collection planning and offline rederivation:
# inventory pages in page order, items in source order, eligibility before
# deduplication, first eligible occurrence per repository ID winning; the
# resulting target set iterates ascending by repository ID.


def _valid_identity(full_name):
    if not isinstance(full_name, str):
        return False
    owner, sep, name = full_name.partition("/")
    return bool(sep and owner and name) and "/" not in name


def _eligible(item):
    repo_id = item.get("id")
    return (isinstance(repo_id, int) and not isinstance(repo_id, bool)
            and repo_id > 0 and _valid_identity(item.get("full_name")))


def discover_targets(page_records):
    """The canonical ordered target set from raw inventory page records.

    Malformed identity is never repaired, inferred, or synthesized; an earlier
    malformed occurrence of an ID never suppresses a later eligible one.
    """
    by_id = {}
    for record in page_records:
        if record is None:
            continue
        body = body_of(record)
        if not (200 <= record["envelope"]["status"] < 300
                and shape_ok(body, "object_array")):
            continue
        for item in body:
            if _eligible(item) and item["id"] not in by_id:
                by_id[item["id"]] = {
                    "id": item["id"],
                    "full_name": item["full_name"],
                    "name": item.get("name"),
                    "inventory_item": item,
                }
    return tuple(by_id[repo_id] for repo_id in sorted(by_id))


def descriptor_inputs(target, descriptor):
    """Required inputs, evaluated only after eligibility (ADR-0005).

    A usable input is a non-empty string from the target's inventory item;
    anything else is missing — never repaired, inferred, or defaulted.
    Returns (values, missing_input_names).
    """
    item = target["inventory_item"]
    values, missing = {}, []
    for name in descriptor["required_inputs"]:
        value = item.get(name)
        if isinstance(value, str) and value:
            values[name] = value
        else:
            missing.append(name)
    return values, tuple(missing)


# --- Evidence addressing ---------------------------------------------------
# Filesystem paths are scanner-defined storage addresses, never evidence of
# GitHub facts. The repository ID is the addressing key; the annotation is
# non-evidentiary and never affects eligibility or any observed state.

# Annotation-safety rule (spec: scanner-defined, deliberately conservative).
# A trailing "." is excluded separately; ID-keyed directories already defuse
# reserved device names, which is why ADR-0005 rejected name-keyed layouts.
_ANNOTATION = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")


def directory_key(repo_id, name):
    """`<repo-id>[-<name-annotation>]`: annotation verbatim or omitted."""
    if isinstance(name, str) and _ANNOTATION.match(name) and not name.endswith("."):
        return f"{repo_id}-{name}"
    return str(repo_id)


# --- Structural validation -------------------------------------------------
# Paths may be examined for storage addressing and structural validation, but
# never used as the authoritative source of an observed GitHub fact.

# The scanner writes IDs as canonical positive integers, so a recognized
# directory is <digits-without-leading-zero>[-<annotation>].
_DIRECTORY = re.compile(r"^([1-9][0-9]*)(?:-(.+))?$")


def claimed_repository_id(directory_name):
    """The repository ID a directory name claims, or None if unrecognized.

    The annotation never participates in the claim.
    """
    match = _DIRECTORY.match(directory_name)
    return int(match.group(1)) if match else None


def structural_conflicts(claims):
    """Detect structural evidence conflicts (ADR-0005) deterministically.

    ``claims`` is an iterable of ``(directory_name, envelope_repository_ids)``
    pairs — the enclosed envelopes' repository IDs as found, unrepaired.
    Duplicate directory claims on one ID and any path/envelope disagreement
    are conflicts: no winner is selected, nothing deduplicates silently, and
    every affected directory is reported so no affected evidence can surface
    as an apparently valid observation.
    """
    directories_by_id, mismatched, unrecognized = {}, [], []
    for directory_name, envelope_ids in claims:
        claimed = claimed_repository_id(directory_name)
        if claimed is None:
            unrecognized.append(directory_name)
            continue
        directories_by_id.setdefault(claimed, []).append(directory_name)
        if any(envelope_id != claimed for envelope_id in envelope_ids):
            mismatched.append(directory_name)
    duplicate_ids = tuple(sorted(
        repo_id for repo_id, dirs in directories_by_id.items() if len(dirs) > 1
    ))
    conflicted = set(mismatched)
    for repo_id in duplicate_ids:
        conflicted.update(directories_by_id[repo_id])
    return {
        "duplicate_ids": duplicate_ids,
        "mismatched_directories": tuple(sorted(mismatched)),
        "unrecognized_directories": tuple(sorted(unrecognized)),
        "conflicted_directories": tuple(sorted(conflicted)),
    }
