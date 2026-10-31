"""Regras de colunas em unidades lógicas da área útil da janela."""

from math import ceil

MODOS = ("Amplo", "Confortável", "Compacto")
LIMIAR_CONFORTAVEL = 1560
LARGURA_COMPACTA = 360
TOLERANCIA = 24


def criar_perfil(personagem=""):
    return {"personagem": personagem.strip(), "visivel": True}


def titulo_personagem(perfil):
    return perfil["personagem"] or "Personagem não identificado"


def numero_colunas(largura, modo, anterior=None, intervalo=8):
    """A tolerância impede troca repetida de coluna perto de um limite."""
    if modo == "Amplo":
        return 1
    if modo == "Confortável":
        if anterior == 2 and largura < LIMIAR_CONFORTAVEL + TOLERANCIA:
            return 2
        if anterior == 3 and largura > LIMIAR_CONFORTAVEL - TOLERANCIA:
            return 3
        return 3 if largura >= LIMIAR_CONFORTAVEL else 2
    if modo != "Compacto":
        raise ValueError("Modo desconhecido")
    ideal = max(3, int((largura - intervalo) // (LARGURA_COMPACTA + intervalo)))
    if anterior is not None and anterior >= 3:
        entrada = (anterior + 1) * (LARGURA_COMPACTA + intervalo) + intervalo
        saida = anterior * (LARGURA_COMPACTA + intervalo) + intervalo
        if ideal > anterior and largura < entrada + TOLERANCIA:
            return anterior
        if ideal < anterior and largura > saida - TOLERANCIA:
            return anterior
    return ideal


def resolver_modo(escolhido, perfis, largura_disponivel, altura_disponivel):
    """Somente ocultação promove o modo, preservando a preferência original."""
    visiveis = sum(perfil["visivel"] for perfil in perfis)
    if visiveis == 0 or visiveis == len(perfis):
        return escolhido
    if visiveis == 1:
        return "Amplo"
    if escolhido == "Compacto" and visiveis <= numero_colunas(largura_disponivel, "Confortável"):
        return "Confortável"
    return escolhido


def dimensoes_cartao(largura, altura, quantidade, modo, intervalo=8, colunas=None):
    colunas = colunas or numero_colunas(largura, modo, intervalo=intervalo)
    largura_util = max(1, int(largura) - intervalo * (colunas + 1))
    largura_cartao = max(1, largura_util // colunas)
    if modo == "Amplo":
        altura_cartao = max(1, int(altura) - intervalo * 2)
        # Uma coluna mesmo em ultrawide: limitar a proporção em vez de deformar.
        largura_cartao = min(largura_cartao, round(altura_cartao * 2.2))
        altura_cartao = min(altura_cartao, max(1, round(largura_cartao / 1.25)))
    else:
        proporcao = 1.45 if modo == "Confortável" else 1.6
        altura_cartao = max(150, round(largura_cartao / proporcao))
        if modo == "Confortável":
            # Duas linhas completas quando a altura permite, sem alongar o cartão.
            duas_linhas = (int(altura) - intervalo * 3) // 2
            minimo_paisagem = max(150, ceil(largura_cartao / 2.2))
            altura_cartao = max(minimo_paisagem, min(altura_cartao, duas_linhas))
    return largura_cartao, altura_cartao


def calcular_layout(largura_disponivel, perfis, modo="Confortável", intervalo=8,
                    altura_disponivel=700, colunas=None):
    visiveis = [i for i, perfil in enumerate(perfis) if perfil["visivel"]]
    if not visiveis:
        return [], intervalo * 2
    colunas = colunas or numero_colunas(largura_disponivel, modo, intervalo=intervalo)
    largura, altura = dimensoes_cartao(largura_disponivel, altura_disponivel,
                                      len(visiveis), modo, intervalo, colunas)
    grade_largura = colunas * largura + (colunas - 1) * intervalo
    esquerda = max(intervalo, (int(largura_disponivel) - grade_largura) // 2)
    posicoes = [(indice, esquerda + (ordem % colunas) * (largura + intervalo),
                 intervalo + (ordem // colunas) * (altura + intervalo), largura, altura)
                for ordem, indice in enumerate(visiveis)]
    return posicoes, intervalo + ceil(len(visiveis) / colunas) * (altura + intervalo)
