"""Idleboard: protótipo visual com dados simulados e funções pequenas."""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from core import perfis as cadastro
from core import jogos as catalogo_jogos
from core import configuracoes
from core.ambiente import EDICAO_USO, EDICAO_CANDIDATA, adquirir_instancia
from versao import VERSAO
from aparencia import BOTAO_CARTAO, LARGURA_ICONE_CARTAO
from rolagem import instalar_barra_leve
from movimento import animar_largura, configurar_rolagem_suave, animar_grade
from layout import criar_perfil, titulo_personagem, calcular_layout, resolver_modo, numero_colunas

FUNDO = "#121212"
PAINEL = "#1d1d20"
DESTAQUE = "#b94722"
HOVER = "#393337"
CORES_SELETOR = dict(fg_color=PAINEL, button_color=PAINEL,
    button_hover_color=HOVER, dropdown_fg_color=PAINEL,
    dropdown_hover_color=HOVER, text_color="#DCE4EE")
FONTE_ICONES = ("Segoe MDL2 Assets", 16)
ICONES = {"foco": "\ue740", "grade": "\ue80a", "recolher": "\ue76b", "expandir": "\ue76c", "ocultar": "\ue921", "recarregar": "\ue72c"}
JOGOS = {"pokeidle": {"nome": "PokeIdle", "extensoes": ("/hunt",)}}


def obter_extensoes(jogo_id):
    """Um jogo sem configuração não herda ferramentas de outro jogo."""
    return JOGOS.get(jogo_id, {}).get("extensoes", ())


def criar_janela():
    ctk.set_appearance_mode("dark")
    janela = ctk.CTk(fg_color=FUNDO)
    janela.title(f'ZasaBoard · Candidata {VERSAO}' if EDICAO_CANDIDATA else
                 'ZasaBoard · Uso' if EDICAO_USO else 'ZasaBoard · Desenvolvimento')
    from marca import aplicar
    aplicar(janela,ctk)
    janela.geometry("1100x720")
    janela.minsize(860, 600)
    janela.grid_columnconfigure(1, weight=1)
    janela.grid_rowconfigure(0, weight=1)
    return janela


def criar_barra_lateral(janela, navegar):
    barra = ctk.CTkFrame(janela, width=190, corner_radius=0, fg_color=PAINEL)
    reserva = ctk.CTkFrame(janela, width=190, corner_radius=0, fg_color=PAINEL)
    reserva.grid(row=0, column=0, sticky="nsew")
    reserva.grid_propagate(False)
    barra.place(x=0, y=0, relheight=1)
    barra.grid_propagate(False)
    barra.grid_columnconfigure(0, weight=1)
    cabecalho = ctk.CTkFrame(barra, fg_color="transparent", height=42)
    cabecalho.grid(row=0, column=0, sticky="ew", padx=6, pady=(8, 12))
    cabecalho.grid_columnconfigure(0, weight=1)
    titulo = ctk.CTkLabel(cabecalho, text="ZasaBoard", font=("Segoe UI", 20, "bold"))
    titulo.grid(row=0, column=0, padx=(6, 0), sticky="w")
    itens = {"Início": "\ue80f", "Jogos e URLs": "\ue8b7", "Perfis": "\ue77b",
             "Lives": "\ue714", "Extensões": "\ue8a5", "Configurações": "\ue713"}
    barra.grid_rowconfigure(len(itens) + 1, weight=1)
    botoes, textos = {}, {}
    trilho = ctk.CTkFrame(reserva, width=54, corner_radius=0, fg_color=PAINEL)
    trilho.grid_columnconfigure(0, weight=1)
    recolhida = False

    def alternar():
        nonlocal recolhida
        recolhida = not recolhida
        barra.place(x=0,y=0,relheight=1)
        barra.lift()
        titulo.grid_remove()
        for texto in textos.values():
            texto.grid_remove()
        controle.configure(text=ICONES["expandir" if recolhida else "recolher"])

        def concluir():
            reserva.configure(width=54 if recolhida else 190)
            if recolhida:
                trilho.place(x=0,y=0,relheight=1)
                barra.place_forget()
            else:
                trilho.place_forget()
                barra.lift()
                titulo.grid()
                for texto in textos.values():
                    texto.grid()

        animar_largura(barra, 54 if recolhida else 190, concluir)

    controle = ctk.CTkButton(cabecalho, text=ICONES["recolher"], font=FONTE_ICONES,
                            width=30, height=32, fg_color="transparent", command=alternar)
    controle.grid(row=0, column=1, sticky="e")
    ctk.CTkButton(trilho, text=ICONES["expandir"], font=FONTE_ICONES,
        width=36,height=40,fg_color=PAINEL,command=alternar).grid(row=0,column=0,padx=6,pady=(8,12))
    for linha, (nome, icone) in enumerate(itens.items(), start=1):
        item = ctk.CTkFrame(barra, fg_color=PAINEL, corner_radius=6)
        item.grid(row=linha, column=0, padx=6, pady=3, sticky="ew")
        item.grid_columnconfigure(1, weight=1)
        acao = lambda destino=nome: navegar(destino)
        simbolo = ctk.CTkButton(item, text=icone, font=FONTE_ICONES, width=36, height=38,
                      fg_color=PAINEL, hover=False, corner_radius=0, command=acao)
        simbolo.grid(row=0, column=0)
        texto = ctk.CTkButton(item, text=nome, width=100, height=38, anchor="w",
                              fg_color=PAINEL, hover=False, corner_radius=0, command=acao)
        texto.grid(row=0, column=1, sticky="ew")
        textos[nome] = texto
        botoes[nome] = item
        icone_recolhido = ctk.CTkButton(trilho,text=icone,font=FONTE_ICONES,
            width=36,height=38,fg_color=PAINEL,command=acao)
        icone_recolhido.grid(row=linha,column=0,padx=6,pady=3)
        item._idleboard_icone_recolhido = icone_recolhido
        instalar_hover_lateral(item, (simbolo, texto))
    barra.lift()
    return botoes


