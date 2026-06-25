"""STNF tests: codec correctness (oracle) + label-free reach (static)."""
from papers.p1_toolmorph.stnf import (
    OracleCanonicalizer, StaticCanonicalizer, static_coverage_table)
from papers.p1_toolmorph.tasks import all_tasks
from papers.p1_toolmorph.transforms.dsl import apply_transform
from papers.p1_toolmorph.transforms.families import (
    LexicalAliasing, StructuralNesting, all_strict_transforms)


def _canonical_snapshot(task):
    env = task.env_factory(); env.reset()
    tools = {t.name: t for t in env.tools()}
    for tname, args in task.plan:
        tools[tname].executor(args)
    return env.snapshot()


def test_oracle_stnf_preserves_state_for_every_transform():
    """Routing a canonical call through oracle STNF reaches the env with a
    byte-identical state transition, for every strict family."""
    oc = OracleCanonicalizer()
    for transform in all_strict_transforms():
        for task in all_tasks():
            ref = _canonical_snapshot(task)
            env = task.env_factory(); env.reset()
            canon = {t.name: t for t in env.tools()}
            for tname, args in task.plan:
                norm = oc.normalize(canon[tname], transform)
                norm.presented.executor(args)  # agent uses canonical args
            assert env.snapshot() == ref, f"{transform.family}/{task.task_id}"


def test_static_stnf_covers_nesting_and_abstains_on_lexical():
    sc = StaticCanonicalizer()
    nesting = StructuralNesting()
    lexical = LexicalAliasing()
    for task in all_tasks():
        ref = _canonical_snapshot(task)
        # structural nesting: static unwraps -> canonical calls reach env
        env = task.env_factory(); env.reset()
        canon = {t.name: t for t in env.tools()}
        for tname, args in task.plan:
            deployed = apply_transform(canon[tname], nesting)
            norm = sc.normalize(deployed)
            assert norm.covered
            norm.presented.executor(args)
        assert env.snapshot() == ref
        # lexical: static cannot recover names -> abstains
        env2 = task.env_factory(); env2.reset()
        canon2 = {t.name: t for t in env2.tools()}
        first_tool = task.plan[0][0]
        deployed_lex = apply_transform(canon2[first_tool], lexical)
        assert sc.normalize(deployed_lex).covered is False


def test_static_coverage_is_honest():
    cov = static_coverage_table()
    assert cov["structural_nesting"] is True
    assert cov["response_representation"] is True
    assert cov["error_representation"] is True
    assert cov["lexical_aliasing"] is False
    assert cov["enum_encoding"] is False
    assert cov["optional_default"] is False
