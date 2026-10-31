"""Controle efêmero de cliques entre cartões compatíveis do mesmo jogo."""
import json
import math
import re
import secrets
import time
import tkinter as tk
from urllib.parse import urlsplit
from core import browserman,espelho_scripts as scripts


def origem_url(url):
    p=urlsplit(url)
    if p.scheme not in ('http','https') or not p.hostname or p.username or p.password:
        raise ValueError('Origem de jogo inválida.')
    host=p.hostname.encode('idna').decode('ascii').lower()
    if ':' in host:host='['+host+']'
    porta=p.port
    sufixo=':'+str(porta) if porta and porta!={'http':80,'https':443}[p.scheme] else ''
    return p.scheme+'://'+host+sufixo


def validar_evento(texto,token):
    if not isinstance(texto,str) or len(texto.encode('utf-8'))>2048:raise ValueError('Mensagem inválida.')
    try:e=json.loads(texto)
    except (ValueError,RecursionError):raise ValueError('JSON de evento inválido.') from None
    campos={'token','seq','tipo','x','y','w','h','dpr','sx','sy','path','marca','rota','ate'}
    if isinstance(e,dict) and e.get('tipo')=='rolagem':campos.add('roda')
    if not isinstance(e,dict) or set(e)!=campos or e['token']!=token or e['tipo'] not in ('clique','pausa','parar','rolagem'):
        raise ValueError('Evento inválido.')
    for k in ('x','y','w','h','dpr','sx','sy'):
        if type(e[k]) not in (int,float) or not math.isfinite(e[k]):raise ValueError('Coordenada inválida.')
    if type(e['seq']) is not int or e['seq']<1:
        raise ValueError('Sequência ou viewport inválido.')
    if not (100<=e['w']<=16384 and 100<=e['h']<=16384 and 0<=e['x']<e['w'] and 0<=e['y']<e['h'] and 0<e['dpr']<=64):
        raise ValueError('Evento fora da área de jogo.')
    if not (0<=e['sx']<=10**7 and 0<=e['sy']<=10**7) or not isinstance(e['path'],str) or len(e['path'])>500:
        raise ValueError('Posição inválida.')
    if not isinstance(e['rota'],str) or not re.fullmatch(r'[0-9a-f]{1,8}',e['rota']):raise ValueError('Rota inválida.')
    if type(e['ate']) is not int or not 0<e['ate']-time.time()*1000<=1000:raise ValueError('Evento expirado.')
    if e['tipo']=='rolagem':
        r=e['roda']
        if not isinstance(r,dict) or set(r)!={'top','left'} or any(type(n) not in (int,float) or not math.isfinite(n) or not 0<=n<=10**7 for n in r.values()):raise ValueError('Rolagem inválida.')
    m=e['marca']
    if not isinstance(m,dict) or set(m)!={'tag','id','texto'} or any(not isinstance(v,str) or len(v)>100 for v in m.values()):
        raise ValueError('Alvo inválido.')
    return e


def decodificar(valor):
    for _ in range(3):
        if not isinstance(valor,str):break
        valor=json.loads(valor)
    return valor


