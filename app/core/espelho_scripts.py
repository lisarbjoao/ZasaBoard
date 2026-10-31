"""Scripts locais de clique simples; sem leitura de credenciais ou transporte de teclas."""
import json

PARAR="window.__idleboardEspelho?.parar();"
ROTA_FN="""function rota(){let h=2166136261;const r=location.pathname+location.search+location.hash;for(let i=0;i<r.length;i++)h=Math.imul(h^r.charCodeAt(i),16777619);return (h>>>0).toString(16);} """

SONDAR=r'''(() => {
 if (window.top!==window) return JSON.stringify({erro:'quadro'});
 if (location.origin!==__ORIGEM__) return JSON.stringify({erro:'origem'});
 __ROTA_FN__
 window.scrollTo(0,0);
 return JSON.stringify({w:innerWidth,h:innerHeight,dpr:devicePixelRatio,path:location.pathname,rota:rota()});
})()'''

INSTALAR=r'''(() => {
 const token=__TOKEN__,origem=__ORIGEM__;
 if (window.top!==window || location.origin!==origem) return false;
 __ROTA_FN__
 if(__ROTA__!==null && rota()!==__ROTA__)return false;
 window.__idleboardEspelho?.parar();
 const eventos=new AbortController();let sequencia=0;
 function bloqueado(no) {
   if(!no)return true;
   if(no.closest('iframe,input:not([type=checkbox]):not([type=radio]):not([type=button]),textarea,select,[contenteditable]:not([contenteditable=false])') ||
      no.closest('form')?.querySelector('input[type=password]'))return true;
   const associado=no.closest('label')?.control;
   return associado && associado!==no ? bloqueado(associado) : false;
 }
 function alvo(x,y) {
   const no=document.elementFromPoint(x,y);
   if(bloqueado(no))return null;
   return no;
 }
 function marca(no) {
   const c=no.closest('button,a,[role=button],input,canvas') || no;
   const rotulo=n=>(n.textContent || '').replace(/\s+/g,' ').trim().slice(0,100);
   let identidade;
   if(c.id && [...document.querySelectorAll('[id]')].filter(n=>n.id===c.id).length===1)identidade='#'+c.id;
   else if(c.matches('button,a,[role=button]') && rotulo(c) &&
      [...document.querySelectorAll('button,a,[role=button]')].filter(n=>n.tagName===c.tagName && rotulo(n)===rotulo(c)).length===1)
       identidade=c.tagName+':'+rotulo(c);
   else return null;
   const caminho=[];let atual=no;
   while(atual!==c){
     const pai=atual.parentElement;if(!pai || caminho.length>=8)return null;
     caminho.unshift(atual.tagName+':'+[...pai.children].indexOf(atual));atual=pai;
   }
   const id=identidade+'/'+caminho.join('/');if(id.length>100)return null;
   return {tag:no.tagName,id,texto:c.matches('button,a,[role=button]')?rotulo(c):''};
 }
 function areasRolagem(x,y){
   const areas=[];
   let no=document.elementFromPoint(x,y);if(bloqueado(no))return areas;
   while(no && no!==document.documentElement){
     const css=getComputedStyle(no);
     if((/(auto|scroll)/.test(css.overflowY) && no.scrollHeight>no.clientHeight) ||
        (/(auto|scroll)/.test(css.overflowX) && no.scrollWidth>no.clientWidth))areas.push(no);
     no=no.parentElement;
   }
   if(document.scrollingElement && !areas.includes(document.scrollingElement))areas.push(document.scrollingElement);
   return areas;
 }
 function marcaRolagem(no){
   const caminho=[];let n=no;
   while(n && n!==document.documentElement){
     const pai=n.parentElement;if(!pai || caminho.length>=16)return null;
     caminho.unshift(n.tagName+':'+[...pai.children].indexOf(n));n=pai;
   }
   const id=caminho.join('/');if(id.length>100)return null;
   return {tag:no.tagName,id,texto:''};
 }
 const estado={token,alvo,marca,rota,areasRolagem,marcaRolagem,ativo:true,ultima:0,pendente:null};
 function enviar(tipo,no,x=0,y=0,roda=null){
   window.ipc.postMessage(JSON.stringify({token,seq:++sequencia,tipo,x,y,w:innerWidth,h:innerHeight,
    dpr:devicePixelRatio,sx:scrollX,sy:scrollY,path:location.pathname,rota:rota(),ate:Date.now()+750,
    ...(roda?{roda}:{}),marca:no?(roda?marcaRolagem(no):marca(no))||{tag:'',id:'',texto:''}:{tag:'',id:'',texto:''}}));
 }
 function mudou(){if(estado.ativo){estado.ativo=false;enviar('parar',null);}}
 function capturar(e) {
   if(!estado.ativo || !e.isTrusted || e.button!==0 || e.ctrlKey || e.altKey || e.shiftKey || e.metaKey || e.detail===0)return;
   const no=alvo(e.clientX,e.clientY);if(!no)return;
   enviar(e.detail===1 && marca(no)?'clique':'pausa',no,e.clientX,e.clientY);
 }
 document.addEventListener('click',capturar,{capture:true,signal:eventos.signal});
 let rodaTimer=null,capturaRoda=null;
 document.addEventListener('wheel',e=>{
   if(!estado.ativo || !e.isTrusted || e.ctrlKey || e.altKey || e.shiftKey || e.metaKey)return;
   const areas=areasRolagem(e.clientX,e.clientY);if(!areas.length)return;
   if(!capturaRoda)capturaRoda=new Map();
   for(const no of areas)if(!capturaRoda.has(no))capturaRoda.set(no,{top:no.scrollTop,left:no.scrollLeft});
   clearTimeout(rodaTimer);
   rodaTimer=setTimeout(()=>{
     const capturadas=capturaRoda;capturaRoda=null;
     if(!estado.ativo || !capturadas)return;
     const alteradas=[...capturadas].filter(([no,p])=>no.isConnected && (Math.abs(no.scrollTop-p.top)>.01 || Math.abs(no.scrollLeft-p.left)>.01));
     if(alteradas.length===0)return;
     if(alteradas.length!==1){enviar('pausa',null);return;}
     const no=alteradas[0][0];if(!marcaRolagem(no)){enviar('pausa',null);return;}
     enviar('rolagem',no,e.clientX,e.clientY,{top:no.scrollTop,left:no.scrollLeft});
   },80);
 },{capture:true,passive:true,signal:eventos.signal});
 eventos.signal.addEventListener('abort',()=>{clearTimeout(rodaTimer);capturaRoda=null;});
 document.addEventListener('keydown',e=>{
   if(e.isTrusted && e.key==='Escape')mudou();
 },{capture:true,signal:eventos.signal});
 window.addEventListener('hashchange',mudou,{signal:eventos.signal});
 window.addEventListener('popstate',mudou,{signal:eventos.signal});
 const originais={},envolvidos={};
 for(const nome of ['pushState','replaceState']){
   originais[nome]=history[nome];
   envolvidos[nome]=function(...args){const antes=rota();const r=Reflect.apply(originais[nome],this,args);if(rota()!==antes)mudou();return r;};
   history[nome]=envolvidos[nome];
 }
 estado.parar=()=>{estado.ativo=false;eventos.abort();for(const nome of Object.keys(originais))if(history[nome]===envolvidos[nome])history[nome]=originais[nome];delete window.__idleboardEspelho;};
 window.__idleboardEspelho=estado;
 return true;
})()'''

