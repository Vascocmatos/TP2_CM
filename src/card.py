CARD_WIDTH = 70
CARD_HEIGHT = 100
CARD_OFFSET = 20
DROP_PROXIMITY = 20

import flet as ft
import os

import slot

class Card(ft.GestureDetector):
    def __init__(self, solitaire, suite, rank):
        super().__init__()
        self.mouse_cursor=ft.MouseCursor.MOVE
        self.drag_interval=5
        self.on_pan_start=self.start_drag
        self.on_pan_update=self.drag
        self.on_pan_end=self.drop
        self.suite=suite
        self.rank=rank
        self.face_up=False
        self.top=None
        self.left=None
        self.solitaire = solitaire
        self.slot = None

        # Resolve image path relative to card.py location
        image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets",
            "images",
            "card_back.png",
        )

        self.content=ft.Container(
            width=CARD_WIDTH,
            height=CARD_HEIGHT,
            border_radius = ft.BorderRadius.all(6),
            content=ft.Image(src=image_path))

    def move_on_top(self):
        """Brings draggable card pile to the top of the stack"""

        # for card in self.get_draggable_pile():
        for card in self.draggable_pile:
            self.solitaire.controls.remove(card)
            self.solitaire.controls.append(card)
        self.solitaire.update()

    def bounce_back(self):
        """Returns draggable pile to its original position"""
        for card in self.draggable_pile:
            card.top = card.slot.top + card.slot.pile.index(card) * CARD_OFFSET
            card.left = card.slot.left
        self.solitaire.update()

    def place(self, slot):
        """Place draggable pile to the slot"""
        # refresh tile set in case this is called during deal / drop
        self.get_draggable_pile()

        if slot in self.solitaire.tableau:
            self.top = slot.top + len(slot.pile) * CARD_OFFSET
        else:
            self.top = slot.top
        self.left = slot.left

        for card in self.draggable_pile:
            card.top = slot.top + len(slot.pile) * CARD_OFFSET
            card.left = slot.left

            # remove card from it's original slot, if it exists
            if card.slot is not None:
                card.slot.pile.remove(card)

            # change card's slot to a new slot
            card.slot = slot

            # add card to the new slot's pile
            slot.pile.append(card)

        self.solitaire.update()

    def start_drag(self, e: ft.DragStartEvent):
       self.start_top = self.top
       self.start_left = self.left
       self.get_draggable_pile()
       self.move_on_top()
       self.update()

    def drag(self, e: ft.DragUpdateEvent):
       if e.local_delta is None:
           return
       self.get_draggable_pile()
       for card in self.draggable_pile:
            card.top = max(0, card.top + e.local_delta.y)
            card.left = max(0, card.left + e.local_delta.x)
       self.solitaire.update()

    def drop(self, e: ft.DragEndEvent):
       for slot in self.solitaire.slots:
           if (
               abs(self.top - slot.top) < DROP_PROXIMITY
           and abs(self.left - slot.left) < DROP_PROXIMITY
         ):
               self.place(slot)
               self.update()
               return

       self.bounce_back()
       self.update()

    def get_draggable_pile(self):
        """returns list of cards that will be dragged together, starting with the current card"""
        if self.slot is not None:
            self.draggable_pile = self.slot.pile[self.slot.pile.index(self) :]
        else:
            self.draggable_pile = [self]
        return self.draggable_pile

    
