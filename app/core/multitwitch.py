"""Controles oficiais de embeds Twitch, restritos à página Multitwitch."""
import json


def validar(opcoes):
    if opcoes is None:opcoes={}
    if not isinstance(opcoes,dict):raise ValueError('Preferências do Multitwitch inválidas.')
    qualidade=opcoes.get('qualidade','minima')
    silenciado=opcoes.get('silenciado',True)
    if qualidade not in ('minima','auto') or type(silenciado) is not bool:
        raise ValueError('Preferências do Multitwitch inválidas.')
    return {'qualidade':qualidade,'silenciado':silenciado}


SCRIPT=r'''(() => {
  if (location.protocol !== 'https:' || !['multitwitch.tv','www.multitwitch.tv'].includes(location.hostname))
    return JSON.stringify({estado:'pagina_incompativel',canais:[]});
  const opcoes = __OPCOES__;
  const chave = '__idleboardMultitwitch';
  let s = window[chave];
  if (!s) {
    s = window[chave] = {estado:'aguardando_sdk',opcoes,players:new Map(),contador:0};
    s.ajustar = item => {
      if (!item.pronto) return;
      try {
        item.player.setMuted(s.opcoes.silenciado);
        const qualidades = item.player.getQualities();
        const nomes = Array.isArray(qualidades) ? qualidades.map(q =>
          typeof q === 'string' ? q : q && typeof q.group === 'string' ? q.group : null).filter(Boolean) : [];
        let alvo = s.opcoes.qualidade === 'auto' && nomes.includes('auto') ? 'auto' : null;
        if (s.opcoes.qualidade === 'minima') {
          const video = nomes.filter(q => /^\d+p(?:\d+)?$/.test(q));
          video.sort((a,b) => parseInt(a)-parseInt(b) || (parseInt(a.split('p')[1])||0)-(parseInt(b.split('p')[1])||0));
          alvo = video[0] || null;
        }
        if (alvo && item.player.getQuality() !== alvo) item.player.setQuality(alvo);
        item.qualidade = item.player.getQuality() || null;
        item.qualidade_disponivel = !!alvo;
        item.estado = 'controles_prontos';
      } catch (_) { item.estado = 'controle_indisponivel'; }
    };
    s.converter = () => {
      if (!window.Twitch?.Player) return;
      s.estado = 'controles_instalados';
      for (const [no,item] of s.players) {
        if (!no.isConnected) { try { item.player.pause(); } catch (_) {} s.players.delete(no); }
      }
      document.querySelectorAll('iframe.stream').forEach(original => {
        let url;
        try { url = new URL(original.src); } catch (_) { return; }
        const canal = url.searchParams.get('channel');
        if (url.protocol !== 'https:' || url.hostname !== 'player.twitch.tv' || !/^[a-z0-9_]{1,64}$/i.test(canal || '')) return;
        const no = document.createElement('div');
        no.id = 'idleboard-twitch-' + (++s.contador);
        no.className = original.className;
        no.style.cssText = original.style.cssText;
        no.style.minWidth = '400px'; no.style.minHeight = '300px';
        original.after(no);
        try {
          const player = new Twitch.Player(no.id, {channel:canal,width:'100%',height:'100%',
            parent:[location.hostname],autoplay: false,muted:s.opcoes.silenciado});
          const item = {canal,player,pronto:false,estado:'aguardando_player',qualidade:null};
          s.players.set(no,item);
          player.addEventListener(Twitch.Player.READY, () => { item.pronto=true; s.ajustar(item); });
          player.addEventListener(Twitch.Player.PLAYING, () => s.ajustar(item));
          original.remove();
        } catch (_) { no.remove(); s.estado='conversao_indisponivel'; }
      });
    };
    const observador = new MutationObserver(() => s.converter());
    observador.observe(document.getElementById('streams') || document.body,{childList:true});
    s.observador = observador;
    if (!window.Twitch?.Player) {
      const sdk=document.createElement('script');
      sdk.src='https://player.twitch.tv/js/embed/v1.js';
      sdk.onload=() => s.converter();
      sdk.onerror=() => { s.estado='sdk_indisponivel'; };
      document.head.appendChild(sdk);
    }
  }
  s.opcoes=opcoes;
  s.converter();
  for (const item of s.players.values()) s.ajustar(item);
  return JSON.stringify({estado:s.estado,canais:[...s.players.values()].map(i =>
    ({canal:i.canal,estado:i.estado,qualidade:i.qualidade,qualidade_disponivel:!!i.qualidade_disponivel}))});
})();'''


def script(opcoes):
    return SCRIPT.replace('__OPCOES__',json.dumps(validar(opcoes),ensure_ascii=True))


def aplicar(estado,opcoes,concluiu=None,falhou=None):
    codigo=script(opcoes)
    web=estado.get('web')
    if web is None or not web.ready:return False
    def receber(valor):
        try:
            for _ in range(3):
                if not isinstance(valor,str):break
                valor=json.loads(valor)
            if not isinstance(valor,dict) or not isinstance(valor.get('estado'),str) or not isinstance(valor.get('canais'),list):
                raise ValueError('Resposta de controle inválida.')
        except (ValueError,TypeError):
            if falhou:falhou('Resposta de controle indisponível.')
            return
        if concluiu:concluiu(valor)
    try:web.eval_js_with_callback(codigo,callback=receber,on_error=falhou)
    except (RuntimeError,ValueError) as erro:
        if falhou:falhou(str(erro))
        return False
    return True