APLICAR=r'''(() => {
 const e=__EVENTO__,s=window.__idleboardEspelho;
 const doc=document,conferir=__CONFERIR__;
 function valido(){return window.top===window && location.origin===__ORIGEM__ && s && s.ativo &&
   window.__idleboardEspelho===s && document===doc && s.token===e.token && Date.now()<=e.ate &&
   (conferir?e.rodada===s.ultima:e.rodada>s.ultima) && Math.abs(innerWidth-e.w)<=1 && Math.abs(innerHeight-e.h)<=1 &&
   devicePixelRatio===e.dpr && (e.tipo==='rolagem' || (scrollX===e.sx && scrollY===e.sy)) && location.pathname===e.path && s.rota()===e.rota;}
 if(!valido())return JSON.stringify({ok:false});
 const rolando=e.tipo==='rolagem';
 const alvoAtual=()=>rolando?s.areasRolagem(e.x,e.y).find(n=>JSON.stringify(s.marcaRolagem(n))===JSON.stringify(e.marca)):s.alvo(e.x,e.y);
 const no=alvoAtual();
 const assinatura=()=>rolando?s.marcaRolagem(no):s.marca(no);
 function mesmo(){return no && no.isConnected && valido() && alvoAtual()===no && JSON.stringify(assinatura())===JSON.stringify(e.marca);}
 if(!mesmo())return JSON.stringify({ok:false});
 if(rolando && (e.roda.top>Math.max(0,no.scrollHeight-no.clientHeight)+1 || e.roda.left>Math.max(0,no.scrollWidth-no.clientWidth)+1))return JSON.stringify({ok:false});
 if(conferir)return JSON.stringify({ok:rolando && Math.abs(no.scrollTop-e.roda.top)<=1 && Math.abs(no.scrollLeft-e.roda.left)<=1});
 if(__EXECUTAR__){
   if(!s.pendente || s.pendente.rodada!==e.rodada || s.pendente.ate!==e.ate)return JSON.stringify({ok:false});
   if(rolando){no.scrollTo({top:e.roda.top,left:e.roda.left,behavior:'instant'});s.ultima=e.rodada;s.pendente=null;return JSON.stringify({ok:true});}
   const base={bubbles:true,cancelable:true,composed:true,view:window,clientX:e.x,clientY:e.y,button:0};
   const lista=[new PointerEvent('pointerdown',{...base,buttons:1,pointerId:1,pointerType:'mouse',isPrimary:true}),
    new MouseEvent('mousedown',{...base,buttons:1}),new PointerEvent('pointerup',{...base,buttons:0,pointerId:1,pointerType:'mouse',isPrimary:true}),
    new MouseEvent('mouseup',{...base,buttons:0}),new MouseEvent('click',{...base,buttons:0,detail:1})];
   for(const evento of lista){if(!mesmo())return JSON.stringify({ok:false});no.dispatchEvent(evento);}
   s.ultima=e.rodada;s.pendente=null;
 }else s.pendente={rodada:e.rodada,ate:e.ate};
 return JSON.stringify({ok:true});
})()'''


def sondar(origem):return SONDAR.replace('__ORIGEM__',json.dumps(origem)).replace('__ROTA_FN__',ROTA_FN)
def instalar(origem,token,rota=None):return INSTALAR.replace('__ORIGEM__',json.dumps(origem)).replace('__TOKEN__',json.dumps(token)).replace('__ROTA__',json.dumps(rota)).replace('__ROTA_FN__',ROTA_FN)
def aplicar(origem,evento,executar,conferir=False):
    return APLICAR.replace('__ORIGEM__',json.dumps(origem)).replace('__EVENTO__',json.dumps(evento,allow_nan=False)).replace('__EXECUTAR__','true' if executar else 'false').replace('__CONFERIR__','true' if conferir else 'false')
