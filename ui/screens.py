import flet as ft
from datetime import datetime
import database as db
import validators
from ui.components import *
import reports


def main_view(page):
    # Barra de navegación lateral
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Dashboard"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                selected_icon=ft.Icons.ACCOUNT_BALANCE_WALLET,
                label="Transacciones"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CATEGORY_OUTLINED,
                selected_icon=ft.Icons.CATEGORY,
                label="Categorías"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PIE_CHART_OUTLINE,
                selected_icon=ft.Icons.PIE_CHART,
                label="Gráficos"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                selected_icon=ft.Icons.NOTIFICATIONS,
                label="Alertas"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
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
            main_content.content = dashboard_view()
        elif index == 1:
            main_content.content = transacciones_view()
        elif index == 2:
            main_content.content = categorias_view()
        elif index == 3:
            main_content.content = graficos_view()
        elif index == 4:
            main_content.content = alertas_view()
        elif index == 5:
            main_content.content = configuracion_view()

        page.update()

    # Inicializar con dashboard
    main_content.content = dashboard_view()

    return ft.Row([
        rail,
        ft.VerticalDivider(width=1),
        main_content
    ], expand=True)


def dashboard_view():
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
                        color=ft.colors.ORANGE if len(alertas) > 0 else ft.Colors.GREY)
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
        transacciones_widgets.append(TransactionCard(t))

    # Gráfico simple (placeholder)
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
        ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD),
        tarjetas,
        ft.Row([
            ft.Column([
                ft.Text("Últimas Transacciones", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column(transacciones_widgets),
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


def transacciones_view():
    # Variables para el formulario
    monto_field = CustomTextField("Monto", keyboard_type=ft.KeyboardType.NUMBER)
    descripcion_field = CustomTextField("Descripción")

    # Dropdown para categorías
    categorias = db.get_categorias()
    categoria_dropdown = ft.Dropdown(
        label="Categoría",
        options=[ft.dropdown.Option(c[0], c[1]) for c in enumerate([cat[1] for cat in categorias], start=1)],
        width=200,
        border_radius=8
    )

    # Tipo de transacción
    tipo_dropdown = ft.Dropdown(
        label="Tipo",
        options=[
            ft.dropdown.Option("gasto", "Gasto"),
            ft.dropdown.Option("ingreso", "Ingreso")
        ],
        width=150,
        border_radius=8
    )

    # Fecha
    fecha_field = ft.TextField(
        label="Fecha",
        value=datetime.now().strftime("%Y-%m-%d"),
        width=150,
        border_radius=8
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
                                ft.IconButton(ft.Icons.EDIT, icon_size=20),
                                ft.IconButton(ft.Icons.DELETE, icon_size=20,
                                              on_click=lambda e, tid=t[0]: eliminar_transaccion(tid)),
                            ], spacing=5)
                        ),
                    ]
                )
            )

        tabla_transacciones.rows = rows

    def agregar_transaccion(e):
        # Validaciones
        valido, mensaje = validators.validar_monto(monto_field.value)
        if not valido:
            mostrar_alerta("Error", mensaje)
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

        # Recargar tabla
        cargar_transacciones()

        # Mostrar mensaje
        mostrar_alerta("Éxito", "Transacción agregada correctamente", es_error=False)

    def eliminar_transaccion(transaccion_id):
        def confirmar_eliminar(e):
            db.eliminar_transaccion(transaccion_id)
            cargar_transacciones()
            page.dialog.open = False
            page.update()

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
                        CustomElevatedButton("Agregar", agregar_transaccion)
                    ], wrap=True, spacing=10)
                ], spacing=10),
                padding=20
            )
        ),
        ft.Divider(),
        ft.Row([
            ft.Text("Historial de Transacciones", size=20, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("Exportar a Excel", icon=ft.Icons.DOWNLOAD,
                              on_click=lambda e: reports.exportar_a_excel()),
            ft.ElevatedButton("Exportar a PDF", icon=ft.Icons.PICTURE_AS_PDF,
                              on_click=lambda e: reports.exportar_a_pdf()),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(
            content=ft.Column([tabla_transacciones], scroll=ft.ScrollMode.AUTO),
            height=400,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=8,
            padding=10
        )
    ], spacing=20, scroll=ft.ScrollMode.AUTO)


def categorias_view():
    categorias = db.get_categorias()

    # Formulario para nueva categoría
    nombre_field = CustomTextField("Nombre")
    tipo_dropdown = ft.Dropdown(
        label="Tipo",
        options=[
            ft.dropdown.Option("ingreso", "Ingreso"),
            ft.dropdown.Option("gasto", "Gasto")
        ],
        width=150
    )
    color_field = ft.TextField(label="Color (hex)", value="#795548", width=150)
    presupuesto_field = CustomTextField("Presupuesto", keyboard_type=ft.KeyboardType.NUMBER)

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

    def agregar_categoria(e):
        if not nombre_field.value:
            return

        db.agregar_categoria(
            nombre_field.value,
            tipo_dropdown.value or "gasto",
            color_field.value,
            float(presupuesto_field.value or 0)
        )

        nombre_field.value = ""
        presupuesto_field.value = ""
        cargar_categorias()

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
                        CustomElevatedButton("Agregar", agregar_categoria)
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


def graficos_view():
    # Obtener datos para gráficos
    gastos_por_categoria = db.get_gastos_por_categoria()
    resumen = db.get_resumen_mes()

    # Gráfico de torta para gastos
    pie_chart_sections = []
    if gastos_por_categoria:
        for categoria in gastos_por_categoria:
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
    )

    # Gráfico de barras para ingresos vs gastos
    bar_chart = ft.BarChart(
        bar_groups=[
            ft.BarChartGroup(
                x=0,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=resumen['ingresos'] / 100,
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
                        to_y=resumen['gastos'] / 100,
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

    return ft.Column([
        ft.Text("Gráficos y Estadísticas", size=28, weight=ft.FontWeight.BOLD),
        ft.Row([
            ft.Column([
                ft.Text("Distribución de Gastos por Categoría", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=pie_chart,
                    padding=20,
                    bgcolor=ft.Colors.SURFACE,
                    border_radius=12,
                    alignment=ft.alignment.center
                )
            ], expand=1),
            ft.Column([
                ft.Text("Ingresos vs Gastos (Mes Actual)", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=bar_chart,
                    padding=20,
                    bgcolor=ft.Colors.SURFACE,
                    border_radius=12,
                    alignment=ft.alignment.center
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


def alertas_view():
    alertas = db.get_alertas_no_leidas()

    # Lista de alertas
    lista_alertas = ft.Column()

    def cargar_alertas():
        lista_alertas.controls.clear()

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

                if "exceso" in alerta[2].lower():
                    icono = ft.Icons.ERROR
                    color = ft.Colors.RED
                elif "alerta" in alerta[2].lower():
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
        cargar_alertas()
        page.update()

    def marcar_todas_leidas(e):
        for alerta in alertas:
            db.marcar_alerta_leida(alerta[0])
        cargar_alertas()
        page.update()

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
                        ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=16),
                                ft.Text("No hay ingresos registrados en más de 7 días")]),
                    ], spacing=5)
                ]),
                padding=20
            )
        )
    ], spacing=20, scroll=ft.ScrollMode.AUTO)


