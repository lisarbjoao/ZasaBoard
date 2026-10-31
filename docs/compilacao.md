# Compilar a beta

Windows x64, Python 3.12 x64, Tcl/Tk e compilador C# do .NET Framework são necessários na máquina de compilação. Os executáveis gerados não exigem Python instalado na máquina de uso.

`.gitattributes` desativa conversão de finais de linha em `app/` para preservar exatamente os bytes do checkpoint e seus hashes em qualquer checkout.

Instale as dependências fixadas com `python -m pip install --require-hashes -r requirements-runtime.lock`, em ambiente separado. Depois execute:

```powershell
python -m unittest discover -s tests
python tools/build_beta.py --python "PASTA_BASE_PYTHON312" --dependencias "PASTA_SITE_PACKAGES" --tcl "PASTA_TCL" --saida "dist/beta1" --csc "C:/Windows/Microsoft.NET/Framework64/v4.0.30319/csc.exe"
```

O comando recusa saída existente e fontes do núcleo com hash diferente. A seleção do runtime exclui site-packages de origem, testes, caches, diretórios WebView2, certificados/chaves avulsos e arquivos específicos do ambiente Codex; somente os quatro pacotes declarados são copiados depois. Nenhum diretório de dados da aplicação é consultado.

Saídas: `Setup.exe`, ZIP portátil, pasta com `IdleboardBeta.exe`, manifesto e SHA256SUMS. O instalador incorpora o ZIP verificado. `Setup.exe --verify` verifica o payload sem instalar; `--silent` instala sem interface. O executável aceita `--smoke-test`, que abre a interface invisível e encerra normalmente usando uma pasta sintética distinta dos perfis reais. O desinstalador aceita `--silent` e preserva os dados.

Essas opções são para validação da distribuição. O teste de abertura não prova desempenho, autenticação ou compatibilidade de serviços externos.
