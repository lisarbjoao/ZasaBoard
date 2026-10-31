"""Prova de uma sessão WebView2 persistente, isolada e sem ponte página→Python."""

from pathlib import Path
from urllib.parse import urlsplit
import msvcrt
import tkinter as tk
from core.ambiente import PASTA_PERFIS

URL_POKEIDLE = "https://pokeidle.io/app"
PASTA_PROVA = PASTA_PERFIS / 'pokeidle' / 'prova-01'


def criar_estado(pasta=PASTA_PROVA):
    return {"pasta": Path(pasta).resolve(), "web": None, "sessao": None,
            "trava": None, "host": None, "status": "Fechado", "notificar": None, '_grupo': None,
            'pagina_pronta': False}


def informar(estado, mensagem):
    estado["status"] = mensagem
    if estado["notificar"] is not None:
        estado["notificar"](mensagem)


def validar_url(url):
    destino = urlsplit(url)
    return destino.scheme in ("http", "https") and bool(destino.hostname) and not destino.username and not destino.password


def zoom_cartao(largura, escala=1.0, modo='encaixar'):
    """Conserva uma largura desktop de referência, sem ampliar acima de 100%."""
    if modo == 'responsiva':
        return 1.0
    return max(0.25, min(1.0, largura / (1100 * escala)))


def ajustar_zoom(estado):
    web, host = estado["web"], estado["host"]
    if web is None or not web.ready or host is None or not host.winfo_ismapped():
        return
    escala = host.winfo_fpixels("1i") / 96
    zoom = estado.get('_zoom_espelhado',round(zoom_cartao(host.winfo_width(), escala, estado.get('visualizacao', 'encaixar')), 3))
    if estado.get("zoom") != zoom:
        web.set_zoom(zoom)
        estado["zoom"] = zoom


def cancelar_ajuste_zoom(estado):
    tarefa = estado.pop('_ajuste_zoom', None)
    host = estado.get('host')
    if tarefa is not None and host is not None:
        try:
            host.after_cancel(tarefa)
        except tk.TclError:
            pass
    estado['_ajuste_zoom'] = None


def agendar_zoom(estado):
    host = estado.get('host')
    if host is None:
        return
    cancelar_ajuste_zoom(estado)

    def aplicar():
        estado['_ajuste_zoom'] = None
        if estado.get('host') is host:
            ajustar_zoom(estado)

    estado['_ajuste_zoom'] = host.after(60, aplicar)


def abrir(estado, host, url=URL_POKEIDLE, compartilhar=None):
    """Executar na thread da janela. Uma pasta não pode abrir em dois processos."""
    if estado["web"] is not None:
        return
    estado['pagina_pronta']=False
    if not validar_url(url):
        informar(estado, "Endereço inválido")
        return
    try:
        from tkwry import WebSession, WebView, PageLoadEvent, NewWindowResponse, PermissionResponse
        grupo = compartilhar.get('_grupo') if compartilhar is not None else None
        if grupo is not None:
            if compartilhar['pasta'] != estado['pasta'] or grupo['referencias'] <= 0:
                raise ValueError('Sessão compartilhada pertence a outro perfil.')
            grupo['referencias'] += 1
            estado['_grupo'] = grupo
            estado['sessao'] = grupo['sessao']
        else:
            estado["pasta"].mkdir(parents=True, exist_ok=True)
            trava = (estado["pasta"] / ".idleboard.lock").open("a+b")
            estado["trava"] = trava
            if trava.tell() == 0:
                trava.write(b"0"); trava.flush()
            trava.seek(0)
            msvcrt.locking(trava.fileno(), msvcrt.LK_NBLCK, 1)
            estado['sessao'] = WebSession(data_directory=estado['pasta'])
            estado['_grupo'] = {'sessao': estado['sessao'], 'trava': trava, 'referencias': 1}
        estado["host"] = host
        informar(estado, "Abrindo navegador…")

        def carregou(evento, endereco):
            if estado["web"] is not None:
                concluir=estado.pop('_espelho_concluir',None)
                if concluir is not None:concluir()
                estado['pagina_pronta']=evento!=PageLoadEvent.Started
                ajustar_zoom(estado)
                informar(estado, "Carregando página…" if evento == PageLoadEvent.Started else "Página carregada · perfil local")
                if evento != PageLoadEvent.Started and estado.get('_pagina_carregada'):
                    estado['_pagina_carregada']()

        def falhou(erro):
            fechar(estado, avisar=False)
            informar(estado, "Não foi possível abrir o navegador")

        def navegar(evento):
            interromper=estado.get('_espelho_invalidar')
            if interromper is not None:interromper('Espelhamento pausado: página mudou.')
            estado['pagina_pronta']=False
            return validar_url(evento.url) or evento.url=='about:blank'

        from core.hunt_local import script_para
        script_hunt = script_para(estado['pasta'])
        scripts = [s for s in (estado.get('_script_inicial'), script_hunt) if s]
        estado["web"] = WebView(host, url=url, session=estado["sessao"],
            bridge_origins=["https://idleboard.invalid"], bridge_allow=lambda _: False,
            on_navigation=navegar,
            on_page_load=carregou, on_creation_failed=falhou,
            on_new_window=lambda _: NewWindowResponse.Deny,
            on_download=lambda _: False, permission_handler=lambda _: PermissionResponse.Deny,
            javascript_enabled=True, autoplay=False, devtools=False, focused=False,
            initialization_script='\n;\n'.join(scripts) or None,
            background_color=(34,40,59,255))
        # O host nativo acompanha o cartão; o zoom mantém o conteúdo proporcional.
        if not getattr(host, "_idleboard_zoom_instalado", False):
            host.bind("<Configure>", lambda _evento: agendar_zoom(estado), add="+")
            host._idleboard_zoom_instalado = True
        host.bind("<Destroy>", lambda evento: fechar(estado) if evento.widget == host else None, add="+")
    except (ImportError, OSError, RuntimeError, ValueError):
        fechar(estado, avisar=False)
        informar(estado, "Navegador indisponível ou perfil já aberto")


def fechar(estado, avisar=True):
    """Encerra a página e libera a pasta; não apaga cookies nem dados do perfil."""
    encerrar_lives=estado.pop('_ao_fechar_jogo',None)
    if encerrar_lives is not None:encerrar_lives()
    interromper=estado.pop('_espelho_parar',None)
    if interromper is not None:interromper('Espelhamento pausado: sessão fechada.')
    estado['pagina_pronta']=False
    janela_audio = estado.pop('_janela_audio', None)
    if janela_audio is not None and janela_audio.winfo_exists():
        janela_audio.destroy()
    cancelar_ajuste_zoom(estado)
    web, sessao, trava = estado["web"], estado["sessao"], estado["trava"]
    grupo = estado.get('_grupo')
    if web is None and sessao is None and trava is None:
        return
    estado.update(web=None, sessao=None, trava=None, host=None, zoom=None, _grupo=None)
    try:
        if web is not None:
            web.destroy()
    finally:
        if grupo is not None:
            grupo['referencias'] -= 1
            if grupo['referencias'] > 0:
                sessao, trava = None, None
            else:
                sessao, trava = grupo['sessao'], grupo['trava']
                grupo.update(sessao=None, trava=None)
        try:
            if sessao is not None:
                sessao.close()
        finally:
            if trava is not None:
                # Fechar o handle libera também uma eventual trava não adquirida.
                trava.close()
    if avisar:
        informar(estado, "Fechado · perfil preservado")


def recarregar(estado):
    if estado["web"] is not None and estado["web"].ready:
        estado["web"].reload()
