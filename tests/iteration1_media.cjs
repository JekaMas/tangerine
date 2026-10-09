// Test-owned native S3 fixture driver. No replacement storage server or SDK mock.
const crypto = require('node:crypto');
const hash = x => crypto.createHash('sha256').update(x).digest('hex');
const hmac = (key, x) => crypto.createHmac('sha256', key).update(x).digest();
async function main() {
 const operation = process.argv[2];
 const policy = operation === 'public' || operation === 'private';
 const method = operation === 'put' || operation === 'public' ? 'PUT' : operation === 'private' ? 'DELETE' : 'GET';
 const query = policy ? 'policy=' : '';
 const path = policy ? '/tangerine-audio' : '/tangerine-audio/iteration1-fixture.bin';
 const body = operation === 'put' ? 'native-iteration1-object\n' : operation === 'public' ? JSON.stringify({Version:'2012-10-17',Statement:[{Effect:'Allow',Principal:{AWS:['*']},Action:['s3:GetObject'],Resource:['arn:aws:s3:::tangerine-audio/*']}]}) : '';
 const stamp = new Date().toISOString().replace(/[:-]|\.\d{3}/g,''); const day=stamp.slice(0,8);
 const payload=hash(body);const headers=`host:minio:9000\nx-amz-content-sha256:${payload}\nx-amz-date:${stamp}\n`;
 const names='host;x-amz-content-sha256;x-amz-date';
 const canonical=[method,path,query,headers,names,payload].join('\n');const scope=`${day}/us-east-1/s3/aws4_request`;
 let key=hmac('AWS4'+process.env.MINIO_ROOT_PASSWORD,day);key=hmac(key,'us-east-1');key=hmac(key,'s3');key=hmac(key,'aws4_request');
 const signature=hmac(key,['AWS4-HMAC-SHA256',stamp,scope,hash(canonical)].join('\n')).toString('hex');
 const response=await fetch('http://minio:9000'+path+(policy?'?policy':''),{method,headers:{'x-amz-date':stamp,'x-amz-content-sha256':payload,Authorization:`AWS4-HMAC-SHA256 Credential=${process.env.MINIO_ROOT_USER}/${scope}, SignedHeaders=${names}, Signature=${signature}`},body:method==='PUT'?body:undefined});
 const text=await response.text();if(!response.ok)throw new Error('Native S3 operation failed: '+response.status);
 console.log(JSON.stringify({status:response.status,sha256:hash(text),size:Buffer.byteLength(text)}));
}
main().catch(e=>{console.error(e.message);process.exit(1)});
