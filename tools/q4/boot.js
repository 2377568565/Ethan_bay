// 首页开头的小脚本（online.py 把它放进 <head>，%B% %J% 换成文件名）：
// 取各课正文和主程序：先看手机里（IndexedDB 'q4lz'）有没有，没有才下载（失败隔 2 秒重试，最多 3 次），下载的存起来；
// 网页骨架读完后，把正文放回每课的 <main>，再运行主程序。旧版本的文件 15 秒后从手机里删掉。
(function(){
var B=%B%,J=%J%,K=[B,J],P;
function db(){if(!P)P=new Promise(function(ok){try{var r=indexedDB.open('q4lz',1);r.onupgradeneeded=function(){r.result.createObjectStore('f');};
 r.onsuccess=function(){ok(r.result);};r.onerror=r.onblocked=function(){ok(null);};}catch(e){ok(null);}});return P;}
function tx(m,f){return db().then(function(d){if(!d)return null;return new Promise(function(ok){
 try{var t=d.transaction('f',m),q=f(t.objectStore('f'));t.oncomplete=function(){ok(q?q.result:null);};t.onerror=t.onabort=function(){ok(null);};}catch(e){ok(null);}});});}
function net(u,n){return fetch(u).then(function(r){if(!r.ok)throw 0;return r.text();}).catch(function(e){
 if(n>0)return new Promise(function(ok){setTimeout(ok,2000);}).then(function(){return net(u,n-1);});throw e;});}
function get(u){return tx('readonly',function(s){return s.get(u);}).then(function(v){if(typeof v==='string'&&v)return v;
 return net(u,3).then(function(t){tx('readwrite',function(s){return s.put(t,u);});return t;});});}
var pb=get(B),pj=get(J);
function fail(){var m=document.querySelector('#boot .bt-m');if(m)m.innerHTML='网络不太好，<a href="" onclick="location.reload();return false" style="color:inherit;text-decoration:underline">点这里重新打开</a>';
 var b=document.getElementById('boot');if(b)b.style.animation='none';}
function run(){Promise.all([pb,pj]).then(function(a){
 var L;try{L=JSON.parse(a[0]);}catch(e){tx('readwrite',function(s){s.delete(B);return s.delete(J);});fail();return;}
 for(var id in L){var m=document.querySelector('#'+id+' > .layout > main');if(m)m.innerHTML=L[id];}
 var s=document.createElement('script');s.text=a[1];document.body.appendChild(s);
 setTimeout(function(){tx('readwrite',function(s){if(!s.getAllKeys)return null;var q=s.getAllKeys();
  q.onsuccess=function(){(q.result||[]).forEach(function(k){if(K.indexOf(k)<0)s.delete(k);});};return q;});},15000);
},fail);}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run);else run();
})();