def instalar_hover_lateral(item, partes):
    """Ícone e texto compartilham o mesmo estado de interação."""
    item._idleboard_cor_base = PAINEL

    def pintar(cor):
        item.configure(fg_color=cor)
        for parte in partes:
            parte.configure(fg_color=cor)

    def sair(_evento):
        # Cruzar do ícone para o texto não encerra o hover da linha.
        def conferir():
            if not item.winfo_exists():
                return
            x, y = item.winfo_pointerxy()
            dentro = (item.winfo_rootx() <= x < item.winfo_rootx() + item.winfo_width()
                      and item.winfo_rooty() <= y < item.winfo_rooty() + item.winfo_height())
            pintar(HOVER if dentro else item._idleboard_cor_base)
        item.after_idle(conferir)

    for parte in (item, *partes):
        parte.bind("<Enter>", lambda _evento: pintar(HOVER), add="+")
        parte.bind("<Leave>", sair, add="+")


def criar_cartao(area, nome, selecionar, em_foco=False, ocultar=None, perfil=None):
    """O mesmo componente serve para a grade e para o modo foco."""
    cartao = ctk.CTkFrame(area, fg_color=PAINEL, corner_radius=6)
    cartao._idleboard_perfil = perfil
    cartao.grid_propagate(False)
    cartao.grid_columnconfigure(0, weight=1)
    cartao.grid_rowconfigure(1, weight=1)
    titulo = ctk.CTkLabel(cartao, text=nome, width=1, anchor="w", font=("Segoe UI", 14, "bold"))
    titulo.grid(row=0, column=0, padx=10, pady=6, sticky="ew")
    # O título encolhe antes dos controles em cartões compactos.
    import tkinter.font as tkfont
    fonte = tkfont.Font(family="Segoe UI", size=-round(14 * titulo._get_widget_scaling()), weight="bold")
    ultimo_titulo = {"chave": None, "texto": None}
    def ajustar_titulo(_evento=None):
        # A largura calculada do cartão é estável mesmo com a aba oculta.
        com_audio = bool(perfil and perfil.get('prova_navegador'))
        controles = LARGURA_ICONE_CARTAO * ((3 if ocultar is not None else 2) + int(com_audio)) + 13
        limite = max(0, round((cartao.cget('width') - controles - 24) * titulo._get_widget_scaling()))
        visivel = bool(cartao.winfo_ismapped())
        chave = (nome, limite, visivel)
        if chave == ultimo_titulo['chave']:
            return
        ultimo_titulo['chave'] = chave
        if not visivel or limite <= 0 or fonte.measure(nome) <= limite:
            texto = nome
        else:
            inicio, fim = 0, len(nome)
            while inicio < fim:
                meio = (inicio + fim + 1) // 2
                if fonte.measure(nome[:meio] + "…") <= limite:
                    inicio = meio
                else:
                    fim = meio - 1
            texto = nome[:inicio] + "…"
        if texto != ultimo_titulo["texto"]:
            titulo.configure(text=texto)
            ultimo_titulo["texto"] = texto
    titulo.bind("<Configure>", ajustar_titulo, add="+")
    titulo.bind('<Map>', ajustar_titulo, add='+')
    def atualizar_nome():
        nonlocal nome
        novo_nome = titulo_personagem(perfil)
        nome = novo_nome
        ajustar_titulo()
    cartao._idleboard_atualizar_nome = atualizar_nome
    cartao._idleboard_titulo = titulo
    if perfil is not None and '_salvar' in perfil:
        from perfis_interface import editar_nome
        cartao._idleboard_editar_nome = lambda: editar_nome(cartao, perfil)
        titulo.bind('<Double-Button-1>', lambda _evento: cartao._idleboard_editar_nome(), add='+')
    if ocultar is not None:
        ctk.CTkButton(cartao, text=ICONES["ocultar"], font=FONTE_ICONES, width=LARGURA_ICONE_CARTAO,
            **BOTAO_CARTAO, command=ocultar).grid(row=0, column=1, padx=1, pady=4)
    from core.browserman import recarregar
    def atualizar_pagina():
        estado = (perfil or {}).get("_sessao_teste")
        if estado is not None:
            recarregar(estado)
    refresh = ctk.CTkButton(cartao, text=ICONES["recarregar"], font=FONTE_ICONES,
        width=LARGURA_ICONE_CARTAO, **BOTAO_CARTAO,
        state="normal" if perfil and perfil.get("prova_navegador") else "disabled",
        command=atualizar_pagina)
    refresh.grid(row=0, column=2, padx=1, pady=4)
    cartao._idleboard_recarregar = refresh
    botao_foco = ctk.CTkButton(
        cartao, text=ICONES["grade" if em_foco else "foco"], font=FONTE_ICONES,
        width=LARGURA_ICONE_CARTAO, **BOTAO_CARTAO, command=selecionar,
    )
    botao_foco.grid(row=0, column=3, padx=(1, 4), pady=4)
    cartao._idleboard_botao_foco = botao_foco
    previa = ctk.CTkFrame(cartao, fg_color="#252529", corner_radius=3)
    previa.grid(row=1, column=0, columnspan=5 if perfil and perfil.get('prova_navegador') else 4,
                padx=3, pady=(0, 3), sticky="nsew")
    nome_jogo = (perfil or {}).get('_nome_jogo', 'PokeIdle')
    mensagem = ctk.CTkLabel(
        previa, text=f"{nome_jogo}\nPrévia simulada",
        text_color="#d5ccc7", font=("Segoe UI", 15),
    )
    mensagem.pack(expand=True, padx=14, pady=20)
    rodape = ctk.CTkLabel(cartao, text="○ Desconectada", text_color="#bcb5b2")
    rodape.grid(row=2, column=0, columnspan=4, padx=10, pady=(0, 4), sticky="w")
    if perfil is not None and '_salvar' in perfil:
        from contas_vinculadas import gerenciar
        ctk.CTkButton(cartao, text='\ue8fa', font=FONTE_ICONES,
                      width=LARGURA_ICONE_CARTAO, **BOTAO_CARTAO,
                      command=lambda: gerenciar(cartao, perfil)).grid(
                          row=2, column=3 if perfil.get("prova_navegador") else 2, padx=1, pady=4)
    if perfil is not None and perfil.get("prova_navegador"):
        from prova_navegador import instalar
        mensagem.configure(text=f"{nome_jogo}\nSessão independente")
        rodape.configure(width=1,anchor="w")
        rodape.grid_configure(columnspan=2,sticky="ew")
        instalar(cartao, previa, mensagem, rodape, perfil)
    return cartao


