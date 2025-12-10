import flet as ft
from datetime import datetime


class CustomTextField(ft.TextField):
    def __init__(self, label, **kwargs):
        super().__init__(
            label=label,
            border_color=ft.Colors.OUTLINE,
            focused_border_color=ft.Colors.PRIMARY,
            border_radius=8,
            **kwargs
        )


class CustomElevatedButton(ft.ElevatedButton):
    def __init__(self, text, on_click, **kwargs):
        super().__init__(
            text=text,
            on_click=on_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=12)
            ),
            **kwargs
        )


class DatePickerField(ft.Row):
    def __init__(self, label="Fecha", value=None):
        self.date_picker = ft.DatePicker()
        self.text_field = ft.TextField(
            label=label,
            value=value or datetime.now().strftime("%Y-%m-%d"),
            read_only=True,
            width=200,
            border_radius=8
        )

        self.button = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: self.date_picker.pick_date()
        )

        self.date_picker.on_change = self.on_date_change

        super().__init__(
            controls=[self.text_field, self.button],
            alignment=ft.MainAxisAlignment.START
        )

    def on_date_change(self, e):
        if self.date_picker.value:
            self.text_field.value = self.date_picker.value.strftime("%Y-%m-%d")
            self.update()

    @property
    def value(self):
        return self.text_field.value


class TransactionCard(ft.Container):
    def __init__(self, transaction):
        icon = ft.icons.TRENDING_UP if transaction[5] == 'ingreso' else ft.Icons.TRENDING_DOWN
        color = ft.colors.GREEN if transaction[5] == 'ingreso' else ft.Colors.RED

        super().__init__(
            content=ft.Row([
                ft.Icon(icon, color=color),
                ft.Column([
                    ft.Text(transaction[2] or "Sin descripción", weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Text(transaction[3], size=12, color=ft.Colors.GREY_600),
                        ft.Text(f"${transaction[1]:.2f}", size=14, weight=ft.FontWeight.BOLD, color=color),
                    ], spacing=10)
                ], expand=True),
                ft.Text(transaction[4], size=12, color=ft.Colors.GREY_600)
            ]),
            padding=10,
            border_radius=8,
            bgcolor=ft.Colors.ON_SURFACE_VARIANT,
            margin=ft.margin.only(bottom=5)
        )


class CategoryBadge(ft.Container):
    def __init__(self, nombre, color):
        super().__init__(
            content=ft.Text(nombre, size=12, color=ft.Colors.WHITE),
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            border_radius=20,
            bgcolor=color
        )


class AlertDialog(ft.AlertDialog):
    def __init__(self, title, content, on_confirm=None, on_cancel=None):
        actions = []
        if on_confirm:
            actions.append(ft.TextButton("Confirmar", on_click=on_confirm))
        if on_cancel:
            actions.append(ft.TextButton("Cancelar", on_click=on_cancel))

        super().__init__(
            title=ft.Text(title),
            content=ft.Text(content),
            actions=actions,
            modal=True
        )