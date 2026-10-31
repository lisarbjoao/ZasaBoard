"""Cadastro pequeno e explícito: criar, renomear e localizar os cartões."""

import customtkinter as ctk
from tkinter import messagebox
from core import perfis as cadastro
from layout import titulo_personagem
from aparencia import JanelaAuxiliar


def confirmar_exclusao(pai, perfil):
    """None cancela; False preserva dados; True autoriza apagar a pasta local."""
    dialogo = JanelaAuxiliar(pai)
    dialogo.title('Excluir perfil')
    dialogo.geometry('520x280')
    dialogo.resizable(False, False)
    dialogo.transient(pai)
    resultado = {'apagar': None}
    apagar = ctk.BooleanVar(dialogo, False)
    ctk.CTkLabel(dialogo, text=f'Excluir {titulo_personagem(perfil)}?',
                font=('Segoe UI', 18, 'bold'), wraplength=440).pack(padx=20, pady=(20, 8))
    ctk.CTkLabel(dialogo, text='O cartão e suas sessões serão fechados.',
                text_color='#bcb5b2').pack(pady=(0, 12))
    ctk.CTkCheckBox(dialogo, text='Apagar também os dados salvos deste perfil',
                    variable=apagar).pack(anchor='w', padx=22)
    ctk.CTkLabel(dialogo, text='Inclui logins, cookies e cache do jogo e das contas vinculadas.\n'
                'Marcando esta opção, os dados locais serão apagados permanentemente.',
                text_color='#bcb5b2', justify='left', wraplength=440).pack(anchor='w', padx=22, pady=8)
    botoes = ctk.CTkFrame(dialogo, fg_color='transparent')
    botoes.pack(pady=(0, 12))

    def confirmar():
        resultado['apagar'] = apagar.get()
        dialogo.destroy()

    ctk.CTkButton(botoes, text='Cancelar', width=120, fg_color='#393337',
                  command=dialogo.destroy).pack(side='left', padx=6)
    ctk.CTkButton(botoes, text='Excluir perfil', width=140, fg_color='#71394d',
                  command=confirmar).pack(side='left', padx=6)
    dialogo.grab_set()
    pai.wait_window(dialogo)
    return resultado['apagar']


def renomear(perfil, nome):
    nome = cadastro.nome_valido(nome)
    anterior = perfil['personagem']
    perfil['personagem'] = nome
    if not perfil['_salvar']():
        perfil['personagem'] = anterior
        return False
    return True


def editar_nome(pai, perfil):
    root = pai.winfo_toplevel()
    dialogo = JanelaAuxiliar(root)
    dialogo.title('Renomear cartão')
    dialogo.geometry('420x180')
    dialogo.resizable(False, False)
    dialogo.transient(root)
    ctk.CTkLabel(dialogo, text='Nome do personagem (até 80 caracteres):').pack(padx=20, pady=(18, 10))
    entrada = ctk.CTkEntry(dialogo, width=370)
    entrada.insert(0, perfil['personagem'])
    entrada.pack(padx=20, pady=(0, 14))
    entrada.select_range(0, 'end')

    def salvar():
        try:
            if renomear(perfil, entrada.get()):
                dialogo.destroy()
        except ValueError as erro:
            messagebox.showerror('Nome inválido', str(erro), parent=dialogo)

    botoes = ctk.CTkFrame(dialogo, fg_color='transparent')
    botoes.pack()
    ctk.CTkButton(botoes, text='Cancelar', width=130, fg_color='#393337',
                  command=dialogo.destroy).pack(side='left', padx=6)
    ctk.CTkButton(botoes, text='Salvar', width=130, fg_color='#b94722',
                  command=salvar).pack(side='left', padx=6)
    entrada.bind('<Return>', lambda _evento: salvar())
    dialogo.after(100, entrada.focus_set)
    dialogo.grab_set()
    root.wait_window(dialogo)


def mostrar(conteudo, registros, adicionar, abrir, excluir=None):
    ctk.CTkLabel(conteudo, text='Perfis', font=('Segoe UI', 26, 'bold')).pack(anchor='w')
    ctk.CTkLabel(conteudo, text='Nomes e cartões são salvos neste computador. Cada conta tem sua própria sessão.',
                text_color='#bcb5b2', wraplength=650, justify='left').pack(anchor='w', pady=(6, 12))
    ctk.CTkButton(conteudo, text='+ Perfil', fg_color='#b94722',
                  command=adicionar).pack(anchor='w', pady=(0, 12))
    lista = ctk.CTkScrollableFrame(conteudo, fg_color='transparent')
    lista.pack(fill='both', expand=True)
    edicoes = []
    conteudo._idleboard_salvar_edicoes = lambda: all(salvar() for salvar in edicoes)
    for indice, perfil in enumerate(registros, 1):
        linha = ctk.CTkFrame(lista, fg_color='#1d1d20')
        linha.pack(fill='x', pady=4)
        linha.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(linha, text=f'Cartão {indice} · ' + ('visível' if perfil['visivel'] else 'oculto'),
                    text_color='#bcb5b2').grid(row=0, column=0, sticky='w', padx=12, pady=(8, 0))
        entrada = ctk.CTkEntry(linha, placeholder_text=titulo_personagem(perfil))
        entrada.insert(0, perfil['personagem'])
        entrada.grid(row=1, column=0, sticky='ew', padx=12, pady=(0, 12))

        aviso = ctk.CTkLabel(linha, text='', text_color='#bcb5b2')
        aviso.grid(row=2, column=0, sticky='w', padx=12)
        controle = {'salvando': False}
        def salvar(p=perfil, campo=entrada, status=aviso, guard=controle):
            if not campo.winfo_exists():
                return True
            if guard['salvando']:
                return False
            guard['salvando'] = True
            try:
                if campo.get().strip() == p['personagem']:
                    return True
                if renomear(p, campo.get()):
                    campo.delete(0, 'end')
                    campo.insert(0, p['personagem'])
                    status.configure(text='Nome salvo')
                    return True
            except ValueError as erro:
                messagebox.showerror('Nome inválido', str(erro), parent=conteudo.winfo_toplevel())
            finally:
                guard['salvando'] = False
            return False

        edicoes.append(salvar)
        entrada.bind('<Return>', lambda _evento, acao=salvar: acao())
        entrada.bind('<FocusOut>', lambda _evento, acao=salvar: acao())
        ctk.CTkButton(linha, text='Salvar nome', width=100, fg_color='#393337', command=salvar).grid(
            row=1, column=1, padx=(0, 8), pady=(0, 12))
        ctk.CTkButton(linha, text='Abrir cartão', width=100, fg_color='#393337',
                      command=lambda p=perfil: abrir(p)).grid(row=1, column=2, padx=(0, 12), pady=(0, 12))
        from contas_vinculadas import gerenciar
        ctk.CTkButton(linha, text='Contas vinculadas', width=130, fg_color='#393337',
                      command=lambda p=perfil: gerenciar(conteudo, p)).grid(
                          row=3, column=0, sticky='w', padx=12, pady=(0, 10))
        if excluir is not None:
            ctk.CTkButton(linha, text='Excluir perfil', width=100, fg_color='#542d3d',
                          command=lambda p=perfil: excluir(p)).grid(
                              row=3, column=2, padx=(0, 12), pady=(0, 10))
