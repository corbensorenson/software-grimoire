import json
from pathlib import PurePosixPath


def load_handoff():
    return json.loads(open("handoff.json", encoding="utf-8").read())


def assert_repo_local(path):
    parsed = PurePosixPath(path)
    assert not parsed.is_absolute()
    assert path.startswith("tmp/")


def test_scratch_paths_are_repo_local():
    handoff = load_handoff()
    assert_repo_local(handoff["scratch_root"])
    for artifact in handoff["artifacts"]:
        assert_repo_local(artifact["path"])


def test_all_steps_use_declared_allowlist():
    handoff = load_handoff()
    allowlist = set(handoff["allowlist"])
    assert allowlist == {"read-fixture", "write-artifact", "run-tests", "record-evidence"}
    for step in handoff["steps"]:
        assert step["tool"] in allowlist


def test_required_gates_have_evidence():
    handoff = load_handoff()
    gates = {gate["name"]: gate for gate in handoff["gates"]}
    assert {"preflight", "execution", "evidence"} <= set(gates)
    for gate in gates.values():
        assert gate["passed"] is True
        assert gate["evidence"]


def test_handoff_does_not_claim_human_approval():
    handoff = load_handoff()
    assert handoff["final_status"] == "ready-for-human-review"
    assert handoff["human_signoff"] == "pending"
