import flet as ft
from datetime import datetime
import database as db
import validators
import reports
import sqlite3
import os


def main_view(page):
    # Barra de navegación lateral
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD,
                selected_icon=ft.Icons.DASHBOARD,
                label="Dashboard"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.ACCOUNT_BALANCE_WALLET,
                selected_icon=ft.Icons.ACCOUNT_BALANCE_WALLET,
                label="Transacciones"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CATEGORY,
                selected_icon=ft.Icons.CATEGORY,
                label="Categorías"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PIE_CHART,
                selected_icon=ft.Icons.PIE_CHART,
                label="Gráficos"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.NOTIFICATIONS,
                selected_icon=ft.Icons.NOTIFICATIONS,
                label="Alertas"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS,
                selected_icon=ft.Icons.SETTINGS,
                label="Configuración"
            ),
        ],
        on_change=lambda e: cambiar_pantalla(e.control.selected_index)
    )

    # Contenedor principal
    main_content = ft.Container(expand=True, padding=20)

    # Función para cambiar pantallas
    def cambiar_pantalla(index):
        main_content.content = None
        page.update()

        if index == 0:
            main_content.content = dashboard_view(page)
        elif index == 1:
            main_content.content = transacciones_view(page)
        elif index == 2:
            main_content.content = categorias_view(page)
        elif index == 3:
            main_content.content = graficos_view(page)
        elif index == 4:
            main_content.content = alertas_view(page)
        elif index == 5:
            main_content.content = configuracion_view(page)

        page.update()

    # Inicializar con dashboard
    main_content.content = dashboard_view(page)

    return ft.Row([
        rail,
        ft.VerticalDivider(width=1),
        main_content
    ], expand=True)


