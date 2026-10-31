import json
import time
import unittest
from unittest.mock import Mock
from core.espelho import validar_evento,origem_url,Controlador


class EspelhoTest(unittest.TestCase):
    def evento(self):
        return {'token':'abc','seq':1,'tipo':'clique','x':20,'y':30,'w':800,'h':600,'dpr':1,
                'sx':0,'sy':0,'path':'/app','rota':'abc','ate':int(time.time()*1000)+750,'marca':{'tag':'BUTTON','id':'mercado','texto':'Mercado'}}

    def test_validates_only_expected_click_fields_and_matching_token(self):
        e=self.evento();self.assertEqual(validar_evento(json.dumps(e),'abc'),e)
        with self.assertRaises(ValueError):validar_evento(json.dumps(self.evento()),'outro')
        e=self.evento();e['password']='nao aceitar'
        with self.assertRaises(ValueError):validar_evento(json.dumps(e),'abc')

    def test_rejects_invalid_coordinates_boolean_and_oversized_messages(self):
        for campo,valor in (('x',-1),('x',800),('y',float('nan')),('w',True),('seq',False),('dpr',0),('tipo','teclado'),('rota','invalida'),('ate',0),('ate',True)):
            with self.subTest(campo=campo),self.assertRaises(ValueError):
                validar_evento(json.dumps(dict(self.evento(),**{campo:valor})),'abc')
        with self.assertRaises(ValueError):validar_evento(' '*3000,'abc')

    def test_origin_is_exact_and_does_not_accept_credentials(self):
        self.assertEqual(origem_url('https://game.example/app?x=1'),'https://game.example')
        self.assertEqual(origem_url('https://game.example:444/app'),'https://game.example:444')
        for url in ('file:///tmp/a','https://user:pass@game.example','javascript:alert(1)'):
            with self.assertRaises(ValueError):origem_url(url)

    def test_navigation_revokes_immediately_without_native_or_tk_calls(self):
        pai=Mock();c=Controlador(pai,[],Mock());s={}
        c.grupo=[{'estado':s}];c.ativo=True;c.parar=Mock()
        c.invalidar('Página mudou')
        self.assertFalse(c.ativo)
        self.assertEqual(pai.mock_calls,[])
        c.parar.assert_not_called()
        s['_espelho_concluir']()
        c.parar.assert_called_once_with('Página mudou')

    def test_stale_async_callback_does_not_resume_old_round(self):
        c=Controlador(Mock(),[],Mock());web=Mock();callback=Mock()
        item={'web':web,'estado':{'web':web}}
        c._consultar(item,'JSON.stringify(true)',callback,c.geracao)
        receber=web.eval_js_with_callback.call_args.kwargs['callback']
        c.geracao+=1
        receber('true')
        callback.assert_not_called()


class MedidasWebViewTest(unittest.TestCase):
    def test_medidas_css_fracionarias_e_escala_positiva(self):
        c=Controlador(Mock(),[],Mock());c.origem='https://game.example';c.grupo=[{'i':0},{'i':1}]
        c._instalar=Mock()
        viewport={'w':1100.5,'h':600.25,'dpr':0.2,'path':'/app','rota':'abc'}
        c._consultar=lambda item,script,callback,g:callback(dict(viewport))
        c._sondar(c.geracao)
        c._instalar.assert_called_once()

    def test_medidas_invalidas_continuam_bloqueadas_e_explicadas(self):
        for w,h,dpr in [(0,600,1),(1100,0,1),(True,600,1),(1100,600,0),(1100,600,float('nan'))]:
            c=Controlador(Mock(),[],Mock());c.origem='https://game.example';c.grupo=[{}]
            c.parar=Mock();c._instalar=Mock()
            c._consultar=lambda item,script,callback,g:callback({'w':w,'h':h,'dpr':dpr,'path':'/app','rota':'abc'})
            c._sondar(c.geracao)
            c._instalar.assert_not_called();self.assertIn('medidas inválidas',c.parar.call_args.args[0])


class RolagemProtocoloTest(unittest.TestCase):
    def test_rolagem_aceita_so_posicoes_finitas_limitadas(self):
        base=EspelhoTest().evento();base.update(tipo='rolagem',roda={'top':120,'left':0})
        self.assertEqual(validar_evento(json.dumps(base),'abc')['roda']['top'],120)
        for posicao in (-1,True,float('nan'),10**8):
            e=dict(base,roda={'top':posicao,'left':0})
            with self.assertRaises(ValueError):validar_evento(json.dumps(e),'abc')
        with self.assertRaises(ValueError):validar_evento(json.dumps(dict(base,tipo='clique')),'abc')
