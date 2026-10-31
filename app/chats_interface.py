"""Chats reais da Twitch em páginas próprias da mesma conta vinculada."""
import re
import tkinter as tk
import customtkinter as ctk
from aparencia import JanelaAuxiliar
from core import browserman,perfis,sessoes_vinculadas


def endereco_chat(canal):
    if not isinstance(canal,str) or not re.fullmatch('[a-z0-9_]{1,64}',canal):
        raise ValueError('Canal Twitch inválido.')
    return 'https://www.twitch.tv/popout/'+canal+'/chat?popout='


def abrir(pai,perfil,vinculo,canais):
    canais=list(dict.fromkeys(canais))
    urls=[endereco_chat(c) for c in canais]
    if not urls:raise ValueError('Adicione um canal Twitch antes de abrir os chats.')
    existente=vinculo.get('_janela_chats')
    if existente is not None and existente.winfo_exists():
        existente.deiconify();existente.lift();return existente
    janela=JanelaAuxiliar(pai._root())
    janela.title('Chats Twitch · '+(vinculo.get('nome') or 'Conta vinculada'))
    janela.geometry('1000x700');janela.minsize(760,500)
    vinculo['_janela_chats']=janela
    ctk.CTkLabel(janela,text='Confira o login em cada chat. Fechar esta janela encerra os chats; minimizar mantém as páginas abertas.',
                 wraplength=900,justify='left').pack(fill='x',padx=14,pady=(12,4))
    ctk.CTkLabel(janela,text='Usa a mesma conta do Multitwitch. Não envia mensagens automaticamente nem comprova bônus no jogo.',
                 text_color='#bcb5b2',wraplength=900,justify='left').pack(fill='x',padx=14,pady=(0,8))
    area=ctk.CTkScrollableFrame(janela,fg_color='transparent')
    area.pack(fill='both',expand=True,padx=10,pady=6)
    area.grid_columnconfigure((0,1),weight=1)
    estados=[];tarefas=[]
    janela._idleboard_chats_estados=estados
    pasta=perfis.pasta_vinculo(perfil['_jogo_id'],perfil,vinculo)
    def fechar():
        if janela.winfo_exists():janela.destroy()
    for indice,(canal,url) in enumerate(zip(canais,urls)):
        painel=ctk.CTkFrame(area,height=470)
        painel.grid(row=indice//2,column=indice%2,sticky='nsew',padx=4,pady=4)
        painel.grid_propagate(False);painel.grid_columnconfigure(0,weight=1);painel.grid_rowconfigure(1,weight=1)
        ctk.CTkLabel(painel,text=canal,font=('Segoe UI',15,'bold')).grid(row=0,column=0,padx=8,pady=4)
        host=tk.Frame(painel,bg='#252529');host.grid(row=1,column=0,sticky='nsew')
        status=ctk.CTkLabel(painel,text='Abrindo chat real…',text_color='#bcb5b2')
        status.grid(row=2,column=0,sticky='ew',padx=6,pady=3)
        estado=browserman.criar_estado(pasta)
        estado.update(visualizacao='responsiva',_fechar_card=fechar,
            notificar=lambda texto,rotulo=status:rotulo.configure(text=texto) if rotulo.winfo_exists() else None)
        estados.append(estado)
        def iniciar(s=estado,h=host,u=url):
            compartilhada=sessoes_vinculadas.ativa(vinculo)
            sessoes_vinculadas.registrar(vinculo,s)
            browserman.abrir(s,h,u,compartilhar=compartilhada)
        tarefas.append(janela.after_idle(iniciar))
    def finalizar(evento):
        if evento.widget is not janela:return
        for tarefa in tarefas:
            try:janela.after_cancel(tarefa)
            except tk.TclError:pass
        for s in estados:
            browserman.fechar(s,avisar=False);sessoes_vinculadas.remover(vinculo,s)
        if vinculo.get('_janela_chats') is janela:vinculo.pop('_janela_chats',None)
    janela.bind('<Destroy>',finalizar,add='+')
    def ocultar_ou_fechar():
        if perfil.get('_sessao_teste',{}).get('web') is not None:janela.iconify()
        else:fechar()
    janela.protocol('WM_DELETE_WINDOW',ocultar_ou_fechar)
    barra=ctk.CTkFrame(janela,fg_color='transparent');barra.pack(fill='x',padx=14,pady=8)
    ctk.CTkButton(barra,text='Minimizar',width=110,command=janela.iconify).pack(side='left')
    ctk.CTkButton(barra,text='Ocultar / encerrar',width=130,fg_color='#393337',command=ocultar_ou_fechar).pack(side='right')
    return janela