def dashboard_view(page):
    # Obtener datos del dashboard
    resumen = db.get_resumen_mes()
    ultimas_transacciones = db.get_ultimas_transacciones(5)
    alertas = db.get_alertas_no_leidas()

    # Tarjetas de resumen
    tarjetas = ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Text("Saldo Actual", size=14, color=ft.Colors.GREY_600),
                ft.Text(f"${resumen['saldo']:.2f}", size=28, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN if resumen['saldo'] >= 0 else ft.Colors.RED)
            ]),
            padding=20,
            bgcolor=ft.Colors.ON_SURFACE_VARIANT,
            border_radius=12,
            expand=1
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("Ingresos Mensuales", size=14, color=ft.Colors.GREY_600),
                ft.Text(f"${resumen['ingresos']:.2f}", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN)
            ]),
            padding=20,
            bgcolor=ft.Colors.ON_SURFACE_VARIANT,
            border_radius=12,
            expand=1
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("Gastos Mensuales", size=14, color=ft.Colors.GREY_600),
                ft.Text(f"${resumen['gastos']:.2f}", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.RED)
            ]),
            padding=20,
            bgcolor=ft.Colors.ON_SURFACE_VARIANT,
            border_radius=12,
            expand=1
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("Alertas Activas", size=14, color=ft.Colors.GREY_600),
                ft.Text(str(len(alertas)), size=28, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ORANGE if len(alertas) > 0 else ft.Colors.GREY)
            ]),
            padding=20,
            bgcolor=ft.Colors.ON_SURFACE_VARIANT,
            border_radius=12,
            expand=1
        ),
    ], spacing=20)

    # Últimas transacciones
    transacciones_widgets = []
    for t in ultimas_transacciones:
        icon = ft.Icons.TRENDING_UP if t[5] == 'ingreso' else ft.Icons.TRENDING_DOWN
        color = ft.Colors.GREEN if t[5] == 'ingreso' else ft.Colors.RED

        transacciones_widgets.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(icon, color=color),
                        ft.Column([
                            ft.Text(t[2] or "Sin descripción", weight=ft.FontWeight.BOLD),
                            ft.Row([
                                ft.Text(t[3], size=12, color=ft.Colors.GREY_600),
                                ft.Text(f"${t[1]:.2f}", size=14, weight=ft.FontWeight.BOLD, color=color),
                            ], spacing=10)
                        ], expand=True),
                        ft.Text(t[4], size=12, color=ft.Colors.GREY_600)
                    ]),
                    padding=15
                )
            )
        )

    # Función para mostrar alertas
    def mostrar_alerta(titulo, mensaje, es_error=True):
        dialog = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton("OK", on_click=lambda e: setattr(page.dialog, 'open', False))
            ]
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    # Botón para agregar transacción rápida
    def mostrar_form_rapido(e):
        monto_field = ft.TextField(label="Monto", keyboard_type=ft.KeyboardType.NUMBER)
        desc_field = ft.TextField(label="Descripción")
        tipo_dropdown = ft.Dropdown(
            label="Tipo",
            options=[
                ft.dropdown.Option("ingreso", "Ingreso"),
                ft.dropdown.Option("gasto", "Gasto")
            ],
            value="gasto"
        )

        def guardar_rapido(e):
            try:
                monto = float(monto_field.value)
                desc = desc_field.value
                tipo = tipo_dropdown.value

                if monto <= 0 or not desc:
                    mostrar_alerta("Error", "Complete todos los campos")
                    return

                # Usar categoría por defecto (1 = Alimentación)
                db.agregar_transaccion(monto, desc, 1, datetime.now().strftime("%Y-%m-%d"), tipo)

                page.dialog.open = False
                mostrar_alerta("Éxito", "Transacción agregada", es_error=False)

                # Recargar dashboard
                page.update()
                main_content.content = dashboard_view(page)
                page.update()

            except Exception as ex:
                mostrar_alerta("Error", f"No se pudo guardar: {str(ex)}")

        dialog = ft.AlertDialog(
            title=ft.Text("Nueva Transacción Rápida"),
            content=ft.Column([
                monto_field,
                desc_field,
                tipo_dropdown
            ], height=180),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False)),
                ft.TextButton("Guardar", on_click=guardar_rapido)
            ]
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    # Gráfico simple
    chart = ft.BarChart(
        bar_groups=[
            ft.BarChartGroup(
                x=0,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=resumen['ingresos'] / 100,
                        width=20,
                        color=ft.Colors.GREEN,
                        border_radius=0,
                    ),
                ],
            ),
            ft.BarChartGroup(
                x=1,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=resumen['gastos'] / 100,
                        width=20,
                        color=ft.Colors.RED,
                        border_radius=0,
                    ),
                ],
            ),
        ],
        border=ft.border.all(1, ft.Colors.GREY_400),
        left_axis=ft.ChartAxis(
            labels_size=40,
        ),
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(
                    value=0,
                    label=ft.Container(ft.Text("Ingresos"), padding=10),
                ),
                ft.ChartAxisLabel(
                    value=1,
                    label=ft.Container(ft.Text("Gastos"), padding=10),
                ),
            ],
            labels_size=40,
        ),
        horizontal_grid_lines=ft.ChartGridLines(
            color=ft.Colors.GREY_300,
            width=1,
            dash_pattern=[3, 3],
        ),
        tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.GREY_900),
        interactive=True,
        expand=True,
        height=200
    )

    return ft.Column([
        ft.Row([
            ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("+ Transacción Rápida", on_click=mostrar_form_rapido,
                              icon=ft.Icons.ADD, bgcolor=ft.Colors.PRIMARY)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        tarjetas,
        ft.Row([
            ft.Column([
                ft.Text("Últimas Transacciones", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column(transacciones_widgets, spacing=8),
                    padding=15,
                    bgcolor=ft.Colors.SURFACE,
                    border_radius=12,
                    expand=True
                )
            ], expand=2),
            ft.Column([
                ft.Text("Ingresos vs Gastos", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=chart,
                    padding=15,
                    bgcolor=ft.Colors.SURFACE,
                    border_radius=12,
                    expand=True
                )
            ], expand=1),
        ], spacing=20, expand=True)
    ], spacing=20, scroll=ft.ScrollMode.AUTO)


def transacciones_view(page):
    # Variables para el formulario
    monto_field = ft.TextField(label="Monto", keyboard_type=ft.KeyboardType.NUMBER, width=150)
    descripcion_field = ft.TextField(label="Descripción", width=250)

    # Dropdown para categorías
    categorias = db.get_categorias()
    categoria_dropdown = ft.Dropdown(
        label="Categoría",
        options=[ft.dropdown.Option(str(cat[0]), cat[1]) for cat in categorias],
        width=200
    )

    # Tipo de transacción
    tipo_dropdown = ft.Dropdown(
        label="Tipo",
        options=[
            ft.dropdown.Option("gasto", "Gasto"),
            ft.dropdown.Option("ingreso", "Ingreso")
        ],
        width=150
    )

    # Fecha
    fecha_field = ft.TextField(
        label="Fecha",
        value=datetime.now().strftime("%Y-%m-%d"),
        width=150
    )

    # Tabla de transacciones
    tabla_transacciones = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Fecha")),
            ft.DataColumn(ft.Text("Descripción")),
            ft.DataColumn(ft.Text("Categoría")),
            ft.DataColumn(ft.Text("Monto")),
            ft.DataColumn(ft.Text("Tipo")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[]
    )

    # Funciones auxiliares
    def mostrar_alerta(titulo, mensaje, es_error=True):
        dialog = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton("OK", on_click=lambda e: setattr(page.dialog, 'open', False))
            ]
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    def cargar_transacciones():
        transacciones = db.get_transacciones()
        rows = []

        for t in transacciones:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(t[0]))),
                        ft.DataCell(ft.Text(t[4])),
                        ft.DataCell(ft.Text(t[2] or "")),
                        ft.DataCell(ft.Text(t[3] or "")),
                        ft.DataCell(ft.Text(f"${t[1]:.2f}",
                                            color=ft.Colors.GREEN if t[5] == 'ingreso' else ft.Colors.RED)),
                        ft.DataCell(ft.Text("Ingreso" if t[5] == 'ingreso' else "Gasto")),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(ft.Icons.DELETE, icon_size=20,
                                              on_click=lambda e, tid=t[0]: eliminar_transaccion(tid)),
                            ], spacing=5)
                        ),
                    ]
                )
            )

        tabla_transacciones.rows = rows
        page.update()

    def agregar_transaccion(e):
        # Validaciones
        if not monto_field.value:
            mostrar_alerta("Error", "Ingrese un monto")
            return

        if not descripcion_field.value:
            mostrar_alerta("Error", "Ingrese una descripción")
            return

        if not categoria_dropdown.value:
            mostrar_alerta("Error", "Seleccione una categoría")
            return

        if not tipo_dropdown.value:
            mostrar_alerta("Error", "Seleccione un tipo")
            return

        try:
            # Agregar a BD
            db.agregar_transaccion(
                float(monto_field.value),
                descripcion_field.value,
                int(categoria_dropdown.value),
                fecha_field.value,
                tipo_dropdown.value
            )

            # Limpiar campos
            monto_field.value = ""
            descripcion_field.value = ""
            categoria_dropdown.value = None

            # Recargar tabla
            cargar_transacciones()

            # Mostrar mensaje
            mostrar_alerta("Éxito", "Transacción agregada correctamente", es_error=False)

        except Exception as ex:
            mostrar_alerta("Error", f"No se pudo guardar: {str(ex)}")

    def eliminar_transaccion(transaccion_id):
        def confirmar_eliminar(e):
            db.eliminar_transaccion(transaccion_id)
            cargar_transacciones()
            page.dialog.open = False
            page.update()
            mostrar_alerta("Éxito", "Transacción eliminada", es_error=False)

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Está seguro de eliminar esta transacción?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False)),
                ft.TextButton("Eliminar", on_click=confirmar_eliminar)
            ]
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    def exportar_excel(e):
        try:
            archivo = reports.exportar_a_excel()
            mostrar_alerta("Éxito", f"Exportado a: {archivo}", es_error=False)
        except Exception as ex:
            mostrar_alerta("Error", f"No se pudo exportar: {str(ex)}")

    def exportar_pdf(e):
        try:
            archivo = reports.exportar_a_pdf()
            mostrar_alerta("Éxito", f"Exportado a: {archivo}", es_error=False)
        except Exception as ex:
            mostrar_alerta("Error", f"No se pudo exportar: {str(ex)}")

    # Cargar datos iniciales
    cargar_transacciones()

    return ft.Column([
        ft.Text("Transacciones", size=28, weight=ft.FontWeight.BOLD),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Nueva Transacción", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        monto_field,
                        descripcion_field,
                        categoria_dropdown,
                        tipo_dropdown,
                        fecha_field,
                        ft.ElevatedButton("Agregar", on_click=agregar_transaccion,
                                          icon=ft.Icons.ADD)
                    ], wrap=True, spacing=10)
                ], spacing=10),
                padding=20
            )
        ),
        ft.Divider(),
        ft.Row([
            ft.Text("Historial de Transacciones", size=20, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("Exportar a Excel", icon=ft.Icons.DOWNLOAD,
                              on_click=exportar_excel),
            ft.ElevatedButton("Exportar a PDF", icon=ft.Icons.PICTURE_AS_PDF,
                              on_click=exportar_pdf),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(
            content=ft.Column([tabla_transacciones], scroll=ft.ScrollMode.AUTO),
            height=400,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=8,
            padding=10
        )
    ], spacing=20, scroll=ft.ScrollMode.AUTO)


def categorias_view(page):
    categorias = db.get_categorias()

    # Formulario para nueva categoría
    nombre_field = ft.TextField(label="Nombre", width=200)
    tipo_dropdown = ft.Dropdown(
        label="Tipo",
        options=[
            ft.dropdown.Option("ingreso", "Ingreso"),
            ft.dropdown.Option("gasto", "Gasto")
        ],
        width=150
    )
    color_field = ft.TextField(label="Color (hex)", value="#795548", width=150)
    presupuesto_field = ft.TextField(label="Presupuesto", keyboard_type=ft.KeyboardType.NUMBER, width=150)

    # Tabla de categorías
    tabla_categorias = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Tipo")),
            ft.DataColumn(ft.Text("Color")),
            ft.DataColumn(ft.Text("Presupuesto")),
        ],
        rows=[]
    )

    def mostrar_alerta(titulo, mensaje, es_error=True):
        dialog = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton("OK", on_click=lambda e: setattr(page.dialog, 'open', False))
            ]
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    def cargar_categorias():
        rows = []
        for cat in categorias:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(cat[0]))),
                        ft.DataCell(ft.Text(cat[1])),
                        ft.DataCell(
                            ft.Container(
                                ft.Text("Ingreso" if cat[2] == 'ingreso' else "Gasto",
                                        color=ft.Colors.WHITE),
                                padding=5,
                                border_radius=5,
                                bgcolor=ft.Colors.GREEN if cat[2] == 'ingreso' else ft.Colors.RED
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                width=20,
                                height=20,
                                border_radius=10,
                                bgcolor=cat[3] if cat[3] else "#795548"
                            )
                        ),
                        ft.DataCell(ft.Text(f"${cat[4]:.2f}" if cat[4] > 0 else "Sin límite")),
                    ]
                )
            )
        tabla_categorias.rows = rows
        page.update()

    def agregar_categoria(e):
        if not nombre_field.value:
            mostrar_alerta("Error", "Ingrese un nombre")
            return

        try:
            presupuesto = float(presupuesto_field.value or 0)
            db.agregar_categoria(
                nombre_field.value,
                tipo_dropdown.value or "gasto",
                color_field.value,
                presupuesto
            )

            nombre_field.value = ""
            presupuesto_field.value = ""

            # Recargar categorías
            nonlocal categorias
            categorias = db.get_categorias()
            cargar_categorias()

            mostrar_alerta("Éxito", "Categoría agregada", es_error=False)

        except Exception as ex:
            mostrar_alerta("Error", f"No se pudo agregar: {str(ex)}")

    # Cargar datos iniciales
    cargar_categorias()

    return ft.Column([
        ft.Text("Categorías", size=28, weight=ft.FontWeight.BOLD),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Nueva Categoría", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        nombre_field,
                        tipo_dropdown,
                        color_field,
                        presupuesto_field,
                        ft.ElevatedButton("Agregar", on_click=agregar_categoria,
                                          icon=ft.Icons.ADD)
                    ], wrap=True, spacing=10)
                ], spacing=10),
                padding=20
            )
        ),
        ft.Divider(),
        ft.Text("Lista de Categorías", size=20, weight=ft.FontWeight.BOLD),
        ft.Container(
            content=ft.Column([tabla_categorias], scroll=ft.ScrollMode.AUTO),
            height=400,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=8,
            padding=10
        )
    ], spacing=20, scroll=ft.ScrollMode.AUTO)


