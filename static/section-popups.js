/* DSA King System — cinematic section entrance animations.
   Scoped to the fourth/main DSA console; does not alter the login or scroll scenes. */
(()=>{
  'use strict';
  const root=document.querySelector('#platform');
  const page=document.querySelector('#platform #page');
  const nav=document.querySelector('#platform #nav');
  if(!root||!page||!nav)return;
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
  const watched=new WeakSet();
  let pending=0;
  const selector=':scope > .panel, :scope > .hero-panel, :scope > .stats, :scope > .grid, :scope > .innovation-hero, :scope > .innovation-tabs, :scope > .innovation-panel, :scope > .card, :scope > .section, :scope > .feature-grid';
  function collect(){
    const blocks=[...page.children];
    const items=[];
    for(const block of blocks){
      if(block.matches('.grid,.stats,.innovation-galaxy,.innovation-network')){
        items.push(block);
        for(const child of block.children)items.push(child);
      }else items.push(block);
    }
    return items.filter(el=>el instanceof HTMLElement);
  }
  function animate(){
    if(reduced.matches)return;
    const blocks=collect();
    const viewport=window.innerHeight;
    blocks.forEach((el,i)=>{
      if(watched.has(el))return;
      watched.add(el);
      const rect=el.getBoundingClientRect();
      // Animate newly rendered cards and visible section blocks; defer offscreen cards until scrolled into view.
      if(rect.top>viewport+100){
        observer.observe(el);
      }else{
        el.classList.add('dsa-enter');
        el.style.setProperty('--dsa-delay',`${Math.min(i,10)*58}ms`);
      }
    });
    [...nav.querySelectorAll('button')].forEach((el,i)=>{
      if(watched.has(el))return;
      watched.add(el);
      el.classList.add('dsa-nav-enter');
      el.style.setProperty('--dsa-delay',`${Math.min(i,12)*32}ms`);
    });
  }
  const observer=new IntersectionObserver(entries=>{
    for(const entry of entries){
      if(!entry.isIntersecting)continue;
      const el=entry.target;
      el.classList.add('dsa-enter');
      el.style.setProperty('--dsa-delay','0ms');
      observer.unobserve(el);
    }
  },{rootMargin:'0px 0px 70px 0px',threshold:0.06});
  const mo=new MutationObserver(()=>{
    cancelAnimationFrame(pending);
    pending=requestAnimationFrame(animate);
  });
  mo.observe(page,{childList:true});
  mo.observe(nav,{childList:true});
  animate();
  window.addEventListener('pageshow',animate,{passive:true});
})();
