import flet as ft
import flet_audio as fta
from solitaire import Solitaire
from menu import MenuOverlay
from state import load_settings
from savegame import save_game, load_game
import asyncio

class GameApp(ft.Stack):
    def __init__(self, page: ft.Page):
        super().__init__(width=1000, height=650)
        self.app_page = page
        self.settings = load_settings(self.app_page)
        
        # 1. VERIFICAR SE ESTAMOS NO BROWSER
        self.is_web = self.app_page.web

        # 2. CARREGAR ÁUDIO APENAS SE NÃO FOR BROWSER
        if not self.is_web:
            self.bg_music = fta.Audio(
                src="sounds/Balatro.mp3",
                volume=float(self.settings.get("music_volume", 0.5)),
                on_state_change=self.loop_music
            )
            self.sfx_card = fta.Audio(
                src="sounds/som_carta.mp3",
                volume=float(self.settings.get("sfx_volume", 0.8)),
                release_mode=fta.ReleaseMode.STOP
            )
            self.sfx_btn = fta.Audio(
                src="sounds/botao.mp3",
                volume=float(self.settings.get("sfx_volume", 0.8)),
                release_mode=fta.ReleaseMode.STOP
            )
            
            # Adicionar à página
            if hasattr(self.app_page, "services") and self.app_page.services is not None:
                self.app_page.services.extend([self.bg_music, self.sfx_card, self.sfx_btn])
            else:
                self.app_page.overlay.extend([self.bg_music, self.sfx_card, self.sfx_btn])
        else:
            # Se for Web/Telemóvel, anulamos os objetos de áudio
            self.bg_music = None
            self.sfx_card = None
            self.sfx_btn = None

        self.is_music_playing = False
        self.app_page.update()
        # 3. PASSAR APENAS FUNÇÕES SEGURAS PARA OS OUTROS FICHEIROS
        self.solitaire = Solitaire(
            card_back=self.settings["card_back"],
            play_card_sound=self.play_card_sound,
            play_btn_sound=self.play_btn_sound,
            on_pause=self.toggle_pause  
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

    def _restore_music_volume(self):
        if self.bg_music:
            self.bg_music.volume = float(self.settings.get("music_volume", 0.5))
            try:
                self.bg_music.update()
            except Exception:
                pass

    def _muffle_music_volume(self):
        if self.bg_music:
            normal_vol = float(self.settings.get("music_volume", 0.5))
            self.bg_music.volume = normal_vol * 0.3
            try:
                self.bg_music.update()
            except Exception:
                pass

    # FUNÇÕES SEGURAS PARA TOCAR ÁUDIO (Resolve a falta de som na Web)
    def play_card_sound(self):
        if self.sfx_card:
            async def _play():
                try:
                    await self.sfx_card.seek(0)
                except Exception:
                    pass  
                try:
                    await self.sfx_card.play()
                except Exception:
                    pass
            self.app_page.run_task(_play)

    def start_bg_music(self):
        if self.bg_music and not self.is_music_playing:
            self.is_music_playing = True
            async def _play_music():
                try:
                    await self.bg_music.play()
                except Exception as e:
                    print(f"Erro ao tocar música: {e}")
            self.app_page.run_task(_play_music)

    def play_btn_sound(self):
        if self.sfx_btn:
            async def _play():
                try:
                    await self.sfx_btn.seek(0)
                except Exception:
                    pass  
                try:
                    await self.sfx_btn.play()
                except Exception:
                    pass
            self.app_page.run_task(_play)

    def loop_music(self, e):
        if e.data == "completed" and self.bg_music:
            async def _replay():
                try:
                    await self.bg_music.seek(0)
                except Exception:
                    pass
                try:
                    await self.bg_music.play()
                except Exception:
                    pass
            self.app_page.run_task(_replay)

    def apply_settings(self, settings):
        self.settings = settings
        self.solitaire.set_card_back(settings["card_back"])

        if self.bg_music:
            if self.menu.visible:
                self.bg_music.volume = float(settings.get("music_volume", 0.5)) * 0.3
            else:
                self.bg_music.volume = float(settings.get("music_volume", 0.5))

            self.sfx_card.volume = float(settings.get("sfx_volume", 0.8))
            self.sfx_btn.volume = float(settings.get("sfx_volume", 0.8))

            self.bg_music.update()
            self.sfx_card.update()
            self.sfx_btn.update()
            
        self.app_page.update()

    def new_game(self):
        self.controls.remove(self.solitaire)
        self.solitaire = Solitaire(
            card_back=self.settings["card_back"],
            play_card_sound=self.play_card_sound,
            play_btn_sound=self.play_btn_sound,
            on_pause=self.toggle_pause
        )
        self.controls.insert(0, self.solitaire)
        self.menu.hide()
        
        self._restore_music_volume()
        self.start_bg_music()
        self.update()

    def continue_game(self):
        self.menu.hide()
        self._restore_music_volume()
        self.start_bg_music()

    def resume_game(self):
        self.menu.hide()
        self._restore_music_volume()
        self.start_bg_music()

    def toggle_pause(self):
        if self.menu.visible:
            if self.menu.mode == "pause":
                self.menu.hide()
                self._restore_music_volume()
        else:
            self.menu.show_pause()
            self._muffle_music_volume()

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
        self._restore_music_volume()


def main(page: ft.Page):
    page.on_error = lambda e: print("Page error:", e.data)
    page.padding = 0  # Remover margens para usar o ecrã todo

    app = GameApp(page)
    
    root_stack = ft.Stack([app], expand=True)
    page.add(root_stack)
    
    page.on_keyboard_event = app.on_key_event

    def on_resize(e):
            if page.width == 0 or page.height == 0:
                return
                
            GAME_W = 720
            GAME_H = 600
            
            scale_w = page.width / GAME_W
            scale_h = page.height / GAME_H
            final_scale = min(scale_w, scale_h, 1.0)
            
            app.scale = ft.Scale(scale=final_scale, alignment=ft.Alignment(-1.0, -1.0))
            
            sobra_w = page.width - (GAME_W * final_scale)
            
            app.left = sobra_w / 2
            app.top = 25 
            
            app.update()

    page.on_resize = on_resize
    on_resize(None)


ft.run(main, assets_dir="assets")