"""Move cohesive existing functions without changing behavior; no workflow changes."""
from pathlib import Path
import re
R=Path(__file__).resolve().parents[2]/'services/api/internal/app'
def functions(name):
 s=(R/name).read_text();m=list(re.finditer(r'^func ',s,re.M));return {s[x.start():].split('(')[0] if False else i:s[x.start():m[i+1].start() if i+1<len(m) else len(s)] for i,x in enumerate(m)}
def write(name,imports,bodies):
 (R/name).write_text('package app\n\nimport (\n'+''.join(' "'+x+'"\n' for x in imports)+')\n\n'+''.join(bodies))
p=functions('source_import.go');assert len(p)==9,len(p)
write('source_import.go',['context'],[p[0]])
# stagedSourceRow is declared between stageSource and writeSourceRows and moves
# with its parsing owner. Storage batch writes remain their own cohesive method.
write('source_staging.go',['context','path','github.com/jackc/pgx/v5','tangerine.local/api/internal/source'],[p[1],p[2]])
write('source_mapping.go',['context','fmt','strconv','tangerine.local/api/internal/source'],[p[3],p[4]])
write('source_mapping_storage.go',['context','fmt','strings','tangerine.local/api/internal/contracts','tangerine.local/api/internal/source'],[p[5],p[6],p[7]])
write('source_projection.go',['fmt','tangerine.local/api/internal/contracts','tangerine.local/api/internal/source'],[p[8]])
p=functions('source_connector.go');prefix=(R/'source_connector.go').read_text();typ=prefix[prefix.index('type sourceExportProgress'):prefix.index('func ')];assert len(p)==4,len(p)
write('source_connector_http.go',['context','encoding/json','net/http','strconv','strings','github.com/google/uuid','tangerine.local/api/internal/contracts','tangerine.local/api/internal/source'],[p[0],p[3]])
write('source_connector_secret.go',['fmt','os','path/filepath'],[p[1]])
write('source_connector.go',['context','encoding/json','fmt','net/http','os','path/filepath','strings','tangerine.local/api/internal/source'],[typ,p[2]])
