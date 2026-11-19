// usage: node render.cjs <outDir> <w> <h> <fps> [times(comma)]
const {chromium}=require('playwright'); const fs=require('fs');
(async()=>{
  const [out,w,h,fps,times]=[process.argv[2],+process.argv[3],+process.argv[4],+process.argv[5],process.argv[6]];
  fs.mkdirSync(out,{recursive:true});
  const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:w,height:h},deviceScaleFactor:1});
  p.on('console',m=>{ if(m.type()==='error'||m.type()==='warning') console.log('[page]',m.text()); }); p.on('pageerror',e=>console.log('[pageerror]',e.message));
  await p.goto(`http://127.0.0.1:8123/index.html?w=${w}&h=${h}`); await p.evaluate(()=>window.ready);
  const list = times ? times.split(',').map(Number) : Array.from({length:Math.round(20*fps)},(_,i)=>i/fps);
  const t0=Date.now();
  for (let i=0;i<list.length;i++){ await p.evaluate(t=>window.renderAt(t),list[i]);
    const name = times ? `t_${list[i].toFixed(2)}.png` : `f_${String(i).padStart(4,'0')}.jpg`;
    await p.screenshot({path:`${out}/${name}`, type: times?'png':'jpeg', quality: times?undefined:90});
    if(i%50===0) console.log(i, ((Date.now()-t0)/1000).toFixed(1)+'s'); }
  await b.close();
})();
