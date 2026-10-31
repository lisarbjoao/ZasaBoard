# Perfis, cartões e contas vinculadas

Atualizado em 2026-10-29.

## Cadastro e sincronização

Perfis e cartões usam os mesmos objetos de cadastro, identificados de forma estável. A aba Perfis permite criar, editar, abrir e excluir. Os nomes são salvos pelo botão Salvar nome, Enter, saída do campo ou navegação para outra aba. Ao fechar o app, edições pendentes também são concluídas; uma falha de gravação é apresentada e não é tratada como sucesso.

Dois cliques no título do cartão abrem a renomeação. O texto completo fica no cadastro; o cabeçalho pode abreviar nomes longos. A edição por duplo clique usa diálogo próprio com Salvar/Cancelar e grava imediatamente o cadastro; o título usa a largura calculada do cartão, e não uma medida transitória do rótulo oculto. A correção desta etapa ignora dimensões mínimas de títulos em telas ocultas e recalcula o texto quando o cartão volta a aparecer. A tela inicial atualiza os cartões ao retornar da aba Perfis.

Criar um perfil por + Perfil ou + Conta salva seu cadastro, abre Início, mostra o cartão e inicia seu navegador isolado. Não inicia automaticamente todas as contas existentes. Os demais cartões são preservados ao adicionar ou excluir um perfil; sua identidade não depende da posição na lista.

Excluir perfil abre uma confirmação com a opção Apagar também os dados salvos deste perfil, desmarcada por padrão. Sem marcar, remove o cadastro/cartão e fecha as sessões, preservando os dados locais. Marcando, também apaga permanentemente a pasta local do perfil, incluindo cookies, logins, cache e os diretórios das contas vinculadas. Isso não exclui contas nos serviços. As sessões são fechadas antes da limpeza. Se arquivos permanecerem bloqueados após tentativas limitadas, o perfil volta à lista e a falha é informada; arquivos já removidos não podem ser restaurados. A limpeza valida o caminho absoluto, limita-se ao perfil escolhido e recusa atalhos ou junções. Dados pessoais continuam excluídos do Git.

## Contas vinculadas

O botão Contas no cartão e Contas vinculadas na lista de Perfis abrem o mesmo gerenciador do perfil selecionado. Colar a URL HTTPS da plataforma e clicar em Adicionar cria o vínculo imediatamente e abre uma janela de navegador do próprio Idleboard para o login manual. URLs sem esquema recebem https://; endereços com usuário/senha embutidos ou esquemas inseguros são recusados. Abrir sessão reutiliza uma janela já aberta desse vínculo. Fechar o gerenciador não fecha essas janelas. Desvincular remove o vínculo e fecha sua janela, mantendo os dados locais do navegador.

O vínculo guarda id, serviço, nome de referência, URL quando informada e a confirmação manual. O botão ✓ no rodapé salva a indicação Confirmado por você e fecha a janela preservando a sessão. Essa indicação registra a confirmação do usuário, sem detectar autenticação ou garantir validade futura do login. Fechar pelo × deixa o vínculo pendente se ainda não foi confirmado. Falha ao salvar mantém a janela aberta e restaura a indicação anterior. Não há campos de senha, leitura de senhas pelo Manager ou cofre de credenciais implementado. O login persistente depende dos cookies e armazenamento do navegador e das regras do serviço, podendo expirar. O cadastro não comprova que uma conta está autenticada ou recebendo bônus.

Estrutura local, excluída do Git:

- `data/profiles/catalogo.json`: id, personagem, visibilidade e vínculos.
- `data/profiles/<jogo>/<perfil-id>/`: navegador do jogo.
- `data/profiles/<jogo>/<perfil-id>/vinculos/<vinculo-id>/`: navegador de cada conta vinculada.

O primeiro perfil existente conserva o id `prova-01`; renomear não troca diretórios. Perfis antigos sem vínculos são lidos como lista vazia, preservando nomes, identificadores e visibilidade. Objetos de janelas, funções e estados do navegador não entram no JSON. A gravação continua atômica.

## Limites deste incremento

Esta etapa entrega associação e janelas de login por conta. Multitwitch, composição de lives dentro dos cartões, roteamento de áudio e integração automática de bônus continuam futuros. Login real de Twitch/Kick ainda exige conferência manual. Pop-ups e permissões continuam bloqueados pela política do navegador; fluxos de autenticação que dependam deles podem não funcionar. Não há garantia de compatibilidade com desafios dos serviços.

Endereços oficiais usados para abrir as sessões: https://www.twitch.tv/login e https://kick.com/ . Não copiar cookies entre contas ou alterar identificadores de navegador para contornar desafios.

## Verificação

`python -m unittest discover -s tests` executa testes de dados e controles. No Windows com desktop Tk disponível, usar `$env:IDLEBOARD_UI_TESTS='1'` antes do mesmo comando para incluir o teste funcional da interface.

Nesta etapa passaram 12 testes, incluindo o fluxo completo dos quatro nomes, exclusão com preservação dos outros cartões, criação com abertura automática e adição/desvinculação de conta. Uma página local com dados sintéticos validou duas sessões vinculadas simultâneas, isolamento, reabertura persistente e fechamento do gerenciador sem interromper as sessões. Outro teste local revalidou recarga, zoom, foco, ocultação e persistência do navegador do jogo. Esses testes não medem a latência do mercado no jogo real, que permanece em investigação.

## Exclusão pelo cartão e persistência entre processos

A lixeira do rodapé e Excluir perfil na lista usam a mesma confirmação, com a mesma escolha sobre apagar os dados locais. Excluir pelo cartão mantém Início aberto. O controle antigo de apenas fechar o navegador não deve ser apresentado como exclusão.

A sessão de cada cartão é persistida automaticamente pelo navegador no diretório do id daquele perfil. Não é necessário salvar a senha no cadastro. Teste com página local e cookies sintéticos confirmou escrita em um processo, encerramento completo e recuperação em outro processo, mantendo o mesmo id do catálogo. A validade do login real depende das regras e da expiração da sessão no serviço; nome do personagem continua manual.
