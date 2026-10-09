const fs=require('fs'),crypto=require('crypto'),Y=require('/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml');
const root='specification/v2/';const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(root+p)).digest('hex');
let sem=Y.parse(fs.readFileSync(root+'domain/semantic-invariants.yaml','utf8'));
for(const p of ['audio-measurement','render-plan','speech-render-request'])sem.schemas[p].schema_sha256=hash('contracts/'+p+'.schema.json');
fs.writeFileSync(root+'domain/semantic-invariants.yaml',Y.stringify(sem));
let compat=Y.parse(fs.readFileSync(root+'domain/version-compatibility.yaml','utf8'));let paths=[];
function scan(p){for(const x of fs.readdirSync(root+p,{withFileTypes:true})){const f=p+x.name;if(x.isDirectory())scan(f+'/');else if(f!=='domain/version-compatibility.yaml')paths.push(f);}}
scan('');compat.files=paths.sort().map(path=>({path,sha256:hash(path)}));fs.writeFileSync(root+'domain/version-compatibility.yaml',Y.stringify(compat));
console.log(JSON.stringify({version_files:paths.length}));
