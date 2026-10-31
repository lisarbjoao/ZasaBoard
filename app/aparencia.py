"""Medidas e estados compartilhados pelos controles dos cartões."""

import customtkinter as ctk

BOTAO_CARTAO = dict(height=30, corner_radius=6,
                    fg_color='#29272a', hover_color='#393337')
LARGURA_ICONE_CARTAO = 32


class JanelaAuxiliar(ctk.CTkToplevel):
    """Cancela ajustes visuais pendentes ao fechar rapidamente no Windows."""
    def __init__(self, *args, **kwargs):
        self._tarefas = set()
        self._encerrando = False
        super().__init__(*args, **kwargs)

    def after(self, ms, func=None, *args):
        if self._encerrando:return None
        if func is None:return super().after(ms)
        tarefa=None
        def executar():
            self._tarefas.discard(tarefa)
            if not self._encerrando and self.winfo_exists():func(*args)
        tarefa=super().after(ms,executar)
        self._tarefas.add(tarefa)
        return tarefa

    def destroy(self):
        if self._encerrando:return
        self._encerrando=True
        for tarefa in tuple(self._tarefas):
            self.after_cancel(tarefa)
        self._tarefas.clear()
        super().destroy()
