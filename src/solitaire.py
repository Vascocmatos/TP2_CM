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

        # ADICIONAR BOTÃO DE MENU PARA TELEMÓVEL
        self.pause_btn = ft.ElevatedButton(
            "Menu",
            icon="menu",  # <--- MUDAR AQUI: Usar apenas a palavra "menu" entre aspas
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
        self.controls.clear()
        self.history = []
        self.create_card_deck()
        self.create_slots()
        self.controls.extend(self.cards)

        # reset timer/score
        self._reset_score_timer()
        self.controls.extend(self.cards) 

        card_map = {}
        for c in self.cards:
            card_map[(c.suite.name, c.rank.name)] = c

        def place_list(cards, slot):
            for card_data in cards:
                card = card_map[(card_data["suite"], card_data["rank"])]
                card.place(slot)
                if card_data["face_up"]:
                    card.turn_face_up()
                else:
                    card.turn_face_down()

        for slot, pile_data in zip(self.tableau, state["tableau"]):
            place_list(pile_data, slot)
        for slot, pile_data in zip(self.foundations, state["foundations"]):
            place_list(pile_data, slot)
        place_list(state["stock"], self.stock)
        place_list(state["waste"], self.waste)

        for card in list(self.cards):
            if card in self.controls:
                self.controls.remove(card)
        for slot in [self.stock, self.waste, *self.foundations, *self.tableau]:
            for card in slot.pile:
                self.controls.append(card)

        self.suppress_history = False
        self.update()



    async def _timer_loop(self):
        while self._timer_task_running:
            self._update_score_text()
            await asyncio.sleep(1)

    def will_unmount(self):
        self._timer_task_running = False