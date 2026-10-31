"""Barra de rolagem leve: desenha só o indicador, sem forçar redraw da janela."""

import tkinter as tk


def instalar_barra_leve(rolagem):
    original = rolagem._scrollbar
    canvas = rolagem._parent_canvas
    grade = dict(original.grid_info())
    grade.pop("in", None)
    largura = original.winfo_reqwidth()
    original.grid_remove()
    barra = tk.Canvas(rolagem._parent_frame, width=largura, height=1,
                       bg="#121212", highlightthickness=0, borderwidth=0)
    barra.grid(**grade)
    rolagem._idleboard_barra_leve = barra
    estado = {"primeiro": 0.0, "ultimo": 1.0, "topo": 0, "tamanho": 0, "arraste": None}
    indicador = barra.create_line(0, 0, 0, 1, fill="#666a7a", capstyle="round")

    def desenhar(evento=None):
        altura = max(1, barra.winfo_height())
        fracao = estado["ultimo"] - estado["primeiro"]
        tamanho = min(altura, max(22, fracao * altura))
        topo = 0 if fracao >= 1 else estado["primeiro"] / (1 - fracao) * (altura - tamanho)
        estado.update(topo=topo, tamanho=tamanho)
        espessura = max(5, round(barra.winfo_width() * 0.45))
        meio = barra.winfo_width() / 2
        barra.itemconfigure(indicador, width=espessura, state="hidden" if fracao >= 1 else "normal")
        barra.coords(indicador, meio, topo + espessura/2, meio, topo + tamanho - espessura/2)
        # Acompanha uma troca de escala do Windows sem alterar a largura reservada.
        nova_largura = original.winfo_reqwidth()
        if int(barra.cget("width")) != nova_largura:
            barra.configure(width=nova_largura)

    def atualizar(primeiro, ultimo):
        primeiro, ultimo = float(primeiro), float(ultimo)
        if (primeiro, ultimo) != (estado["primeiro"], estado["ultimo"]):
            estado.update(primeiro=primeiro, ultimo=ultimo)
            desenhar()

    def pressionar(evento):
        barra.focus_set()
        if estado["topo"] <= evento.y <= estado["topo"] + estado["tamanho"]:
            estado["arraste"] = evento.y - estado["topo"]
        else:
            estado["arraste"] = None
            canvas.yview_scroll(-1 if evento.y < estado["topo"] else 1, "pages")

    def arrastar(evento):
        if estado["arraste"] is None:
            return
        percurso = max(1, barra.winfo_height() - estado["tamanho"])
        proporcao = max(0, min(1, (evento.y - estado["arraste"]) / percurso))
        canvas.yview_moveto(proporcao * (1 - estado["ultimo"] + estado["primeiro"]))

    canvas.configure(yscrollcommand=atualizar)
    barra.bind("<Configure>", desenhar)
    barra.bind("<Button-1>", pressionar)
    barra.bind("<B1-Motion>", arrastar)
    barra.bind("<ButtonRelease-1>", lambda e: estado.update(arraste=None))
    barra.bind("<Enter>", lambda e: barra.itemconfigure(indicador, fill="#858a9b"))
    barra.bind("<Leave>", lambda e: barra.itemconfigure(indicador, fill="#666a7a"))
    for tecla, direcao, unidade in (("Up",-1,"units"),("Down",1,"units"),("Prior",-1,"pages"),("Next",1,"pages")):
        barra.bind(f"<{tecla}>", lambda e,d=direcao,u=unidade: canvas.yview_scroll(d,u))
    barra.bind("<Home>", lambda e: canvas.yview_moveto(0))
    barra.bind("<End>", lambda e: canvas.yview_moveto(1))
    return barra
