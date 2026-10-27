// Readable projections of saved measurements. Never infer missing observations.
export const count=value=>new Intl.NumberFormat('en-GB').format(value);
const reasons={leaf_annotation_scope_not_declared:'This category was not fully annotated.',correct_opportunity_annotations_absent:'Correct-use opportunities were not counted.',native_token_exposure_unknown:'The relevant word count is not available.',no_inspected_denominator:'No eligible observations were counted for this measurement.',pair_annotation_scope_not_declared:'These categories were not fully annotated together.'};
export function readableMetric(metric,kind='percent') {
  if(!metric||metric.missing_reason||!metric.exact)return {value:'Not measured',basis:reasons[metric?.missing_reason]||'The required observations are not available.'};
  const n=Number(metric.numerator),d=Number(metric.denominator),ratio=Number(metric.exact.numerator)/Number(metric.exact.denominator);
  const shown=new Intl.NumberFormat('en-GB',ratio&&Math.abs(ratio)<.001?{maximumSignificantDigits:3}:{maximumFractionDigits:2}).format(kind==='percent'?ratio*100:ratio);
  return {value:shown+(kind==='percent'?'%':kind==='lift'?' times':''),basis:kind==='lift'?'Compared with separate occurrence rates.':`${count(n)} out of ${count(d)}${kind==='density'?' (scaled to 1,000 words)':''}`};
}
const nativeNames={s:'Phone substitution',d:'Phone deletion',a:'Phone addition',noop:'No change',UNK:'Unresolved annotation',Um:'Unresolved annotation'};
const pos={ADJ:'Adjective',ADV:'Adverb',CONJ:'Conjunction',CONTR:'Contraction',DET:'Determiner',MORPH:'Word form',NOUN:'Noun',ORTH:'Capitalisation or spelling',OTHER:'Other',PART:'Particle',PREP:'Preposition',PRON:'Pronoun',PUNCT:'Punctuation',SPELL:'Spelling',VERB:'Verb',WO:'Word order'};
const detail={SVA:'agreement',NUM:'number',TENSE:'tense',FORM:'form',INFL:'inflection',POSS:'possessive'};
export function nativeName(label) {
  if(nativeNames[label])return nativeNames[label];
  const [operation,part,sub]=label.split(':');
  if(['R','M','U'].includes(operation)&&pos[part])return `${pos[part]}${detail[sub]?' '+detail[sub]:''} — ${operation==='M'?'missing':operation==='U'?'unnecessary':'changed'}`;
  return 'Other source annotation';
}
export function categoryName(id,labels={}) {return labels[id]||id.split('.').at(-1).replaceAll('_',' ').replace(/^./,s=>s.toUpperCase());}
export function sourceExclusion(reason) {return {noop:'No-change annotations',invalid:'Annotations with unusable positions',unresolved_native_label:'Annotations with unresolved labels',unchanged_phone:'Unchanged phone intervals',empirical_window_projection_absent:'Records without the requested observations'}[reason]||'Other excluded observations';}
