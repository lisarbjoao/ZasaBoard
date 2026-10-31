# Controle espelhado de cliques

## Uso

No Início, abra pelo menos dois cartões visíveis do mesmo jogo, deixe-os na mesma tela e clique em **Espelhar**. O aplicativo iguala a área de exibição e o zoom, usando o menor tamanho disponível entre os participantes. Cartões maiores podem ficar com margem durante o espelhamento. Clique em **Parar** ou pressione **Esc** para desligar e restaurar a apresentação normal.

O grupo fica congelado na ativação. Não inclui lives, contas vinculadas, cartões fechados ou ocultados. Páginas ainda carregando ou fora da mesma origem não podem participar. O estado não é salvo: reiniciar o aplicativo começa com espelhamento desligado.

## Contrato

- Repete clique simples esquerdo sem modificadores, a partir de qualquer participante, nas mesmas coordenadas CSS.
- Não replica teclado, textos, senhas, colagem, arraste, roda do mouse ou clique em iframe. Duplo clique suspende o modo em vez de duplicar ações indevidamente.
- Confere viewport, escala, posição da página, rota (incluindo consulta/fragmento) e assinatura do alvo antes de enviar e novamente junto do clique. Controles editáveis e formulários de senha são excluídos também no destino.
- Só existe uma rodada em andamento. Não há fila, repetição automática ou tentativa de refazer uma ação após erro.
- Mudança de navegação, tamanho, visibilidade, grupo ou sessão, alvo incompatível, resposta inválida ou timeout suspende e exige nova ativação.

Mesma resolução e zoom não tornam os estados das contas iguais. Modais, conteúdo, rolagem interna e canvas podem divergir. A comparação do alvo reduz erros, mas não prova equivalência do estado do jogo. Ações já realizadas não são desfeitas e não há transação entre contas. Alguns sites exigem eventos nativos confiáveis e podem não responder aos eventos DOM replicados.

## Limites de segurança e arquitetura

Não há hook global de mouse nem captura de teclado. O listener da página aceita somente eventos manuais confiáveis para produzir notificações; os eventos sintéticos nos destinos não voltam para o grupo. A ponte IPC só fica autorizada no origin exato do jogo enquanto o modo está ativo, sem RPC exposto. Payloads são limitados a 2 KiB, validados por campos, coordenadas, token efêmero e sequência. Não há leitura de cookies, valores de campos ou envio de credenciais.

O token separa ativações e bloqueia mensagens antigas; ele não transforma a página em uma autoridade segura contra comprometimento. Uma página autorizada da mesma origem pode tentar usar a ponte enquanto o usuário permite o modo. O único comando admitido é o protocolo limitado de clique/parada para o grupo escolhido. Ao desligar, a política é revogada antes da limpeza e restauração.

A navegação invalida estado e geração imediatamente, mas o callback nativo não chama Tk/WebView. A limpeza é drenada no evento de carregamento, fora desse callback. O primeiro ensaio nativo encontrou uma falha fatal de reentrância do runtime ao tentar limpar ali; a correção é coberta por teste de ausência de chamadas Tk no invalidator e por recarga real em fixture isolada.

## Evidências

Testes sintéticos cobrem protocolo, origem, coordenadas, descarte de callbacks antigos, filtros de eventos e bloqueio por alvo/viewport diferente. O teste WebView2 local confere zoom, entrega nos dois sentidos e revogação na recarga. Um teste visual separado usou clique físico pela automação de UI: o contador da página fonte passou a 1 e o da outra página também a 1, sem loop. Nenhuma conta real foi usada nesses ensaios. Compatibilidade e ações concretas no jogo continuam para conferência.


## Alinhar — Beta 2 revisão 6

O botão Alinhar fica ao lado de Espelhar. Ajusta área e zoom dos cartões visíveis abertos para o menor tamanho comum e verifica os viewports, sem instalar captura ou autorizar IPC. Não replica cliques nem navega contas. O estado é temporário; sair da tela, redimensionar, mudar a grade ou encerrar uma sessão desfaz o alinhamento e restaura as medidas anteriores. Espelhar pode ser acionado depois e repete a verificação antes de autorizar eventos. Mesma apresentação não iguala modais, rotas ou estado das contas. O teste WebView2 verifica alinhamento sem listener/ponte e a posterior ativação do espelhamento. Suíte completa: 82 testes aprovados.


## Rolagem do mouse — revisão 8

Com Espelhar ativo, o evento manual da roda identifica a área rolável sob o cursor e replica sua posição absoluta, incluindo rolagem horizontal. Ctrl/Alt/Shift/Meta não são replicados. Movimentos são agrupados após 80 ms; em uma rodada ocupada permanece apenas o movimento mais recente. O destino deve possuir o mesmo caminho de painel, viewport e rota e comportar a posição pedida. Divergência pausa; não há repetição de cliques ou mensagens de chat. A atuação é no DOM de páginas acessíveis, sem gestos de zoom ou controles próprios de canvas. O teste nativo confere a posição CSS real do painel, que pode ser fracionária sob zoom.

A revisão 9 observa qual ancestral realmente mudou com a roda. Se mais de um painel muda no mesmo gesto, pausa por ambiguidade. O destino é resolvido pela assinatura desse ancestral, inclusive quando o painel interno está no limite. Após aplicar, confere a posição duas vezes com intervalo de 80 ms e tolerância de 1 pixel CSS; scroll-snap divergente suspende o modo. Esses casos têm testes JavaScript específicos e revisão adicional.
