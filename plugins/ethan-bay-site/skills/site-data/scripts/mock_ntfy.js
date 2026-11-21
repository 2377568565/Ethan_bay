// 本机模拟 ntfy：POST /topic 投递，GET /topic/json?poll=1&since= 读取
const http=require('http');const DB={};
http.createServer((q,s)=>{
  const u=new URL(q.url,'http://x');const H={'Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers':'*','Access-Control-Allow-Methods':'GET, POST'};
  if(q.method==='OPTIONS'){s.writeHead(200,H);return s.end();}
  const parts=u.pathname.split('/').filter(Boolean),topic=parts[0];
  if(q.method==='POST'&&parts.length===1){let b='';q.setEncoding('utf8');q.on('data',c=>b+=c);q.on('end',()=>{
    const now=Math.floor(Date.now()/1000),m={id:Math.random().toString(36).slice(2,14),time:now,expires:now+43200,event:'message',topic,message:b};
    (DB[topic]=DB[topic]||[]).push(m);s.writeHead(200,Object.assign({'Content-Type':'application/json'},H));s.end(JSON.stringify(m));});return;}
  if(q.method==='GET'&&parts[1]==='json'){
    const since=u.searchParams.get('since')||'all',now=Math.floor(Date.now()/1000);
    let t=since==='all'?0:/^\d+h$/.test(since)?now-3600*parseInt(since):/^\d+$/.test(since)?+since:0;
    const out=(DB[topic]||[]).filter(m=>m.time>=t).map(m=>JSON.stringify(m)).join('\n');
    s.writeHead(200,Object.assign({'Content-Type':'application/x-ndjson'},H));return s.end(out?out+'\n':'');}
  s.writeHead(404,H);s.end('nf');
}).listen(8090,()=>console.log('mock ntfy on 8090'));