def graficos_view(page):
    # Obtener datos para gráficos
    gastos_por_categoria = db.get_gastos_por_categoria()
    resumen = db.get_resumen_mes()

    # Gráfico de torta para gastos
    pie_chart_sections = []
    if gastos_por_categoria:
        for categoria in gastos_por_categoria:
            if categoria[2]:  # Si tiene valor
                pie_chart_sections.append(
                    ft.PieChartSection(
                        categoria[2] or 0,
                        title=f"{categoria[0]}\n${categoria[2]:.0f}",
                        color=categoria[1] if categoria[1] else ft.Colors.BLUE,
                        radius=80
                    )
                )

    pie_chart = ft.PieChart(
        sections=pie_chart_sections,
        sections_space=1,
        center_space_radius=40,
        height=300
    ) if pie_chart_sections else ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.PIE_CHART, size=50, color=ft.Colors.GREY_400),
            ft.Text("No hay datos para mostrar", color=ft.Colors.GREY_600)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=50,
        alignment=ft.alignment.center
    )

    # Gráfico de barras para ingresos vs gastos
    bar_chart = ft.BarChart(
        bar_groups=[
            ft.BarChartGroup(
                x=0,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=resumen['ingresos'] / 100 if resumen['ingresos'] > 0 else 1,
                        width=30,
                        color=ft.Colors.GREEN,
                        border_radius=0,
                    ),
                ],
            ),
            ft.BarChartGroup(
                x=1,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=resumen['gastos'] / 100 if resumen['gastos'] > 0 else 1,
                        width=30,
                        color=ft.Colors.RED,
                        border_radius=0,
                    ),
                ],
            ),
        ],
        border=ft.border.all(1, ft.Colors.GREY_400),
        left_axis=ft.ChartAxis(labels_size=40),
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(value=0, label=ft.Text("Ingresos")),
                ft.ChartAxisLabel(value=1, label=ft.Text("Gastos")),
            ],
            labels_size=40,
        ),
        horizontal_grid_lines=ft.ChartGridLines(
            color=ft.Colors.GREY_300,
            width=1,
            dash_pattern=[3, 3],
        ),
        tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.GREY_900),
        interactive=True,
        expand=True,
        height=300
    )

    # Botón para actualizar gráficos
    def actualizar_graficos(e):
        page.update()

    return ft.Column([
        ft.Row([
            ft.Text("Gráficos y Estadísticas", size=28, weight=ft.FontWeight.BOLD),
            ft.IconButton(ft.Icons.REFRESH, on_click=actualizar_graficos,
                          tooltip="Actualizar gráficos")
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([
            ft.Column([
                ft.Text("Distribución de Gastos por Categoría", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=pie_chart,
                    padding=20,
                    bgcolor=ft.Colors.SURFACE,
                    border_radius=12,
                    alignment=ft.alignment.center,
                    height=350
                )
            ], expand=1),
            ft.Column([
                ft.Text("Ingresos vs Gastos (Mes Actual)", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=bar_chart,
                    padding=20,
                    bgcolor=ft.Colors.SURFACE,
                    border_radius=12,
                    alignment=ft.alignment.center,
                    height=350
                )
            ], expand=1),
        ], spacing=20),
        ft.Divider(),
        ft.Text("Resumen Estadístico", size=20, weight=ft.FontWeight.BOLD),
        ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Métrica")),
                ft.DataColumn(ft.Text("Valor")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Total Ingresos")),
                    ft.DataCell(ft.Text(f"${resumen['ingresos']:.2f}", color=ft.Colors.GREEN)),
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Total Gastos")),
                    ft.DataCell(ft.Text(f"${resumen['gastos']:.2f}", color=ft.Colors.RED)),
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Saldo Neto")),
                    ft.DataCell(ft.Text(f"${resumen['saldo']:.2f}",
                                        color=ft.Colors.GREEN if resumen['saldo'] >= 0 else ft.Colors.RED)),
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Número de Categorías")),
                    ft.DataCell(ft.Text(str(len(gastos_por_categoria)))),
                ]),
            ]
        )
    ], spacing=20, scroll=ft.ScrollMode.AUTO)


