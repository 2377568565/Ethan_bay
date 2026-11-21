/* ---------- 提问区的共同规则：网页和 GitHub 同步任务用同一份 ----------
   每条消息 = {p: 内容(JSON 字符串), s: 签名}。内容里带发消息那台设备的公钥 pk，
   身份码 uid = sha256(pk) 的前 32 位；签名对得上才算数，所以别人冒充不了、删不了你的内容。
   时间一律用消息中转站（ntfy）记下的服务器时间，不信任手机上的时间。 */
(function(root){
  var C=(typeof globalThis!=='undefined'&&globalThis.crypto)||root.crypto;
  var BAD=/(加微|微信号|vx|v信|威信|QQ群|扣扣|代开|发票|贷款|网贷|博彩|彩票|棋牌|兼职|刷单|返利|https?:\/\/|www\.)/i;
  var ID=/^[qrdvpcauw]_[0-9a-z]{10,24}$/,DAY=/^l\d{1,2}-(sab|sun|mon|tue|wed|thu|fri|sum)$/,NOTE=/^l\d{1,2}-(sab|sun|mon|tue|wed|thu|fri)-[qe]\d{1,2}$/,QA=/^qa\d{1,3}$/;
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

  /* 补齐数据里可能缺的部分（老的存档只有问题和回复） */
  function norm(S){
    S.seen=S.seen||{};S.admins=S.admins||[];S.questions=S.questions||[];S.replies=S.replies||[];
    S.answers=S.answers||[];S.votes=S.votes||{};S.checks=S.checks||{};S.accounts=S.accounts||{};S.vault=S.vault||{};S.hits=S.hits||0;return S;
  }
  /* 把一条验过签的消息用到数据上。t = 服务器时间（毫秒）。返回 '' 表示成功，否则是不通过的原因
     q 提问 · r 回复 · a 讨论区回答 · d 删除 · v “我也想知道/有帮助” · c 读完打卡 · p 管理员置顶/标记已整理
     u 账号（把这台设备的身份用密码加密后存起来） · w 账号同步的数据（用密码加密的设置、笔记等，只有本人能写） */
  function apply(S,P,uid,t){
    norm(S);
    var admin=S.admins.indexOf(uid)>=0,day=t-864e5,q,i,list;
    function find(arr,id){for(var j=0;j<arr.length;j++)if(arr[j].id===id)return arr[j];return null;}
    function text(min,max){var x=typeof P.text==='string'?P.text.trim():'';return x.length>=min&&x.length<=max?x:null;}
    function who(){
      var name=typeof P.name==='string'?P.name.trim():'',loc=typeof P.loc==='string'?P.loc.trim():'';
      return name.length>=1&&name.length<=16&&loc.length<=30?{name:name,loc:loc}:null;
    }
    function busy(arr,max){   // 防刷：15 秒内只能发一条；每天有上限（管理员不限）
      if(admin)return '';var mine=arr.filter(function(x){return x.uid===uid;});
      if(mine.some(function(x){return x.ts>t-15e3;}))return 'fast';
      return mine.filter(function(x){return x.ts>day;}).length>=max?'limit':'';
    }
    if(P.op==='q'||P.op==='r'||P.op==='a'){
      if(find(S.questions,P.id)||find(S.replies,P.id)||find(S.answers,P.id))return 'dup';
      var w=who();if(!w)return 'bad';
      var tx=text(P.op==='q'?4:2,P.op==='r'?300:500);if(tx===null)return 'bad';
      if(!admin&&(BAD.test(tx)||BAD.test(w.name)||/1[3-9]\d{9}/.test(tx)))return 'spam';
      list=P.op==='q'?S.questions:P.op==='r'?S.replies:S.answers;
      var why=busy(list,P.op==='q'?10:30);if(why)return why;
      if(P.op==='q'){S.questions.push({id:P.id,uid:uid,name:w.name,loc:w.loc,text:tx,allow:P.allow!==false,ts:t});return '';}
      if(P.op==='a'){
        if(!NOTE.test(P.k||''))return 'bad';
        S.answers.push({id:P.id,k:P.k,uid:uid,name:w.name,loc:w.loc,text:tx,ts:t});return '';
      }
      q=find(S.questions,P.qid);
      if(!q)return 'gone';
      if(!q.allow&&q.uid!==uid&&!admin)return 'closed';
      if(P.admin&&!admin)return 'notadmin';
      S.replies.push({id:P.id,qid:q.id,uid:uid,name:w.name,loc:w.loc,text:tx,admin:!!(P.admin&&admin),ts:t});
      return '';
    }
    if(P.op==='d'){
      if(!ID.test(P.target||''))return 'bad';
      var groups=[S.questions,S.replies,S.answers];
      for(var g=0;g<groups.length;g++)for(i=0;i<groups[g].length;i++)if(groups[g][i].id===P.target){
        if(groups[g][i].uid!==uid&&!admin)return 'notyours';
        groups[g].splice(i,1);delete S.votes[P.target];
        if(g===0)S.replies=S.replies.filter(function(r){return r.qid!==P.target;});
        return '';
      }
      return 'gone';
    }
    if(P.op==='v'){   // 同一个人对同一条只算一次；on=false 表示收回
      if(!find(S.questions,P.target)&&!find(S.answers,P.target))return 'gone';
      var vs=S.votes[P.target]||[],at=vs.indexOf(uid);
      if(P.on===false){if(at>=0)vs.splice(at,1);}else if(at<0)vs.push(uid);
      if(vs.length)S.votes[P.target]=vs;else delete S.votes[P.target];
      return '';
    }
    if(P.op==='c'){   // 读完打卡：每个人每一天的学课只记一次，只存身份码的前 12 位
      if(!DAY.test(P.k||''))return 'bad';
      var cs=S.checks[P.k]||(S.checks[P.k]=[]),u=uid.slice(0,12);
      if(cs.indexOf(u)<0)cs.push(u);
      return '';
    }
    if(P.op==='p'){   // 管理员：置顶 / 标记“已整理成问题彩蛋”
      if(!admin)return 'notadmin';
      q=find(S.questions,P.target);if(!q)return 'gone';
      if(typeof P.pin==='boolean'){if(P.pin)q.pin=t;else delete q.pin;}
      if(typeof P.qa==='string'){if(QA.test(P.qa))q.qa=P.qa;else if(!P.qa)delete q.qa;}
      return '';
    }
    if(P.op==='u'){   // 账号 = 账号名的哈希 aid → 身份码 + 用密码加密的身份钥匙；同一身份可以重新提交（改密码）
      if(!/^[0-9a-f]{32}$/.test(P.aid||'')||!str(P.ek,1600)||!/^[A-Za-z0-9_-]+$/.test(P.ek))return 'bad';
      var ac=S.accounts[P.aid];
      if(ac&&ac.uid!==uid)return 'taken';
      S.accounts[P.aid]={uid:uid,ek:P.ek,ts:t};return '';
    }
    if(P.op==='w'){   // 同步数据：每格 slot 一段密文；空内容表示删除
      var ac2=S.accounts[P.aid];if(!ac2)return 'noacct';if(ac2.uid!==uid)return 'notyours';
      if(!/^[0-9a-f]{16}$/.test(P.slot||'')||typeof P.d!=='string'||P.d.length>2900||!/^[A-Za-z0-9_-]*$/.test(P.d))return 'bad';
      var V=S.vault[P.aid]||(S.vault[P.aid]={});
      if(!P.d){delete V[P.slot];return '';}
      if(!V[P.slot]&&Object.keys(V).length>=3000)return 'limit';
      V[P.slot]={d:P.d,ts:t};return '';
    }
    return 'bad';
  }

  /* 访问计数：打开网页时发一条 {h:1,id:'h_…'}（不带身份、不签名），只把人次加一 */
  function hit(msg){try{var o=JSON.parse(msg);return !!(o&&o.h===1&&!o.p&&/^h_[0-9a-z]{10,24}$/.test(o.id||''));}catch(e){return false;}}
  /* 把中转站里新的消息（按时间顺序）合进数据。msgs: [{id, time(秒), message}] */
  function merge(S,msgs){
    norm(S);
    msgs=msgs.filter(function(m){return m&&m.event==='message'&&typeof m.message==='string'&&!S.seen[m.id];})
             .sort(function(a,b){return a.time-b.time||(a.id<b.id?-1:1);});
    var out=[];
    return msgs.reduce(function(chain,m){
      if(hit(m.message))return chain.then(function(){S.seen[m.id]=m.time;if(m.time>(S.last||0))S.last=m.time;S.hits++;out.push({id:m.id,why:''});});
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
  function empty(){return norm({v:1,updated:0,last:0});}

  root.Q4Ask={open:open,apply:apply,merge:merge,norm:norm,DAY:DAY,NOTE:NOTE,keys:keys,sign:sign,rid:rid,uidOf:uidOf,empty:empty};
})(typeof module!=='undefined'&&module.exports?module.exports:this);
