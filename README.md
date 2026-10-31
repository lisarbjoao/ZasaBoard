# Idleboard Beta

Interface desktop para gerenciar múltiplas sessões de jogos, com cartões ajustáveis, perfis persistentes e contas vinculadas. Beta pública de avaliação para Windows 10/11 de 64 bits.

Esta distribuição usa o checkpoint de uso aprovado `85f5036`, preservando o código dos cartões e perfis. As abas disponíveis são **Início** e **Perfis**. Não inclui o laboratório experimental, ferramentas em desenvolvimento, extensão /hunt de terceiros, cadastros ou logins do desenvolvedor.

## Instalar

1. Abra a [página desta beta](https://github.com/lisarbjoao/Idleboard-Beta/releases/tag/v0.1.0-beta.1).
2. Baixe o arquivo terminado em **Setup.exe** e execute-o.
3. Clique em **Instalar**. Depois abra **Idleboard Beta** pelo atalho da área de trabalho.
4. Crie/edite seus próprios perfis e faça login nas páginas dos cartões.

Não precisa instalar Python nem executar como administrador. O Windows precisa ter **Microsoft Edge WebView2 Runtime**; em caso de ausência, use a [página oficial da Microsoft](https://developer.microsoft.com/microsoft-edge/webview2/). O instalador desta beta não tem assinatura digital; o Windows pode mostrar uma identificação de editor desconhecido.

Alternativa portátil: baixe o ZIP, extraia a pasta inteira e execute `IdleboardBeta.exe`. Não envie ou mova apenas esse executável: ele depende dos arquivos que o acompanham. O instalador já leva esses arquivos dentro dele.

## Dados e remoção

Cada usuário começa sem cadastros ou sessões do desenvolvedor. Metadados e dados de navegação ficam em `%LOCALAPPDATA%\IdleboardBeta\profiles`. A aplicação não envia diagnósticos ou credenciais ao desenvolvedor; os sites acessados mantêm suas próprias conexões e políticas.

Para remover, feche a beta e use **Configurações do Windows → Aplicativos → Idleboard Beta → Desinstalar**, ou o atalho Desinstalar no menu Iniciar. Os perfis locais são preservados. Não compartilhe essa pasta: ela pode conter sessões autenticadas.

## Testar e relatar

Confira criação, renomeação e exclusão de perfis, persistência após reabrir, abertura e recarga das páginas, modos da grade, ocultação/foco e contas vinculadas por URL. O layout de uso foi aprovado pelo autor; desempenho prolongado em outros computadores ainda precisa de avaliação.

Relate problemas em [Issues](https://github.com/lisarbjoao/Idleboard-Beta/issues), informando versão, versão do Windows, quantidade de sessões e passos para reproduzir. Não envie senhas, cookies, pastas de perfil ou capturas com dados pessoais. Não há garantia de bônus de lives ou de compatibilidade permanente com sites externos.

## Código e documentação

- [Estado da beta](docs/estado.md)
- [Diário de desenvolvimento](docs/diario.md)
- [Decisões de distribuição](docs/distribuicao.md)
- [Compilação](docs/compilacao.md)
- [Changelog](CHANGELOG.md)
- [Dependências e licenças](THIRD-PARTY-NOTICES.md)

O código próprio está publicado para inspeção da beta. Ainda não foi definida uma licença de redistribuição comercial. As dependências conservam suas licenças próprias. Este repositório não contém o histórico privado de desenvolvimento ou a investigação do PokeIdle.
