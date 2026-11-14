# Constituição da documentação do projeto
Versão 1.0 · 13/11/2026 · orientação solicitada pelo proprietário para continuidade dos projetos.

## Finalidade e hierarquia
Manter documentação útil para desenvolver, revisar, operar e estudar o projeto. O pedido atual do proprietário e as permissões do ambiente prevalecem; preservar decisões e autorizações existentes.
Esta constituição não certifica segurança, qualidade ou conclusão. Não cria uma aprovação que não ocorreu. Adapte exigências ao tamanho e ao risco: um protótipo não precisa de documentação de uma plataforma corporativa.
A base geral de consulta está no [guia central](https://github.com/lisarbjoao/Brumas/blob/main/Docs/Geral/GUIA-GERAL-DE-DESENVOLVIMENTO.md). Cada projeto tem sua cópia local e seu mapa; atualizar o guia central não altera automaticamente as cópias.

## Entrada e anamnese
Ao iniciar ou retomar: ler índice, plano/estado, arquitetura e instruções locais; procurar respostas antes de perguntar. Em projeto novo, esclarecer problema, usuários, fluxo, entrada/saída, sucesso, escopo, ambiente, dados, integrações, restrições e forma de entrega.
Perguntar progressivamente o que afeta a próxima decisão; não impor questionário completo quando o contexto já existe. Registrar premissas e dúvidas. Não escolher tecnologia antes de compreender a necessidade.

## Conteúdo mínimo, sem duplicação
1. Objetivo, usuários, estado atual, escopo e exclusões.
2. Requisitos/fluxos e critérios de aceite; plano com pendências e próximo passo.
3. Guia de arquitetura com módulos reais, caminho dos dados, persistência, fronteiras, decisões e trilha de leitura.
4. Ambiente, dependências, instalação, comandos, convenções e versionamento.
5. Dados, acessos, segurança, privacidade, retenção, backup e recuperação, conforme aplicável.
6. Estratégia de testes, evidências, falhas conhecidas e limitações.
7. Decisões relevantes, histórico, referência da versão e continuidade.
8. Entrega/operação: artefato, configuração, atualização, recuperação e aceite humano.

Esses assuntos podem compartilhar arquivos. PLANO-DOCUMENTACAO.md aponta a fonte canônica e as lacunas; não criar páginas vazias ou textos genéricos para marcar itens como completos. Identificar explicitamente o que não se aplica e por quê.

## Desenvolvimento e segurança
Trabalhar em incrementos verificáveis, preservar autoria e alterações alheias, justificar dependências e manter comandos reproduzíveis. Evitar mudanças fora de escopo e complexidade sem necessidade.
Documentar dados sensíveis e fronteiras de confiança, menor privilégio, validação de entrada/saída, segredos fora do Git e riscos residuais. Usar massa sintética em exemplos. Não registrar credenciais, cookies, tokens, relatórios pessoais/corporativos ou backup privado em texto público.
Não remover proteções, enfraquecer testes ou inventar evidências para declarar conformidade. Revisão documental não substitui teste de integração, auditoria de segurança ou restauração.

## Evidências e versionamento
Distinguir: proposto, decidido, implementado, testado em simulação, testado no ambiente real e aceito. Registrar data, versão/commit, ambiente, comando/cenário, resultado e limites.
Estado atual tem um ponto de entrada claro. Preservar histórico com rótulo de versão; conflitos entre documentos devem ser identificados e reconciliados quando houver evidência, sem apagar registros.
Falha conhecida tem identificação, reprodução, esperado/observado, impacto conhecido, hipótese, tratamento e reteste. Não atribuir causa definitiva sem validação.

## Conhecimento do proprietário e apresentação
A cada marco, explicar o que mudou, onde fica no código, motivo, verificação e pendências. Manter roteiro de leitura de 20–30 minutos e um exemplo que percorra entrada até saída.
O proprietário deve conseguir explicar fonte de verdade, responsabilidades, uma falha/recuperação e limites do resultado. Não substituir participação por um resumo para decorar. Registrar dúvidas e decisões de estudo sem atribuir testes não realizados.

## Fechamento e manutenção
Antes de entregar: atualizar índice, guia/estado afetados, decisões, evidências e pendências; conferir vínculos e publicar apenas no destino autorizado. Informar o que ficou bloqueado e o que depende do usuário.
Em mudança pequena, uma atualização curta basta. Em mudança de arquitetura/integração/dados, revisar o mapa, os riscos e os testes. Novos documentos têm lugar e responsabilidade definidos no plano.
Para um projeto novo, copiar esta constituição, adaptar o mapa abaixo, criar um índice/estado mínimo e realizar a anamnese do guia geral. Não copiar fatos, testes ou escolhas técnicas de outro projeto.

## Mapa desta cópia
Projeto: ZasaBoard. Escopo: Aplicativo desktop distribuído para sessões de jogos.
Entrada: [README.md](README.md). Arquitetura: [docs/arquitetura.md](docs/arquitetura.md). Inventário e lacunas: [PLANO-DOCUMENTACAO.md](PLANO-DOCUMENTACAO.md).
