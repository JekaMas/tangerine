"""Current full literal set graph; structural evidence, never behavior."""
from pathlib import Path
R=Path(__file__).resolve().parents[2]
code=(R/'audit/iteration-15-recovery-20261021/check_property_sets.py').read_text().replace("len(s['properties'])==672","len(s['properties'])==680").replace('iterations1.through15','iterations1.through16')
exec(compile(code,str(Path(__file__)),'exec'))
