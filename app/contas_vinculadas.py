"""Contas de serviços associadas a um perfil; login fica no navegador isolado."""

import tkinter as tk
import re
from urllib.parse import urlsplit
from tkinter import messagebox
import customtkinter as ctk
from core import browserman, perfis as cadastro
from core import sessoes_vinculadas
from layout import titulo_personagem
from core.vinculos_stream import conta_sessao,eh_multitwitch
from aparencia import BOTAO_CARTAO, LARGURA_ICONE_CARTAO, JanelaAuxiliar

SERVICOS = {'Twitch': ('twitch', 'https://www.twitch.tv/login'),
            'Kick': ('kick', 'https://kick.com/')}


def endereco_vinculo(vinculo):
    if 'url' in vinculo:
        return cadastro.normalizar_url(vinculo['url'])
    return next(url for servico, url in SERVICOS.values() if servico == vinculo['servico'])


def abrir_sessao(pai, perfil, vinculo):
    try:conta=conta_sessao(perfil,vinculo)
    except ValueError as erro:
        messagebox.showinfo('Conta Twitch',str(erro),parent=pai);return
    existente = vinculo.get('_janela')
    if existente is not None and existente.winfo_exists():
        existente.deiconify()
        existente.lift()
        return
    janela = JanelaAuxiliar(pai._root())
    janela.title(f"{vinculo['nome'] or vinculo['servico'].title()} · {titulo_personagem(perfil)}")
    janela.geometry('1000x720')
    janela.minsize(600, 450)
    janela.grid_columnconfigure(0, weight=1)
    janela.grid_rowconfigure(1, weight=1)
    pasta = cadastro.pasta_vinculo(perfil['_jogo_id'], perfil, conta)
    estado = browserman.criar_estado(pasta)
    vinculo.update(_janela=janela, _sessao=estado)
    estado['_fechar_card']=janela.destroy
    barra = ctk.CTkFrame(janela, fg_color='#1d1d20')
    barra.grid(row=0, column=0, sticky='ew')
    status = ctk.CTkLabel(barra, text='Abrindo sessão…')
    status.pack(side='left', padx=12, pady=6)
    ctk.CTkButton(barra, text='Recarregar', width=100, fg_color='#393337',
                  command=lambda: browserman.recarregar(estado)).pack(side='right', padx=8)
    host = tk.Frame(janela, bg='#252529')
    host.grid(row=1, column=0, sticky='nsew')
    url = endereco_vinculo(vinculo)
    def abrir_chats():
        from chats_interface import abrir
        canais=[c for c in urlsplit(url).path.strip('/').lower().split('/') if re.fullmatch('[a-z0-9_]{1,64}',c)]
        if not canais:
            messagebox.showinfo('Canais Twitch','Adicione os nomes dos canais na URL do Multitwitch.',parent=janela);return
        return abrir(janela,perfil,conta,canais)
    if eh_multitwitch(vinculo):
        ctk.CTkButton(barra,text='Chats Twitch',width=110,command=abrir_chats).pack(side='right',padx=8)
        janela._abrir_chats_stream=abrir_chats
    rodape = ctk.CTkFrame(janela, fg_color='#1d1d20')
    rodape.grid(row=2, column=0, sticky='ew')
    ctk.CTkLabel(rodape, text='✓ salva a confirmação e fecha esta página. Para assistir, use Lives e mantenha os players/chats abertos.',
                 wraplength=760,justify='left').pack(
        side='left', padx=12, pady=8)

    def confirmar():
        if estado['web'] is None or not estado['web'].ready:
            return
        anterior = vinculo.get('confirmado', False)
        vinculo['confirmado'] = True
        if not perfil['_salvar']():
            vinculo['confirmado'] = anterior
            return
        painel = perfil.get('_painel_vinculos')
        if painel is not None and painel.winfo_exists():
            painel._idleboard_atualizar()
        fechar_janela()

    check = ctk.CTkButton(rodape, text='\ue73e', font=('Segoe MDL2 Assets', 16),
        width=LARGURA_ICONE_CARTAO, **BOTAO_CARTAO, state='disabled', command=confirmar)
    check.pack(side='right', padx=12, pady=6)
    janela._idleboard_confirmar_login = check

    def atualizar_status(texto):
        if status.winfo_exists():
            status.configure(text=texto)
            check.configure(state='normal' if estado['web'] is not None and estado['web'].ready else 'disabled')
    estado['notificar'] = atualizar_status

    abertura = {'tarefa': None}
    def iniciar():
        abertura['tarefa'] = None
        compartilhada = sessoes_vinculadas.ativa(conta)
        sessoes_vinculadas.registrar(conta,estado)
        if compartilhada is not None:
            browserman.abrir(estado, host, url, compartilhar=compartilhada)
        else:
            browserman.abrir(estado, host, url)

    def finalizar(evento):
        if evento.widget is not janela:
            return
        if abertura['tarefa'] is not None:
            janela.after_cancel(abertura['tarefa'])
        browserman.fechar(estado, avisar=False)
        sessoes_vinculadas.remover(conta,estado)
        if vinculo.get('_janela') is janela:
            vinculo.pop('_janela', None)
            vinculo.pop('_sessao', None)

    janela.bind('<Destroy>', finalizar, add='+')
    def fechar_janela():
        jogo=perfil.get('_sessao_teste',{})
        if eh_multitwitch(vinculo) and jogo.get('web') is not None:janela.withdraw()
        else:janela.destroy()
    janela.protocol('WM_DELETE_WINDOW', fechar_janela)
    abertura['tarefa'] = janela.after_idle(iniciar)