def mostrar_inicio(conteudo, jogo_id, perfis, preferencias):
    preferencias.setdefault("modo_escolhido", preferencias["modo"])
    conteudo.grid_columnconfigure(0, weight=1)
    conteudo.grid_rowconfigure(1, weight=1)
    ferramentas = ctk.CTkFrame(conteudo, fg_color="transparent")
    ferramentas.grid(row=0, column=0, sticky="ew", pady=(0, 6))
    ferramentas.grid_columnconfigure(0, weight=1)
    resumo = ctk.CTkLabel(ferramentas, text="", text_color="#bcb5b2")
    resumo.grid(row=0, column=0, sticky="w")
    area = ctk.CTkFrame(conteudo, fg_color="transparent")
    area.grid(row=1, column=0, sticky="nsew")
    conteudo._idleboard_area = area
    from core.espelho import Controlador
    aviso=ctk.CTkLabel(ferramentas,text='',anchor='w',text_color='#bcb5b2',wraplength=650)
    def avisar_espelho(texto):
        if not conteudo.winfo_exists():return
        aviso.configure(text=texto)
        aviso.grid(row=1,column=0,columnspan=6,sticky='ew',pady=(3,0))
        alinhar.configure(fg_color=DESTAQUE if controle.alinhado else PAINEL)
        ativo=controle.ativo or controle.preparando
        espelhar.configure(text='Parar' if ativo else 'Espelhar',fg_color=DESTAQUE if ativo else PAINEL)
    controle=Controlador(conteudo,perfis,avisar_espelho)
    def alternar_espelho():
        if controle.ativo or controle.preparando:controle.parar()
        else:controle.ativar()
    espelhar=ctk.CTkButton(ferramentas,text='Espelhar',width=84,height=28,fg_color=PAINEL,command=alternar_espelho)
    alinhar=ctk.CTkButton(ferramentas,text='Alinhar',width=72,height=28,fg_color=PAINEL,command=controle.alinhar)
    alinhar.grid(row=0,column=3,padx=4)
    conteudo._idleboard_botao_alinhar=alinhar
    espelhar.grid(row=0,column=4,padx=4)
    conteudo._idleboard_espelho=controle
    conteudo._idleboard_botao_espelho=espelhar
    raiz=conteudo.winfo_toplevel()
    escape=raiz.bind('<Escape>',lambda _:controle.parar() if controle.ativo or controle.preparando or controle.alinhado else None,add='+')
    def sair_espelho(evento):
        if evento.widget is conteudo and (controle.ativo or controle.preparando or controle.alinhado):controle.parar('Espelhamento desligado ao sair da tela.')
    conteudo.bind('<Unmap>',sair_espelho,add='+')
    def destruir_espelho(evento):
        if evento.widget is conteudo:
            controle.parar();raiz.unbind('<Escape>',escape)
    conteudo.bind('<Destroy>',destruir_espelho,add='+')

    def atualizar():
        if controle.ativo or controle.preparando or controle.alinhado:controle.parar('Alinhamento pausado: disposição alterada.')
        for perfil in perfis:perfil['_espelho_controlador']=controle
        visiveis = sum(perfil["visivel"] for perfil in perfis)
        contexto = "prova de navegador" if any(p.get("prova_navegador") for p in perfis) else "simulação"
        resumo.configure(text=f"{visiveis}/{len(perfis)} visíveis · {contexto}")
        recuperar.configure(text=f"Ocultos ({len(perfis) - visiveis})",
                             state="normal" if visiveis < len(perfis) else "disabled")
        mostrar_grade(area, perfis, preferencias, atualizar, modo.set)

    def mudar_modo(modo):
        preferencias["modo_escolhido"] = modo
        preferencias["modo"] = modo
        atualizar()

    def adicionar():
        if '_adicionar' in preferencias:
            preferencias['_adicionar']()
            return
        dialogo = ctk.CTkInputDialog(text="Nome do personagem (pode preencher depois):", title="Adicionar conta")
        nome = dialogo.get_input()
        if nome is not None:
            try:
                perfil = cadastro.novo(nome)
                perfil.update(prova_navegador=True, _salvar=preferencias['_salvar'])
                perfis.append(perfil)
                if not preferencias['_salvar']():
                    perfis.pop()
                    return
                atualizar()
            except ValueError as erro:
                messagebox.showerror('Nome inválido', str(erro), parent=conteudo.winfo_toplevel())

    modo = ctk.CTkOptionMenu(
        ferramentas, values=["Amplo", "Confortável", "Compacto"],
        width=130, height=28, command=mudar_modo,
        **CORES_SELETOR,
    )
    modo.set(preferencias["modo"])
    modo.grid(row=0, column=1, padx=4)

    recuperar = ctk.CTkButton(ferramentas, text="Ocultos (0)", width=100, height=28,
        fg_color=PAINEL, command=lambda: abrir_ocultos(conteudo, perfis, atualizar))
    recuperar.grid(row=0, column=2, padx=4)
    ctk.CTkButton(ferramentas, text="+ Conta", width=82, height=28,
                  fg_color=DESTAQUE, command=adicionar).grid(row=0, column=5)
    atualizar()
    conteudo._idleboard_atualizar = atualizar


