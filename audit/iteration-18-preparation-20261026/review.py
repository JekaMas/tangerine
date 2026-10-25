"""Development-only review predicates over actual observed UI facts."""
import importlib.util
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('i17_review',ROOT/'audit/iteration-17-reconciliation-20261025/verify.py')
i17=importlib.util.module_from_spec(spec);spec.loader.exec_module(i17)
def px(value):return float(value.removesuffix('px'))
def contrast(foreground,background):
    def luminance(value):
        colors=[int(n)/255 for n in re.findall(r'\d+',value)[:3]]
        linear=[x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4 for x in colors]
        return sum(x*y for x,y in zip(linear,[0.2126,0.7152,0.0722]))
    a,b=sorted([luminance(foreground),luminance(background)])
    return (b+0.05)/(a+0.05)
def readability_issues(facts):
    issues=[]
    if facts.get('overflow'):issues.append('page overflow')
    if not facts.get('loaded'):issues.append('font not loaded')
    if facts.get('body',{}).get('size')!='17px':issues.append('body scale changed')
    if not facts.get('nodes'):issues.append('caption observations missing')
    for n in facts.get('nodes',[]):
        if px(n['size'])<13:issues.append('caption below13px: '+n['text'])
        if n['scrollWidth']>n['width']+1 or n['height']<=0:issues.append('clipped caption: '+n['text'])
        if contrast(n['color'],n['background'])<4.5:issues.append('low-contrast caption: '+n['text'])
    return issues

def review_errors(packet,facts,view,submitted):
    errors=i17.review_errors(packet)
    errors+=readability_issues(facts)
    if packet.get('unexecuted_cases'):errors.append('unexecuted cases cannot pass')
    if packet.get('reference_origin')!='independently authored literal expectations':errors.append('unsupported reference origin')
    if view['topic']!=submitted['topic'] or view['fields']['Mistakes']!=str(submitted['mutation_count']):errors.append('view and submitted request differ')
    return errors
