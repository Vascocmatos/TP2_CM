import flet as ft
import flet_audio as fta
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

        # 1. CRIAR OS CONTROLOS DE ÁUDIO
        self.bg_music = fta.Audio(
            src="/sounds/Balatro OST in the style of Masayoshi Takanaka.mp3",
            autoplay=True,
            volume=float(self.settings.get("music_volume", 0.5)),
            on_state_change=self.loop_music
        )
        self.sfx_card = fta.Audio(
            src="/sounds/som_carta.mp3",
            volume=float(self.settings.get("sfx_volume", 0.8))
        )
        self.sfx_btn = fta.Audio(
            src="/sounds/botao.mp3",
            volume=float(self.settings.get("sfx_volume", 0.8))
        )

        # 2. REGISTAR COMO SERVICE (não overlay)
        if hasattr(self.app_page, "services") and self.app_page.services is not None:
            self.app_page.services.extend([self.bg_music, self.sfx_card, self.sfx_btn])
        else:
            # fallback antigo
            self.app_page.overlay.extend([self.bg_music, self.sfx_card, self.sfx_btn])

        self.app_page.update()

        # 3. PASSAR APENAS FUNÇÕES SEGURAS PARA OS OUTROS FICHEIROS
        self.solitaire = Solitaire(
            card_back=self.settings["card_back"],
            play_card_sound=self.play_card_sound,
            play_btn_sound=self.play_btn_sound
        )

        self.menu = MenuOverlay(
            page=self.app_page,
            on_new_game=self.new_game,
            on_continue=self.continue_game,
            on_resume=self.resume_game,
            on_quit=self.quit_game,
            on_apply_settings=self.apply_settings,
            on_save_slot=self.save_slot,
            on_load_slot=self.load_slot,
            play_btn_sound=self.play_btn_sound
        )

        self.controls = [self.solitaire, self.menu]
        self.menu.show_main()

    # FUNÇÕES SEGURAS PARA TOCAR ÁUDIO
    def play_card_sound(self):
        if self.sfx_card:
            self.app_page.run_task(self.sfx_card.play)

    def play_btn_sound(self):
        if self.sfx_btn:
            self.app_page.run_task(self.sfx_btn.play)

    def loop_music(self, e):
        if e.data == "completed" and self.bg_music:
            self.app_page.run_task(self.bg_music.play)

    def apply_settings(self, settings):
        self.settings = settings
        self.solitaire.set_card_back(settings["card_back"])

        if self.bg_music:
            self.bg_music.volume = float(settings.get("music_volume", 0.5))
            self.sfx_card.volume = float(settings.get("sfx_volume", 0.8))
            self.sfx_btn.volume = float(settings.get("sfx_volume", 0.8))

            self.bg_music.update()
            self.sfx_card.update()
            self.sfx_btn.update()

    def new_game(self):
        self.controls.remove(self.solitaire)
        self.solitaire = Solitaire(
            card_back=self.settings["card_back"],
            play_card_sound=self.play_card_sound,
            play_btn_sound=self.play_btn_sound
        )
        self.controls.insert(0, self.solitaire)
        self.menu.hide()
        self.update()

    def continue_game(self):
        self.menu.hide()

    def resume_game(self):
        self.menu.hide()

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