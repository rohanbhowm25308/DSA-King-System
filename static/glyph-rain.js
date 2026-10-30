/* Falling glyph columns ported from the user's original GlyphRain animation. */
(()=>{const parent=document.querySelector('#awaken .sticky');if(!parent)return;
 const c=document.createElement('canvas');c.className='glyph-rain';c.setAttribute('aria-hidden','true');parent.appendChild(c);
 const ctx=c.getContext('2d');const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 const glyphs='ピカチュウカミナリデンキアイウエオカキクケコサシスセソタチツテト01';
 let w=0,h=0,columns=[],visible=true,last=performance.now(),raf=0;
 const rand=(a,b)=>a+Math.random()*(b-a),fontSize=18,speed=58;
 function resize(){w=c.clientWidth;h=c.clientHeight;const dpr=Math.min(devicePixelRatio||1,1.5);
   c.width=Math.round(w*dpr);c.height=Math.round(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);
   ctx.font=`${fontSize}px 'Noto Sans JP',monospace`;ctx.textBaseline='top';
   const count=Math.max(6,Math.round(w/(fontSize*1.75)*.85));
   columns=Array.from({length:count},(_,i)=>({x:(i+.5)*(w/count)+rand(-6,6),y:rand(-h*.35,h),speed:rand(speed*.45,speed*1.35),len:Math.round(rand(6,16)),chars:Array.from({length:18},()=>glyphs[(Math.random()*glyphs.length)|0]),swap:rand(.1,.4),t:0}));
 }
 function draw(now){raf=requestAnimationFrame(draw);if(!visible||document.hidden)return;
   const dt=Math.min((now-last)/1000,.05);last=now;ctx.clearRect(0,0,w,h);
   for(const col of columns){col.y+=col.speed*dt;col.t+=dt;
     if(col.t>col.swap){col.t=0;col.chars[(Math.random()*col.chars.length)|0]=glyphs[(Math.random()*glyphs.length)|0]}
     if(col.y-col.len*24.3>h){col.y=rand(-h*.5,-24);col.speed=rand(speed*.45,speed*1.35)}
     for(let i=0;i<col.len;i++){const y=col.y-i*24.3;if(y<-25||y>h)continue;
       const fade=1-i/col.len;ctx.fillStyle=i===0?'#d9a400':'#8d8a97';ctx.shadowBlur=i===0?12:0;ctx.shadowColor='#8d8a97';ctx.globalAlpha=.38*fade*fade;
       ctx.fillText(col.chars[i%col.chars.length],col.x,y)
     }
   }
   ctx.globalAlpha=1;ctx.shadowBlur=0;
 }
 const obs=new IntersectionObserver(es=>{visible=es[0].isIntersecting;last=performance.now()});obs.observe(parent);
 resize();if(reduced){draw(performance.now());cancelAnimationFrame(raf)}else raf=requestAnimationFrame(draw);
 window.addEventListener('resize',resize,{passive:true});
})();
