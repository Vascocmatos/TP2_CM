# Solitário - TP2_85234

Este trabalho é a criação do jogo Solitário desenvolvida em Python utilizando a framework Flet. O projeto cumpre todos os requisitos obrigatórios e inclui diversas funcionalidades extra que se basearam na melhoria visual do jogo, incluindo visibilidade e performan-se, adicionado mecânicas e particularidades de jogabilidade e Quality of life incluindo sistema de audio.

---

## Funcionalidades Base

**Base**
Foi utilizado como base o tutorial fornecido pelo docente.

O jogo e funcionalidades são alteradas e implementadas a travez de um menu de jogo e menu inicial. Varias das funcionalidades pedidas no guião estão ligadas atravez do menu.

*   **Reiniciar o Jogo:** O botão no menu (`novo jogo`) permite iniciar um jogo do inicio sem ter de sair da app.
*   **Desfazer Jogadas (Undo):** O sistema guarda cada movimento (origem, destino, cartas envolvidas e cartas viradas) num histórico (`self.history`). Ao fazer *undo*, as cartas regressam à origem e as cartas reveladas voltam a ser viradas para baixo.
*   **Salvar e Carregar:** Utiliza um sistema híbrido (`duckdb_store.py` e ficheiro `local_storage.json`) que guarda o estado exato das pilhas, a posição das cartas e o tempo decorrido, repondo visualmente as camadas do Flet no carregamento.
*   **Traseira das Cartas:** Disponível no menu de Opções (Dropdown com 4 escolhas: Clássico, Blasphemous, Bach, Amarelo). As definições sao aplicadas em tempo real.
*   **Pontuação e Cronómetro:** Baseado na fórmula `Pontuação = Tempo + Penalizações`. O relógio é atualizado assincronamente a cada segundo e as ações de *undo* adicionam 5 pontos de penalização (onde menos pontos significa um melhor desempenho).

---

## Funcionalidades Extra

### 1. Sistema de Dicas Inteligente com Animação Visual e Penalização

**Motivos de Inclusão:**
Muitas vezes, durante um jogo, pode haver bloqueios e nao ser claro que opções estão possiveis. Neste caso o botão dica apresenta que possibilidades de jogadas existem.

**Descrição:**
Quando o botão "Dica" (`get_hint`) é precionado. o codigo verifica o estado atual do tabuleiro e procura a melhor jogada legal. O processo obedece a uma hierarquia de prioridades: primeiro, analisa a viabilidade de mover a carta de topo do *waste* ou do *tableau* para as *foundations*; de seguida, testa movimentos legais entre as várias colunas do *tableau* (evitando *loops* infinitos de reis a moverem-se entre colunas vazias). 

Quando o algoritmo encontra uma jogada válida, aciona um método de animação assíncrono (`show_glow`). Esta função manipula a propriedade `shadow` do Flet, criando um efeito néon azul/ciano que faz a carta sugerida piscar de forma suave (*ease-in-out*) três vezes, sem bloquear a *thread* principal do jogo. Se não houver jogadas no tabuleiro, o sistema destaca o baralho ou o botão de reiniciar o baralho, orientando o jogador. A cada vez que o botão é precionado é aplicado uma penalização de 10 pontos ao *score* do jogador.

---

### 2. Sistema de Áudio

**Motivos de Inclusão:**
Um jogo com audio integrado é sempre mais dinâmico e interativo. Para isso foi adicionado som ao clicar em botões, ao interagir com cartas e uma musica de fundo.

**Descrição:**
O código utiliza o módulo `flet_audio` (`fta.Audio`), dividindo os sons em três canais independentes: Música de Fundo (BGM), Efeitos das Cartas (SFX_Card) e Efeitos de Interface (SFX_Btn).
Numa tentativa de contornar bloqueios dos browsers e dispositivos audio, foi implementado um delay de espera para que o audio so fosse tocado apos a interação do jogador. Infelistmente apenas funciona quando é corrido localmente no PC.

O audio tem como caractristica o efeito de abafamento de áudio. Quando o jogador prime o botão de menu (ou a tecla `Escape`) durante uma partida, o jogo entra em pausa e o código chama `_muffle_music_volume()`. Esta função interceta o volume global definido pelo utilizador e reduz a música dinamicamente para 30% da sua capacidade dando a ilusão de abafo.

É possivel alterar o volume de audio atravez das opções nos menus.

---

### 3. Menu

**Motivos de Inclusão:**
Para facilitar a manipulação de opções e para facilitar a interação com as varias funcionalidades implementadas foi adicionado um menu. Este contem todas as funcionalidades nao relacionadas com o jogo em si.

**Descrição:**
Foi criada a classe `MenuOverlay` no ficheiro `menu.py`. Esta interface flutua sobre a classe principal do jogo através do uso de `ft.Stack`. Possui um fundo escuro, contendo um painel central. O menu gere o seu próprio estado (`mode`), permitindo alternar de forma fluida entre Ecrã Inicial, Pausa, Carregar/Gravar Jogo, Opções e Tutorial, reciclando a mesma estrutura visual. O módulo de Tutorial, em específico, explica as regras de pontuação do jogo.

Adicionalmente, foi colocado uma funcionalidade de `on_resize` da janela (`main.py`). Esta parte calcula fatores de escala virtuais baseados no rácio de resolução interna. Ao detetar uma alteração no tamanho da janela , o código aplica um `ft.Scale` exato e calcula as sobras de ecrã horizontais para centrar a `Stack` do jogo ao meio do monitor. Isto garante que o jogo nunca sofre recortes indesejados e que a *hitbox* das cartas permanece fidedigna.