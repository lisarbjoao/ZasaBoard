"""Endereços de lives e sua associação à conta vinculada de um perfil."""

import re
from urllib.parse import urlsplit
from uuid import uuid4
from core.enderecos import normalizar_url


def plataforma(url):
    host = urlsplit(normalizar_url(url)).hostname.lower()
    if host in ('twitch.tv', 'www.twitch.tv', 'm.twitch.tv'):
        return 'twitch'
    if host in ('kick.com', 'www.kick.com'):
        return 'kick'
    raise ValueError('Use um endereço de live da Twitch ou da Kick.')


def plataforma_conta(vinculo):
    if vinculo.get('url'):
        return plataforma(vinculo['url'])
    if vinculo.get('servico') in ('twitch', 'kick'):
        return vinculo['servico']
    raise ValueError('Vincule uma conta da Twitch ou da Kick a este perfil.')


def validar(live, vinculos):
    for campo in ('id', 'vinculo_id'):
        valor = live.get(campo)
        if not isinstance(valor, str) or not re.fullmatch(r'[a-zA-Z0-9-]{1,64}', valor):
            raise ValueError('Identificação de live inválida.')
    url = normalizar_url(live.get('url'))
    canal = urlsplit(url).path.strip('/')
    if not canal:
        raise ValueError('Cole o endereço do canal, incluindo seu nome após o domínio.')
    conta = next((v for v in vinculos if v['id'] == live['vinculo_id']), None)
    if conta is None or plataforma_conta(conta) != plataforma(url):
        raise ValueError('Escolha uma conta vinculada à mesma plataforma da live.')
    silenciado = live.get('silenciado', True)
    if not isinstance(silenciado, bool):
        raise ValueError('Preferência de áudio inválida.')
    return {'id': live['id'], 'vinculo_id': live['vinculo_id'], 'url': url,
            'silenciado': silenciado}


def nova(url, vinculo, vinculos):
    return validar({'id': uuid4().hex, 'vinculo_id': vinculo['id'], 'url': url}, vinculos)


def titulo(live):
    if live.get('_multitwitch'):
        return f"Multitwitch · {len(live['_itens'])} canais"
    return urlsplit(live['url']).path.strip('/')[:80]


def canal_twitch(url):
    canal = urlsplit(url).path.strip('/').split('/')[0].lower()
    if not re.fullmatch(r'[a-z0-9_]{1,64}', canal):
        raise ValueError('Use a URL de um canal da Twitch.')
    return canal


def chave_cartao(live):
    return f"twitch-{live['vinculo_id']}" if plataforma(live['url']) == 'twitch' else live['id']


def agrupar(registros):
    """Projeção para a interface; não altera os endereços individuais salvos."""
    grupos = {}
    for live in registros:
        chave = chave_cartao(live)
        if plataforma(live['url']) != 'twitch':
            grupos[chave] = live
            continue
        grupo = grupos.setdefault(chave, {'id': chave, 'vinculo_id': live['vinculo_id'],
                                         '_multitwitch': True, '_itens': []})
        grupo['_itens'].append(live)
    for grupo in grupos.values():
        if grupo.get('_multitwitch'):
            canais = dict.fromkeys(canal_twitch(item['url']) for item in grupo['_itens'])
            grupo['url'] = 'https://multitwitch.tv/' + '/'.join(canais)
    return grupos
