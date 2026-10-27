"""Reuse I36's real private stack/GET-only gateway for new verification cases."""
import argparse,importlib.util,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['red','green','regression','regression-fixed','visual','states']);args=parser.parse_args()
spec=importlib.util.spec_from_file_location('jfleg_browser',ROOT/'audit/iteration-36-jfleg-20261027/browser.py')
browser=importlib.util.module_from_spec(spec);spec.loader.exec_module(browser)
folder=ROOT/('data/iteration-36-verification-20261027/browser-'+args.phase)
if folder.exists():raise RuntimeError('Keep the original observation; use another evidence folder for a repair run')
os.environ['TANGERINE_JFLEG_VERIFY_FIXTURES']=str(ROOT/'data/iteration-36-verification-20261027/verify-ui-fixtures.json')
os.environ['TANGERINE_JFLEG_NATIVE_EXPECTED']=str(ROOT/'data/iteration-36-jfleg-20261027/native-expected.json')
program={'regression':'tests/jfleg_browser.cjs','regression-fixed':'tests/jfleg_browser.cjs','visual':'tests/jfleg_visual.cjs','states':'tests/jfleg_empty_visual.cjs'}.get(args.phase,'tests/jfleg_verify_browser.cjs')
sys.exit(browser.main(program=program,folder=folder,image='tangerine-i36-web' if args.phase=='red' else 'tangerine-i36-verify-web'))
