"""Catálogo interno por identidade de jogo; cadastro não instala código."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Extensao:
    id: str
    nome: str
    descricao: str
    disponivel: bool
    pendencias: tuple[str, ...] = ()


_CATALOGO = {'pokeidle': (
    Extensao('hunt', '/hunt',
        'Ferramenta de hunts do PokeIdle. A execução será integrada após validar as regras do jogo.',
        False, ('Concluir a base de regras e a cobertura das mecânicas.',
                'Integrar e verificar o motor de hunts.',
                'Definir explicitamente o destino: simulação ou sessão real.')),
    Extensao('ficha-sintetica','Ficha sintética',
        'Laboratório local com ficha, cenários salvos, comparação de resultados e hunts experimentais com parâmetros explícitos. Não altera contas reais.',True),
)}


def listar(jogo_id):
    """Uma tupla imutável; jogos desconhecidos não herdam módulos pelo nome."""
    return _CATALOGO.get(jogo_id, ())
