<p align="center">
  <img src="assets/charizard-capa.png" width="280" alt="Shiny Charizard preto com asas vermelhas e chamas alaranjadas" />
</p>

<h1 align="center">ZasaBoard</h1>

<p align="center">Uma interface para organizar múltiplas sessões web, perfis e plataformas.</p>
<p align="center"><strong>Windows x64 · Python · CustomTkinter · WebView2</strong></p>

---

O ZasaBoard reúne sessões independentes em cartões para acompanhar jogos, plataformas e fluxos de trabalho. O projeto começou como Idleboard Manager e explora uma interface reutilizável para gerenciar várias sessões sem perder a organização dos perfis.

## O que você pode fazer

- **Organizar cartões:** modos Amplo, Confortável e Compacto, foco individual e ocultação mantendo a sessão aberta.
- **Manter perfis:** nomes editáveis, armazenamento persistente e contas de plataformas associadas a cada personagem.
- **Controlar páginas:** recarga, visualização, áudio e zoom por cartão.
- **Acompanhar lives:** grupos Multitwitch, páginas Kick e chats Twitch usando a conta associada ao perfil.
- **Alinhar e espelhar:** padronizar área e zoom antes de ativar a repetição de cliques entre cartões compatíveis.
- **Usar extensões por jogo:** catálogo contextual, com integração pessoal opt-in do `/hunt` para PokeIdle e acesso ao laboratório configurado separadamente.

## Beta 2 para Windows

Cartões, perfis, contas vinculadas, Multitwitch, áudio, Alinhar e espelhamento de cliques/rolagem. Cliques confirmados pelo autor no PokeIdle; rolagem e suíte completa validadas com navegadores locais. Estabilidade prolongada em outros computadores continua em avaliação.

### Baixar e instalar

1. Abra a [página da Beta 2](https://github.com/lisarbjoao/Idleboard-Beta/releases/tag/v2.0.0-beta.9).
2. Baixe **ZasaBoard-2.0.0-beta.9-Setup.exe** e execute-o.
3. Abra **ZasaBoard Beta 2** pelo atalho da área de trabalho ou pelo menu Iniciar.

Não precisa instalar Python nem manter VS Code aberto. Requer Windows 10/11 x64 e Microsoft Edge WebView2 Runtime. O instalador não tem assinatura digital. O ZIP é a alternativa portátil: extraia a pasta completa e execute `ZasaBoardBeta.exe`.

### Seus dados

O pacote começa sem contas, cookies ou credenciais do desenvolvedor. Os dados ficam em `%LOCALAPPDATA%/IdleboardBeta/profiles`, conservando o local da Beta 1. A desinstalação preserva os perfis. Não compartilhe essa pasta.

Esta é a distribuição pública do gerenciador. **Não inclui o script externo do `/hunt` nem a base do laboratório PokeIdle-Lab**. O carregador de extensões é código próprio e fica disponível para configuração local. Autenticação e bônus dependem das plataformas; manter uma página aberta não garante benefícios.

## Desenvolvimento

Use Python 3.12 x64 com suporte a Tk:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-runtime.lock
.\.venv\Scripts\python.exe app/main.py
```

O desenvolvimento, a candidata e a edição de uso possuem diretórios de dados separados. Confira [edições](docs/edicoes.md) antes de atualizar a instalação ou compartilhar uma pasta de perfil.

## Estrutura do projeto

| Área | Responsabilidade |
| --- | --- |
| `main.py`, `layout.py` | Interface, cartões e distribuição responsiva |
| `movimento.py`, `rolagem.py` | Transições e navegação da grade |
| `core/browserman.py` | Sessões WebView2 e diretórios persistentes |
| `core/espelho.py`, `core/espelho_scripts.py` | Alinhamento, validação e repetição de cliques |
| `contas_vinculadas.py`, `lives_interface.py` | Contas associadas e plataformas de lives |
| `tests/` | Testes unitários, de interface e de navegador local |
| `tools/` | Congelamento de edições e preparação de distribuições |
| `assets/`, `docs/` | Identidade visual, decisões e histórico |

## Testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Os ensaios desktop/WebView2 exigem Windows interativo e `IDLEBOARD_UI_TESTS=1`; sem essa variável, são explicitamente ignorados. A última suíte completa registrada passou em **86 testes**. Testes sintéticos não substituem login, bônus ou conferência prolongada no jogo real.

## Documentação

- [Diário de desenvolvimento](docs/diario-desenvolvimento.md)
- [Identidade visual](docs/design-zasaboard.md)
- [Alinhamento e espelhamento](docs/espelhamento.md)
- [Perfis e contas associadas](docs/perfis.md)
- [Lives e sessões](docs/lives.md)
- [Verificação da Beta 2](docs/verificacao-beta2.md)
- [Histórico de alterações](CHANGELOG.md)

## Escopo e créditos

A engenharia reversa e o laboratório PokeIdle-Lab são projetos separados. O ZasaBoard fornece a interface de gerenciamento; não representa uma reconstrução completa do servidor do jogo. Hivemind também permanece separado.

A identidade com Shiny Charizard pertence à edição pessoal. Pokémon e Charizard são personagens de terceiros; as referências dos arquivos estão no [registro de design](docs/design-zasaboard.md). Scripts externos do `/hunt`, sessões e diagnósticos pessoais do computador permanecem fora do Git. Este repositório público contém uma exportação do produto; o histórico de desenvolvimento privado permanece separado.
