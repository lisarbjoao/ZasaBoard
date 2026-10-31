"""Controles de navegador para cada perfil isolado."""

import tkinter as tk
import customtkinter as ctk
from core import browserman
from core.perfis import PASTA
from aparencia import BOTAO_CARTAO, LARGURA_ICONE_CARTAO


def instalar(cartao, corpo, mensagem, rodape, perfil):
    pasta = PASTA / perfil.get('_jogo_id', 'pokeidle') / perfil['id'] if 'id' in perfil else browserman.PASTA_PROVA
    estado = perfil.setdefault("_sessao_teste", browserman.criar_estado(pasta))
    host = tk.Frame(corpo, bg="#22283b")
    abrir = ctk.CTkButton(corpo, text=f"Abrir {perfil.get('_nome_jogo', 'PokeIdle')}", width=150, fg_color="#7965ed")
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
        abrir.configure(state="disabled")
        abrir.pack_forget()
        mensagem.pack_forget()
        host.pack(fill="both", expand=True, padx=0, pady=0)
        if perfil.get('_url_jogo'):
            browserman.abrir(estado, host, perfil['_url_jogo'])
        else:
            browserman.abrir(estado, host)

    def atualizar_jogo():
        nome = perfil.get('_nome_jogo', 'PokeIdle')
        abrir.configure(text=f'Abrir {nome}')
        mensagem.configure(text=f'{nome}\nSessão independente')

    abrir.configure(command=iniciar)
    excluir = perfil.get('_excluir')
    botao_excluir = ctk.CTkButton(cartao, text="\ue74d" if excluir else "\ue711", font=('Segoe MDL2 Assets', 16),
        width=LARGURA_ICONE_CARTAO, **BOTAO_CARTAO,
        command=lambda: excluir(perfil) if excluir else browserman.fechar(estado))
    botao_excluir.grid(row=2,column=3,padx=(1,4),pady=4)
    cartao._idleboard_excluir = botao_excluir
    cartao._idleboard_web_host = host
    cartao._idleboard_abrir_web = abrir
    cartao._idleboard_atualizar_jogo = atualizar_jogo
