SOLITAIRE_WIDTH = 1000
SOLITAIRE_HEIGHT = 500
CARD_HEIGHT = 100

import random

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
    def __init__(self, card_back="/images/card_back.png"):
        super().__init__()
        self.controls = []
        self.width = SOLITAIRE_WIDTH
        self.height = SOLITAIRE_HEIGHT
        self.history = []
        self.suppress_history = False
        self.card_back = card_back

    def did_mount(self):
        self.create_card_deck()
        self.create_slots()
        self.deal_cards()

    def create_card_deck(self):
        suites = [
            Suite("hearts", "RED"),
            Suite("diamonds", "RED"),
            Suite("clubs", "BLACK"),
            Suite("spades", "BLACK"),
        ]
        ranks = [
            Rank("Ace", 1),
            Rank("2", 2),
            Rank("3", 3),
            Rank("4", 4),
            Rank("5", 5),
            Rank("6", 6),
            Rank("7", 7),
            Rank("8", 8),
            Rank("9", 9),
            Rank("10", 10),
            Rank("Jack", 11),
            Rank("Queen", 12),
            Rank("King", 13),
        ]

        self.cards = []

        for suite in suites:
            for rank in ranks:
                self.cards.append(Card(solitaire=self, suite=suite, rank=rank))

    def create_slots(self):
        self.stock = Slot(solitaire=self, top=0, left=0, border=ft.border.all(1))
        self.waste = Slot(solitaire=self, top=0, left=100, border=None)

        self.foundations = []
        x = 300
        for i in range(4):
            self.foundations.append(
                Slot(solitaire=self, top=0, left=x, border=ft.border.all(1, "outline"))
            )
            x += 100

        self.tableau = []
        x = 0
        for i in range(7):
            self.tableau.append(Slot(solitaire=self, top=150, left=x, border=None))
            x += 100

        self.controls.append(self.stock)
        self.controls.append(self.waste)
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

        self.update()

    def on_reset_click(self, e):
        if len(self.stock.pile) == 0:
            self.restart_stock()

    def deal_cards(self):
        self.suppress_history = True

        random.shuffle(self.cards)
        self.controls.extend(self.cards)

        # deal to tableau
        first_slot = 0
        remaining_cards = self.cards

        while first_slot < len(self.tableau):
            for slot in self.tableau[first_slot:]:
                top_card = remaining_cards[0]
                top_card.place(slot)
                remaining_cards.remove(top_card)
            first_slot += 1

        # place remaining cards to stock pile
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
        if not self.history:
            return
        move = self.history.pop()

        # remove cartas do destino e volta ao slot original
        for card in move["cards"]:
            if card in move["to"].pile:
                move["to"].pile.remove(card)
            card.slot = move["from"]
            move["from"].pile.append(card)

        # reposicionar visualmente
        for card in move["cards"]:
            if move["from"] in self.tableau:
                card.top = move["from"].top + move["from"].pile.index(card) * CARD_OFFSET
            else:
                card.top = move["from"].top
            card.left = move["from"].left

        # se houve cartas viradas automaticamente, desvirar
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
            ft.AlertDialog(title=ft.Text("Congratulations! You won!"), open=True)
        )