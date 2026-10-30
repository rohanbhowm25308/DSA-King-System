/* Fullscreen cinematic thunder, adapted as vanilla JavaScript.
   Audio starts ONLY after the visitor clicks the sound control (browser policy). */
(() => {
  const canvas = document.getElementById('thunder-canvas');
  
  const arise = document.getElementById('arise');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let W = 1, H = 1, dpr = 1, bolts = [], lastBurst = -5000, started = performance.now();
  let soundEnabled = false, audio = null, audioBuffer = null;
  let lastHoverTone=0, lastPointerX=null, lastPointerY=null;
  function resize() {
    dpr = Math.min(devicePixelRatio || 1, 2);
    W = innerWidth; H = innerHeight;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  function path(x0, y0, x1, y1) {
    let pts = [[x0,y0],[x1,y1]], spread=W*.19;
    for(let depth=0;depth<6;depth++){
      let next=[pts[0]];
      for(let i=0;i<pts.length-1;i++){
        const a=pts[i],b=pts[i+1],mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2;
        const nx=-(b[1]-a[1]),ny=b[0]-a[0],len=Math.hypot(nx,ny)||1;
        next.push([mx+nx/len*(Math.random()-.5)*spread,my+ny/len*(Math.random()-.5)*spread],b);
      }
      pts=next;spread*=.56;
    }
    return pts;
  }
  function makeBolts(){
    bolts=Array.from({length:2+Math.floor(Math.random()*2)},()=>{
      const x=W*(.12+Math.random()*.76);
      return {points:path(x,-H*.1,x+(Math.random()-.5)*W*.42,H*1.1),width:1.5+Math.random()*2};
    });
  }
  function initAudio(){
    if(audio)return;
    audio=new (window.AudioContext||window.webkitAudioContext)();
    const sampleRate=audio.sampleRate;
    audioBuffer=audio.createBuffer(1,Math.floor(sampleRate*2.7),sampleRate);
    const data=audioBuffer.getChannelData(0);
    let smooth=0;
    for(let i=0;i<data.length;i++){
      smooth=smooth*.985+(Math.random()*2-1)*.015;
      const t=i/sampleRate, decay=Math.pow(Math.max(0,1-t/2.7),1.7);
      data[i]=(smooth*.85+(Math.random()*2-1)*.13)*decay;
    }
  }
  function thunderSound(){
    if(document.body.classList.contains("auth-locked"))return;
    if(!soundEnabled || !audio)return;
    if(audio.state==='suspended')audio.resume().catch(()=>{});
    const source=audio.createBufferSource();source.buffer=audioBuffer;
    const filter=audio.createBiquadFilter();filter.type='lowpass';filter.frequency.value=340;
    const gain=audio.createGain(), now=audio.currentTime;
    gain.gain.setValueAtTime(.0001,now);
    gain.gain.exponentialRampToValueAtTime(.75,now+.09);
    gain.gain.exponentialRampToValueAtTime(.0001,now+2.65);
    source.connect(filter).connect(gain).connect(audio.destination);
    source.start(now+.08);source.stop(now+2.7);
  }
  // Browsers may block autoplay audio. Try on page load; unlock on the first
  // user interaction without displaying a separate sound toggle.
  async function enableAudio(){
    if(document.body.classList.contains("auth-locked"))return;
    try{initAudio();await audio.resume();soundEnabled=audio.state==='running'}
    catch(err){soundEnabled=false}
  }
  window.addEventListener("dsa:authenticated",()=>{enableAudio();lastBurst=performance.now()-2900});
  if(!document.body.classList.contains("auth-locked"))enableAudio();
  for(const eventName of ['pointerdown','keydown','touchstart','wheel','mousemove']){
    window.addEventListener(eventName,()=>{if(!soundEnabled)enableAudio()},{passive:true});
  }
  // Soft magical chime only in the ARISE portrait reveal. Throttled to prevent
  // audio overload and cursor stutter; no extra audio files or dependencies.
  function hoverChime(now, speed){
    if(document.body.classList.contains("auth-locked"))return;
    if(!soundEnabled || !audio || audio.state!=='running' || now-lastHoverTone<190)return;
    lastHoverTone=now;
    const start=audio.currentTime, frequency=440+Math.min(speed,90)*3.4;
    const osc=audio.createOscillator(),gain=audio.createGain();
    osc.type='sine';osc.frequency.setValueAtTime(frequency,start);
    osc.frequency.exponentialRampToValueAtTime(frequency*1.38,start+.16);
    gain.gain.setValueAtTime(.0001,start);
    gain.gain.exponentialRampToValueAtTime(.055,start+.018);
    gain.gain.exponentialRampToValueAtTime(.0001,start+.25);
    osc.connect(gain).connect(audio.destination);osc.start(start);osc.stop(start+.27);
  }
  if(arise){
    arise.addEventListener('pointermove',e=>{
      if(e.pointerType==='touch')return;
      const rect=arise.getBoundingClientRect();
      if(rect.bottom<=0||rect.top>=innerHeight)return;
      const speed=lastPointerX===null?0:Math.hypot(e.clientX-lastPointerX,e.clientY-lastPointerY);
      lastPointerX=e.clientX;lastPointerY=e.clientY;
      if(speed>2)hoverChime(performance.now(),speed);
    },{passive:true});
    arise.addEventListener('pointerleave',()=>{lastPointerX=null;lastPointerY=null});
  }
  function active(){ return !document.hidden; }
  function frame(now){
    ctx.clearRect(0,0,W,H);
    if(!document.hidden && active() && !reduced){
      if(now-lastBurst>2900 && (now-started>450)){
        lastBurst=now;makeBolts();thunderSound();
      }
      const age=(now-lastBurst)/1000;
      if(age>=0 && age<.5){
        const alpha=age<.08?.82:age<.16?.16:age<.24?.56:Math.max(0,(.5-age)*.55);
        ctx.fillStyle=`rgba(210,225,255,${alpha*.17})`;
        ctx.fillRect(0,0,W,H);
        for(const b of bolts){
          for(const [width,color] of [[b.width*7,'rgba(80,140,255,.20)'],[b.width*2.7,'rgba(100,170,255,.48)'],[b.width,'rgba(235,248,255,.98)']]){
            ctx.beginPath();ctx.moveTo(...b.points[0]);
            for(const pt of b.points.slice(1))ctx.lineTo(...pt);
            ctx.strokeStyle=color;ctx.lineWidth=width;ctx.shadowBlur=width*2;ctx.shadowColor='#6ba8ff';ctx.stroke();
          }
        }
        ctx.shadowBlur=0;
      }
    }
    requestAnimationFrame(frame);
  }
  resize();window.addEventListener('resize',resize,{passive:true});
  if(!reduced){makeBolts();lastBurst=performance.now()-2500;requestAnimationFrame(frame)}
})();
