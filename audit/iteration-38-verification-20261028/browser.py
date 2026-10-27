"""Reuse I38's actual application/Chrome harness with fresh verification evidence."""
import importlib.util,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
path=ROOT/'audit/iteration-38-empirical-20261027/browser.py'
spec=importlib.util.spec_from_file_location('i38_browser_owner',path)
owner=importlib.util.module_from_spec(spec)
spec.loader.exec_module(owner)
owner.OUT=ROOT/'data/iteration-38-verification-20261028'
if __name__=='__main__':
    raise SystemExit(owner.main('--coverage' in sys.argv or '--coverage-visual' in sys.argv,'--coverage-visual' in sys.argv))
