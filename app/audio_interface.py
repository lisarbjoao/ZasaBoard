"""Diálogo curto de som por cartão, com confirmação e reversão do preview."""

import tkinter as tk
import customtkinter as ctk
from aparencia import JanelaAuxiliar
from core import audio


def mostrar(pai, perfil, estado):
    existente = estado.get('_janela_audio')
    if existente is not None and existente.winfo_exists():
        existente.lift()
        return
    raiz = pai.winfo_toplevel()
    janela = JanelaAuxiliar(raiz)
    estado['_janela_audio'] = janela
    janela.title('Som do cartão')
    janela.geometry('340x210')
    janela.resizable(False, False)
    janela.transient(raiz)
    config = audio.validar(perfil.get('audio'))
    silenciado = tk.BooleanVar(janela, config['silenciado'])
    titulo = ctk.CTkLabel(janela, text=f"Volume: {config['volume']}%")
    titulo.pack(pady=(15, 5))

    def valor():
        return {'volume': round(slider.get()), 'silenciado': silenciado.get()}

    def preview(_valor=None):
        atual = valor()
        titulo.configure(text=f"Volume: {atual['volume']}%")
        audio.aplicar(estado, atual)

    slider = ctk.CTkSlider(janela, from_=0, to=100, number_of_steps=100, command=preview,
                          progress_color='#b94722', button_color='#b94722')
    slider.set(config['volume'])
    slider.pack(fill='x', padx=25, pady=10)
    ctk.CTkCheckBox(janela, text='Silenciar este cartão', variable=silenciado,
                    fg_color='#b94722', command=preview).pack(pady=8)

    def cancelar():
        audio.aplicar(estado, perfil.get('audio'))
        janela.destroy()

    def salvar():
        if audio.salvar(perfil, estado, valor()):
            janela.destroy()

    botoes = ctk.CTkFrame(janela, fg_color='transparent')
    botoes.pack(pady=10)
    ctk.CTkButton(botoes, text='Cancelar', width=100, fg_color='#29272a',
                  command=cancelar).pack(side='left', padx=5)
    ctk.CTkButton(botoes, text='Salvar', width=100, fg_color='#b94722',
                  command=salvar).pack(side='left', padx=5)
    janela.protocol('WM_DELETE_WINDOW', cancelar)
    janela.bind('<Escape>', lambda _: cancelar())
    janela.bind('<Return>', lambda _: salvar())
    janela._idleboard_slider = slider
    janela._idleboard_salvar = salvar
