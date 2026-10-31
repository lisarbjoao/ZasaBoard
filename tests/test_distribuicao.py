import hashlib
import json
from pathlib import Path
import unittest
from tools.build_beta import permitido,RAIZ


class DistribuicaoTest(unittest.TestCase):
    def test_approved_sources_are_unchanged(self):
        base=json.loads((RAIZ/'BASE.json').read_text(encoding='utf-8'))
        self.assertEqual(base['checkpoint'],'e7fb8d201569076df904e189b6777781d2f55dfb')
        for nome,sha in base['fontes_sha256'].items():
            p=RAIZ/'app'/nome
            self.assertTrue(p.resolve().is_relative_to((RAIZ/'app').resolve()))
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),sha,nome)

    def test_runtime_selection_excludes_sessions_and_unselected_packages(self):
        for nome in ('python.exe.WebView2/Default/Cookies','Lib/site-packages/private/a.py',
                     'Lib/__pycache__/os.pyc','Lib/test/a.py','Scripts/pip.exe',
                     'Lib/codex-rejected-cas.pem','Lib/private.key'):
            self.assertFalse(permitido(Path(nome)),nome)
        for nome in ('pythonw.exe','python312.dll','DLLs/_tkinter.pyd','Lib/json/decoder.py'):
            self.assertTrue(permitido(Path(nome)),nome)

    def test_no_private_profile_or_extension_in_sources(self):
        for p in (RAIZ/'app').rglob('*'):
            if p.is_file():self.assertEqual(p.suffix,'.py')
        self.assertFalse((RAIZ/'data').exists())
        self.assertFalse((RAIZ/'personal').exists())
