// Read-only audit helper using the already installed OpenSpec YAML parser.
const fs=require('fs'), cp=require('child_process');
const Y=require('/opt/homebrew/lib/node_modules/@fission-ai/openspec/node_modules/yaml');
const root='specification/v2', out={};
for(const name of ['error-taxonomy.v1','metrics.v1','corpus-sources.v1','providers.v1','operation-ownership','configuration-registry','semantic-invariants','version-compatibility']) out[name]=Y.parse(fs.readFileSync(root+'/domain/'+name+'.yaml','utf8'));
out.prompts=Y.parse(fs.readFileSync(root+'/prompts/manifest.yaml','utf8'));
out.baseline_sources=Y.parse(cp.execFileSync('git',['show','b654e64:'+root+'/domain/corpus-sources.v1.yaml'],{encoding:'utf8'}));
let count=0;
function walk(dir){for(const x of fs.readdirSync(dir,{withFileTypes:true})){const p=dir+'/'+x.name;if(x.isDirectory())walk(p);else if(p.endsWith('.yaml')||p.endsWith('.yml')){Y.parse(fs.readFileSync(p,'utf8'));count++;}}}
walk(root);out.yaml_files_parsed=count;
process.stdout.write(JSON.stringify(out));
