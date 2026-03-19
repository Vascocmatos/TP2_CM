SOLITAIRE_WIDTH = 1000
SOLITAIRE_HEIGHT = 500

import random

import flet as ft
from slot import Slot
from card import Card

class Solitaire(ft.Stack):
    def __init__(self):
        super().__init__()
        self.controls = []
        self.slots = []
        self.cards = []
        self.width = SOLITAIRE_WIDTH
        self.height = SOLITAIRE_HEIGHT

    def did_mount(self):
        self.create_card_deck()
        self.create_slots()
        self.deal_cards()

    def create_card_deck(self):
        suites = [
            Solitaire.Suite("hearts", "RED"),
            Solitaire.Suite("diamonds", "RED"),
            Solitaire.Suite("clubs", "BLACK"),
            Solitaire.Suite("spades", "BLACK"),
        ]
        ranks = [
            Solitaire.Rank("Ace", 1),
            Solitaire.Rank("2", 2),
            Solitaire.Rank("3", 3),
            Solitaire.Rank("4", 4),
            Solitaire.Rank("5", 5),
            Solitaire.Rank("6", 6),
            Solitaire.Rank("7", 7),
            Solitaire.Rank("8", 8),
            Solitaire.Rank("9", 9),
            Solitaire.Rank("10", 10),
            Solitaire.Rank("Jack", 11),
            Solitaire.Rank("Queen", 12),
            Solitaire.Rank("King", 13),
        ]

        self.cards = []

        for suite in suites:
            for rank in ranks:
                self.cards.append(Card(solitaire=self, suite=suite, rank=rank))

    def create_slots(self):
        self.stock = Slot(top=0, left=0, border=ft.Border.all(1))
        self.waste = Slot(top=0, left=100, border=None)

        self.foundations = []
        x = 300
        for i in range(4):
            self.foundations.append(Slot(top=0, left=x, border=ft.Border.all(1, "outline")))
            x += 100

        self.tableau = []
        x = 0
        for i in range(7):
            self.tableau.append(Slot(top=150, left=x, border=None))
            x += 100

        self.controls.append(self.stock)
        self.controls.append(self.waste)
        self.controls.extend(self.foundations)
        self.controls.extend(self.tableau)
        self.update()

    def deal_cards(self):
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
            first_slot +=1

        # place remaining cards to stock pile
        for card in remaining_cards:
            card.place(self.stock)

        self.update()

    class Suite:
        def __init__(self, suite_name, suite_color):
            self.name = suite_name
            self.color = suite_color

    class Rank:
        def __init__(self, card_name, card_value):
            self.name = card_name
            self.value = card_value