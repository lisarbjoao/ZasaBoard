"""Painel de páginas de lives, com sessão compartilhada somente por conta."""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from aparencia import BOTAO_CARTAO, LARGURA_ICONE_CARTAO, JanelaAuxiliar
from core import browserman, lives as cadastro, perfis, sessoes_vinculadas, streamopt
from layout import titulo_personagem, numero_colunas
from rolagem import instalar_barra_leve
from movimento import configurar_rolagem_suave


class CartaoLive(ctk.CTkFrame):
    def __init__(self, pai, perfil, live, vinculo, excluir, foco):
        super().__init__(pai, fg_color='#191d2b', corner_radius=6)
        self.perfil, self.live, self.vinculo = perfil, live, vinculo
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.titulo = ctk.CTkLabel(self, text='', width=1, anchor='w', font=('Segoe UI', 14, 'bold'))
        self.titulo.grid(row=0, column=0, sticky='ew', padx=10, pady=6)
        self._botao_icone('\ue740', foco).grid(row=0, column=1, padx=1, pady=4)
        self._botao_icone('\ue74d', excluir).grid(row=0, column=2, padx=(1, 4), pady=4)
        self._excluir = excluir
        self.canais = None
        if live.get('_multitwitch'):
            self.canais = ctk.CTkButton(self, text='Canais', width=70, **BOTAO_CARTAO,
                                       command=self.gerenciar_canais)
            self.canais.grid(row=0, column=3, padx=(0, 4))
        self.host = tk.Frame(self, bg='#22283b')
        self.host.grid(row=1, column=0, columnspan=4, sticky='nsew', padx=3)
        self.mensagem = ctk.CTkLabel(self.host, text='Abra a live e inicie a reprodução na plataforma.',
                                     wraplength=260, text_color='#a8adc2')
        self.mensagem.place(relx=.5, rely=.5, anchor='center')
        if live.get('_multitwitch'):
            self.mensagem.configure(text='Abra o Multitwitch e controle reprodução e som nos players.')
        rodape = ctk.CTkFrame(self, fg_color='transparent')
        rodape.grid(row=2, column=0, columnspan=4, sticky='ew', padx=4, pady=4)
        rodape.grid_columnconfigure(0, weight=1)
        self.status = ctk.CTkLabel(rodape, text='Fechada', width=1, anchor='w', text_color='#a8adc2')
        self.status.grid(row=0, column=0, sticky='ew', padx=6)
        for coluna, (icone, acao) in enumerate((('\ue768', self.abrir), ('\ue71a', self.parar),
                                                ('\ue72c', lambda: browserman.recarregar(self.estado))), 1):
            ctk.CTkButton(rodape, text=icone, font=('Segoe MDL2 Assets', 16),
                          width=LARGURA_ICONE_CARTAO, **BOTAO_CARTAO, command=acao).grid(
                              row=0, column=coluna, padx=1)
        pasta = perfis.pasta_vinculo(perfil['_jogo_id'], perfil, vinculo)
        self.estado = browserman.criar_estado(pasta)
        self.estado.update(notificar=self._status, _fechar_card=self.parar)
        self.estado['_pagina_carregada'] = self.aplicar_audio
        self.botao_audio = ctk.CTkButton(rodape, text='', font=('Segoe MDL2 Assets', 16),
            width=LARGURA_ICONE_CARTAO, **BOTAO_CARTAO, command=self.alternar_audio)
        self.botao_audio.grid(row=0, column=4, padx=1)
        self.atualizar_audio()
        self.atualizar_titulo()

    def _botao_icone(self, icone, acao):
        return ctk.CTkButton(self, text=icone, font=('Segoe MDL2 Assets', 16),
                             width=LARGURA_ICONE_CARTAO, **BOTAO_CARTAO, command=acao)

    def atualizar_titulo(self):
        nome = f'{cadastro.titulo(self.live)} · {titulo_personagem(self.perfil)}'
        self.titulo.configure(text=nome[:42] + ('…' if len(nome) > 42 else ''))

    def _status(self, texto):
        if not self.winfo_exists():
            return
        self.status.configure(text=texto)
        if self.estado['web'] is not None:
            self.mensagem.place_forget()
        else:
            self.mensagem.configure(text=texto)
            self.mensagem.place(relx=.5, rely=.5, anchor='center')
            if self.estado['sessao'] is None:
                sessoes_vinculadas.remover(self.vinculo, self.estado)

    def abrir(self):
        if self.estado['web'] is not None:
            return
        self.atualizar_audio()
        compartilhada = sessoes_vinculadas.ativa(self.vinculo)
        sessoes_vinculadas.registrar(self.vinculo, self.estado)
        if compartilhada is not None:
            browserman.abrir(self.estado, self.host, self.live['url'], compartilhar=compartilhada)
        else:
            browserman.abrir(self.estado, self.host, self.live['url'])

    def atualizar_audio(self):
        if self.live.get('_multitwitch'):
            self.botao_audio.grid_remove()
            self.estado['_script_inicial'] = None
            return
        silenciado = self.live.get('silenciado', True)
        self.botao_audio.configure(text='\ue74f' if silenciado else '\ue767')
        self.estado['_script_inicial'] = streamopt.script_audio(silenciado)

    def aplicar_audio(self):
        if self.live.get('_multitwitch'):
            return
        streamopt.aplicar_audio(self.estado, self.live.get('silenciado', True),
            falhou=lambda _erro: self._status('Controle de áudio indisponível nesta página'))

    def alternar_audio(self):
        anterior = self.live.get('silenciado', True)
        self.live['silenciado'] = not anterior
        if not self.perfil['_salvar']():
            self.live['silenciado'] = anterior
            return
        self.atualizar_audio()
        self.aplicar_audio()

    def atualizar_live(self, live):
        mudou = self.live['url'] != live['url']
        self.live = live
        self.atualizar_titulo()
        if mudou and self.estado['web'] is not None:
            self.estado['web'].load_url(live['url'])

    def gerenciar_canais(self):
        janela = JanelaAuxiliar(self.winfo_toplevel())
        janela.title('Canais do Multitwitch')
        janela.geometry('420x320')
        janela.transient(self.winfo_toplevel())
        ctk.CTkLabel(janela, text='Remova um canal sem excluir a conta vinculada.').pack(pady=12)
        lista = ctk.CTkScrollableFrame(janela)
        lista.pack(fill='both', expand=True, padx=12, pady=(0, 12))
        for item in self.live['_itens']:
            linha = ctk.CTkFrame(lista, fg_color='transparent')
            linha.pack(fill='x', pady=3)
            ctk.CTkLabel(linha, text=cadastro.canal_twitch(item['url'])).pack(side='left', padx=6)
            def remover(identificador=item['id']):
                janela.destroy()
                self._excluir(identificador)
            ctk.CTkButton(linha, text='Remover', width=80, command=remover).pack(side='right', padx=6)

    def parar(self):
        browserman.fechar(self.estado, avisar=False)
        sessoes_vinculadas.remover(self.vinculo, self.estado)
        self._status('Fechada · sessão preservada')

    def destroy(self):
        self.parar()
        super().destroy()


