"""Preferências iniciais; salvar não interrompe navegadores em execução."""

import tkinter as tk
import customtkinter as ctk
from versao import VERSAO


def mostrar(pai, preferencias, salvar):
    ctk.CTkLabel(pai, text='Configurações', font=('Segoe UI', 26, 'bold')).pack(anchor='w')
    ctk.CTkLabel(pai, text='Padrões para a próxima abertura e para novos perfis.',
                text_color='#bcb5b2').pack(anchor='w', pady=(5, 20))
    formulario = ctk.CTkFrame(pai, fg_color='#1d1d20')
    formulario.pack(fill='x')
    formulario.grid_columnconfigure(1, weight=1)
    cores = dict(fg_color='#29272a', button_color='#393337', dropdown_fg_color='#1d1d20')
    for linha, texto in enumerate(('Grade inicial', 'Visualização de novos perfis')):
        ctk.CTkLabel(formulario, text=texto).grid(row=linha, column=0, padx=16, pady=12, sticky='w')
    grade = ctk.CTkOptionMenu(formulario, values=['Amplo', 'Confortável', 'Compacto'], **cores)
    grade.set(preferencias['layout_padrao'])
    grade.grid(row=0, column=1, sticky='ew', padx=16, pady=12)
    opcoes = {'Página inteira ajustada': 'encaixar', 'Tamanho natural (leve)': 'responsiva'}
    visualizacao = ctk.CTkOptionMenu(formulario, values=list(opcoes), **cores)
    visualizacao.set(next(nome for nome, valor in opcoes.items() if valor == preferencias['visualizacao_padrao']))
    visualizacao.grid(row=1, column=1, sticky='ew', padx=16, pady=12)
    maximizar = tk.BooleanVar(pai, preferencias['maximizar_ao_abrir'])
    ctk.CTkCheckBox(formulario, text='Abrir a janela maximizada', variable=maximizar, fg_color='#b94722').grid(
        row=2, column=0, columnspan=2, sticky='w', padx=16, pady=15)
    status = ctk.CTkLabel(pai, text='', text_color='#bcb5b2')
    status.pack(anchor='w', pady=8)

    def gravar():
        dados = {'layout_padrao': grade.get(), 'visualizacao_padrao': opcoes[visualizacao.get()],
                 'maximizar_ao_abrir': maximizar.get()}
        if dados == preferencias:
            return True
        if not salvar(dados):
            return False
        status.configure(text='Preferências salvas.')
        return True

    ctk.CTkButton(pai, text='Salvar preferências', fg_color='#b94722', command=gravar).pack(anchor='w')
    pai._idleboard_salvar_edicoes = gravar
    ctk.CTkLabel(pai, text=f'Idleboard Manager · {VERSAO}', text_color='#bcb5b2').pack(anchor='w', pady=20)
