"""Transições curtas, agendadas no ciclo da interface, sem bloquear a janela."""

from time import perf_counter
from math import exp
import tkinter as tk


def animar_largura(widget, destino, ao_terminar=None, duracao=0.20):
    estado = getattr(widget, "_animacao_largura", {"tarefa": None})
    widget._animacao_largura = estado
    if estado["tarefa"] is not None:
        widget.after_cancel(estado["tarefa"])
    inicio, largura_inicial = perf_counter(), float(widget.cget("width"))

    def quadro():
        estado["tarefa"] = None
        if not widget.winfo_exists():
            return
        progresso = min(1, (perf_counter() - inicio) / duracao)
        suave = 1 - (1 - progresso) ** 3
        widget.configure(width=round(largura_inicial + (destino - largura_inicial) * suave))
        if progresso < 1:
            estado["tarefa"] = widget.after(16, quadro)
        elif ao_terminar is not None:
            ao_terminar()

    quadro()


def configurar_rolagem_suave(rolagem):
    """Liga a roda somente aos widgets deste painel, sem captura global."""
    canvas = rolagem._parent_canvas
    anterior = getattr(rolagem, "_idleboard_roda", None)
    if anterior is not None:
        anterior["ligar"](rolagem)
        return anterior
    estado = {"destino": None, "tarefa": None, "instante": perf_counter()}
    rolagem._idleboard_roda = estado

    def limites():
        caixa = canvas.bbox("all")
        total = max(1, caixa[3] - caixa[1]) if caixa else 1
        return total, max(0, total - canvas.winfo_height())

    def quadro():
        estado["tarefa"] = None
        total, maximo = limites()
        atual = canvas.yview()[0] * total
        destino = max(0, min(maximo, estado["destino"]))
        diferenca = destino - atual
        if abs(diferenca) <= 1:
            canvas.yview_moveto(destino / total)
            estado["destino"] = None
            return
        agora = perf_counter()
        delta_t = min(0.05, max(0.008, agora - estado["instante"]))
        estado["instante"] = agora
        canvas.yview_moveto((atual + diferenca * (1 - exp(-delta_t / 0.045))) / total)
        estado["tarefa"] = canvas.after(16, quadro)

    def roda(evento):
        total, maximo = limites()
        if maximo == 0:
            return "break"
        atual = canvas.yview()[0] * total
        if estado["destino"] is None:
            estado["destino"] = atual
        delta = -evento.delta / 120 * 84 if getattr(evento, "delta", 0) else (-84 if evento.num == 4 else 84)
        estado["destino"] = max(0, min(maximo, estado["destino"] + delta))
        if estado["tarefa"] is None:
            quadro()
        return "break"

    def cancelar(evento):
        if evento.widget == canvas and estado["tarefa"] is not None:
            canvas.after_cancel(estado["tarefa"])
            estado["tarefa"] = None

    def ligar(widget):
        # Bind no próprio widget impede que a rolagem padrão global também execute.
        if not getattr(widget, "_idleboard_roda_ligada", False):
            tk.Misc.bind(widget, "<MouseWheel>", roda)
            tk.Misc.bind(widget, "<Button-4>", roda)
            tk.Misc.bind(widget, "<Button-5>", roda)
            widget._idleboard_roda_ligada = True
        # Incluir também Canvas/Label internos que o CTk oculta em winfo_children.
        for filho in tk.Misc.winfo_children(widget):
            ligar(filho)

    estado["ligar"] = ligar
    ligar(rolagem)
    tk.Misc.bind(canvas, "<MouseWheel>", roda)
    leve = getattr(rolagem, "_idleboard_barra_leve", None)
    if leve is not None:
        tk.Misc.bind(leve, "<MouseWheel>", roda)
    tk.Misc.bind(canvas, "<Destroy>", cancelar, add="+")
    return estado


def animar_grade(rolagem, cartoes, origens, destinos, nomes, concluir, duracao=0.18):
    """Anima desenhos leves; os widgets completos só mudam de tamanho no fim."""
    anterior = getattr(rolagem, "_idleboard_transicao", None)
    if anterior is not None:
        if anterior["tarefa"] is not None:
            rolagem.after_cancel(anterior["tarefa"])
        anterior["tarefa"] = None
        origens = dict(anterior["posicoes"])
        overlay = anterior["canvas"]
        if anterior.get("destruir_id"):
            overlay.unbind("<Destroy>", anterior["destruir_id"])
        overlay.delete("all")
    else:
        overlay = tk.Canvas(rolagem, bg="#10121b", highlightthickness=0)
    escala = rolagem._get_widget_scaling()
    altura = rolagem._parent_canvas.winfo_height()
    overlay.place(x=0, y=0, width=rolagem.winfo_width(), height=altura)
    for cartao in cartoes.values():
        cartao.place_forget()
    estado = {"canvas": overlay, "tarefa": None, "posicoes": dict(origens)}
    rolagem._idleboard_transicao = estado
    itens = {}
    for indice, destino in destinos.items():
        origem = origens.get(indice, destino)
        if min(origem[1], destino[1]) * escala > altura * 1.2:
            continue
        itens[indice] = (
            overlay.create_rectangle(0, 0, 1, 1, fill="#191d2b", outline=""),
            overlay.create_rectangle(0, 0, 1, 1, fill="#22283b", outline=""),
            overlay.create_text(0, 0, text=nomes[indice][:30], anchor="w", fill="#edf0fb",
                                font=("Segoe UI", -round(14 * escala), "bold")),
            overlay.create_text(0, 0, text="PokeIdle · prévia simulada", fill="#b8bfd8",
                                font=("Segoe UI", -round(14 * escala))),
        )
    inicio = perf_counter()

    def quadro():
        estado["tarefa"] = None
        if not overlay.winfo_exists():
            return
        if not rolagem.winfo_toplevel().winfo_viewable():
            concluir()
            overlay.destroy()
            rolagem._idleboard_transicao = None
            return
        progresso = min(1, (perf_counter() - inicio) / duracao)
        t = 1 - (1 - progresso) ** 3
        for indice, destino in destinos.items():
            origem = origens.get(indice, destino)
            valores = tuple(a + (b - a) * t for a, b in zip(origem, destino))
            estado["posicoes"][indice] = valores
            if indice not in itens:
                continue
            x, y, largura, altura_cartao = (v * escala for v in valores)
            fundo, corpo, titulo, previa = itens[indice]
            overlay.coords(fundo, x, y, x + largura, y + altura_cartao)
            overlay.coords(corpo, x + 3, y + 38 * escala, x + largura - 3, y + altura_cartao - 28 * escala)
            overlay.coords(titulo, x + 10 * escala, y + 19 * escala)
            overlay.coords(previa, x + largura / 2, y + altura_cartao / 2)
        if progresso < 1:
            estado["tarefa"] = rolagem.after(12, quadro)
        else:
            concluir()
            overlay.destroy()
            rolagem._idleboard_transicao = None

    def cancelar(evento):
        if evento.widget == overlay and estado["tarefa"] is not None:
            rolagem.after_cancel(estado["tarefa"])
            estado["tarefa"] = None

    estado["destruir_id"] = overlay.bind("<Destroy>", cancelar)
    quadro()