def ocultar_perfil(perfil, atualizar):
    """Somente a apresentação muda; o perfil e a futura sessão são preservados."""
    perfil["visivel"] = False
    if '_salvar' in perfil:
        perfil['_salvar']()
    atualizar()


def abrir_ocultos(pai, perfis, atualizar):
    painel = ctk.CTkToplevel(pai)
    painel.title("Cartões ocultos")
    painel.geometry("400x400")
    painel.transient(pai.winfo_toplevel())
    painel.grab_set()
    ctk.CTkLabel(painel, text="Ocultar não encerra a conta.", text_color="#bcb5b2").pack(pady=12)
    lista = ctk.CTkScrollableFrame(painel)
    lista.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def exibir(perfil, linha):
        perfil["visivel"] = True
        if '_salvar' in perfil:
            perfil['_salvar']()
        linha.destroy()
        atualizar()
        if all(p["visivel"] for p in perfis):
            painel.destroy()

    for perfil in perfis:
        if perfil["visivel"]:
            continue
        linha = ctk.CTkFrame(lista, fg_color=PAINEL)
        linha.pack(fill="x", pady=4)
        ctk.CTkLabel(linha, text=titulo_personagem(perfil), wraplength=200).pack(side="left", padx=8)
        ctk.CTkButton(linha, text="Exibir", width=65,
            command=lambda p=perfil, l=linha: exibir(p, l)).pack(side="right", padx=8, pady=8)
    return painel


def limpar_area(area):
    grade = getattr(area, "_idleboard_grade", None)
    if grade is not None:
        if grade.get("tarefa") is not None:
            area.after_cancel(grade["tarefa"])
        area._idleboard_grade = None
    for componente in area.winfo_children():
        componente.destroy()
    # Limpa também os pesos que o layout anterior deixou na grade.
    for indice in range(3):
        area.grid_rowconfigure(indice, weight=0, uniform="")
        area.grid_columnconfigure(indice, weight=0, uniform="")


