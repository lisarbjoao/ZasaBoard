"""Apresentação do catálogo contextual, sem execução de módulos pendentes."""

import customtkinter as ctk
from tkinter import messagebox
from core.extensoes import listar


def mostrar(conteudo, jogo_id, nome_jogo):
    ctk.CTkLabel(conteudo, text=f'Extensões · {nome_jogo}',
                font=('Segoe UI', 26, 'bold')).pack(anchor='w')
    ctk.CTkLabel(conteudo, text='Ferramentas específicas do jogo selecionado.',
                text_color='#bcb5b2').pack(anchor='w', pady=(6, 12))
    modulos = listar(jogo_id)
    if not modulos:
        ctk.CTkLabel(conteudo, text='Nenhuma extensão configurada para este jogo.',
                    text_color='#bcb5b2').pack(anchor='w', pady=18)
        return
    lista = ctk.CTkScrollableFrame(conteudo, fg_color='transparent', corner_radius=0)
    lista.pack(fill='both', expand=True)
    for modulo in modulos:
        cartao = ctk.CTkFrame(lista, fg_color='#1d1d20')
        cartao.pack(fill='x', pady=(0, 10))
        ctk.CTkLabel(cartao, text=modulo.nome, font=('Segoe UI', 18, 'bold')).pack(
            anchor='w', padx=16, pady=(14, 4))
        estado = 'Disponível' if modulo.disponivel else 'Em preparação · execução indisponível'
        ctk.CTkLabel(cartao, text=estado, text_color='#bcb5b2').pack(anchor='w', padx=16)
        descricao = ctk.CTkLabel(cartao, text=modulo.descricao, justify='left', anchor='w')
        descricao.pack(fill='x', padx=16, pady=(10, 8))
        textos = [descricao]
        if modulo.id=='ficha-sintetica':
            from core import laboratorio
            try:
                configurado=laboratorio.carregar() is not None
            except (OSError,ValueError):
                configurado=False
            def abrir_ficha():
                try:
                    laboratorio.abrir()
                except (OSError,ValueError) as erro:
                    messagebox.showerror('Ficha sintética',str(erro),parent=conteudo.winfo_toplevel())
            ctk.CTkButton(cartao,text='Abrir laboratório' if configurado else 'Configuração local necessária',
                state='normal' if configurado else 'disabled',fg_color='#b94722',command=abrir_ficha).pack(
                    anchor='w',padx=16,pady=(0,14))
        if modulo.pendencias:
            pendencias = ctk.CTkLabel(cartao, text='Para disponibilizar:\n' + '\n'.join(
                f'• {item}' for item in modulo.pendencias), justify='left', anchor='w', text_color='#bcb5b2')
            pendencias.pack(fill='x', padx=16, pady=(0, 14))
            textos.append(pendencias)
        def ajustar_textos(evento, rotulos=textos, quadro=cartao):
            largura = max(120, evento.width / quadro._get_widget_scaling() - 36)
            for rotulo in rotulos:
                rotulo.configure(wraplength=largura)
        cartao.bind('<Configure>', ajustar_textos, add='+')
