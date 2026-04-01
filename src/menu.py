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
        on_set_card_back,
        on_save_slot,
        on_load_slot,
    ):
        super().__init__()
        self.app_page = page
        self.on_new_game = on_new_game
        self.on_continue = on_continue
        self.on_resume = on_resume
        self.on_quit = on_quit
        self.on_set_card_back = on_set_card_back
        self.on_save_slot = on_save_slot
        self.on_load_slot = on_load_slot

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

    def did_mount(self):
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
        self._set_panel(
            "Start",
            [
                ft.ElevatedButton("Novo Jogo", on_click=lambda e: self.on_new_game()),
                ft.ElevatedButton("Continuar", on_click=lambda e: self._build_load_menu()),
                ft.OutlinedButton("Voltar", on_click=lambda e: self._build_main_menu()),
            ],
        )

    def _build_pause_menu(self):
        self.mode = "pause"
        self._set_panel(
            "Pausa",
            [
                ft.ElevatedButton("Continuar", on_click=lambda e: self.on_resume()),
                ft.ElevatedButton("Novo Jogo", on_click=lambda e: self.on_new_game()),
                ft.ElevatedButton("Salvar Jogo", on_click=lambda e: self._build_save_menu()),
                ft.ElevatedButton("Carregar Jogo", on_click=lambda e: self._build_load_menu()),
                ft.OutlinedButton("Opções", on_click=lambda e: self._build_options_menu()),
                ft.OutlinedButton("Menu Inicial", on_click=lambda e: self._build_main_menu()),
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
                on_click=lambda e, slot=s["slot"]: self.on_load_slot(slot),
            )
            controls.append(btn_load)

            btn_delete = ft.OutlinedButton(
                f"Apagar {title}",
                disabled=s["data"] is None,
                on_click=lambda e, slot=s["slot"]: self._delete_slot(slot),
            )
            controls.append(btn_delete)

        controls.append(ft.OutlinedButton("Voltar", on_click=lambda e: self._build_start_menu()))
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
                on_click=lambda e, slot=s["slot"]: self.on_save_slot(slot),
            )
            controls.append(btn)

        controls.append(ft.OutlinedButton("Voltar", on_click=lambda e: self._build_pause_menu()))
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

        self._set_panel(
            "Opções",
            [
                self.card_back_dd,
                ft.ElevatedButton("Aplicar", on_click=self._apply_card_back),
                ft.OutlinedButton("Voltar", on_click=lambda e: self._build_main_menu()),
            ],
        )

    def _apply_card_back(self, e):
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
        save_settings(self.app_page, settings)
        self.on_set_card_back(selected_path)

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
        self.visible = False
        self.update()