def mostrar_grade(area, perfis, preferencias, atualizar=None, ao_mudar_modo=None):
    """Reutiliza cartões e limita o redesenho completo ao fim das transições."""
    existente = getattr(area, "_idleboard_grade", None)
    if existente is not None:
        existente["externo"] = atualizar
        existente["seletor"] = ao_mudar_modo
        existente["renderizar"](True)
        return
    limpar_area(area)
    area.grid_columnconfigure(0, weight=1)
    area.grid_rowconfigure(0, weight=1)
    rolagem = ctk.CTkScrollableFrame(area, fg_color="transparent", corner_radius=0)
    rolagem.grid(row=0, column=0, sticky="nsew")
    instalar_barra_leve(rolagem)
    espaco = tk.Frame(rolagem, width=1, height=1, bg=FUNDO)
    espaco.grid(row=0, column=0)
    vazio = ctk.CTkLabel(rolagem, text="Nenhum cartão visível. Use Ocultos para reexibir suas contas.")
    estado = {"tarefa": None, "cartoes": {}, "posicoes": {}, "externo": atualizar,
              "seletor": ao_mudar_modo, "tamanho": None, "modo": None, "novos": False, "foco": None}
    area._idleboard_grade = estado

    def atualizar_externo():
        if estado["externo"] is not None:
            estado["externo"]()
        else:
            renderizar(True)

    def renderizar(transicao=False):
        if estado["tarefa"] is not None:
            area.after_cancel(estado["tarefa"])
        estado["tarefa"] = None
        if not area.winfo_toplevel().winfo_viewable():
            return
        tamanho = (rolagem.winfo_width(), rolagem._parent_canvas.winfo_height())
        if min(tamanho) <= 10:
            return
        escala = rolagem._get_widget_scaling()
        largura, altura = (valor / escala for valor in tamanho)
        efetivo = resolver_modo(preferencias.get("modo_escolhido", preferencias["modo"]), perfis, largura, altura)
        preferencias["modo"] = efetivo
        if estado["seletor"] is not None:
            estado["seletor"](efetivo)
        historico = preferencias.setdefault("colunas_por_modo", {})
        colunas = numero_colunas(largura, efetivo, historico.get(efetivo))
        historico[efetivo] = colunas
        posicoes, altura_total = calcular_layout(largura, perfis, efetivo,
                                                 altura_disponivel=altura, colunas=colunas)
        anteriores = list(estado['cartoes'].values())
        identidades = tuple(id(p) for p in perfis)
        if estado.get('identidades') != identidades:
            foco_anterior = estado['cartoes'].get(estado['foco'])
            perfil_foco = getattr(foco_anterior, '_idleboard_perfil', None)
            atuais = {id(p): i for i, p in enumerate(perfis)}
            estado['cartoes'] = {atuais[id(c._idleboard_perfil)]: c for c in anteriores
                                 if id(c._idleboard_perfil) in atuais}
            for cartao in anteriores:
                if id(cartao._idleboard_perfil) not in atuais:
                    cartao.destroy()
            estado['foco'] = atuais.get(id(perfil_foco))
            estado['posicoes'] = {}
            estado['identidades'] = identidades
        foco = estado["foco"]
        if foco is not None and not perfis[foco]["visivel"]:
            estado["foco"] = foco = None
        if foco is not None:
            posicoes = [(foco,8,8,max(1,int(largura)-16),max(1,int(altura)-16))]
            altura_total = altura
        alvos = {i: (x,y,w,h) for i,x,y,w,h in posicoes}
        for indice, perfil in enumerate(perfis):
            if indice not in estado["cartoes"]:
                estado["novos"] = True
                estado["cartoes"][indice] = criar_cartao(rolagem, titulo_personagem(perfil),
                    lambda p=perfil: mostrar_foco(area,p,perfis,preferencias,atualizar_externo),
                    ocultar=lambda p=perfil: ocultar_perfil(p,atualizar_externo), perfil=perfil)
            cartao = estado["cartoes"][indice]
            cartao._idleboard_atualizar_nome()
            icone = ICONES["grade" if indice == foco else "foco"]
            if cartao._idleboard_botao_foco.cget("text") != icone:
                cartao._idleboard_botao_foco.configure(text=icone)
            if indice not in alvos:
                cartao.place_forget()
        if not alvos:
            vazio.configure(text='Nenhum perfil neste jogo. Use + Conta para criar o primeiro.' if not perfis
                            else 'Nenhum cartão visível. Use Ocultos para reexibir suas contas.')
            vazio.place(x=12,y=20)
        else:
            vazio.place_forget()
        espaco.configure(height=round(max(altura_total, altura) * escala))

        def aplicar():
            for indice, (x,y,w,h) in alvos.items():
                cartao = estado["cartoes"][indice]
                if (cartao.cget("width"), cartao.cget("height")) != (w,h):
                    # API interna da versão fixada do CTk: atualiza ambos numa passagem.
                    cartao._set_dimensions(width=w,height=h)
                if estado["posicoes"].get(indice) != (x,y,w,h) or not cartao.winfo_ismapped():
                    cartao.place(x=x,y=y)
                cartao._idleboard_atualizar_nome()
            estado["posicoes"] = alvos
            if estado["novos"]:
                configurar_rolagem_suave(rolagem)
                estado["novos"] = False

        if transicao and estado["posicoes"] and alvos:
            if transicao != "redimensionar":
                rolagem._parent_canvas.yview_moveto(0)
            animar_grade(rolagem,estado["cartoes"],estado["posicoes"],alvos,
                {i:titulo_personagem(perfis[i]) for i in alvos},aplicar,
                duracao=0.10 if transicao == "redimensionar" else 0.18)
        else:
            anterior = getattr(rolagem,"_idleboard_transicao",None)
            if anterior is not None:
                anterior["canvas"].destroy()
                rolagem._idleboard_transicao = None
            aplicar()
        estado["modo"] = efetivo
        estado["tamanho"] = tamanho

    def redimensionar(evento):
        tamanho = (rolagem.winfo_width(),rolagem._parent_canvas.winfo_height())
        if tamanho == estado["tamanho"]:
            return
        # Agrupar eventos sem reiniciar a espera a cada pixel do arraste.
        if estado["tarefa"] is None:
            estado["tarefa"] = area.after(24,lambda: renderizar("redimensionar"))

    estado["renderizar"] = renderizar
    rolagem.bind("<Configure>",redimensionar,add="+")
    rolagem._parent_canvas.bind("<Configure>",redimensionar,add="+")
    estado["tarefa"] = area.after_idle(renderizar)


def mostrar_foco(area, perfil, perfis, preferencias, atualizar=None):
    grade = getattr(area,"_idleboard_grade",None)
    if grade is not None:
        indice = next(i for i,p in enumerate(perfis) if p is perfil)
        grade["foco"] = None if grade["foco"] == indice else indice
        grade["renderizar"](False)
        return
    # Sem contêiner rolável: foco ocupa a área disponível e não percorre outros cartões.
    limpar_area(area)
    area.grid_columnconfigure(0, weight=1)
    area.grid_rowconfigure(0, weight=1)
    cartao = criar_cartao(area, titulo_personagem(perfil),
        atualizar or (lambda: mostrar_grade(area, perfis, preferencias)), em_foco=True,
        ocultar=lambda: ocultar_perfil(perfil, atualizar or (lambda: mostrar_grade(area, perfis, preferencias))))
    cartao.grid(row=0, column=0, sticky="nsew")


def mostrar_extensoes(conteudo, jogo_id):
    from extensoes_interface import mostrar
    mostrar(conteudo, jogo_id, JOGOS[jogo_id]['nome'])


def mostrar_secao(conteudo, nome):
    ctk.CTkLabel(conteudo, text=nome, font=("Segoe UI", 26, "bold")).pack(anchor="w")
    mensagens = {
        "Configurações": "Aqui ficarão as preferências do aplicativo.",
    }
    ctk.CTkLabel(
        conteudo, text=mensagens[nome], justify="left", wraplength=560,
        text_color="#bcb5b2", font=("Segoe UI", 16),
    ).pack(anchor="w", pady=24)


