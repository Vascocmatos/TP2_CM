import flet as ft

CARD_WIDTH = 70
CARD_HEIGHT = 100
DROP_PROXIMITY = 30
CARD_OFFSET = 20


class Card(ft.GestureDetector):
    def __init__(self, solitaire, suite, rank):
        super().__init__()
        self.mouse_cursor = ft.MouseCursor.MOVE
        self.drag_interval = 20
        self.on_pan_start = self.start_drag
        self.on_pan_update = self.drag
        self.on_pan_end = self.drop
        self.on_tap = self.click
        self.on_double_tap = self.doubleclick
        self.suite = suite
        self.rank = rank
        self.face_up = False
        self.top = None
        self.left = None
        self.solitaire = solitaire
        self.slot = None
        self.content = ft.Container(
            width=CARD_WIDTH,
            height=CARD_HEIGHT,
            border_radius=ft.BorderRadius.all(6),
            content=ft.Image(src=self.solitaire.card_back),
        )
        self.draggable_pile = [self]

    def _play_card_sound(self):
        if not self.solitaire.suppress_history and self.solitaire.play_card_sound:
            self.solitaire.play_card_sound()

    def turn_face_up(self):
        self._play_card_sound()
        self.face_up = True
        self.content.content.src = f"/images/{self.rank.name}_{self.suite.name}.svg"
        self.update()  # <-- Mudar de self.solitaire.update() para self.update()

    def turn_face_down(self):
        self._play_card_sound()
        self.face_up = False
        self.content.content.src = self.solitaire.card_back
        self.update()  # <-- Mudar de self.solitaire.update() para self.update()

    def move_on_top(self):
        # OTIMIZAÇÃO: Verificar se as cartas a arrastar JÁ ESTÃO no fim da lista (topo visual)
        # Se já estiverem, saímos da função e poupamos o peso do update total!
        if self.solitaire.controls[-len(self.draggable_pile):] == self.draggable_pile:
            return
            
        for card in self.draggable_pile:
            self.solitaire.controls.remove(card)
            self.solitaire.controls.append(card)
        self.solitaire.update()

    def bounce_back(self):
        for card in self.draggable_pile:
            if card.slot in self.solitaire.tableau:
                card.top = card.slot.top + card.slot.pile.index(card) * CARD_OFFSET
            else:
                card.top = card.slot.top
            card.left = card.slot.left
        self.solitaire.update()

    def place(self, slot):
        original_slot = self.slot

        self.move_on_top()

        if not self.solitaire.suppress_history and original_slot is not None:
            self._play_card_sound()
            self.solitaire.history.append(
                {
                    "cards": self.draggable_pile.copy(),
                    "from": original_slot,
                    "to": slot,
                    "flipped_cards": [],
                }
            )

        for card in self.draggable_pile:
            if slot in self.solitaire.tableau:
                card.top = slot.top + len(slot.pile) * CARD_OFFSET
            else:
                card.top = slot.top
            card.left = slot.left

            if card.slot is not None:
                card.slot.pile.remove(card)

            card.slot = slot
            slot.pile.append(card)

        if self.solitaire.check_win():
            self.solitaire.winning_sequence()

        self.solitaire.update()

    def get_draggable_pile(self):
        if (
            self.slot is not None
            and self.slot != self.solitaire.stock
            and self.slot != self.solitaire.waste
        ):
            self.draggable_pile = self.slot.pile[self.slot.pile.index(self) :]
        else: 
            self.draggable_pile = [self]

    def start_drag(self, e: ft.DragStartEvent):
        if self.face_up:
            self.get_draggable_pile()
            
            # 1. CRIAR "GHOST CARDS" NO TOPO PARA O ARRASTO
            self.solitaire.ghosts = []
            for c in self.draggable_pile:
                # Esconde a imagem da carta original (mas mantém o clique ativo)
                c.content.opacity = 0
                c.update()
                
                # Cria um clone exato que vai ficar por cima de tudo visualmente
                ghost = ft.Container(
                    width=CARD_WIDTH,
                    height=CARD_HEIGHT,
                    top=c.top,
                    left=c.left,
                    border_radius=ft.BorderRadius.all(6),
                    content=ft.Image(src=c.content.content.src)
                )
                self.solitaire.ghosts.append(ghost)
                self.solitaire.controls.append(ghost)
                
            self.solitaire.update()

    def drag(self, e: ft.DragUpdateEvent):
        if self.face_up:
            for i, c in enumerate(self.draggable_pile):
                # 2. ATUALIZAR POSIÇÃO DA CARTA ORIGINAL (INVISÍVEL)
                c.top = (
                    max(0, self.top + e.local_delta.y)
                    + i * CARD_OFFSET
                )
                c.left = max(0, self.left + e.local_delta.x)
                c.update()

                # 3. ATUALIZAR POSIÇÃO DO CLONE VISUAL
                if hasattr(self.solitaire, "ghosts") and i < len(self.solitaire.ghosts):
                    ghost = self.solitaire.ghosts[i]
                    ghost.top = c.top
                    ghost.left = c.left
                    ghost.update()

    def drop(self, e: ft.DragEndEvent):
        if self.face_up:
            # 4. LIMPAR OS CLONES QUANDO LARGAMOS AS CARTAS
            if hasattr(self.solitaire, "ghosts"):
                for ghost in self.solitaire.ghosts:
                    if ghost in self.solitaire.controls:
                        self.solitaire.controls.remove(ghost)
                self.solitaire.ghosts.clear()

            # 5. MOSTRAR AS CARTAS ORIGINAIS NOVAMENTE
            for c in self.draggable_pile:
                c.content.opacity = 1
            
            # 6. MOVER AS ORIGINAIS PARA O TOPO (agora é seguro, o arrasto já acabou)
            self.move_on_top()

            for slot in self.solitaire.tableau:
                if (
                    abs(self.top - (slot.top + len(slot.pile) * CARD_OFFSET))
                    < DROP_PROXIMITY
                    and abs(self.left - slot.left) < DROP_PROXIMITY
                ) and self.solitaire.check_tableau_rules(self, slot):
                    self.place(slot)
                    return

            if len(self.draggable_pile) == 1:
                for slot in self.solitaire.foundations:
                    if (
                        abs(self.top - slot.top) < DROP_PROXIMITY
                        and abs(self.left - slot.left) < DROP_PROXIMITY
                    ) and self.solitaire.check_foundations_rules(self, slot):
                        self.place(slot)
                        return

            self.bounce_back()

    def click(self, e):
        self.get_draggable_pile()
        if self.slot in self.solitaire.tableau:
            if not self.face_up and len(self.draggable_pile) == 1:
                # virar carta manualmente (não entra no undo)
                self.turn_face_up()
                # ADICIONAR ESTAS DUAS LINHAS PARA O UNDO FUNCIONAR:
                if self.solitaire.history:
                    self.solitaire.history[-1]["flipped_cards"].append(self)
        elif self.slot == self.solitaire.stock:
            if len(self.solitaire.stock.pile) == 0:
                self.solitaire.restart_stock()
                return

            self._play_card_sound() 
            self.move_on_top()
            self.place(self.solitaire.waste)
            self.turn_face_up()

            if self.solitaire.history:
                self.solitaire.history[-1]["flipped_cards"].append(self)

    def doubleclick(self, e):
        self.get_draggable_pile()
        if self.face_up and len(self.draggable_pile) == 1:
            self.move_on_top()
            for slot in self.solitaire.foundations:
                if self.solitaire.check_foundations_rules(self, slot):
                    self.place(slot)
                    return