class PainelLives(ctk.CTkFrame):
    def __init__(self, pai, registros, nome_jogo):
        super().__init__(pai, fg_color='transparent')
        self.registros = registros
        self.cartoes, self.perfis_opcoes, self.contas_opcoes = {}, {}, {}
        self.perfil_id = self.conta_id = self.foco = self.tarefa = None
        self._encerrando = False
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.cabecalho = ctk.CTkLabel(self, text=f'Lives · {nome_jogo}', font=('Segoe UI', 24, 'bold'))
        self.cabecalho.grid(row=0, column=0, sticky='w', pady=(0, 10))
        formulario = ctk.CTkFrame(self, fg_color='#191d2b')
        formulario.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        formulario.grid_columnconfigure((0, 1), weight=1)
        self.menu_perfil = ctk.CTkOptionMenu(formulario, values=['Sem perfis'],
            fg_color='#24293b', button_color='#30354b', command=self._selecionar_perfil)
        self.menu_perfil.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        self.menu_conta = ctk.CTkOptionMenu(formulario, values=['Sem contas vinculadas'],
            fg_color='#24293b', button_color='#30354b', command=self._selecionar_conta)
        self.menu_conta.grid(row=0, column=1, sticky='ew', padx=(0, 10), pady=10)
        ctk.CTkButton(formulario, text='Vincular conta', width=110, fg_color='#30354b',
                      command=self.vincular).grid(row=0, column=2, padx=(0, 10), pady=10)
        self.url = ctk.CTkEntry(formulario, placeholder_text='URL do canal na Twitch ou Kick')
        self.url.grid(row=1, column=0, columnspan=2, sticky='ew', padx=10, pady=(0, 10))
        self.adicionar_botao = ctk.CTkButton(formulario, text='+ Live', width=110,
            fg_color='#7965ed', command=self.adicionar)
        self.adicionar_botao.grid(row=1, column=2, padx=(0, 10), pady=(0, 10))
        self.url.bind('<Return>', lambda _evento: self.adicionar())
        self.area = ctk.CTkScrollableFrame(self, fg_color='transparent', corner_radius=0)
        self.area.grid(row=2, column=0, sticky='nsew')
        instalar_barra_leve(self.area)
        self.espaco = tk.Frame(self.area, width=1, height=1, bg='#10121b')
        self.espaco.grid(row=0, column=0)
        self.vazio = ctk.CTkLabel(self.area, text='Associe uma conta ao perfil e adicione a URL de uma live.',
                                 text_color='#a8adc2')
        self.area.bind('<Configure>', lambda _evento: self.agendar_layout(), add='+')
        self.area._parent_canvas.bind('<Configure>', lambda _evento: self.agendar_layout(), add='+')
        self._idleboard_atualizar = self.sincronizar
        self.sincronizar()

    def perfil_atual(self):
        return next((p for p in self.registros if p['id'] == self.perfil_id), None)

    def _selecionar_perfil(self, texto):
        self.perfil_id = self.perfis_opcoes.get(texto)
        self.conta_id = None
        self._atualizar_contas()

    def _selecionar_conta(self, texto):
        self.conta_id = self.contas_opcoes.get(texto)

    def _atualizar_contas(self):
        perfil = self.perfil_atual()
        opcoes = {}
        for indice, conta in enumerate((perfil or {}).get('vinculos', []), 1):
            try:
                plataforma = cadastro.plataforma_conta(conta)
            except ValueError:
                continue
            opcoes[f"{conta['nome'] or plataforma.title()} · {indice}"] = conta['id']
        self.contas_opcoes = opcoes
        if self.conta_id not in opcoes.values():
            self.conta_id = next(iter(opcoes.values()), None)
        self.menu_conta.configure(values=list(opcoes) or ['Sem contas vinculadas'],
                                   state='normal' if opcoes else 'disabled')
        self.menu_conta.set(next((nome for nome, chave in opcoes.items() if chave == self.conta_id),
                                 'Sem contas vinculadas'))
        self.adicionar_botao.configure(state='normal' if opcoes else 'disabled')

    def sincronizar(self):
        if self._encerrando or not self.winfo_exists():
            return
        self.perfis_opcoes = {f'{titulo_personagem(p)} · {i}': p['id']
                             for i, p in enumerate(self.registros, 1)}
        if self.perfil_id not in self.perfis_opcoes.values():
            self.perfil_id = next(iter(self.perfis_opcoes.values()), None)
        self.menu_perfil.configure(values=list(self.perfis_opcoes) or ['Sem perfis'],
                                    state='normal' if self.perfis_opcoes else 'disabled')
        self.menu_perfil.set(next((nome for nome, chave in self.perfis_opcoes.items() if chave == self.perfil_id),
                                  'Sem perfis'))
        self._atualizar_contas()
        esperados = {}
        for perfil in self.registros:
            for chave_live, live in cadastro.agrupar(perfil.get('lives', [])).items():
                conta = next((v for v in perfil['vinculos'] if v['id'] == live['vinculo_id']), None)
                if conta is not None:
                    esperados[(perfil['id'], chave_live)] = (perfil, live, conta)
        for chave in list(self.cartoes):
            if chave not in esperados:
                self.cartoes.pop(chave).destroy()
        novos = False
        for chave, (perfil, live, conta) in esperados.items():
            if chave not in self.cartoes:
                novos = True
                self.cartoes[chave] = CartaoLive(self.area, perfil, live, conta,
                    lambda item_id=None, k=chave: self.excluir(k, item_id), lambda k=chave: self.alternar_foco(k))
            self.cartoes[chave].atualizar_live(live)
        if self.foco not in self.cartoes:
            self.foco = None
        if novos:
            configurar_rolagem_suave(self.area)
        self.agendar_layout()

    def vincular(self):
        perfil = self.perfil_atual()
        if perfil is None:
            messagebox.showinfo('Lives', 'Crie um perfil de jogo antes de vincular uma conta.', parent=self.winfo_toplevel())
            return
        from contas_vinculadas import gerenciar
        gerenciar(self, perfil)

    def adicionar(self):
        perfil = self.perfil_atual()
        if perfil is None:
            return
        conta = next((v for v in perfil['vinculos'] if v['id'] == self.conta_id), None)
        if conta is None:
            return
        try:
            live = cadastro.nova(self.url.get(), conta, perfil['vinculos'])
            if cadastro.plataforma(live['url']) == 'twitch':
                canal = cadastro.canal_twitch(live['url'])
                if any(v['vinculo_id'] == conta['id'] and cadastro.canal_twitch(v['url']) == canal
                       for v in perfil.get('lives', [])):
                    raise ValueError('Este canal já está no Multitwitch desta conta.')
            perfil.setdefault('lives', []).append(live)
            if not perfil['_salvar']():
                perfil['lives'].pop()
                return
            self.url.delete(0, 'end')
            self.sincronizar()
            card = self.cartoes[(perfil['id'], cadastro.chave_cartao(live))]
            self.after_idle(lambda: card.abrir() if card.winfo_exists() else None)
        except ValueError as erro:
            messagebox.showerror('Live', str(erro), parent=self.winfo_toplevel())

    def excluir(self, chave, item_id=None):
        card = self.cartoes[chave]
        itens = card.live.get('_itens', [card.live])
        ids = {item['id'] for item in itens if item_id is None or item['id'] == item_id}
        mensagem = ('Remover todos os canais deste Multitwitch?' if card.live.get('_multitwitch') and item_id is None
                    else 'Remover este endereço de live?')
        if not messagebox.askyesno('Excluir live', mensagem + ' O login da conta será preservado.',
                                   parent=self.winfo_toplevel()):
            return
        anteriores = card.perfil['lives']
        card.perfil['lives'] = [item for item in anteriores if item['id'] not in ids]
        if not card.perfil['_salvar']():
            card.perfil['lives'] = anteriores
            return
        self.sincronizar()

    def alternar_foco(self, chave):
        self.foco = None if self.foco == chave else chave
        self.area._parent_canvas.yview_moveto(0)
        self.agendar_layout()

    def agendar_layout(self):
        if self._encerrando:
            return
        if self.tarefa is not None:
            self.after_cancel(self.tarefa)
        self.tarefa = self.after(40, self._organizar)

    def _organizar(self):
        self.tarefa = None
        escala = self.area._get_widget_scaling()
        largura = self.area.winfo_width() / escala
        altura = self.area._parent_canvas.winfo_height() / escala
        if largura < 20:
            return
        chaves = [self.foco] if self.foco else list(self.cartoes)
        colunas = 1 if self.foco else min(numero_colunas(largura, 'Confortável'),
            max(1, int(largura / 400)), max(1, len(chaves)))
        largura_card = max(1, (largura - 8 * (colunas + 1)) / colunas)
        altura_card = max(300, altura - 16) if self.foco else max(280, largura_card * 9 / 16 + 80)
        for chave, card in self.cartoes.items():
            if chave not in chaves:
                card.place_forget()
        for indice, chave in enumerate(chaves):
            card = self.cartoes[chave]
            card.configure(width=round(largura_card), height=round(altura_card))
            card.place(x=8 + (indice % colunas) * (largura_card + 8),
                       y=8 + (indice // colunas) * (altura_card + 8))
        linhas = (len(chaves) + colunas - 1) // colunas
        self.espaco.configure(height=round(max(altura, linhas * (altura_card + 8) + 8) * escala))
        if self.cartoes:
            self.vazio.place_forget()
        else:
            self.vazio.place(x=12, y=20)

    def atualizar_jogo(self, nome):
        self.cabecalho.configure(text=f'Lives · {nome}')

    def fechar_todas(self):
        for card in list(self.cartoes.values()):
            card.parar()

    def destroy(self):
        self._encerrando = True
        if self.tarefa is not None:
            self.after_cancel(self.tarefa)
        self.fechar_todas()
        super().destroy()