def configuracion_view():
    tema_actual = "claro"

    def cambiar_tema(e):
        nonlocal tema_actual
        if tema_actual == "claro":
            page.theme_mode = ft.ThemeMode.DARK
            tema_actual = "oscuro"
            boton_tema.text = "Cambiar a Tema Claro"
            boton_tema.icon = ft.Icons.LIGHT_MODE
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            tema_actual = "claro"
            boton_tema.text = "Cambiar a Tema Oscuro"
            boton_tema.icon = ft.Icons.DARK_MODE
        page.update()

    boton_tema = ft.ElevatedButton(
        "Cambiar a Tema Oscuro",
        icon=ft.Icons.DARK_MODE,
        on_click=cambiar_tema
    )

    def exportar_datos(e):
        try:
            archivo_excel = reports.exportar_a_excel()
            archivo_pdf = reports.exportar_a_pdf()

            dialog = ft.AlertDialog(
                title=ft.Text("Exportación Exitosa"),
                content=ft.Column([
                    ft.Text("Se han exportado los datos a:"),
                    ft.Text(f"• {archivo_excel}"),
                    ft.Text(f"• {archivo_pdf}"),
                ]),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: setattr(page.dialog, 'open', False))
                ]
            )

            page.dialog = dialog
            dialog.open = True
            page.update()
        except Exception as ex:
            print(f"Error exportando: {ex}")

    def limpiar_base_datos(e):
        def confirmar_limpieza(e):
            try:
                conn = sqlite3.connect('finanzas.db')
                cursor = conn.cursor()
                cursor.execute('DELETE FROM transacciones')
                cursor.execute('DELETE FROM alertas')
                conn.commit()
                conn.close()

                dialog2 = ft.AlertDialog(
                    title=ft.Text("Base de datos limpiada"),
                    content=ft.Text("Todos los datos han sido eliminados."),
                    actions=[
                        ft.TextButton("OK", on_click=lambda e: setattr(page.dialog, 'open', False))
                    ]
                )

                page.dialog = dialog2
                dialog2.open = True
                page.update()
            except Exception as ex:
                print(f"Error: {ex}")

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