import flet as ft

CARD_WIDTH = 70
CARD_HEIGHT = 100


class Slot(ft.Container):
    def __init__(self, solitaire, top=0, left=0, border=None, bgcolor=None):
        super().__init__(top=top, left=left, width=CARD_WIDTH, height=CARD_HEIGHT, border=border, bgcolor=bgcolor)
        self.solitaire = solitaire
        self.pile = []

    def get_top_card(self):
        return self.pile[-1] if self.pile else None