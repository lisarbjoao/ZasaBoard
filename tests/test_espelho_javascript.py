import json
from pathlib import Path
import shutil
import subprocess
import unittest
from core import espelho_scripts as scripts

NODE=shutil.which('node') or ('C:/Program Files/nodejs/node.exe' if Path('C:/Program Files/nodejs/node.exe').is_file() else None)


@unittest.skipUnless(NODE,'Requer Node para executar scripts sintéticos')
class EspelhoJavascriptTest(unittest.TestCase):
    def test_manual_click_only_target_guards_and_no_feedback_loop(self):
        codigo=r'''
const vm=require('node:vm'),assert=require('node:assert/strict');
const fontes=JSON.parse(process.argv[1]),mensagens=[],eventos={},rotas={};let bloqueado=false,cliques=0;
const no={tagName:'BUTTON',id:'teste',textContent:'Somar',isConnected:true,
 closest(sel){if(sel.startsWith('iframe,'))return bloqueado?this:null;if(sel==='form' || sel==='label')return null;return this;},
 matches(){return true;},dispatchEvent(e){if(e.type==='click'){cliques++;eventos.click?.(e);}return true;}};
class Evento{constructor(tipo,opcoes){Object.assign(this,opcoes);this.type=tipo;this.isTrusted=false;}}
const window={ipc:{postMessage(m){mensagens.push(JSON.parse(m));}}};window.top=window;window.addEventListener=(tipo,fn)=>rotas[tipo]=fn;
const document={querySelectorAll(){return [no];},elementFromPoint(){return no;},addEventListener(tipo,fn,op){eventos[tipo]=fn;op.signal.addEventListener('abort',()=>delete eventos[tipo]);}};
const c=vm.createContext({window,document,location:{origin:'https://game.example',pathname:'/app',search:'',hash:''},history:{pushState(){},replaceState(){}},
 innerWidth:800,innerHeight:600,devicePixelRatio:1,scrollX:0,scrollY:0,setTimeout,clearTimeout,AbortController,PointerEvent:Evento,MouseEvent:Evento});
assert.equal(vm.runInContext(fontes.instalar,c),true);
const e={isTrusted:true,button:0,detail:1,clientX:40,clientY:40};
eventos.click({...e,isTrusted:false});assert.equal(mensagens.length,0);
eventos.click({...e,ctrlKey:true});assert.equal(mensagens.length,0);
bloqueado=true;eventos.click(e);assert.equal(mensagens.length,0);bloqueado=false;
eventos.click(e);assert.equal(mensagens.length,1);assert.equal(mensagens[0].token,'token-teste');
mensagens[0].rodada=1;
const aplicar=fontes.aplicar.replace('__EVENTO_TESTE__',JSON.stringify(mensagens[0]));
assert.equal(JSON.parse(vm.runInContext(aplicar.replace('if(true){','if(false){'),c)).ok,true);
assert.equal(JSON.parse(vm.runInContext(aplicar,c)).ok,true);assert.equal(cliques,1);
assert.equal(mensagens.length,1);
assert.equal(JSON.parse(vm.runInContext(aplicar,c)).ok,false);assert.equal(cliques,1);
no.textContent='Outro alvo';assert.equal(JSON.parse(vm.runInContext(aplicar,c)).ok,false);assert.equal(cliques,1);
no.textContent='Somar';c.innerWidth=8010;assert.equal(JSON.parse(vm.runInContext(aplicar,c)).ok,false);
c.innerWidth=800;
mensagens[0].rodada=2;mensagens[0].ate=Date.now()-1;
assert.equal(JSON.parse(vm.runInContext(fontes.aplicar.replace('__EVENTO_TESTE__',JSON.stringify(mensagens[0])),c)).ok,false);
no.id='';document.querySelectorAll=()=>[no,{tagName:'BUTTON',textContent:'Somar'}];
eventos.click(e);assert.equal(mensagens.at(-1).tipo,'pausa');
no.tagName='CANVAS';no.matches=()=>false;eventos.click(e);assert.equal(mensagens.at(-1).tipo,'pausa');
const quantidade=mensagens.length;
const antigo=no.closest;no.closest=sel=>sel==='label'?{control:{closest(){return {};}}}:antigo.call(no,sel);
eventos.click(e);assert.equal(mensagens.length,quantidade);no.closest=antigo;
c.location.hash='#outra-tela';rotas.hashchange();assert.equal(mensagens.at(-1).tipo,'parar');
assert.equal(window.__idleboardEspelho.ativo,false);
vm.runInContext(fontes.parar,c);assert.equal(eventos.click,undefined);
'''
        fonte=scripts.APLICAR.replace('__ORIGEM__',json.dumps('https://game.example')).replace('__EXECUTAR__','true').replace('__EVENTO__','__EVENTO_TESTE__').replace('__CONFERIR__','false')
        dados={'instalar':scripts.instalar('https://game.example','token-teste'),'aplicar':fonte,'parar':scripts.PARAR}
        p=subprocess.run([NODE,'-e',codigo,json.dumps(dados)],capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,0,p.stderr)