def alertas_view(page):
    # Lista de alertas
    lista_alertas = ft.Column()

    def mostrar_alerta(titulo, mensaje, es_error=True):
        dialog = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton("OK", on_click=lambda e: setattr(page.dialog, 'open', False))
            ]
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    def cargar_alertas():
        lista_alertas.controls.clear()
        alertas = db.get_alertas_no_leidas()  # Variable local

        if not alertas:
            lista_alertas.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=50, color=ft.Colors.GREEN),
                        ft.Text("No hay alertas pendientes", size=16)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40,
                    alignment=ft.alignment.center
                )
            )
        else:
            for alerta in alertas:
                icono = ft.Icons.WARNING
                color = ft.Colors.ORANGE

                if "exceso" in str(alerta[2]).lower():
                    icono = ft.Icons.ERROR
                    color = ft.Colors.RED
                elif "alerta" in str(alerta[2]).lower():
                    icono = ft.Icons.INFO
                    color = ft.Colors.BLUE

                lista_alertas.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row([
                                ft.Icon(icono, color=color),
                                ft.Column([
                                    ft.Text(alerta[1], weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Fecha: {alerta[3]}", size=12, color=ft.Colors.GREY_600)
                                ], expand=True),
                                ft.IconButton(
                                    ft.Icons.CLOSE,
                                    on_click=lambda e, aid=alerta[0]: marcar_como_leida(aid)
                                )
                            ]),
                            padding=15
                        )
                    )
                )

    def marcar_como_leida(alerta_id):
        db.marcar_alerta_leida(alerta_id)
        cargar_alertas()  # Simplemente recargar
        page.update()
        mostrar_alerta("Información", "Alerta marcada como leída", es_error=False)

    def marcar_todas_leidas(e):
        alertas = db.get_alertas_no_leidas()
        for alerta in alertas:
            db.marcar_alerta_leida(alerta[0])
        cargar_alertas()  # Simplemente recargar
        page.update()
        mostrar_alerta("Éxito", "Todas las alertas marcadas como leídas", es_error=False)

    # Cargar alertas iniciales
    cargar_alertas()

    return ft.Column([
        ft.Row([
            ft.Text("Sistema de Alertas", size=28, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("Marcar todas como leídas",
                              icon=ft.Icons.CHECKLIST,
                              on_click=marcar_todas_leidas)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Container(
            content=lista_alertas,
            height=500,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=8,
            padding=10
        ),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Configurar Alertas", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Las alertas se generan automáticamente cuando:", size=14),
                    ft.Column([
                        ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=16),
                                ft.Text("Se excede el presupuesto de una categoría")]),
                        ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=16),
                                ft.Text("Se alcanza el 80% del presupuesto")]),
                    ], spacing=5)
                ]),
                padding=20
            )
        )
    ], spacing=20, scroll=ft.ScrollMode.AUTO)