def fechar_perfil(perfil):
    for vinculo in perfil.get('vinculos', []):
        sessoes_vinculadas.fechar_reprodutores(vinculo)
        estado = vinculo.pop('_sessao', None)
        if estado is not None:
            browserman.fechar(estado, avisar=False)
        janela = vinculo.pop('_janela', None)
        if janela is not None and janela.winfo_exists():
            janela.destroy()
    painel = perfil.pop('_painel_vinculos', None)
    if painel is not None and painel.winfo_exists():
        painel.destroy()


def gerenciar(pai, perfil):
    existente = perfil.get('_painel_vinculos')
    if existente is not None and existente.winfo_exists():
        existente.lift()
        return
    painel = JanelaAuxiliar(pai.winfo_toplevel())
    perfil['_painel_vinculos'] = painel
    painel.title(f'Contas vinculadas · {titulo_personagem(perfil)}')
    painel.geometry('640x480')
    ctk.CTkLabel(painel, text=f'Contas de {titulo_personagem(perfil)}',
                font=('Segoe UI', 20, 'bold')).pack(anchor='w', padx=16, pady=(16, 8))
    ctk.CTkLabel(painel, text='Cada vínculo mantém seu próprio login neste computador.\n'
                'Cole a URL da plataforma e faça login na janela que abrir.',
                justify='left', text_color='#bcb5b2').pack(anchor='w', padx=16)
    formulario = ctk.CTkFrame(painel, fg_color='transparent')
    formulario.pack(fill='x', padx=16, pady=12)
    url_entrada = ctk.CTkEntry(formulario, placeholder_text='https://plataforma.com', width=420)
    url_entrada.pack(side='left', padx=(0, 8), fill='x', expand=True)
    lista = ctk.CTkScrollableFrame(painel, fg_color='transparent')
    lista.pack(fill='both', expand=True, padx=12, pady=(0, 12))

    def atualizar():
        for filho in lista.winfo_children():
            filho.destroy()
        for vinculo in perfil['vinculos']:
            linha = ctk.CTkFrame(lista, fg_color='#1d1d20')
            linha.pack(fill='x', pady=4)
            situacao = 'Confirmado por você' if vinculo.get('confirmado') else 'Aguardando confirmação'
            ctk.CTkLabel(linha, text=f"{vinculo['nome'] or vinculo['servico'].title()}\n{situacao}",
                        wraplength=210, justify='left').pack(side='left', padx=12, pady=10)
            ctk.CTkButton(linha, text='Desvincular', width=90, fg_color='#542d3d',
                          command=lambda v=vinculo: remover(v)).pack(side='right', padx=8)
            ctk.CTkButton(linha, text='Abrir sessão', width=100, fg_color='#393337',
                          command=lambda v=vinculo: abrir_sessao(painel, perfil, v)).pack(side='right', padx=8)

    def remover(vinculo):
        if not messagebox.askyesno('Desvincular conta',
            'Remover este vínculo, suas lives cadastradas e fechar suas janelas?\n'
            'Os dados de login continuarão no computador.', parent=painel):
            return
        indice = next(i for i, v in enumerate(perfil['vinculos']) if v is vinculo)
        lives_anteriores = perfil.get('lives', [])
        perfil['lives'] = [live for live in lives_anteriores if live['vinculo_id'] != vinculo['id']]
        perfil['vinculos'].pop(indice)
        if not perfil['_salvar']():
            perfil['vinculos'].insert(indice, vinculo)
            perfil['lives'] = lives_anteriores
            return
        sessoes_vinculadas.fechar_reprodutores(vinculo)
        estado = vinculo.pop('_sessao', None)
        if estado is not None:
            browserman.fechar(estado, avisar=False)
        janela = vinculo.pop('_janela', None)
        if janela is not None and janela.winfo_exists():
            janela.destroy()
        atualizar()

    def adicionar():
        try:
            vinculo = cadastro.novo_vinculo_url(url_entrada.get())
            perfil['vinculos'].append(vinculo)
            if not perfil['_salvar']():
                perfil['vinculos'].pop()
                return
            url_entrada.delete(0, 'end')
            atualizar()
            abrir_sessao(painel, perfil, vinculo)
        except ValueError as erro:
            messagebox.showerror('Conta vinculada', str(erro), parent=painel)

    ctk.CTkButton(formulario, text='Adicionar', width=90, fg_color='#b94722',
                  command=adicionar).pack(side='left')
    url_entrada.bind('<Return>', lambda _evento: adicionar())
    painel._idleboard_atualizar = atualizar
    atualizar()


def manter_multitwitch(pai,perfil):
    """Abre as páginas cadastradas; ocultar cartão não encerra estas janelas."""
    for v in perfil.get('vinculos',[]):
        if not eh_multitwitch(v):continue
        if v.get('_janela') is None:abrir_sessao(pai,perfil,v)
        janela=v.get('_janela')
        if janela is not None and hasattr(janela,'_abrir_chats_stream'):
            chats=janela._abrir_chats_stream()
            if chats is not None:chats.iconify()

def encerrar_multitwitch(perfil):
    for v in perfil.get('vinculos',[]):
        if not eh_multitwitch(v):continue
        janela=v.get('_janela')
        if janela is not None and janela.winfo_exists():janela.destroy()

    for conta in perfil.get('vinculos',[]):
        chats=conta.get('_janela_chats')
        if chats is not None and chats.winfo_exists():chats.destroy()