@unittest.skipUnless(NODE,'Requer Node')
class RolagemJavascriptTest(unittest.TestCase):
    def test_painel_real_modificadores_encadeamento_e_snap(self):
        codigo=r'''const vm=require('node:vm'),assert=require('node:assert/strict');
const fontes=JSON.parse(process.argv[1]),eventos={},mensagens=[];let tarefa,snap=false;
function node(tag,pai,overflow='visible'){
 const n={tagName:tag,parentElement:pai,children:[],isConnected:true,scrollTop:0,scrollLeft:0,
 scrollHeight:100,clientHeight:100,scrollWidth:100,clientWidth:100,overflow,
 closest(){return null;},scrollTo(p){this.scrollTop=snap?Math.round(p.top/100)*100:p.top;this.scrollLeft=p.left;}};
 if(pai)pai.children.push(n);return n;
}
const html=node('HTML'),body=node('BODY',html),externo=node('DIV',body,'auto'),interno=node('DIV',externo,'auto'),folha=node('SPAN',interno);
externo.scrollHeight=1000;interno.scrollHeight=200;interno.scrollTop=100;
const window={ipc:{postMessage(m){mensagens.push(JSON.parse(m));}},addEventListener(){}};window.top=window;
const document={documentElement:html,scrollingElement:html,elementFromPoint(){return folha;},addEventListener(t,f,o){eventos[t]=f;o.signal.addEventListener('abort',()=>delete eventos[t]);}};
const c=vm.createContext({window,document,location:{origin:'https://game.example',pathname:'/app',search:'',hash:''},history:{pushState(){},replaceState(){}},
innerWidth:800,innerHeight:600,devicePixelRatio:1,scrollX:0,scrollY:0,AbortController,
getComputedStyle(n){return {overflowY:n.overflow,overflowX:n.overflow};},setTimeout(f){tarefa=f;return 1;},clearTimeout(){tarefa=null;}});
assert.equal(vm.runInContext(fontes.instalar,c),true);
const wheel={isTrusted:true,clientX:20,clientY:30};
eventos.wheel({...wheel,isTrusted:false});assert.equal(tarefa,undefined);
eventos.wheel({...wheel,ctrlKey:true});assert.equal(tarefa,undefined);
eventos.wheel(wheel);externo.scrollTop=50;tarefa();
assert.equal(mensagens.length,1);assert.equal(mensagens[0].tipo,'rolagem');
assert.deepEqual(mensagens[0].marca,JSON.parse(JSON.stringify(window.__idleboardEspelho.marcaRolagem(externo))));
const e=mensagens[0];e.rodada=1;
function aplicar(executar,conferir=false){const js=fontes.aplicar.replace('__EVENTO_TESTE__',JSON.stringify(e)).replace('__EXECUTAR__',executar?'true':'false').replace('__CONFERIR__',conferir?'true':'false');return JSON.parse(vm.runInContext(js,c));}
externo.scrollTop=0;assert.equal(aplicar(false).ok,true);assert.equal(aplicar(true).ok,true);assert.equal(aplicar(false,true).ok,true);assert.equal(externo.scrollTop,50);
// Mesmo ponto estrutural com snap: aplicação aceita, confirmação detecta desvio.
e.rodada=2;e.roda.top=75;snap=true;
assert.equal(aplicar(false).ok,true);assert.equal(aplicar(true).ok,true);assert.equal(aplicar(false,true).ok,false);
// Apenas horizontal no filho: a rolagem vertical efetiva continua sendo do pai.
interno.scrollHeight=100;interno.scrollWidth=500;externo.scrollTop=0;
eventos.wheel(wheel);externo.scrollTop=25;tarefa();assert.equal(mensagens.at(-1).marca.id,e.marca.id);
// Dois painéis alterados no mesmo gesto não podem ser confirmados como um só.
eventos.wheel(wheel);externo.scrollTop=40;interno.scrollLeft=20;tarefa();assert.equal(mensagens.at(-1).tipo,'pausa');
'''
        fonte=scripts.APLICAR.replace('__ORIGEM__',json.dumps('https://game.example')).replace('__EVENTO__','__EVENTO_TESTE__')
        dados={'instalar':scripts.instalar('https://game.example','token'),'aplicar':fonte}
        p=subprocess.run([NODE,'-e',codigo,json.dumps(dados)],capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,0,p.stderr)
