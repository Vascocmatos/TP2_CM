import flet as ft
from state import load_settings, save_settings, has_savegame

CARD_BACK_OPTIONS = [
    ("/images/card_back.png", "Clássico"),
    ("/images/card_back_2.png", "Azul"),
    ("/images/card_back_3.png", "Vermelho"),
    ("/images/card_back_4.png", "Verde"),
]


class MenuOverlay(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        on_new_game,
        on_continue,
        on_resume,
        on_quit,
        on_set_card_back,
    ):
        super().__init__()
        self.app_page = page
        self.on_new_game = on_new_game
        self.on_continue = on_continue
        self.on_resume = on_resume
        self.on_quit = on_quit
        self.on_set_card_back = on_set_card_back

        self.visible = True
        self.expand = True
        self.bgcolor = "rgba(0,0,0,0.6)"
        self.alignment = ft.Alignment(0, 0)

        self.panel = ft.Container(
            width=360,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLACK_38),
        )

        self.content = self.panel
        self.mode = "main"
        # NÃO chamar build aqui

    def did_mount(self):
        # só agora está na página, então pode construir
        self._build_main_menu()

    def _set_panel(self, title, controls):
        self.panel.content = ft.Column(
            [
                ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                *controls,
            ],
            tight=True,
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
        try:
            self.update()
        except Exception:
            pass

    def _build_main_menu(self):
        self.mode = "main"
        self._set_panel(
            "Solitaire",
            [
                ft.ElevatedButton("Start", on_click=lambda e: self._build_start_menu()),
                ft.OutlinedButton("Opções", on_click=lambda e: self._build_options_menu()),
                ft.OutlinedButton("Quit", on_click=lambda e: self.on_quit()),
            ],
        )

    def _build_start_menu(self):
        self.mode = "start"
        continue_enabled = has_savegame(self.app_page)
        self._set_panel(
            "Start",
            [
                ft.ElevatedButton("Novo Jogo", on_click=lambda e: self.on_new_game()),
                ft.ElevatedButton(
                    "Continuar",
                    disabled=not continue_enabled,
                    on_click=lambda e: self.on_continue(),
                ),
                ft.OutlinedButton("Voltar", on_click=lambda e: self._build_main_menu()),
            ],
        )

    def _build_options_menu(self):
        self.mode = "options"
        settings = load_settings(self.app_page)

        self.card_back_dd = ft.Dropdown(
            label="Traseira das cartas",
            value=settings.get("card_back", "/images/card_back.png"),
            options=[
                ft.dropdown.Option(key=path, text=label)
                for path, label in CARD_BACK_OPTIONS
            ],
            on_change=self._on_change_card_back,
        )

        self._set_panel(
            "Opções",
            [
                self.card_back_dd,
                ft.OutlinedButton("Voltar", on_click=lambda e: self._build_main_menu()),
            ],
        )

    def _build_pause_menu(self):
        self.mode = "pause"
        self._set_panel(
            "Pausa",
            [
                ft.ElevatedButton("Continuar", on_click=lambda e: self.on_resume()),
                ft.OutlinedButton("Opções", on_click=lambda e: self._build_options_menu()),
                ft.OutlinedButton("Menu Inicial", on_click=lambda e: self._build_main_menu()),
            ],
        )

    def _on_change_card_back(self, e):
        settings = load_settings(self.app_page)
        settings["card_back"] = self.card_back_dd.value
        save_settings(self.app_page, settings)
        self.on_set_card_back(self.card_back_dd.value)

    def show_main(self):
        self.visible = True
        self._build_main_menu()

    def show_pause(self):
        self.visible = True
        self._build_pause_menu()

    def hide(self):
        self.visible = False
        self.update()