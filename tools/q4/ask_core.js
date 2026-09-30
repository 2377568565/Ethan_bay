/* ---------- 提问区的共同规则：网页和 GitHub 同步任务用同一份 ----------
   每条消息 = {p: 内容(JSON 字符串), s: 签名}。内容里带发消息那台设备的公钥 pk，
   身份码 uid = sha256(pk) 的前 32 位；签名对得上才算数，所以别人冒充不了、删不了你的内容。
   时间一律用消息中转站（ntfy）记下的服务器时间，不信任手机上的时间。 */
(function(root){
  var C=(typeof globalThis!=='undefined'&&globalThis.crypto)||root.crypto;
  var BAD=/(加微|微信号|vx|v信|威信|QQ群|扣扣|代开|发票|贷款|网贷|博彩|彩票|棋牌|兼职|刷单|返利|https?:\/\/|www\.)/i;
  var ID=/^[qrd]_[0-9a-z]{10,24}$/;
  function b64u(buf){var s='',a=new Uint8Array(buf);for(var i=0;i<a.length;i++)s+=String.fromCharCode(a[i]);return btoa(s).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');}
  function unb64u(s){s=s.replace(/-/g,'+').replace(/_/g,'/');while(s.length%4)s+='=';var b=atob(s),a=new Uint8Array(b.length);for(var i=0;i<b.length;i++)a[i]=b.charCodeAt(i);return a;}
  function enc(s){return new TextEncoder().encode(s);}
  function hex(buf){return Array.prototype.map.call(new Uint8Array(buf),function(b){return ('0'+b.toString(16)).slice(-2);}).join('');}
  function uidOf(pk){return C.subtle.digest('SHA-256',enc(pk)).then(function(h){return hex(h).slice(0,32);});}
  function rid(prefix){var a=new Uint8Array(10);C.getRandomValues(a);return prefix+'_'+hex(a);}
  function str(v,max){return typeof v==='string'&&v.length<=max;}

  /* 验签：返回 {P: 内容, uid} 或 null */
  function open(msg){
    try{
      var m=typeof msg==='string'?JSON.parse(msg):msg;
      if(!m||typeof m.p!=='string'||typeof m.s!=='string'||m.p.length>3500)return Promise.resolve(null);
      var P=JSON.parse(m.p);
      if(!P||P.v!==1||!str(P.pk,200)||!ID.test(P.id||''))return Promise.resolve(null);
      var xy=P.pk.split('.');if(xy.length!==2)return Promise.resolve(null);
      return C.subtle.importKey('jwk',{kty:'EC',crv:'P-256',x:xy[0],y:xy[1],ext:true},{name:'ECDSA',namedCurve:'P-256'},false,['verify'])
        .then(function(k){return C.subtle.verify({name:'ECDSA',hash:'SHA-256'},k,unb64u(m.s),enc(m.p));})
        .then(function(ok){return ok?uidOf(P.pk).then(function(u){return {P:P,uid:u};}):null;})
        .catch(function(){return null;});
    }catch(e){return Promise.resolve(null);}
  }

  /* 把一条验过签的消息用到数据上。t = 服务器时间（毫秒）。返回 '' 表示成功，否则是不通过的原因 */
  function apply(S,P,uid,t){
    var admin=(S.admins||[]).indexOf(uid)>=0,day=t-864e5,n,q,i;
    function has(id){return S.questions.some(function(x){return x.id===id;})||S.replies.some(function(x){return x.id===id;});}
    if(has(P.id))return 'dup';
    if(P.op==='q'||P.op==='r'){
      var name=typeof P.name==='string'?P.name.trim():'',text=typeof P.text==='string'?P.text.trim():'',loc=typeof P.loc==='string'?P.loc.trim():'';
      if(name.length<1||name.length>16||loc.length>30)return 'bad';
      if(!admin&&(BAD.test(text)||BAD.test(name)||/1[3-9]\d{9}/.test(text)))return 'spam';
      var mine=(P.op==='q'?S.questions:S.replies).filter(function(x){return x.uid===uid;});
      if(!admin&&mine.some(function(x){return x.ts>t-15e3;}))return 'fast';
      n=mine.filter(function(x){return x.ts>day;}).length;
      if(!admin&&n>=(P.op==='q'?10:30))return 'limit';
      if(P.op==='q'){
        if(text.length<4||text.length>500)return 'bad';
        S.questions.push({id:P.id,uid:uid,name:name,loc:loc,text:text,allow:P.allow!==false,ts:t});
      }else{
        if(text.length<2||text.length>300||!ID.test(P.qid||''))return 'bad';
        q=S.questions.filter(function(x){return x.id===P.qid;})[0];
        if(!q)return 'gone';
        if(!q.allow&&q.uid!==uid&&!admin)return 'closed';
        if(P.admin&&!admin)return 'notadmin';
        S.replies.push({id:P.id,qid:q.id,uid:uid,name:name,loc:loc,text:text,admin:!!(P.admin&&admin),ts:t});
      }
      return '';
    }
    if(P.op==='d'){
      if(!ID.test(P.target||''))return 'bad';
      for(i=0;i<S.questions.length;i++)if(S.questions[i].id===P.target){
        if(S.questions[i].uid!==uid&&!admin)return 'notyours';
        S.questions.splice(i,1);S.replies=S.replies.filter(function(r){return r.qid!==P.target;});return '';
      }
      for(i=0;i<S.replies.length;i++)if(S.replies[i].id===P.target){
        if(S.replies[i].uid!==uid&&!admin)return 'notyours';
        S.replies.splice(i,1);return '';
      }
      return 'gone';
    }
    return 'bad';
  }

  /* 把中转站里新的消息（按时间顺序）合进数据。msgs: [{id, time(秒), message}] */
  function merge(S,msgs){
    S.seen=S.seen||{};
    msgs=msgs.filter(function(m){return m&&m.event==='message'&&typeof m.message==='string'&&!S.seen[m.id];})
             .sort(function(a,b){return a.time-b.time||(a.id<b.id?-1:1);});
    var out=[];
    return msgs.reduce(function(chain,m){
      return chain.then(function(){return open(m.message);}).then(function(r){
        S.seen[m.id]=m.time;if(m.time>(S.last||0))S.last=m.time;
        var why=r?apply(S,r.P,r.uid,m.time*1000):'sig';
        out.push({id:m.id,pid:r&&r.P.id,uid:r&&r.uid,why:why});
      });
    },Promise.resolve()).then(function(){return out;});
  }

  /* 本机钥匙：第一次用时生成，存在这台设备上 */
  function keys(store){
    var j=null;try{j=JSON.parse(store.get('sk')||'null');}catch(e){}
    var ready=j&&j.d&&j.x&&j.y?C.subtle.importKey('jwk',j,{name:'ECDSA',namedCurve:'P-256'},true,['sign']).then(function(k){return {k:k,pk:j.x+'.'+j.y};})
      :C.subtle.generateKey({name:'ECDSA',namedCurve:'P-256'},true,['sign','verify']).then(function(kp){
          return C.subtle.exportKey('jwk',kp.privateKey).then(function(jw){store.set('sk',JSON.stringify({kty:'EC',crv:'P-256',x:jw.x,y:jw.y,d:jw.d}));return {k:kp.privateKey,pk:jw.x+'.'+jw.y};});
        });
    return ready.then(function(K){return uidOf(K.pk).then(function(u){K.uid=u;return K;});});
  }
  function sign(K,P){
    P.v=1;P.pk=K.pk;P.t=Date.now();var p=JSON.stringify(P);
    return C.subtle.sign({name:'ECDSA',hash:'SHA-256'},K.k,enc(p)).then(function(sig){return JSON.stringify({p:p,s:b64u(sig)});});
  }
  function empty(){return {v:1,updated:0,last:0,seen:{},admins:[],questions:[],replies:[]};}

  root.Q4Ask={open:open,apply:apply,merge:merge,keys:keys,sign:sign,rid:rid,uidOf:uidOf,empty:empty};
})(typeof module!=='undefined'&&module.exports?module.exports:this);
