import flet as ft
from solitaire import Solitaire
from menu import MenuOverlay
from state import load_settings
from savegame import save_game, load_game


class GameApp(ft.Stack):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.app_page = page
        self.expand = True
        self.settings = load_settings(self.app_page)

        self.solitaire = Solitaire(card_back=self.settings["card_back"])

        self.menu = MenuOverlay(
            page=self.app_page,
            on_new_game=self.new_game,
            on_continue=self.continue_game,
            on_resume=self.resume_game,
            on_quit=self.quit_game,
            on_set_card_back=self.set_card_back,
            on_save_slot=self.save_slot,
            on_load_slot=self.load_slot,
        )

        self.controls = [self.solitaire, self.menu]
        self.menu.show_main()

    def new_game(self):
        self.controls.remove(self.solitaire)
        self.solitaire = Solitaire(card_back=self.settings["card_back"])
        self.controls.insert(0, self.solitaire)
        self.menu.hide()
        self.update()

    def continue_game(self):
        self.menu.hide()

    def resume_game(self):
        self.menu.hide()

    def set_card_back(self, card_back):
        self.settings["card_back"] = card_back
        self.solitaire.set_card_back(card_back)

    def toggle_pause(self):
        if self.menu.visible:
            if self.menu.mode == "pause":
                self.menu.hide()
        else:
            self.menu.show_pause()

    def quit_game(self):
        try:
            self.app_page.window_close()
        except Exception:
            pass
        try:
            self.app_page.window_destroy()
        except Exception:
            pass

    def on_key_event(self, e: ft.KeyboardEvent):
        if e.key == "Escape":
            self.toggle_pause()

    def save_slot(self, slot):
        data = self.solitaire.get_state()
        save_game(self.app_page, slot, data)
        self.menu.show_pause()

    def load_slot(self, slot):
        data = load_game(self.app_page, slot)
        if data:
            self.solitaire.load_state(data)
        self.menu.hide()


def main(page: ft.Page):
    page.on_error = lambda e: print("Page error:", e.data)

    app = GameApp(page)
    page.add(app)

    page.on_keyboard_event = app.on_key_event


ft.run(main, assets_dir="assets")