def main():
    janela = criar_janela()
    try:
        trava_instancia = adquirir_instancia()
    except OSError:
        messagebox.showerror('Idleboard',
            'Já existe uma interface ou sessão usando estes dados, ou a pasta está indisponível.\n'
            'Na primeira troca, feche a interface anterior antes de abrir a edição de uso.', parent=janela)
        janela.destroy()
        return
    janela.bind('<Destroy>', lambda evento: trava_instancia.close()
                if evento.widget is janela else None, add='+')
    try:
        jogos_salvos = catalogo_jogos.carregar()
        catalogo_jogos.salvar(jogos_salvos)
        JOGOS.clear()
        JOGOS.update(jogos_salvos)
        registros = cadastro.carregar(jogos=JOGOS)
        cadastro.salvar(registros)
        preferencias_app = configuracoes.carregar()
    except (OSError, ValueError) as erro:
        messagebox.showerror('Cadastro local', str(erro), parent=janela)
        janela.destroy()
        return
    # A seleção fica fora da área que a navegação reconstrói.
    estado = {"jogo_id": 'pokeidle' if 'pokeidle' in JOGOS else next(iter(JOGOS)), "pagina": "Início",
              "perfis": registros,
              "layouts": {jogo_id: {"modo": preferencias_app['layout_padrao']} for jogo_id in JOGOS}}
    if preferencias_app['maximizar_ao_abrir']:
        janela.state('zoomed')

    def salvar_preferencias(dados):
        try:
            resultado = configuracoes.salvar(dados)
        except (OSError, ValueError) as erro:
            messagebox.showerror('Preferências não salvas', str(erro), parent=janela)
            return False
        preferencias_app.update(resultado)
        return True
    def salvar_cadastro():
        try:
            cadastro.salvar(estado['perfis'])
        except (OSError, ValueError) as erro:
            messagebox.showerror('Não foi possível salvar', str(erro), parent=janela)
            return False
        for tela in telas_inicio.values():
            grade = getattr(tela._idleboard_area, '_idleboard_grade', None)
            if grade is not None:
                for cartao in grade['cartoes'].values():
                    cartao._idleboard_atualizar_nome()
        for painel in telas_lives.values():
            painel.sincronizar()
        return True
    for jogo_id, perfis in estado['perfis'].items():
        for perfil in perfis:
            perfil.update(prova_navegador=True, _salvar=salvar_cadastro, _jogo_id=jogo_id)
            if jogo_id in JOGOS:
                perfil.update(_nome_jogo=JOGOS[jogo_id]['nome'], _url_jogo=JOGOS[jogo_id]['url'])
        if jogo_id in estado['layouts']:
            estado['layouts'][jogo_id]['_salvar'] = salvar_cadastro
    principal = ctk.CTkFrame(janela, fg_color="transparent")
    principal.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
    principal.grid_columnconfigure(0, weight=1)
    principal.grid_rowconfigure(1, weight=1)
    seletor = ctk.CTkOptionMenu(
        principal, values=[jogo["nome"] for jogo in JOGOS.values()],
        command=lambda nome: selecionar_jogo(nome),
        **CORES_SELETOR,
    )
    seletor.set(JOGOS[estado["jogo_id"]]["nome"])
    seletor.grid(row=0, column=0, sticky="w", pady=(0, 6))
    conteudo = ctk.CTkFrame(principal, fg_color="transparent")
    conteudo.grid(row=1, column=0, sticky="nsew")
    conteudo.grid_columnconfigure(0,weight=1)
    conteudo.grid_rowconfigure(0,weight=1)
    telas_inicio = {}
    telas_lives = {}
    tela_secao = None

    def selecionar_jogo(nome):
        identificador = next(chave for chave, jogo in JOGOS.items() if jogo["nome"] == nome)
        salvar_edicoes = getattr(tela_secao, '_idleboard_salvar_edicoes', None)
        if salvar_edicoes is not None and not salvar_edicoes():
            seletor.set(JOGOS[estado['jogo_id']]['nome'])
            return
        estado["jogo_id"] = identificador
        seletor.set(JOGOS[identificador]['nome'])
        navegar(estado["pagina"])

    def aplicar_catalogo(proposta):
        try:
            validos = catalogo_jogos.salvar(proposta)
        except (OSError, ValueError) as erro:
            messagebox.showerror('Cadastro de jogos', str(erro), parent=janela)
            return False
        JOGOS.clear()
        JOGOS.update(validos)
        for identificador, jogo in JOGOS.items():
            perfis = estado['perfis'].setdefault(identificador, [])
            preferencias = estado['layouts'].setdefault(identificador, {'modo': preferencias_app['layout_padrao']})
            preferencias.update(_salvar=salvar_cadastro,
                                _adicionar=lambda chave=identificador: adicionar_perfil(chave))
            for perfil in perfis:
                perfil.update(_nome_jogo=jogo['nome'], _url_jogo=jogo['url'], _excluir=excluir_perfil)
            tela = telas_inicio.get(identificador)
            if tela is not None:
                grade = getattr(tela._idleboard_area, '_idleboard_grade', None)
                if grade is not None:
                    for cartao in grade['cartoes'].values():
                        atualizar_jogo = getattr(cartao, '_idleboard_atualizar_jogo', None)
                        if atualizar_jogo is not None:
                            atualizar_jogo()
            painel_lives = telas_lives.get(identificador)
            if painel_lives is not None:
                painel_lives.atualizar_jogo(jogo['nome'])
        if estado['jogo_id'] not in JOGOS:
            estado['jogo_id'] = next(iter(JOGOS))
        seletor.configure(values=[jogo['nome'] for jogo in JOGOS.values()])
        seletor.set(JOGOS[estado['jogo_id']]['nome'])
        return True

    def adicionar_jogo(nome, url):
        salvar_edicoes = getattr(tela_secao, '_idleboard_salvar_edicoes', None)
        if salvar_edicoes is not None and not salvar_edicoes():
            return
        try:
            identificador, jogo = catalogo_jogos.novo(nome, url)
        except ValueError as erro:
            messagebox.showerror('Cadastro de jogos', str(erro), parent=janela)
            return
        if aplicar_catalogo({**JOGOS, identificador: jogo}):
            estado['jogo_id'] = identificador
            seletor.set(jogo['nome'])
            navegar('Jogos e URLs')

    def editar_jogo(identificador, nome, url):
        return aplicar_catalogo({**JOGOS, identificador: {'nome': nome, 'url': url}})

    def excluir_jogo(identificador):
        salvar_edicoes = getattr(tela_secao, '_idleboard_salvar_edicoes', None)
        if salvar_edicoes is not None and not salvar_edicoes():
            return
        if estado['perfis'].get(identificador):
            messagebox.showinfo('Jogo com perfis', 'Exclua os perfis deste jogo antes de remover seu cadastro.', parent=janela)
            return
        if len(JOGOS) == 1:
            messagebox.showinfo('Cadastro de jogos', 'Mantenha pelo menos um jogo cadastrado.', parent=janela)
            return
        if not messagebox.askyesno('Excluir jogo',
            f"Remover {JOGOS[identificador]['nome']} do cadastro?\nDados locais antigos não serão apagados.", parent=janela):
            return
        if aplicar_catalogo({chave: jogo for chave, jogo in JOGOS.items() if chave != identificador}):
            tela = telas_inicio.pop(identificador, None)
            if tela is not None:
                limpar_area(tela._idleboard_area)
                tela.destroy()
            estado['layouts'].pop(identificador, None)
            painel_lives = telas_lives.pop(identificador, None)
            if painel_lives is not None:
                painel_lives.destroy()
            navegar('Jogos e URLs')

    def escolher_jogo(identificador):
        salvar_edicoes = getattr(tela_secao, '_idleboard_salvar_edicoes', None)
        if salvar_edicoes is not None and not salvar_edicoes():
            return
        estado['jogo_id'] = identificador
        seletor.set(JOGOS[identificador]['nome'])
        navegar('Início')

    def abrir_perfil(perfil, iniciar=True):
        jogo_id = perfil['_jogo_id']
        perfil['visivel'] = True
        if not salvar_cadastro():
            return
        navegar('Início')
        tela = telas_inicio[jogo_id]

        def revelar(tentativa=0):
            if (estado['pagina'] != 'Início' or estado['jogo_id'] != jogo_id
                    or not any(p is perfil for p in estado['perfis'][jogo_id])):
                return
            grade = getattr(tela._idleboard_area, '_idleboard_grade', None)
            if grade is None:
                if tentativa < 20:
                    janela.after(25, lambda: revelar(tentativa + 1))
                return
            grade['foco'] = None
            grade['renderizar'](False)
            indice = next(i for i, p in enumerate(estado['perfis'][jogo_id]) if p is perfil)
            cartao = grade['cartoes'].get(indice)
            if cartao is None:
                if tentativa < 20:
                    janela.after(25, lambda: revelar(tentativa + 1))
                return
            def concluir():
                if estado['pagina'] != 'Início' or not cartao.winfo_exists():
                    return
                posicao = grade['posicoes'].get(indice)
                if posicao is not None:
                    canvas = cartao.master._parent_canvas
                    bbox = canvas.bbox('all')
                    if bbox and bbox[3] > 0:
                        canvas.yview_moveto(posicao[1] * cartao._get_widget_scaling() / bbox[3])
                if iniciar and perfil.get('_sessao_teste', {}).get('web') is None:
                    cartao._idleboard_abrir_web.invoke()
            janela.after_idle(concluir)
        janela.after_idle(revelar)

    def adicionar_perfil(jogo_id):
        dialogo = ctk.CTkInputDialog(text='Nome do personagem:', title='Adicionar perfil')
        nome = dialogo.get_input()
        if nome is None:
            return
        try:
            perfil = cadastro.novo(nome)
            perfil['visualizacao'] = preferencias_app['visualizacao_padrao']
            perfil.update(prova_navegador=True, _salvar=salvar_cadastro, _jogo_id=jogo_id,
                          _excluir=excluir_perfil, _nome_jogo=JOGOS[jogo_id]['nome'],
                          _url_jogo=JOGOS[jogo_id]['url'])
            estado['perfis'][jogo_id].append(perfil)
            if not salvar_cadastro():
                estado['perfis'][jogo_id].pop()
                return
            abrir_perfil(perfil)
        except ValueError as erro:
            messagebox.showerror('Nome inválido', str(erro), parent=janela)

    def excluir_perfil(perfil):
        if estado.get('exclusao_em_andamento'):
            return
        if tela_secao is not None and not tela_secao._idleboard_salvar_edicoes():
            return
        from perfis_interface import confirmar_exclusao
        apagar_dados = confirmar_exclusao(janela, perfil)
        if apagar_dados is None:
            return
        pagina_origem = estado['pagina']
        estado['exclusao_em_andamento'] = True
        registros = estado['perfis'][perfil['_jogo_id']]
        indice = next(i for i, p in enumerate(registros) if p is perfil)
        registros.pop(indice)
        if not salvar_cadastro():
            registros.insert(indice, perfil)
            estado['exclusao_em_andamento'] = False
            return
        from core.browserman import fechar
        from contas_vinculadas import fechar_perfil
        if '_sessao_teste' in perfil:
            fechar(perfil['_sessao_teste'], avisar=False)
        fechar_perfil(perfil)

        def concluir(tentativa=0):
            if apagar_dados:
                from core.limpeza import apagar_dados_perfil
                try:
                    apagar_dados_perfil(perfil['_jogo_id'], perfil['id'])
                except OSError:
                    if tentativa < 5:
                        janela.after(250, lambda: concluir(tentativa + 1))
                        return
                    restaurar()
                    return
                except ValueError:
                    restaurar()
                    return
            tela = telas_inicio.get(perfil['_jogo_id'])
            estado['exclusao_em_andamento'] = False
            if tela is not None:
                tela._idleboard_atualizar()
            navegar(pagina_origem)

        def restaurar():
            registros.insert(min(indice, len(registros)), perfil)
            estado['exclusao_em_andamento'] = False
            salvar_cadastro()
            messagebox.showerror('Dados locais não removidos por completo',
                'Não foi possível concluir a limpeza. O perfil foi mantido na lista.\n'
                'Alguns arquivos podem já ter sido apagados; feche suas sessões e tente novamente.', parent=janela)
            navegar(pagina_origem)

        if apagar_dados:
            janela.after(250, concluir)
        else:
            concluir()

    for jogo_id in JOGOS:
        estado['layouts'][jogo_id]['_adicionar'] = lambda jogo=jogo_id: adicionar_perfil(jogo)
        for perfil in estado['perfis'][jogo_id]:
            perfil['_excluir'] = excluir_perfil

    def navegar(destino):
        nonlocal tela_secao
        salvar_edicoes = getattr(tela_secao, '_idleboard_salvar_edicoes', None)
        if salvar_edicoes is not None and not salvar_edicoes():
            return
        estado["pagina"] = destino
        for tela in telas_inicio.values():
            tela.grid_remove()
        for painel in telas_lives.values():
            painel.grid_remove()
        if tela_secao is not None:
            tela_secao.destroy()
            tela_secao = None
        for nome, botao in botoes.items():
            cor = DESTAQUE if nome == destino else PAINEL
            botao._idleboard_cor_base = cor
            botao.configure(fg_color=cor)
            botao._idleboard_icone_recolhido.configure(fg_color=cor)
            for filho in botao.winfo_children():
                if isinstance(filho, ctk.CTkButton):
                    filho.configure(fg_color=cor)
        jogo_id = estado["jogo_id"]
        if destino == "Início":
            if jogo_id not in telas_inicio:
                tela = ctk.CTkFrame(conteudo,fg_color="transparent")
                tela.grid(row=0,column=0,sticky="nsew")
                telas_inicio[jogo_id] = tela
                mostrar_inicio(tela,jogo_id,estado["perfis"][jogo_id],estado["layouts"][jogo_id])
            telas_inicio[jogo_id].grid()
            janela.after_idle(telas_inicio[jogo_id]._idleboard_atualizar)
        elif destino == 'Lives':
            if jogo_id not in telas_lives:
                from lives_interface import PainelLives
                telas_lives[jogo_id] = PainelLives(conteudo, estado['perfis'][jogo_id], JOGOS[jogo_id]['nome'])
            telas_lives[jogo_id].grid(row=0, column=0, sticky='nsew')
            telas_lives[jogo_id].sincronizar()
        else:
            tela_secao = ctk.CTkFrame(conteudo,fg_color="transparent")
            tela_secao.grid(row=0,column=0,sticky="nsew")
            if destino == "Extensões":
                mostrar_extensoes(tela_secao,jogo_id)
            elif destino == 'Jogos e URLs':
                from jogos_interface import mostrar
                mostrar(tela_secao, JOGOS, estado['perfis'], adicionar_jogo, editar_jogo,
                        excluir_jogo, escolher_jogo)
            elif destino == 'Perfis':
                from perfis_interface import mostrar
                mostrar(tela_secao, estado['perfis'][jogo_id], lambda: adicionar_perfil(jogo_id),
                        abrir_perfil, excluir_perfil)
            elif destino == 'Configurações':
                from configuracoes_interface import mostrar
                mostrar(tela_secao, preferencias_app, salvar_preferencias)
            else:
                mostrar_secao(tela_secao,destino)

    botoes = criar_barra_lateral(janela, navegar)
    navegar("Início")

    def encerrar():
        if estado.get('exclusao_em_andamento'):
            messagebox.showinfo('Excluindo perfil', 'Aguarde a conclusão da limpeza dos dados locais.', parent=janela)
            return
        salvar_edicoes = getattr(tela_secao, '_idleboard_salvar_edicoes', None)
        if salvar_edicoes is not None and not salvar_edicoes():
            return
        from core.browserman import fechar
        from contas_vinculadas import fechar_perfil
        for painel in telas_lives.values():
            painel.fechar_todas()
        for perfis in estado["perfis"].values():
            for perfil in perfis:
                if "_sessao_teste" in perfil:
                    fechar(perfil["_sessao_teste"],avisar=False)
                fechar_perfil(perfil)
        janela.destroy()

    janela.protocol("WM_DELETE_WINDOW",encerrar)
    janela.mainloop()


if __name__ == "__main__":
    main()
