import asyncio



SOLITAIRE_WIDTH = 1000
SOLITAIRE_HEIGHT = 500
CARD_HEIGHT = 100

import random
import time

import flet as ft
from card import Card, CARD_OFFSET
from slot import Slot


class Suite:
    def __init__(self, suite_name, suite_color):
        self.name = suite_name
        self.color = suite_color


class Rank:
    def __init__(self, card_name, card_value):
        self.name = card_name
        self.value = card_value


class Solitaire(ft.Stack):
    def __init__(self, card_back="/images/card_back.png", play_card_sound=None, play_btn_sound=None, on_pause=None):
        super().__init__()
        self.controls = []
        self.width = SOLITAIRE_WIDTH
        self.height = SOLITAIRE_HEIGHT
        self.history = []
        self.suppress_history = False
        self.card_back = card_back

        self.on_pause = on_pause  # Guardar a função de pausa

        # ====== SCORE / TIMER ======
        self.start_time = time.time()
        self.undo_penalty = 0

        self.score_text = ft.Text(
            "Tempo: 00:00  |  Pontos: 0",
            size=16,
            weight=ft.FontWeight.BOLD,
        )
        self.score_box = ft.Container(
            content=self.score_text,
            left=SOLITAIRE_WIDTH / 2 - 120,
            top=SOLITAIRE_HEIGHT - 30,
        )

        self._timer_task_running = False

        
        self.play_card_sound = play_card_sound
        self.play_btn_sound = play_btn_sound

    def did_mount(self):
        self.create_card_deck()
        self.create_slots()
        self.deal_cards()

        # adiciona score ao stack
        self.controls.append(self.score_box)

        # start timer loop (sem ft.Timer)
        self._timer_task_running = True
        self.page.run_task(self._timer_loop)

    def _format_time(self, seconds):
        m = seconds // 60
        s = seconds % 60
        return f"{m:02d}:{s:02d}"

    def _update_score_text(self):
        elapsed = int(time.time() - self.start_time)
        score = elapsed + self.undo_penalty
        self.score_text.value = f"Tempo: {self._format_time(elapsed)}  |  Pontos: {score}"
        
        # Tenta atualizar o texto. Se o Flet disser que ainda não está no ecrã, ignora em silêncio.
        try:
            self.score_text.update()
        except Exception:
            pass

    def _on_timer_tick(self, e):
        self._update_score_text()

    def _reset_score_timer(self):
        self.start_time = time.time()
        self.undo_penalty = 0
        self._update_score_text()

    def create_card_deck(self):
        suites = [
            Suite("hearts", "RED"),
            Suite("diamonds", "RED"),
            Suite("clubs", "BLACK"),
            Suite("spades", "BLACK"),
        ]
        ranks = [
            Rank("Ace", 1), Rank("2", 2), Rank("3", 3), Rank("4", 4),
            Rank("5", 5), Rank("6", 6), Rank("7", 7), Rank("8", 8),
            Rank("9", 9), Rank("10", 10), Rank("Jack", 11),
            Rank("Queen", 12), Rank("King", 13),
        ]
        self.cards = []
        for suite in suites:
            for rank in ranks:
                self.cards.append(Card(solitaire=self, suite=suite, rank=rank))

    def create_slots(self):
        self.stock = Slot(solitaire=self, top=0, left=0, border=ft.Border.all(1))
        self.waste = Slot(solitaire=self, top=0, left=100, border=None)

        self.foundations = []
        x = 300
        for i in range(4):
            self.foundations.append(
                Slot(solitaire=self, top=0, left=x, border=ft.Border.all(1, "outline"))
            )
            x += 100

        self.tableau = []
        x = 0
        for i in range(7):
            self.tableau.append(Slot(solitaire=self, top=150, left=x, border=None))
            x += 100

        self.controls.extend([self.stock, self.waste])
        self.controls.extend(self.foundations)
        self.controls.extend(self.tableau)

        self.reset_btn = ft.ElevatedButton(
            "Reset",
            left=self.waste.left,
            top=self.waste.top + CARD_HEIGHT + 10,
            on_click=self.on_reset_click,
        )
        self.controls.append(self.reset_btn)

        self.undo_btn = ft.ElevatedButton(
            "Undo",
            left=self.reset_btn.left + 80,
            top=self.reset_btn.top,
            on_click=lambda e: self.undo(),
        )
        self.controls.append(self.undo_btn)

        # --- NOVO: BOTÃO DE DICA ---
        self.hint_btn = ft.ElevatedButton(
            "Dica",
            icon="lightbulb_outline", # <-- Alterar apenas esta linha (usar string)
            left=self.undo_btn.left + 80,
            top=self.reset_btn.top,
            on_click=self.get_hint,
        )
        self.controls.append(self.hint_btn)

        # ADICIONAR BOTÃO DE MENU PARA TELEMÓVEL
        self.pause_btn = ft.ElevatedButton(
            "Menu",
            icon="menu",
            left=10,
            top=SOLITAIRE_HEIGHT - 35,
            on_click=lambda e: self.on_pause() if self.on_pause else None,
        )
        self.controls.append(self.pause_btn)

        self.update()

    def on_reset_click(self, e):
        if self.play_btn_sound:
            self.play_btn_sound()
        if len(self.stock.pile) == 0:
            self.restart_stock()

    def deal_cards(self):
        self.suppress_history = True
        random.shuffle(self.cards)
        self.controls.extend(self.cards)
        remaining_cards = self.cards.copy()

        first_slot = 0
        while first_slot < len(self.tableau):
            for slot in self.tableau[first_slot:]:
                top_card = remaining_cards[0]
                top_card.place(slot)
                remaining_cards.remove(top_card)
            first_slot += 1

        for card in remaining_cards:
            card.place(self.stock)

        self.update()
        for slot in self.tableau:
            slot.get_top_card().turn_face_up()

        self.suppress_history = False
        self.update()

    def set_card_back(self, card_back):
        self.card_back = card_back
        for card in self.cards:
            if not card.face_up:
                card.content.content.src = self.card_back
        self.update()

    def check_foundations_rules(self, card, slot):
        top_card = slot.get_top_card()
        if top_card is not None:
            return (
                card.suite.name == top_card.suite.name
                and card.rank.value - top_card.rank.value == 1
            )
        else:
            return card.rank.name == "Ace"

    def undo(self):
        if self.play_btn_sound:
            self.play_btn_sound()
            
        if not self.history:
            return
        move = self.history.pop()

        # penalização
        self.undo_penalty += 5
        self._update_score_text()
        
        if self.play_card_sound:
            self.play_card_sound()

        for card in move["cards"]:
            if card in move["to"].pile:
                move["to"].pile.remove(card)
            card.slot = move["from"]
            move["from"].pile.append(card)
            
            # --- ADICIONAR ESTAS 3 LINHAS PARA CORRIGIR AS CAMADAS ---
            # Remove a carta da lista e volta a adicioná-la no fim
            # para garantir que fica por cima das outras visualmente
            if card in self.controls:
                self.controls.remove(card)
                self.controls.append(card)

        for card in move["cards"]:
            if move["from"] in self.tableau:
                card.top = move["from"].top + move["from"].pile.index(card) * CARD_OFFSET
            else:
                card.top = move["from"].top
            card.left = move["from"].left

        for card in move.get("flipped_cards", []):
            card.turn_face_down()

        self.update()

    def check_tableau_rules(self, card, slot):
        top_card = slot.get_top_card()
        if top_card is not None:
            return (
                card.suite.color != top_card.suite.color
                and top_card.rank.value - card.rank.value == 1
                and top_card.face_up
            )
        else:
            return card.rank.name == "King"

    def restart_stock(self):
        self.suppress_history = True
        if self.play_card_sound:
            self.play_card_sound()
        while len(self.waste.pile) > 0:
            card = self.waste.get_top_card()
            card.turn_face_down()
            card.move_on_top()
            card.place(self.stock)
        self.suppress_history = False

    def check_win(self):
        cards_num = 0
        for slot in self.foundations:
            cards_num += len(slot.pile)
        if cards_num == 52:
            return True
        return False

    def winning_sequence(self):
        for slot in self.foundations:
            for card in slot.pile:
                card.animate_position = 2000
                card.move_on_top()
                card.top = random.randint(0, SOLITAIRE_HEIGHT)
                card.left = random.randint(0, SOLITAIRE_WIDTH)
                self.update()
        self.controls.append(
            ft.AlertDialog(title=ft.Text("Parabens! Ganhaste!"), open=True)
        )

    def get_state(self):
        def card_to_dict(card):
            return {
                "suite": card.suite.name,
                "rank": card.rank.name,
                "face_up": card.face_up,
            }
        return {
            "tableau": [[card_to_dict(c) for c in slot.pile] for slot in self.tableau],
            "foundations": [
                [card_to_dict(c) for c in slot.pile] for slot in self.foundations
            ],
            "stock": [card_to_dict(c) for c in self.stock.pile],
            "waste": [card_to_dict(c) for c in self.waste.pile],
        }

    def load_state(self, state):
        self.suppress_history = True
        self.history.clear()
        
        # 1. Esvazia todas as pilhas atuais
        for slot in [self.stock, self.waste] + self.foundations + self.tableau:
            slot.pile.clear()

        # 2. Cria mapa das cartas atuais para as podermos encontrar
        card_map = {}
        for c in self.cards:
            c.slot = None
            card_map[(c.suite.name, c.rank.name)] = c

        # 3. Função auxiliar para colocar cartas diretamente nos seus lugares
        def place_list(cards_data, slot):
            for i, card_data in enumerate(cards_data):
                card = card_map[(card_data["suite"], card_data["rank"])]
                card.slot = slot
                slot.pile.append(card)
                
                # Coloca a carta nas coordenadas corretas
                if slot in self.tableau:
                    card.top = slot.top + i * CARD_OFFSET
                else:
                    card.top = slot.top
                card.left = slot.left
                
                # Vira a face para cima ou baixo consoante o save
                if card_data["face_up"]:
                    card.turn_face_up()
                else:
                    card.turn_face_down()

        # 4. Distribui os dados guardados para cada secção do jogo
        for slot, pile_data in zip(self.tableau, state["tableau"]):
            place_list(pile_data, slot)
        for slot, pile_data in zip(self.foundations, state["foundations"]):
            place_list(pile_data, slot)
        place_list(state["stock"], self.stock)
        place_list(state["waste"], self.waste)

        # 5. Corrige a ordem das camadas (Z-index)
        # Retira todas as cartas da lista e volta a adicioná-las na ordem certa
        for card in self.cards:
            if card in self.controls:
                self.controls.remove(card)
                
        for slot in [self.stock, self.waste] + self.foundations + self.tableau:
            for card in slot.pile:
                self.controls.append(card)

        # 6. Repõe o tempo e atualiza a interface
        self._reset_score_timer()
        self.suppress_history = False
        self.update()



    async def _timer_loop(self):
        while self._timer_task_running:
            self._update_score_text()
            await asyncio.sleep(1)

    def will_unmount(self):
        self._timer_task_running = False



    def get_hint(self, e):
        if self.play_btn_sound:
            self.play_btn_sound()


        # --- NOVO: PENALIZAÇÃO POR USAR A DICA ---
        # Adiciona 10 pontos (podes mudar para 5 ou 15, como preferires)
        self.undo_penalty += 10 
        self._update_score_text()

        movable_piles = []

        # 1. Procurar cartas no Lixo (Waste)
        if len(self.waste.pile) > 0:
            movable_piles.append([self.waste.get_top_card()])

        # 2. Procurar cartas viradas para cima no Tabuleiro
        for slot in self.tableau:
            for i, card in enumerate(slot.pile):
                if card.face_up:
                    movable_piles.append(slot.pile[i:])

        # 3. Testar todas as cartas possíveis contra todas as casas possíveis
        for pile in movable_piles:
            base_card = pile[0]

            # Tenta mover para as Fundações (só funciona se for uma carta isolada)
            if len(pile) == 1:
                for f_slot in self.foundations:
                    if self.check_foundations_rules(base_card, f_slot):
                        self.show_glow(base_card)
                        return

            # Tenta mover para outra coluna do Tabuleiro
            for t_slot in self.tableau:
                if base_card.slot == t_slot:
                    continue  # Ignora a própria coluna
                
                # Evita recomendar mover um Rei que já está numa casa vazia para outra casa vazia (loop inútil)
                if base_card.rank.name == "King" and base_card.slot in self.tableau and len(base_card.slot.pile) == len(pile):
                    continue

                if self.check_tableau_rules(base_card, t_slot):
                    self.show_glow(base_card)
                    return

        # 4. Se não houver jogadas no tabuleiro, sugere tirar uma carta do baralho!
        if len(self.stock.pile) > 0:
            self.show_glow(self.stock.get_top_card())
        elif len(self.waste.pile) > 0:
            # Se o baralho estiver vazio mas houver lixo, sugere fazer Reset
            self.show_glow(self.reset_btn)

    def show_glow(self, target):
        """ Cria um efeito de pulsar (glow) no alvo (carta ou botão) de forma assíncrona """
        async def animate_glow():
            try:
                # Configura a animação de transição (suave)
                if hasattr(target, "content"):
                    target_container = target.content
                else:
                    target_container = target # Caso seja um botão (reset_btn)

                target_container.animate_shadow = ft.Animation(400, ft.AnimationCurve.EASE_IN_OUT)
                
                # Faz piscar 3 vezes com um azul/ciano "neon"
                for _ in range(3):
                    target_container.shadow = ft.BoxShadow(
                        spread_radius=3, blur_radius=15, color=ft.Colors.CYAN_ACCENT_400
                    )
                    target_container.update()  # <-- Atualiza SÓ o contentor alvo!
                    await asyncio.sleep(0.4)
                    
                    target_container.shadow = None
                    target_container.update()  # <-- Atualiza SÓ o contentor alvo!
                    await asyncio.sleep(0.4)
            except Exception as e:
                print(f"Erro na animação: {e}")

        # Corre a animação em background sem bloquear o jogo
        self.page.run_task(animate_glow)