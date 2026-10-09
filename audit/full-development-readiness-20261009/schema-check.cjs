// Compile affected JSON Schemas and exercise changed field contracts, not app behavior.
const fs=require('fs');const Ajv=require('/opt/homebrew/lib/node_modules/vercel/node_modules/ajv/dist/2020').default;
const dir='specification/v2/contracts/';const ajv=new Ajv({strict:false,validateFormats:false});const schemas={};
for(const n of fs.readdirSync(dir).filter(n=>n.endsWith('.schema.json'))){const d=JSON.parse(fs.readFileSync(dir+n,'utf8'));schemas[n]=d;ajv.addSchema(d);}
const compiled=['render-plan','speech-render-request','audio-measurement'];for(const n of compiled)ajv.getSchema(schemas[n+'.schema.json'].$id);
const checks=[];function ck(name,ok){if(!ok)throw Error(name);checks.push(name);}
for(const n of ['render-plan','speech-render-request']){
 const v=ajv.compile(schemas[n+'.schema.json'].properties.turns.items.properties.locale);
 for(const loc of ['en-US','en-GB','en-IN','en-AU','en'])ck(n+'.locale.accept.'+loc,v(loc));
 for(const loc of ['fr-FR','en_US','en-','en-IN<script>'])ck(n+'.locale.reject.'+loc,!v(loc));
}
const measure={id:'constructed-m1',audio_sha256:'a'.repeat(64),method_id:'praat-ac-v1',method_version:'constructed-parameters',feature:'rhythm',interval:{start:0,end:24000,sample_rate_hz:24000},status:'not_measurable',numeric_value:null,categorical_value:null,unit:'category',evidence_asset_ids:[],reason:'No reliable rhythm interpretation'};
const vm=ajv.getSchema(schemas['audio-measurement.schema.json'].$id);ck('measurement.unknown.allowed',vm(measure));ck('measurement.no.human.status',!vm({...measure,status:'human_required'}));ck('measurement.reject.invalid.unit',!vm({...measure,unit:'imaginary'}));ck('measurement.reject.extra',!vm({...measure,approval_required:true}));
const out={status:'passed',compiled_affected_schemas:compiled,registered_reference_schemas:Object.keys(schemas).length,assertions:checks.length,validate_formats:false,proof_boundary:'Affected Draft 2020-12 compilation and literal field/measurement instances; no cross-field/runtime/voice entitlement/audio acceptance.',checks};fs.writeFileSync('audit/full-development-readiness-20261009/schema-validation.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({...out,checks:undefined}));
