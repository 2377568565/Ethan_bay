/* 提问区连接页里运行的脚本：用云开发匿名身份连数据库，替学习网站执行查询。
   学习网站把查询写成一串步骤（from/select/order…）发过来，这里照做后把结果传回去。 */
(function(){
  var P=window.Q4PARENT;if(!P||!window.cloudbase)return;
  function send(m){P.win.postMessage(m,P.origin);}
  function err(e){return {code:String((e&&(e.code||e.errCode||e.error))||''),message:String((e&&(e.message||e.msg))||e||'')};}
  function snap(){var o={};try{for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);o[k]=localStorage.getItem(k);}}catch(e){}return o;}
  /* 有的手机会清掉嵌入页的存储：学习网站替我们存一份，这里补回去，身份就不会变 */
  try{if(P.ls)for(var k in P.ls)if(localStorage.getItem(k)===null)localStorage.setItem(k,P.ls[k]);}catch(e){}
  var last='';
  function mirror(){var s=JSON.stringify(snap());if(s!==last){last=s;send({q4:'ls',ls:JSON.parse(s)});}}
  var STEP={select:1,order:1,limit:1,lt:1,gt:1,eq:1,'in':1,insert:1,'delete':1};
  var db=null;
  function run(ch){
    if(!db)throw {code:'NOT_READY'};
    if(!ch||!ch.length)throw {code:'BAD_QUERY'};
    var h=ch[0],q;
    if(h[0]==='from'&&typeof h[1]==='string')q=db.from(h[1]);
    else if(h[0]==='rpc'&&typeof h[1]==='string')q=db.rpc(h[1],h[2]||{});
    else throw {code:'BAD_QUERY'};
    for(var i=1;i<ch.length;i++){var s=ch[i];if(!s||!STEP[s[0]])throw {code:'BAD_QUERY'};q=q[s[0]].apply(q,s.slice(1));}
    return Promise.resolve(q).then(function(r){
      return {data:r&&r.data!==undefined?r.data:null,error:r&&r.error?err(r.error):null,status:r&&r.status};
    });
  }
  addEventListener('message',function(e){
    if(e.source!==P.win||e.origin!==P.origin)return;
    var d=e.data||{};if(d.q4!=='call')return;
    var p;try{p=run(d.chain);}catch(x){p=Promise.reject(x);}
    p.then(function(r){send({q4:'res',id:d.id,res:r});mirror();},function(x){send({q4:'res',id:d.id,err:err(x)});});
  });
  var app=window.cloudbase.init({env:P.env,timeout:15000}),auth=app.auth();
  auth.getLoginState().then(function(st){
    if(st&&st.user)return st;
    return auth.signInAnonymously().then(function(r){if(r&&r.error)throw r.error;});
  }).then(function(){return auth.getCurrentUser();}).then(function(u){
    db=app.rdb();mirror();send({q4:'ready',uid:(u&&(u.uid||u.id))||''});
  }).catch(function(x){send({q4:'fail',err:err(x)});});
})();
