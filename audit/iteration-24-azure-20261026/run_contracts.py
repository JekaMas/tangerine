"""Use the existing speech dependency image; never install or call a provider."""
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
args=sys.argv[1:] or ['-m','unittest','-v','tests.test_azure_comparison']
raise SystemExit(subprocess.run(['docker','run','--rm','-e','PYTHONPATH=/repo/tests:/repo/services/speech','-v',str(ROOT)+':/repo:ro','-w','/repo','--entrypoint','python','tangerine-local-speech:local','-B',*args],cwd=ROOT).returncode)
