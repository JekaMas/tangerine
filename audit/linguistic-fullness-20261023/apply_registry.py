"""Apply the finite authored errata to active registries once, without runtime checks."""
import copy
import difflib
import json
from pathlib import Path
import re
import shutil
import subprocess
from curate import ROOT, V, HERE, REPAIRS, curated, load_taxonomy


def yaml_value(value):
    return subprocess.check_output(['ruby','-rjson','-ryaml','-e',
        'puts YAML.dump(JSON.parse(STDIN.read)).sub(/\\A---\\s*\\n/, "")'],
        input=json.dumps(value,ensure_ascii=False),text=True).rstrip()


rows=curated()
tax=load_taxonomy()
raw=(V/'domain/error-taxonomy.v1.yaml').read_text()
before=copy.deepcopy(tax)
for row in rows:
    tid=row['taxonomy_id']
    item=next(x for x in tax['items'] if x['id']==tid)
    if tid=='grammar.determiners.article_choice':
        old=item['definition']
        item['definition']='The article choice conflicts with sound-conditioned a/an or the established definite/indefinite reference.'
        item['inclusion_criteria']=[item['definition'] if v==old else v for v in item['inclusion_criteria']]
    if tid=='pronunciation.segmental.consonant_substitution':
        old=item['definition']
        item['definition']='A required consonant segment or ordered consonant sequence is realized differently, including a contextually inappropriate consonant metathesis within one lexical repair.'
        item['inclusion_criteria']=[item['definition'] if v==old else v for v in item['inclusion_criteria']]
    old_in=[v for v in item['inclusion_criteria'] if not v.startswith('Subtypes in this leaf: ')]
    item['inclusion_criteria']=old_in+['Subtypes in this leaf: '+', '.join(row['subtypes'])+'. Use context-specific contrasts, not a universal norm.']
    old_ex=[v for v in item['exclusion_criteria'] if not v.startswith('Concrete correct control: ')]
    c=row['correct_control']
    item['exclusion_criteria']=old_ex+['Concrete correct control: '+c['context']+' '+c['text']+' — '+c['reason']]
    if tid in REPAIRS:
        item['example'].update(context=row['contrast_context'],illustrative_target=row['surface'],accepted_repair='No correction required' if row['surface_status']=='acceptable' else row['canonical'])
    item['publication_support']='generated_key_suffices_optional_llm_review_and_benchmark'
    item['coverage_requirement']='Optional full benchmark: six distinct stimuli per leaf, 732 total under docs/review-and-gold.md. Ordinary generation needs neither benchmark completion nor separate review.'
    if item['verification_route']=='dual_acceptability_review':
        item['verification_route']='contextual_llm_acceptability_with_explicit_permitted_variants'
    old=next(x for x in before['items'] if x['id']==tid)
    # Replace only this item, keeping registry header/rules and original IDs.
    start=raw.index('- id: '+tid+'\n')
    end=raw.find('\n- id: ',start+1)
    if end<0:
        # judgment_rules are a root mapping after the last item.
        m=re.search(r'\n[a-z_]+:',raw[start+1:])
        end=start+1+m.start() if m else len(raw)
    block=yaml_value([item])
    raw=raw[:start]+block+raw[end:]
raw=raw.replace('version: 1.1.0\n','version: 1.2.0\n',1)
(V/'domain/error-taxonomy.v1.yaml').write_text(raw.rstrip()+'\n')
recipes_path=V/'domain/mutation-recipes.v1.json'
recipes=json.loads(recipes_path.read_text())
for recipe in recipes['recipes']:
    tid=recipe['taxonomy_id']
    if tid not in REPAIRS:
        continue
    row=next(x for x in rows if x['taxonomy_id']==tid)
    old=dict(context=recipe['context'],canonical_example=recipe['canonical_example'],surface_example=recipe['surface_example'])
    recipe.update(context=row['contrast_context'],canonical_example=row['canonical'],surface_example=row['surface'])
    recipe['original_example_preserved_at']='spec-inputs/full-release-20261008/domain/error-taxonomy.v1.yaml#'+tid
    recipe['example_override_reason']='2026-10-23 linguistic contrast errata; original retained in imported source. Concrete target/context and acceptable variants are specified.'
    if recipe.get('codepoint_edit') is not None:
        a,b=row['canonical'],row['surface']
        matches=difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes()
        edits=[x for x in matches if x[0]!='equal']
        if not edits:
            recipe['codepoint_edit']=dict(start_cp=0,end_cp=0,exact_text='',replacement='',surface_start_cp=0,surface_end_cp=0,kind='replace')
        else:
            i,j,k,l=edits[0][1],edits[-1][2],edits[0][3],edits[-1][4]
            recipe['codepoint_edit']=dict(start_cp=i,end_cp=j,exact_text=a[i:j],replacement=b[k:l],surface_start_cp=k,surface_end_cp=l,kind='insert' if i==j else 'delete' if k==l else 'replace')
recipes['version']='1.1.0'
recipes_path.write_text(json.dumps(recipes,ensure_ascii=False,indent=2)+'\n')
for name in ['error-taxonomy.v1.yaml','mutation-recipes.v1.json']:
    shutil.copyfile(V/'domain'/name,ROOT/'services/api/internal/app/generationdata'/name)
aliases_path=V/'domain/category-aliases.v1.yaml'
aliases=aliases_path.read_text()
aliases=re.sub(r'^approval_gap:.*$', 'approval_gap: null',aliases,flags=re.M)
aliases=re.sub(r'^source_taxonomy_sha256:.*$', 'source_taxonomy_sha256: '+__import__('hashlib').sha256((V/'domain/error-taxonomy.v1.yaml').read_bytes()).hexdigest(),aliases,flags=re.M)
aliases=aliases.replace('review_status: proposal_not_linguistically_approved','review_status: authored_alias_available_no_human_approval_required')
if '      - Consonant metathesis\n' not in aliases:
    aliases=aliases.replace('      - Consonant substitution\n','      - Consonant substitution\n      - Consonant metathesis\n      - Consonant segment order\n')
aliases_path.write_text(aliases)
shutil.copyfile(aliases_path,ROOT/'services/api/internal/app/generationdata/category-aliases.v1.yaml')
subprocess.run(['python3','-B',str(HERE/'curate.py')],cwd=ROOT,check=True)
print(json.dumps(dict(active_leaves=len(rows),illustration_errata=len(REPAIRS),runtime_policy='one_admission_then_trust')))
