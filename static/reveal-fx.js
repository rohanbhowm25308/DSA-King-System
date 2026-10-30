/* Port of the supplied Solo Leveling RevealStage effect to vanilla JavaScript.
   Full-bleed, feathered trailing lens, cyan bloom, pointer interpolation. */
(()=>{
 const stage=document.querySelector('#arise .portrait');if(!stage)return;
 const original=stage.querySelector('img:first-child'), awakened=stage.querySelector('img:last-child');
 const canvas=document.createElement('canvas');canvas.className='portrait-fx';canvas.setAttribute('aria-label','Interactive character transformation');
 stage.appendChild(canvas);
 const ctx=canvas.getContext('2d',{alpha:false});const off=document.createElement('canvas'),oc=off.getContext('2d');
 let w=0,h=0,dpr=1,radius=160,raf=0,visible=true,ready=false,trail=[];
 let pointer={x:-9999,y:-9999},smooth={x:-9999,y:-9999},touched=false,last=0;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 const imgs={bottom:new Image(),top:new Image()};
 imgs.bottom.src=original.currentSrc||original.src;imgs.top.src=awakened.currentSrc||awakened.src;
 function resize(){w=stage.clientWidth;h=stage.clientHeight;if(!w||!h)return;
   dpr=Math.min(devicePixelRatio||1,1.5);
   for(const c of [canvas,off]){c.width=Math.round(w*dpr);c.height=Math.round(h*dpr)}
   ctx.setTransform(dpr,0,0,dpr,0,0);oc.setTransform(dpr,0,0,dpr,0,0);
   radius=Math.max(120,Math.min(w,h)*.26);
 }
 function cover(im){const s=Math.max(w/im.width,h/im.height),iw=im.width*s,ih=im.height*s;return [(w-iw)/2,(h-ih)/2,iw,ih]}
 function draw(now){raf=requestAnimationFrame(draw);if(!ready||!visible||document.hidden||!w)return;
   // 60fps target; avoid excessive canvas work on high refresh displays.
   if(now-last<15)return;last=now;
   if(touched){if(smooth.x< -1000){smooth.x=pointer.x;smooth.y=pointer.y}
     smooth.x+=(pointer.x-smooth.x)*.13;smooth.y+=(pointer.y-smooth.y)*.13;
     trail.unshift({x:smooth.x,y:smooth.y});if(trail.length>16)trail.length=16;
   }
   ctx.clearRect(0,0,w,h);
   const cb=cover(imgs.bottom);ctx.filter='grayscale(1) brightness(.62) contrast(1.05)';ctx.drawImage(imgs.bottom,...cb);ctx.filter='none';
   ctx.fillStyle='rgba(6,8,16,.55)';ctx.fillRect(0,0,w,h);
   oc.clearRect(0,0,w,h);oc.globalCompositeOperation='source-over';
   for(let i=trail.length-1;i>=0;i--){const k=1-i/16,r=radius*(.28+.72*k),a=Math.pow(k,1.5);
     const g=oc.createRadialGradient(trail[i].x,trail[i].y,0,trail[i].x,trail[i].y,r);
     g.addColorStop(0,`rgba(0,0,0,${a})`);g.addColorStop(.82,`rgba(0,0,0,${a})`);g.addColorStop(1,'rgba(0,0,0,0)');
     oc.beginPath();oc.arc(trail[i].x,trail[i].y,r,0,Math.PI*2);oc.fillStyle=g;oc.fill();
   }
   oc.globalCompositeOperation='source-in';oc.drawImage(imgs.top,...cover(imgs.top));oc.globalCompositeOperation='source-over';
   ctx.drawImage(off,0,0,w,h);
   const head=trail[0];if(head){ctx.beginPath();ctx.arc(head.x,head.y,radius*.98,0,Math.PI*2);
     ctx.strokeStyle='rgba(159,228,255,.35)';ctx.lineWidth=1.5;ctx.stroke();
     const glow=ctx.createRadialGradient(head.x,head.y,0,head.x,head.y,radius*1.5);
     glow.addColorStop(0,'rgba(190,235,255,.22)');glow.addColorStop(.45,'rgba(56,160,255,.14)');glow.addColorStop(1,'rgba(0,0,0,0)');
     ctx.beginPath();ctx.arc(head.x,head.y,radius*1.5,0,Math.PI*2);ctx.fillStyle=glow;ctx.fill();
   }
 }
 function move(e){const r=stage.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;
   if(x<0||y<0||x>r.width||y>r.height)return;pointer={x,y};touched=true;
 }
 const obs=new IntersectionObserver(es=>{visible=es[0].isIntersecting},{threshold:0});obs.observe(stage);
 stage.addEventListener('pointermove',move,{passive:true});
 window.addEventListener('resize',resize,{passive:true});
 Promise.all(Object.values(imgs).map(im=>im.decode().catch(()=>{}))).then(()=>{if(!imgs.bottom.naturalWidth||!imgs.top.naturalWidth)return;resize();ready=true;stage.classList.add('fx-ready');if(reduced){touched=true;pointer={x:w*.5,y:h*.5};smooth={...pointer};trail=[{...pointer}]}raf=requestAnimationFrame(draw)});
})();
