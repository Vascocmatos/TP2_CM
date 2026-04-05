# Solitário - TP2_85234

Este projeto é uma implementação do clássico jogo Solitário desenvolvida em Python com a framework Flet. Além das mecânicas base do jogo, foram incluídas diversas funcionalidades extra que elevam a qualidade da aplicação, tornando-a mais interativa, personalizável e robusta.

Abaixo encontram-se descritas as funcionalidades extra implementadas, os respetivos motivos de inclusão e as instruções de utilização.

---

## Funcionalidade Extra 1: Sistema de Guardar e Carregar Jogo (Múltiplos Slots)

**Motivos de Inclusão:**
Um jogo de solitário pode prolongar-se por vários minutos e exigir foco. A capacidade de pausar, fechar a aplicação e retomar a sessão mais tarde é uma funcionalidade crucial para a experiência do utilizador, especialmente em cenários móveis ou de sessões curtas. Sem um sistema de gravação, qualquer interrupção resultaria na perda total do progresso, o que gera frustração.

**Descrição Detalhada:**
Foi implementado um sistema de persistência de estado (*state persistence*) robusto e à prova de falhas, que utiliza uma abordagem de armazenamento dupla: suporta-se numa base de dados DuckDB (`duckdb_store.py`) aliada a um ficheiro local em formato JSON (`local_storage.json`). Este sistema arquitetural foi desenhado para suportar até três "slots" de gravação distintos. Isto permite que múltiplos utilizadores partilhem o mesmo dispositivo, ou que um único utilizador mantenha várias experiências de jogo a decorrer em simultâneo. 

Quando o jogador decide guardar o seu progresso através do menu de pausa, o sistema não guarda apenas a pontuação e o tempo; ele serializa o estado exato de todo o tabuleiro. Isto inclui a disposição e ordem rigorosa das cartas nas sete colunas do *tableau*, o estado das *foundations*, e as cartas exatas contidas no *stock* (baralho) e *waste* (lixo), bem como a propriedade de cada carta estar virada para cima ou para baixo. Ao carregar um jogo, a aplicação reconstrói o tabuleiro passo-a-passo, garantindo que o posicionamento visual e as camadas (o *Z-index* no Flet) são repostas na perfeição, sem sobreposições gráficas anormais. O sistema trata também da salvaguarda das opções globais da aplicação de forma transparente.

**Instruções de Utilização:**
1. Durante o jogo, clique no botão "Menu" no canto inferior esquerdo (ou prima a tecla `Escape` no teclado).
2. Para guardar: Selecione "Salvar Jogo" e clique num dos três *slots* disponíveis.
3. Para carregar: No menu principal ou no ecrã de pausa, selecione "Carregar Jogo" e clique num *slot* que contenha uma gravação válida. Pode também apagar gravações através do botão correspondente a cada *slot*.

---

## Funcionalidade Extra 2: Sistema de Dicas Inteligente com Animação e Penalizações

**Motivos de Inclusão:**
O solitário é um jogo de paciência que pode levar a momentos de bloqueio, especialmente para jogadores menos experientes. A inclusão de um sistema de dicas (Hints) torna o jogo mais acessível e educativo. Contudo, para manter a componente de desafio e o aspeto competitivo, foi necessário balancear a ajuda com uma mecânica de risco-recompensa através de penalizações.

**Descrição Detalhada:**
O botão de "Dica" não se limita a ser um mero indicador de sorte; ele é suportado por um algoritmo que varre o estado atual do jogo para calcular a melhor jogada possível. O algoritmo analisa iterativamente as cartas disponíveis no *waste* e todas as cartas visíveis no *tableau*. Em seguida, cruza estas cartas com as regras estritas de colocação, testando primeiro movimentações seguras para as *foundations* e, de seguida, movimentações táticas entre colunas do *tableau*. 

Quando o algoritmo identifica uma jogada legal, ele não a executa automaticamente, pois isso retiraria o controlo ao jogador. Em vez disso, o sistema aciona uma animação visual assíncrona — um efeito *glow* néon azul/ciano que faz a carta sugerida pulsar suavemente durante alguns segundos. Caso não existam movimentos possíveis no tabuleiro, o sistema é inteligente o suficiente para destacar o baralho principal ou o botão de reiniciar o baralho. Para desencorajar o abuso constante do botão de dica (o que tornaria o jogo trivial), introduziu-se um sistema de penalização: cada clique no botão "Dica" adiciona automaticamente 10 pontos à pontuação de penalização do jogador (onde uma pontuação final mais baixa reflete um melhor desempenho, combinada com o tempo de jogo).

**Instruções de Utilização:**
1. Durante a partida, localize o botão "Dica" (representado por um ícone de lâmpada) abaixo do tabuleiro.
2. Ao clicar, repare que o ecrã fará piscar a carta que deve ser movida, ou o local onde deve clicar.
3. Tenha em atenção que o seu contador de "Pontos" sofrerá um incremento de 10 unidades por cada vez que recorrer a esta ajuda.

---

## Funcionalidade Extra 3: Sistema de Áudio Dinâmico e Personalização Visual Temática

**Motivos de Inclusão:**
A estética e a ambiência sonora são essenciais para modernizar um jogo clássico. Dar ao jogador a capacidade de personalizar os elementos visuais cria um sentimento de apropriação do jogo. Ao mesmo tempo, o áudio bem desenhado melhora o *feedback* tátil, tornando o simples ato de virar uma carta numa experiência mais gratificante.

**Descrição Detalhada:**
O jogo foi dotado de um menu de "Opções" abrangente que altera o comportamento global da aplicação em tempo real. A nível visual, implementou-se um sistema de *skins* dinâmicas que permite ao jogador escolher entre múltiplos versos de cartas (por exemplo: "Clássico", "Blasphemous", "Bach" ou "Amarelo"). Assim que a opção é aplicada, o código itera sobre todas as cartas não reveladas no ecrã e altera a sua propriedade `src` para o novo *asset*, sem necessitar de reiniciar a aplicação ou corromper a sessão de jogo ativa.

A nível sonoro, o projeto tira partido do `flet_audio` com uma implementação avançada de canais. Existem efeitos sonoros independentes para o clique em botões de interface e para a movimentação/virar das cartas. O destaque vai para o sistema inteligente da música de fundo (que entra em *loop* dinâmico). De modo a respeitar as restrições dos *browsers* modernos de auto-play, a música só arranca de forma assíncrona na primeira interação real do jogador. Adicionalmente, foi programada uma funcionalidade de *audio muffling* (abafamento sonoro): sempre que o jogador invoca o menu de pausa interativo, o volume da música de fundo é reduzido dinamicamente para 30% da configuração definida, criando uma separação clara entre "estado de jogo" e "estado de menu", sendo restaurado imediatamente ao retomar a partida.

**Instruções de Utilização:**
1. Aceda ao "Menu" e selecione "Opções".
2. Utilize o menu suspenso (Dropdown) "Traseira das cartas" para escolher a temática desejada.
3. Ajuste os controlos deslizantes (*sliders*) independentes para afinar o volume da "Música de Fundo" e dos "Efeitos Sonoros".
4. Clique em "Aplicar" para ver as cartas no tabuleiro atualizarem-se instantaneamente com o novo tema. Repare também na diminuição suave do volume enquanto se encontra neste menu.