class Controlador:
    def __init__(self,pai,perfis,notificar):
        self.pai,self.perfis,self.notificar=pai,perfis,notificar
        self.ativo=self.preparando=self.ocupado=self.alinhado=False
        self.geracao=0;self.grupo=[];self.tarefa=None;self.vigia=None;self.rolagem_pendente=None

    def _cancelar(self):
        if self.tarefa is not None:
            try:self.pai.after_cancel(self.tarefa)
            except tk.TclError:pass
            self.tarefa=None

    def _vigiar(self):
        self.vigia=None
        for item in self.grupo:
            concluir=item['estado'].pop('_espelho_concluir',None)
            if concluir is not None:
                concluir();return
        if self.grupo:self.vigia=self.pai.after(200,self._vigiar)

    def _limite(self):
        self._cancelar()
        self.tarefa=self.pai.after(3000,lambda:self.parar('Espelhamento pausado: página sem resposta.'))

    def invalidar(self,mensagem):
        """Revoga já; chamadas nativas aguardam sair do callback de navegação."""
        if not (self.ativo or self.preparando or self.alinhado):return
        self.ativo=self.preparando=self.alinhado=False;self.geracao+=1
        for item in self.grupo:item['estado']['_espelho_concluir']=lambda:self.parar(mensagem)

    def parar(self,mensagem='Espelhamento desligado.'):
        self.ativo=self.preparando=self.ocupado=self.alinhado=False
        self.rolagem_pendente=None
        self.geracao+=1;self._cancelar()
        if self.vigia is not None:
            try:self.pai.after_cancel(self.vigia)
            except tk.TclError:pass
            self.vigia=None
        grupo,self.grupo=self.grupo,[]
        # Revogar permissão antes de limpar JS ou restaurar geometria.
        for item in grupo:
            s,w=item['estado'],item['web']
            s.pop('_espelho_parar',None);s.pop('_espelho_invalidar',None);s.pop('_espelho_concluir',None);s.pop('_zoom_espelhado',None)
            try:
                w.set_bridge_allow(lambda _:False);w.set_bridge_origins(['https://idleboard.invalid']);w.set_on_ipc(None)
                if s.get('web') is w and w.ready:w.eval_js(scripts.PARAR)
            except (RuntimeError,ValueError,tk.TclError):pass
            for evento,ident in item.get('vinculos',[]):
                try:item['host'].unbind(evento,ident)
                except tk.TclError:pass
            try:
                host=item['host']
                if host.winfo_exists():
                    host.configure(width=item['pedido'][0],height=item['pedido'][1])
                    host.pack_configure(**item['pack'])
                    browserman.agendar_zoom(s)
            except tk.TclError:pass
        self.notificar(mensagem)

    def _consultar(self,item,codigo,callback,geracao):
        if self.geracao!=geracao:return
        if item['estado'].get('web') is not item['web']:
            return self.parar('Espelhamento pausado: sessão alterada.')
        def receber(valor):
            if self.geracao!=geracao:return
            try:callback(decodificar(valor))
            except ValueError as erro:
                conhecidos={'Viewport inválido.','Dimensões inválidas.','Página inválida.','Rota inválida.','Captura indisponível.','Geometria alterada.','Alvo diferente.'}
                detalhe=str(erro) if str(erro) in conhecidos else 'Resposta da página inválida.'
                self.parar('Espelhamento pausado: '+detalhe)
            except (TypeError,KeyError,RecursionError,RuntimeError,tk.TclError):self.parar('Espelhamento pausado: resposta incompatível.')
        def falhou(_):
            if self.geracao==geracao:self.parar('Espelhamento pausado: controle indisponível.')
        try:item['web'].eval_js_with_callback(codigo,callback=receber,on_error=falhou)
        except (RuntimeError,ValueError):falhou(None)

    def alinhar(self):
        return self.ativar(apenas_alinhar=True)

    def ativar(self,apenas_alinhar=False):
        self.parar('Preparando alinhamento…' if apenas_alinhar else 'Preparando espelhamento…')
        self.apenas_alinhar=apenas_alinhar
        try:
            for p in self.perfis:
                s=p.get('_sessao_teste')
                if not p.get('visivel') or not s or s.get('web') is None:continue
                host=s.get('host');web=s['web']
                if not web.ready or not s.get('pagina_pronta') or host is None or not host.winfo_ismapped():
                    raise ValueError('Exiba e aguarde o carregamento dos cartões abertos.')
                self.grupo.append({'estado':s,'web':web,'host':host,'seq':0,'vinculos':[],
                    'origem':origem_url(p.get('_url_jogo',browserman.URL_POKEIDLE)),
                    'pack':host.pack_info(),'pedido':(host.cget('width'),host.cget('height'))})
            if len(self.grupo)<2:raise ValueError('Abra pelo menos dois cartões visíveis do mesmo jogo.')
            if len({i['origem'] for i in self.grupo})!=1:raise ValueError('Os cartões precisam usar a mesma origem de jogo.')
            self.origem=self.grupo[0]['origem'];self.token=secrets.token_hex(16);self.rodada=0
            self.preparando=True;geracao=self.geracao
            self.notificar('Alinhando as páginas para o espelhamento…')
            self.pai.update_idletasks()
            self.largura=min(i['host'].winfo_width() for i in self.grupo)
            self.altura=min(i['host'].winfo_height() for i in self.grupo)
            if min(self.largura,self.altura)<100:raise ValueError('Os cartões estão pequenos demais para alinhar.')
            escala=self.grupo[0]['host'].winfo_fpixels('1i')/96
            zoom=round(browserman.zoom_cartao(self.largura,escala),3)
            for item in self.grupo:
                s,host=item['estado'],item['host']
                browserman.cancelar_ajuste_zoom(s)
                s['_zoom_espelhado']=zoom;s['_espelho_parar']=self.parar;s['_espelho_invalidar']=self.invalidar
                host.configure(width=self.largura,height=self.altura)
                host.pack_configure(fill='none',expand=True)
                browserman.ajustar_zoom(s)
            self._limite();self._vigiar()
            self.pai.after(150,lambda:self._sondar(geracao))
            return True
        except (ValueError,RuntimeError,tk.TclError) as erro:
            self.parar(str(erro));return False

    def _sondar(self,geracao,tentativa=0):
        if self.geracao!=geracao:return
        self.viewport=None;pendentes=set(id(i) for i in self.grupo);valores=[]
        def recebeu(item,v):
            if isinstance(v,dict) and v.get('erro') in ('quadro','origem'):
                self.parar('Espelhamento pausado: '+('o jogo está dentro de outro quadro.' if v['erro']=='quadro' else 'a página aberta está em uma origem diferente da URL cadastrada.'));return
            if not isinstance(v,dict) or set(v)!={'w','h','dpr','path','rota'}:raise ValueError('Viewport inválido.')
            validas=all(type(v[k]) in (int,float) and math.isfinite(v[k]) and 100<=v[k]<=16384 for k in ('w','h'))
            escala_valida=type(v['dpr']) in (int,float) and math.isfinite(v['dpr']) and 0<v['dpr']<=64
            if not validas or not escala_valida:
                def medida(k):
                    n=v.get(k)
                    return f'{n:g}' if type(n) in (int,float) else type(n).__name__
                self.parar(f"Espelhamento pausado: medidas inválidas ({medida('w')} × {medida('h')}, escala {medida('dpr')}).");return
            if not isinstance(v['path'],str) or len(v['path'])>500:raise ValueError('Página inválida.')
            if not isinstance(v['rota'],str) or not re.fullmatch(r'[0-9a-f]{1,8}',v['rota']):raise ValueError('Rota inválida.')
            valores.append(v)
            pendentes.discard(id(item))
            if not pendentes:
                if any(v!=valores[0] for v in valores):
                    if tentativa<6:
                        self.pai.after(200,lambda:self._sondar(geracao,tentativa+1));return
                    motivo='página/rota' if any(v['path']!=valores[0]['path'] or v['rota']!=valores[0]['rota'] for v in valores) else 'área/escala'
                    medidas=' / '.join(f"{v['w']}×{v['h']} @ {v['dpr']:g}" for v in valores)
                    self.parar(f'Espelhamento pausado: {motivo} diferente ({medidas}).');return
                self.viewport=valores[0]
                if getattr(self,'apenas_alinhar',False):
                    self.preparando=False;self.alinhado=True;self._cancelar()
                    for participante in self.grupo:self._observar_geometria(participante)
                    self.notificar(f'{len(self.grupo)} cartões alinhados · clique em Espelhar para ativar');return
                self._instalar(geracao)
        for item in list(self.grupo):
            self._consultar(item,scripts.sondar(self.origem),lambda v,i=item:recebeu(i,v),geracao)

    def _hosts_compativeis(self):
        return all(i['estado'].get('web') is i['web'] and i['estado'].get('pagina_pronta') and i['host'].winfo_ismapped() and (i['host'].winfo_width(),i['host'].winfo_height())==(self.largura,self.altura) for i in self.grupo)

    def _observar_geometria(self,item):
        for evento in ('<Configure>','<Unmap>'):
            def mudou(e,i=item):
                if (self.ativo or self.preparando or self.alinhado) and (e.type==tk.EventType.Unmap or
                   (i['host'].winfo_width(),i['host'].winfo_height())!=(self.largura,self.altura)):
                    self.parar('Espelhamento pausado: tamanho ou visibilidade mudou.')
            item['vinculos'].append((evento,item['host'].bind(evento,mudou,add='+')))

    def _instalar(self,geracao):
        pendentes=set(id(i) for i in self.grupo)
        def pronto(item,valor):
            if valor is not True:raise ValueError('Captura indisponível.')
            pendentes.discard(id(item))
            if not pendentes:
                if not self._hosts_compativeis():raise ValueError('Geometria alterada.')
                self.preparando=False;self.ativo=True;self.ultimo=0;self._cancelar()
                self.notificar(f'Espelhando {len(self.grupo)} cartões · mantenha a mesma tela · Esc para parar')
        for item in list(self.grupo):
            w=item['web']
            w.set_bridge_origins([self.origem])
            def permitir(url):
                try:return self.ativo and origem_url(url)==self.origem and urlsplit(url).path==self.viewport['path']
                except (ValueError,TypeError):return False
            w.set_bridge_allow(permitir)
            w.set_on_ipc(lambda texto,i=item:self.receber(i,texto))
            self._observar_geometria(item)
            self._consultar(item,scripts.instalar(self.origem,self.token,self.viewport['rota']),lambda v,i=item:pronto(i,v),geracao)

    def receber(self,item,texto):
        if not self.ativo or not any(i is item for i in self.grupo):return
        try:e=validar_evento(texto,self.token)
        except (ValueError,TypeError):return self.parar('Espelhamento pausado: evento inválido.')
        if e['tipo']=='rolagem' and self.ocupado:
            self.rolagem_pendente=(item,texto);return
        if e['seq']<=item['seq']:return
        item['seq']=e['seq']
        if e['tipo']=='parar':return self.parar('Espelhamento desligado: tecla Esc ou página alterada.')
        if e['tipo']=='pausa' or self.ocupado or (e['tipo']!='rolagem' and time.monotonic()-self.ultimo<.08):
            return self.parar('Espelhamento pausado: use um clique simples por vez.')
        if any(e[k]!=self.viewport[k] for k in ('w','h','dpr','path','rota')) or not self._hosts_compativeis():
            return self.parar('Espelhamento pausado: página desalinhada.')
        self.rodada+=1;e['rodada']=self.rodada
        self.ultimo=time.monotonic();self.ocupado=True;self._limite()
        geracao=self.geracao;destinos=[i for i in self.grupo if i is not item]
        def concluir():
            self.ocupado=False;self._cancelar()
            proxima=self.rolagem_pendente;self.rolagem_pendente=None
            if proxima:self.receber(*proxima)
        def conferir(restantes):
            if self.geracao!=geracao:return
            pendentes=set(id(i) for i in destinos)
            def confirmou(destino,r):
                if not isinstance(r,dict) or r.get('ok') is not True:
                    self.parar('Espelhamento pausado: o painel não manteve a posição de rolagem.');return
                pendentes.discard(id(destino))
                if not pendentes:
                    if restantes>1:self.pai.after(80,lambda:conferir(restantes-1))
                    else:concluir()
            for destino in destinos:
                self._consultar(destino,scripts.aplicar(self.origem,e,False,conferir=True),lambda r,i=destino:confirmou(i,r),geracao)
        def rodada(executar):
            pendentes=set(id(i) for i in destinos)
            def recebeu(destino,r):
                if not isinstance(r,dict) or r.get('ok') is not True:
                    raise ValueError('Alvo diferente.')
                pendentes.discard(id(destino))
                if not pendentes:
                    if not executar:rodada(True)
                    elif e['tipo']=='rolagem':self.pai.after(80,lambda:conferir(2))
                    else:concluir()
            for destino in destinos:
                self._consultar(destino,scripts.aplicar(self.origem,e,executar),lambda r,i=destino:recebeu(i,r),geracao)
        rodada(False)
