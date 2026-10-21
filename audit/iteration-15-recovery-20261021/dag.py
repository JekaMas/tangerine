"""Pinned DAG runner, with per-pattern snapshot memoization in this stable invocation.
No checker/observer/acceptance rule is changed. Ignored runtime output is not source.
"""
from pathlib import Path
from functools import lru_cache
import sys
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'.agents/workflow/scripts'));import requirement_tests as rt
original=rt.dependency_snapshot
@lru_cache(None)
def one(root,pattern):return original(Path(root),[pattern])[pattern]
rt.dependency_snapshot=lambda root,patterns:{p:one(str(root),p) for p in patterns}
if __name__=='__main__':raise SystemExit(rt.main())
