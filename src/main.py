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
        #self.expand = True
        self.settings = load_settings(self.app_page)

        # 1. CRIAR OS CONTROLOS DE ÁUDIO (sem a "/" inicial no src)
        self.bg_music = fta.Audio(
            src="sounds/Balatro.mp3",  # <-- SEM a barra inicial
            #autoplay=True,
            volume=float(self.settings.get("music_volume", 0.5)),
            on_state_change=self.loop_music
        )
        self.is_music_playing = False
        self.sfx_card = fta.Audio(
            src="sounds/som_carta.mp3",     # <-- SEM a barra inicial
            volume=float(self.settings.get("sfx_volume", 0.8)),
            release_mode=fta.ReleaseMode.STOP
        )
        self.sfx_btn = fta.Audio(
            src="sounds/botao.mp3",         # <-- SEM a barra inicial
            volume=float(self.settings.get("sfx_volume", 0.8)),
            release_mode=fta.ReleaseMode.STOP
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
            # Reduz o volume para 30% do normal (ajusta este 0.3 como preferires)
            normal_vol = float(self.settings.get("music_volume", 0.5))
            self.bg_music.volume = normal_vol * 0.3
            try:
                self.bg_music.update()
            except Exception:
                pass



        # FUNÇÕES SEGURAS PARA TOCAR ÁUDIO
    def play_card_sound(self):
        if self.sfx_card:
            async def _play():
                try:
                    await self.sfx_card.seek(0)
                except Exception:
                    pass
                await self.sfx_card.play()
            self.app_page.run_task(_play)

    def start_bg_music(self):
        if self.bg_music and not self.is_music_playing:
            self.is_music_playing = True
            
            # Dizemos ao Flet que, a partir de agora, esta faixa pode tocar
            self.bg_music.autoplay = True
            self.bg_music.update()
            
            async def _play_music():
                # A MAGIA ESTÁ AQUI: Esperamos meio segundo.
                # Isto dá tempo ao som do botão de tocar primeiro, o que 
                # diz ao browser "O utilizador clicou, desbloqueia o áudio!"
                await asyncio.sleep(0.5)
                
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
                await self.sfx_btn.play()
            self.app_page.run_task(_play)

    def loop_music(self, e):
        if e.data == "completed" and self.bg_music:
            async def _replay():
                await self.bg_music.play()
            self.app_page.run_task(_replay)

    def apply_settings(self, settings):
        self.settings = settings
        self.solitaire.set_card_back(settings["card_back"])

        if self.bg_music:
            # Se o menu estiver visível, aplica o novo volume mas mantém "abafado"
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
        
        self._restore_music_volume()  # <-- Restaura o volume
        self.start_bg_music()
        self.update()

    def continue_game(self):
        self.menu.hide()
        self._restore_music_volume()  # <-- Restaura o volume
        self.start_bg_music()

    def resume_game(self):
        self.menu.hide()
        self._restore_music_volume()  # <-- Restaura o volume
        self.start_bg_music()

    def toggle_pause(self):
        if self.menu.visible:
            if self.menu.mode == "pause":
                self.menu.hide()
                self._restore_music_volume()  # <-- Restaura quando fecha a pausa
        else:
            self.menu.show_pause()
            self._muffle_music_volume()   # <-- Abafa quando abre a pausa


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
        self._restore_music_volume()      # <-- Restaura após fazer o load




def main(page: ft.Page):
    page.on_error = lambda e: print("Page error:", e.data)
    page.padding = 0  # Remover margens para usar o ecrã todo

    app = GameApp(page)
    
    # O SEGREDO: Colocar o app dentro de uma Stack raiz que preenche o ecrã.
    # Assim, o app pode ter o seu tamanho original de 1000x650 sem o Flutter cortar!
    root_stack = ft.Stack([app], expand=True)
    page.add(root_stack)
    
    page.on_keyboard_event = app.on_key_event

    def on_resize(e):
            if page.width == 0 or page.height == 0:
                return
                
            # 1. Ajustar para a largura REAL das cartas (720px) em vez dos 1000px do fundo
            GAME_W = 720
            GAME_H = 600
            
            scale_w = page.width / GAME_W
            scale_h = page.height / GAME_H
            final_scale = min(scale_w, scale_h, 1.0)
            
            app.scale = ft.Scale(scale=final_scale, alignment=ft.Alignment(-1.0, -1.0))
            
            # 2. Calcular apenas a sobra horizontal para o centrar na perfeição
            sobra_w = page.width - (GAME_W * final_scale)
            
            app.left = sobra_w / 2
            # 3. Mini borda fixa no topo em vez de centrar na vertical!
            app.top = 25 
            
            app.update()

    page.on_resize = on_resize
    on_resize(None)

ft.run(main, assets_dir="assets")