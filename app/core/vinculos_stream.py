"""Associa Multitwitch à única conta Twitch do mesmo perfil, sem copiar cookies."""
from urllib.parse import urlsplit

def eh_multitwitch(vinculo):
    return urlsplit(vinculo.get('url','')).hostname in ('multitwitch.tv','www.multitwitch.tv')

def conta_sessao(perfil,vinculo):
    if not eh_multitwitch(vinculo):return vinculo
    contas=[v for v in perfil.get('vinculos',[]) if v.get('servico')=='twitch' or urlsplit(v.get('url','')).hostname in ('twitch.tv','www.twitch.tv')]
    if len(contas)!=1:raise ValueError('Multitwitch requer exatamente uma conta Twitch vinculada a este perfil.')
    return contas[0]