def configuracion_view(page):
    def mostrar_alerta(titulo, mensaje, es_error=True):
        dialog = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton("OK", on_click=lambda e: setattr(page.dialog, 'open', False))
            ]
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    def cambiar_tema(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            boton_tema.text = "Cambiar a Tema Claro"
            boton_tema.icon = ft.Icons.LIGHT_MODE
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            boton_tema.text = "Cambiar a Tema Oscuro"
            boton_tema.icon = ft.Icons.DARK_MODE
        page.update()

    boton_tema = ft.ElevatedButton(
        "Cambiar a Tema Oscuro" if page.theme_mode == ft.ThemeMode.LIGHT else "Cambiar a Tema Claro",
        icon=ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE,
        on_click=cambiar_tema
    )

    def exportar_datos(e):
        try:
            archivo_excel = reports.exportar_a_excel()
            archivo_pdf = reports.exportar_a_pdf()

            mostrar_alerta("Exportación Exitosa",
                           f"Se han exportado los datos a:\n• {archivo_excel}\n• {archivo_pdf}",
                           es_error=False)
        except Exception as ex:
            mostrar_alerta("Error", f"Error al exportar: {str(ex)}")

    def limpiar_base_datos(e):
        def confirmar_limpieza(e):
            try:
                conn = sqlite3.connect('finanzas.db')
                cursor = conn.cursor()
                cursor.execute('DELETE FROM transacciones')
                cursor.execute('DELETE FROM alertas')
                conn.commit()
                conn.close()

                mostrar_alerta("Base de datos limpiada",
                               "Todos los datos han sido eliminados.",
                               es_error=False)
                page.update()
            except Exception as ex:
                mostrar_alerta("Error", f"No se pudo limpiar: {str(ex)}")

        dialog = ft.AlertDialog(
            title=ft.Text("¡ADVERTENCIA!"),
            content=ft.Text("Esta acción eliminará TODOS los datos. ¿Está seguro?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False)),
                ft.TextButton("Confirmar", on_click=confirmar_limpieza)
            ]
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    return ft.Column([
        ft.Text("Configuración", size=28, weight=ft.FontWeight.BOLD),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Apariencia", size=20, weight=ft.FontWeight.BOLD),
                    boton_tema,
                    ft.Divider(),
                    ft.Text("Exportación de Datos", size=20, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("Exportar Todo a Excel/PDF",
                                      icon=ft.Icons.DOWNLOAD,
                                      on_click=exportar_datos),
                    ft.Divider(),
                    ft.Text("Mantenimiento", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
                    ft.Text("Esta sección contiene acciones destructivas",
                            size=14, color=ft.Colors.RED),
                    ft.ElevatedButton("Limpiar Base de Datos",
                                      icon=ft.Icons.DELETE_FOREVER,
                                      color=ft.Colors.RED,
                                      on_click=limpiar_base_datos),
                ], spacing=15),
                padding=20
            )
        ),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Información del Sistema", size=20, weight=ft.FontWeight.BOLD),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Componente")),
                            ft.DataColumn(ft.Text("Estado")),
                        ],
                        rows=[
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text("Base de Datos")),
                                ft.DataCell(ft.Text("SQLite - Conectado", color=ft.Colors.GREEN)),
                            ]),
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text("Exportación Excel")),
                                ft.DataCell(ft.Text("openpyxl - Disponible", color=ft.Colors.GREEN)),
                            ]),
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text("Exportación PDF")),
                                ft.DataCell(ft.Text("reportlab - Disponible", color=ft.Colors.GREEN)),
                            ]),
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text("Versión Flet")),
                                ft.DataCell(ft.Text("0.20.0 o superior")),
                            ]),
                        ]
                    )
                ]),
                padding=20
            )
        )
    ], spacing=20, scroll=ft.ScrollMode.AUTO)