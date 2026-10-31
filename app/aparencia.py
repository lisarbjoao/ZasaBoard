"""Medidas e estados compartilhados pelos controles dos cartões."""

import customtkinter as ctk

BOTAO_CARTAO = dict(height=30, corner_radius=6,
                    fg_color='#24293b', hover_color='#30354b')
LARGURA_ICONE_CARTAO = 32


class JanelaAuxiliar(ctk.CTkToplevel):
    """Cancela ajustes visuais pendentes ao fechar rapidamente no Windows."""
    def __init__(self, *args, **kwargs):
        self._tarefas = set()
        super().__init__(*args, **kwargs)

    def after(self, ms, func=None, *args):
        tarefa = super().after(ms, func, *args)
        if func is not None:
            self._tarefas.add(tarefa)
        return tarefa

    def destroy(self):
        for tarefa in self._tarefas:
            self.tk.call('after', 'cancel', tarefa)
        self._tarefas.clear()
        super().destroy()
