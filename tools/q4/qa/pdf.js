const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const path=require('path'),fs=require('fs');
(async()=>{
  const jobs=JSON.parse(fs.readFileSync(path.join(__dirname,'_jobs.json'),'utf8'));
  const b=await chromium.launch();const p=await b.newPage();
  for(const [key,out] of jobs){
    await p.goto('file://'+path.join(__dirname,'_'+key+'.html'),{waitUntil:'load'});
    await p.evaluate(()=>document.fonts.ready);
    const missing=await p.evaluate(()=>[...document.fonts].filter(f=>f.status!=='loaded').map(f=>f.family+' '+f.weight));
    await p.pdf({path:path.join(__dirname,out+'.pdf'),preferCSSPageSize:true,printBackground:true,displayHeaderFooter:true,
      headerTemplate:'<div style="position:absolute;left:0;top:0;width:100%;height:12mm;background:#FBF7EE;-webkit-print-color-adjust:exact"></div>',
      footerTemplate:'<div style="position:absolute;left:0;bottom:0;width:100%;height:14mm;background:#FBF7EE;-webkit-print-color-adjust:exact;display:flex;align-items:center;justify-content:center;font-size:7.5pt;color:#A89F8C;letter-spacing:1px"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'});
    console.log(out+'.pdf','fonts not loaded:',missing);
  }
  await b.close();
})();
