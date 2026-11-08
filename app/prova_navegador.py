"""Controles de navegador para cada perfil isolado."""

import tkinter as tk
import customtkinter as ctk
from core import browserman, audio
from core.perfis import PASTA
from aparencia import BOTAO_CARTAO, LARGURA_ICONE_CARTAO


def instalar(cartao, corpo, mensagem, rodape, perfil):
    pasta = PASTA / perfil.get('_jogo_id', 'pokeidle') / perfil['id'] if 'id' in perfil else browserman.PASTA_PROVA
    estado = perfil.setdefault("_sessao_teste", browserman.criar_estado(pasta))
    estado['visualizacao'] = perfil.get('visualizacao', 'encaixar')
    estado['_script_inicial'] = audio.script_inicial(perfil.get('audio'))
    estado['_pagina_carregada'] = lambda: audio.aplicar(estado, perfil.get('audio'))
    host = tk.Frame(corpo, bg="#252529")
    abrir = ctk.CTkButton(corpo, text=f"Abrir {perfil.get('_nome_jogo', 'PokeIdle')}", width=150, fg_color="#b94722")
    abrir.pack(pady=(0, 18))

    def atualizar(texto):
        if not cartao.winfo_exists() or not rodape.winfo_exists():
            return
        rodape.configure(text=texto)
        if estado["web"] is None and not texto.startswith("Abrindo"):
            host.pack_forget()
            mensagem.pack(expand=True, padx=14, pady=20)
            abrir.pack(pady=(0,18))
            abrir.configure(state="normal")

    estado["notificar"] = atualizar

    def iniciar():
        espelho=perfil.get('_espelho_controlador')
        if espelho is not None and (espelho.ativo or espelho.preparando):
            espelho.parar('Espelhamento pausado: grupo de cartões mudou.')
        abrir.configure(state="disabled")
        abrir.pack_forget()
        mensagem.pack_forget()
        host.pack(fill="both", expand=True, padx=0, pady=0)
        if perfil.get('_url_jogo'):
            browserman.abrir(estado, host, perfil['_url_jogo'])
        else:
            browserman.abrir(estado, host)
        if estado.get('web') is not None:
            from contas_vinculadas import manter_multitwitch,encerrar_multitwitch
            estado['_ao_fechar_jogo']=lambda:encerrar_multitwitch(perfil)
            # Abertura automática suspensa após relato de travamento do Windows.

    def atualizar_jogo():
        nome = perfil.get('_nome_jogo', 'PokeIdle')
        abrir.configure(text=f'Abrir {nome}')
        mensagem.configure(text=f'{nome}\nSessão independente')

    abrir.configure(command=iniciar)
    def alternar_visualizacao():
        espelho=perfil.get('_espelho_controlador')
        if espelho is not None and (espelho.ativo or espelho.preparando):
            espelho.parar('Espelhamento pausado: visualização mudou.')
        anterior = perfil.get('visualizacao', 'encaixar')
        perfil['visualizacao'] = 'responsiva' if anterior == 'encaixar' else 'encaixar'
        salvar = perfil.get('_salvar')
        if salvar is not None and not salvar():
            perfil['visualizacao'] = anterior
            return
        estado['visualizacao'] = perfil['visualizacao']
        browserman.ajustar_zoom(estado)
        browserman.informar(estado, 'Visualização leve' if perfil['visualizacao'] == 'responsiva'
                            else 'Página inteira ajustada')

    botao_visualizacao = ctk.CTkButton(cartao, text='\ue9a6', font=('Segoe MDL2 Assets', 16),
        width=LARGURA_ICONE_CARTAO, **BOTAO_CARTAO, command=alternar_visualizacao)
    estado['zoom_percentual'] = perfil.get('zoom_percentual')
    def escolher_zoom(percentual):
        anterior = perfil.get('zoom_percentual')
        if anterior == percentual:
            return
        perfil['zoom_percentual'] = percentual
        salvar = perfil.get('_salvar')
        if salvar and not salvar():
            perfil['zoom_percentual'] = anterior
            return
        espelho = perfil.get('_espelho_controlador')
        if espelho and (espelho.ativo or espelho.preparando or espelho.alinhado):
            espelho.parar('Espelhamento pausado: zoom do cartão alterado.')
        estado['zoom_percentual'] = percentual
        browserman.ajustar_zoom(estado)
        browserman.informar(estado, 'Zoom automático' if percentual is None else f'Zoom da página: {percentual}%')

    def abrir_zoom():
        menu = tk.Menu(cartao, tearoff=False)
        valor = tk.StringVar(master=menu, value=str(perfil.get('zoom_percentual')))
        for percentual in (None, 10, 15, 20, 25, 33, 50, 67, 75, 90, 100, 125, 150, 200):
            menu.add_radiobutton(label='Automático' if percentual is None else f'{percentual}%',
                                 variable=valor, value=str(percentual),
                                 command=lambda p=percentual: escolher_zoom(p))
        try:
            menu.tk_popup(botao_zoom.winfo_rootx(), botao_zoom.winfo_rooty()+botao_zoom.winfo_height())
        finally:
            menu.grab_release()

    rodape.grid_configure(columnspan=1)
    botao_zoom = ctk.CTkButton(cartao, text='\ue71e', font=('Segoe MDL2 Assets', 16),
        width=LARGURA_ICONE_CARTAO, **BOTAO_CARTAO, command=abrir_zoom)
    botao_zoom.grid(row=2, column=1, padx=1, pady=4)
    botao_zoom.bind('<Enter>', lambda _: rodape.configure(text='Zoom da página'))
    botao_zoom.bind('<Leave>', lambda _: rodape.configure(text=estado['status']))
    botao_visualizacao.grid(row=2, column=2, padx=1, pady=4)
    botao_visualizacao.bind('<Enter>', lambda _: rodape.configure(
        text='Alternar: visualização leve / página inteira'))
    botao_visualizacao.bind('<Leave>', lambda _: rodape.configure(text=estado['status']))
    cartao._idleboard_alternar_visualizacao = botao_visualizacao
    from audio_interface import mostrar as mostrar_audio
    botao_audio = ctk.CTkButton(cartao, text='\ue767', font=('Segoe MDL2 Assets', 16),
        width=LARGURA_ICONE_CARTAO, **BOTAO_CARTAO,
        command=lambda: mostrar_audio(cartao, perfil, estado))
    botao_audio.grid(row=0, column=3, padx=1, pady=4)
    cartao._idleboard_botao_foco.grid_configure(column=4)
    cartao._idleboard_audio = botao_audio
    def atualizar_icone_audio(config):
        botao_audio.configure(text='\ue74f' if config['silenciado'] or config['volume'] == 0 else '\ue767')
    estado['_audio_atualizado'] = atualizar_icone_audio
    atualizar_icone_audio(audio.validar(perfil.get('audio')))
    excluir = perfil.get('_excluir')
    botao_excluir = ctk.CTkButton(cartao, text="\ue74d" if excluir else "\ue711", font=('Segoe MDL2 Assets', 16),
        width=LARGURA_ICONE_CARTAO, **BOTAO_CARTAO,
        command=lambda: excluir(perfil) if excluir else browserman.fechar(estado))
    botao_excluir.grid(row=2,column=4,padx=(1,4),pady=4)
    cartao._idleboard_excluir = botao_excluir
    cartao._idleboard_web_host = host
    cartao._idleboard_abrir_web = abrir
    cartao._idleboard_atualizar_jogo = atualizar_jogo
