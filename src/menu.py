import flet as ft
from state import load_settings, save_settings
from savegame import list_slots, delete_game

CARD_BACK_OPTIONS = [
    ("Clássico", "/images/card_back/card_back.png"),
    ("blasphamous", "/images/card_back/blasphemous_card.png"),
    ("Bach", "/images/card_back/card_bach.png"),
    ("Amarelo", "/images/card_back/carta_amarela.png"),
]

LABEL_TO_PATH = {label: path for label, path in CARD_BACK_OPTIONS}
PATH_TO_LABEL = {path: label for label, path in CARD_BACK_OPTIONS}


class MenuOverlay(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        on_new_game,
        on_continue,
        on_resume,
        on_quit,
        on_apply_settings,
        on_save_slot,
        on_load_slot,
        play_btn_sound=None
    ):
        super().__init__()
        self.app_page = page
        self.on_new_game = on_new_game
        self.on_continue = on_continue
        self.on_resume = on_resume
        self.on_quit = on_quit
        self.on_apply_settings = on_apply_settings
        self.on_save_slot = on_save_slot
        self.on_load_slot = on_load_slot
        self.play_btn_sound = play_btn_sound

        self.visible = True
        self.expand = True
        self.bgcolor = "rgba(10,10,10,0.65)"
        self.alignment = ft.Alignment(0, 0)

        self.panel = ft.Container(
            width=420,
            padding=22,
            bgcolor="#1E1E1E",
            border_radius=14,
            border=ft.Border.all(1, "#2C2C2C"),
            shadow=ft.BoxShadow(blur_radius=30, color=ft.Colors.BLACK_54),
        )

        self.content = self.panel
        self.mode = "main"
        self.game_in_progress = False  # <-- ADICIONAR ESTA LINHA

    def _play_btn_sound(self):
        if self.play_btn_sound:
            self.play_btn_sound()

    def _wrap_click(self, on_click_action):
        def wrapper(e):
            self._play_btn_sound()
            if on_click_action:
                on_click_action(e)
        return wrapper

    def _title(self, text):
        return ft.Text(text, size=22, weight=ft.FontWeight.BOLD, color="#F5F5F5")

    def _primary_btn(self, label, on_click):
        return ft.ElevatedButton(
            label,
            on_click=self._wrap_click(on_click),
            style=ft.ButtonStyle(
                bgcolor="#3B82F6",
                color="white",
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding.symmetric(horizontal=18, vertical=12),
            ),
        )

    def _secondary_btn(self, label, on_click):
        return ft.OutlinedButton(
            label,
            on_click=self._wrap_click(on_click),
            style=ft.ButtonStyle(
                color="#E5E7EB",
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, "#3B3B3B"),
                padding=ft.Padding.symmetric(horizontal=18, vertical=12),
            ),
        )

    def did_mount(self):
        self._build_main_menu()

    def _set_panel(self, title, controls):
        self.panel.content = ft.Column(
            [
                self._title(title),
                ft.Divider(color="#3A3A3A"),
                *controls,
            ],
            tight=True,
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
        try:
            self.update()
        except Exception:
            pass

    def _build_main_menu(self):
        self.mode = "main"
        
        controls = []
        # Se houver um jogo a decorrer, mostramos o botão Retomar no topo
        if getattr(self, "game_in_progress", False):
            controls.append(self._primary_btn("Retomar Jogo", lambda e: self.on_resume()))
            
        controls.extend([
            self._primary_btn("Iniciar Jogo", lambda e: self._build_start_menu()),
            self._secondary_btn("Opções", lambda e: self._build_options_menu()),
            self._secondary_btn("Tutorial", lambda e: self._build_tutorial_menu()),
            self._secondary_btn("Quit", lambda e: self.on_quit()),
        ])
        
        self._set_panel("Solitaire", controls)

    def _build_tutorial_menu(self):
        self.mode = "tutorial"
        texto = (
            "Regras do Solitário:\n"
            "• Move cartas alternando cores em ordem decrescente.\n"
            "• Só reis podem ir para colunas vazias.\n"
            "• Objetivo: completar as fundações por naipe do Ás ao Rei.\n\n"
            "Particularidades desta app:\n"
            "• O tempo e a pontuação reiniciam quando carregas um save.\n"
            "• Cada Undo adiciona +5 pontos (pior pontuação).\n"
            "• Pontuação = tempo total + penalizações.\n"
        )
        
        # --- VOLTAR INTELIGENTE ---
        def go_back(e):
            if getattr(self, "game_in_progress", False):
                self._build_pause_menu()
            else:
                self._build_main_menu()

        self._set_panel(
            "Tutorial",
            [
                ft.Text(texto, size=14),
                self._secondary_btn("Voltar", go_back),
            ],
        )

    def _build_start_menu(self):
        self.mode = "start"
        self._set_panel(
            "Start",
            [
                self._primary_btn("Novo Jogo", lambda e: self.on_new_game()),
                self._primary_btn("Continuar", lambda e: self._build_load_menu()),
                self._secondary_btn("Voltar", lambda e: self._build_main_menu()),
            ],
        )

    def _build_pause_menu(self):
        self.mode = "pause"
        self._set_panel(
            "Pausa",
            [
                self._primary_btn("Continuar", lambda e: self.on_resume()),
                self._primary_btn("Novo Jogo", lambda e: self.on_new_game()),
                self._primary_btn("Salvar Jogo", lambda e: self._build_save_menu()),
                self._primary_btn("Carregar Jogo", lambda e: self._build_load_menu()),
                self._secondary_btn("Opções", lambda e: self._build_options_menu()),
                self._secondary_btn("Menu Inicial", lambda e: self._build_main_menu()),
            ],
        )

    def _build_load_menu(self):
        self.mode = "load"
        slots = list_slots(self.app_page)

        controls = []
        for s in slots:
            title = f"Slot {s['slot']}"
            label = title if s["data"] else f"{title} (vazio)"

            btn_load = ft.ElevatedButton(
                label,
                disabled=s["data"] is None,
                on_click=self._wrap_click(lambda e, slot=s["slot"]: self.on_load_slot(slot)),
            )
            controls.append(btn_load)

            btn_delete = ft.OutlinedButton(
                f"Apagar {title}",
                disabled=s["data"] is None,
                on_click=self._wrap_click(lambda e, slot=s["slot"]: self._delete_slot(slot)),
            )
            controls.append(btn_delete)

        controls.append(self._secondary_btn("Voltar", lambda e: self._build_start_menu()))
        self._set_panel("Carregar Jogo", controls)

    def _build_save_menu(self):
        self.mode = "save"
        slots = list_slots(self.app_page)
        controls = []
        for s in slots:
            title = f"Slot {s['slot']}"
            label = title if s["data"] else f"{title} (vazio)"
            btn = ft.ElevatedButton(
                f"Salvar em {label}",
                on_click=self._wrap_click(lambda e, slot=s["slot"]: self.on_save_slot(slot)),
            )
            controls.append(btn)

        controls.append(self._secondary_btn("Voltar", lambda e: self._build_pause_menu()))
        self._set_panel("Salvar Jogo", controls)

    def _build_options_menu(self):
        self.mode = "options"
        settings = load_settings(self.app_page)

        current_path = settings.get("card_back", "/images/card_back/card_back.png")
        current_label = PATH_TO_LABEL.get(current_path, "Clássico")

        self.card_back_dd = ft.Dropdown(
            label="Traseira das cartas",
            value=current_label,
            options=[ft.dropdown.Option(text=label) for label, _ in CARD_BACK_OPTIONS],
        )

        self.music_slider = ft.Slider(
            min=0, max=1, divisions=10,
            value=float(settings.get("music_volume", 0.5)), label="{value}"
        )

        self.sfx_slider = ft.Slider(
            min=0, max=1, divisions=10,
            value=float(settings.get("sfx_volume", 0.8)), label="{value}"
        )

        # --- VOLTAR INTELIGENTE ---
        def go_back(e):
            if getattr(self, "game_in_progress", False):
                self._build_pause_menu()
            else:
                self._build_main_menu()

        self._set_panel(
            "Opções",
            [
                ft.Text("Música de Fundo", size=14, color="#E5E7EB"),
                self.music_slider,
                ft.Text("Efeitos Sonoros", size=14, color="#E5E7EB"),
                self.sfx_slider,
                self.card_back_dd,
                self._primary_btn("Aplicar", self._apply_settings),
                self._secondary_btn("Voltar", go_back),
            ],
        )

    def _apply_settings(self, e):
        selected_label = self.card_back_dd.value
        selected_path = LABEL_TO_PATH.get(selected_label)

        if not selected_path and self.card_back_dd.selected_index is not None:
            try:
                selected_path = CARD_BACK_OPTIONS[self.card_back_dd.selected_index][1]
            except Exception:
                selected_path = None

        if not selected_path:
            selected_path = "/images/card_back/card_back.png"

        settings = load_settings(self.app_page)
        settings["card_back"] = selected_path
        settings["music_volume"] = float(self.music_slider.value)
        settings["sfx_volume"] = float(self.sfx_slider.value)
        
        save_settings(self.app_page, settings)
        self.on_apply_settings(settings)

        self.app_page.overlay.append(
            ft.SnackBar(ft.Text("Definições aplicadas com sucesso!"), open=True)
        )
        self.app_page.update()

    def _delete_slot(self, slot):
        delete_game(self.app_page, slot)
        self._build_load_menu()

    def show_main(self):
        self.visible = True
        self._build_main_menu()

    def show_pause(self):
        self.visible = True
        self._build_pause_menu()

    def hide(self):
        self.game_in_progress = True  # <-- ADICIONAR ESTA LINHA
        self.visible = False
        self.update()