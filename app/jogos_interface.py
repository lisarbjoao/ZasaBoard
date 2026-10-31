"""Formulário de jogos e URLs; persistência e navegação ficam no controlador."""

import customtkinter as ctk


def mostrar(conteudo, jogos, perfis, adicionar, editar, excluir, selecionar):
    ctk.CTkLabel(conteudo, text='Jogos e URLs', font=('Segoe UI', 26, 'bold')).pack(anchor='w')
    ctk.CTkLabel(conteudo, text='Cadastre o endereço de cada jogo. Cada um mantém seus próprios perfis e extensões.',
                text_color='#a8adc2', wraplength=680, justify='left').pack(anchor='w', pady=(6, 12))
    formulario = ctk.CTkFrame(conteudo, fg_color='#191d2b')
    formulario.pack(fill='x', pady=(0, 12))
    formulario.grid_columnconfigure(1, weight=1)
    nome = ctk.CTkEntry(formulario, placeholder_text='Nome do jogo', width=170)
    nome.grid(row=0, column=0, padx=10, pady=12)
    url = ctk.CTkEntry(formulario, placeholder_text='https://endereco-do-jogo')
    url.grid(row=0, column=1, sticky='ew', padx=(0, 10), pady=12)

    def criar():
        adicionar(nome.get(), url.get())

    ctk.CTkButton(formulario, text='+ Jogo', width=85, fg_color='#7965ed',
                  command=criar).grid(row=0, column=2, padx=(0, 10), pady=12)
    url.bind('<Return>', lambda _evento: criar())
    lista = ctk.CTkScrollableFrame(conteudo, fg_color='transparent')
    lista.pack(fill='both', expand=True)
    edicoes = []
    conteudo._idleboard_salvar_edicoes = lambda: all(acao() for acao in edicoes)
    for identificador, jogo in jogos.items():
        linha = ctk.CTkFrame(lista, fg_color='#191d2b')
        linha.pack(fill='x', pady=5)
        linha.grid_columnconfigure(1, weight=1)
        titulo = ctk.CTkEntry(linha, width=170)
        titulo.insert(0, jogo['nome'])
        titulo.grid(row=0, column=0, padx=10, pady=(12, 6))
        endereco = ctk.CTkEntry(linha)
        endereco.insert(0, jogo['url'])
        endereco.grid(row=0, column=1, sticky='ew', padx=(0, 10), pady=(12, 6))
        status = ctk.CTkLabel(linha, text=f"{len(perfis.get(identificador, []))} perfis · URL aplicada na próxima abertura da sessão",
                              text_color='#a8adc2', wraplength=520)
        status.grid(row=1, column=0, columnspan=2, sticky='w', padx=10, pady=(0, 10))

        def salvar(jogo_id=identificador, campo_nome=titulo, campo_url=endereco, aviso=status):
            if not campo_nome.winfo_exists() or jogo_id not in jogos:
                return True
            if (campo_nome.get().strip(), campo_url.get().strip()) == (jogos[jogo_id]['nome'], jogos[jogo_id]['url']):
                return True
            if editar(jogo_id, campo_nome.get(), campo_url.get()):
                campo_nome.delete(0, 'end'); campo_nome.insert(0, jogos[jogo_id]['nome'])
                campo_url.delete(0, 'end'); campo_url.insert(0, jogos[jogo_id]['url'])
                aviso.configure(text='Alterações salvas · URL aplicada na próxima abertura da sessão')
                return True
            return False

        edicoes.append(salvar)
        endereco.bind('<Return>', lambda _evento, acao=salvar: acao())
        ctk.CTkButton(linha, text='Salvar', width=80, fg_color='#30354b', command=salvar).grid(
            row=0, column=2, padx=(0, 10), pady=(12, 6))
        ctk.CTkButton(linha, text='Selecionar', width=90, fg_color='#30354b',
                      command=lambda chave=identificador: selecionar(chave)).grid(
                          row=2, column=0, sticky='w', padx=10, pady=(0, 12))
        ctk.CTkButton(linha, text='Excluir jogo', width=90, fg_color='#542d3d',
                      command=lambda chave=identificador: excluir(chave)).grid(
                          row=2, column=2, padx=(0, 10), pady=(0, 12))
