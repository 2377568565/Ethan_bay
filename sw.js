const C_SITE = 'q4-site-v1';
const C_PAGE = 'q4-pages-v1';
const KEEP = [C_SITE, C_PAGE];

self.addEventListener('install', function() {
  self.skipWaiting();
});

self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(ks) {
      return Promise.all(ks.map(function(k) {
        return k.indexOf('q4-') === 0 && KEEP.indexOf(k) < 0 ? caches.delete(k) : null;
      }));
    }).then(function() {
      return self.clients.claim();
    })
  );
});

function putOk(name, key, res) {
  if (res && res.ok && res.type === 'basic') {
    var copy = res.clone();
    caches.open(name).then(function(c) { return c.put(key, copy); }).catch(function() {});
  }
  return res;
}

self.addEventListener('fetch', function(e) {
  var req = e.request;
  if (req.method !== 'GET' || req.headers.has('range')) return;
  var url;
  try { url = new URL(req.url); } catch (err) { return; }
  if (url.origin !== self.location.origin) return;
  var base = new URL(self.registration.scope).pathname;
  if (url.pathname.indexOf(base) !== 0) return;
  var rel = url.pathname.slice(base.length);
  if (rel === 'sw.js' || rel.indexOf('data/') === 0 || rel.indexOf('audio/') === 0 ||
      rel.indexOf('music/') === 0 || rel.indexOf('lessons/') === 0 ||
      /\.(mp3|m4a|wav|ogg|aac|flac|pdf|zip)$/i.test(rel)) return;
  if (/[?&]askmock/.test(url.search)) return;

  // 1) site/ 下的哈希分片与圣经分卷：永久缓存（Cache-First）
  if (rel.indexOf('site/') === 0) {
    var siteKey = url.origin + url.pathname;
    e.respondWith(
      caches.open(C_SITE).then(function(c) {
        return c.match(siteKey).then(function(hit) {
          if (hit) return hit;
          return fetch(req).then(function(res) { return putOk(C_SITE, siteKey, res); });
        });
      })
    );
    return;
  }

  // 2) 首页与各篇静态文章：先用本机缓存秒开，同时在后台检查更新（Stale-While-Revalidate）
  if (rel === '' || rel === 'index.html' || /\.html?$/i.test(rel)) {
    var pageKey = url.origin + base + (rel === 'index.html' ? '' : rel);
    e.respondWith(
      caches.open(C_PAGE).then(function(c) {
        return c.match(pageKey).then(function(hit) {
          var bg = fetch(hit ? new Request(pageKey, { cache: 'no-cache', credentials: 'same-origin' }) : req)
            .then(function(res) { return putOk(C_PAGE, pageKey, res); })
            .catch(function() { return null; });
          if (hit) {
            e.waitUntil(bg);
            return hit;
          }
          return bg.then(function(res) {
            return res || new Response('网络连接异常，请刷新重试', {
              status: 503,
              headers: { 'Content-Type': 'text/plain; charset=utf-8' }
            });
          });
        });
      })
    );
  }
});
