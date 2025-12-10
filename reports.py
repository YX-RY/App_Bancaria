import pandas as pd
from datetime import datetime
import sqlite3
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def exportar_a_excel(ruta_archivo="reporte_transacciones.xlsx", filtros=None):
    """Exporta transacciones a Excel"""
    conn = sqlite3.connect('finanzas.db')

    # Construir query con filtros
    query = '''
    SELECT t.fecha, t.descripcion, c.nombre as categoria, 
           t.monto, t.tipo, c.tipo as tipo_categoria
    FROM transacciones t
    LEFT JOIN categorias c ON t.categoria_id = c.id
    '''

    params = []
    if filtros:
        condiciones = []
        if 'fecha_inicio' in filtros:
            condiciones.append('t.fecha >= ?')
            params.append(filtros['fecha_inicio'])
        if 'fecha_fin' in filtros:
            condiciones.append('t.fecha <= ?')
            params.append(filtros['fecha_fin'])
        if 'tipo' in filtros:
            condiciones.append('t.tipo = ?')
            params.append(filtros['tipo'])

        if condiciones:
            query += ' WHERE ' + ' AND '.join(condiciones)

    query += ' ORDER BY t.fecha DESC'

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Crear archivo Excel
    with pd.ExcelWriter(ruta_archivo, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Transacciones', index=False)

        # Crear resumen
        resumen = {
            'Total Ingresos': df[df['tipo'] == 'ingreso']['monto'].sum(),
            'Total Gastos': df[df['tipo'] == 'gasto']['monto'].sum(),
            'Saldo Neto': df[df['tipo'] == 'ingreso']['monto'].sum() - df[df['tipo'] == 'gasto']['monto'].sum(),
            'Cantidad de Transacciones': len(df)
        }

        resumen_df = pd.DataFrame(list(resumen.items()), columns=['Concepto', 'Valor'])
        resumen_df.to_excel(writer, sheet_name='Resumen', index=False)

    return ruta_archivo


def exportar_a_pdf(ruta_archivo="reporte_transacciones.pdf"):
    """Exporta un resumen a PDF"""
    conn = sqlite3.connect('finanzas.db')

    # Obtener datos para el PDF
    cursor = conn.cursor()

    # Resumen del mes
    cursor.execute('''
    SELECT 
        SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE 0 END) as ingresos,
        SUM(CASE WHEN tipo = 'gasto' THEN monto ELSE 0 END) as gastos
    FROM transacciones
    WHERE strftime("%Y-%m", fecha) = strftime("%Y-%m", "now")
    ''')

    resumen = cursor.fetchone()

    # Top categorías de gastos
    cursor.execute('''
    SELECT c.nombre, SUM(t.monto) as total
    FROM transacciones t
    JOIN categorias c ON t.categoria_id = c.id
    WHERE t.tipo = 'gasto' AND strftime("%Y-%m", t.fecha) = strftime("%Y-%m", "now")
    GROUP BY c.id
    ORDER BY total DESC
    LIMIT 5
    ''')

    top_categorias = cursor.fetchall()
    conn.close()

    # Crear PDF
    doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
    elementos = []
    estilos = getSampleStyleSheet()

    # Título
    titulo = Paragraph("Reporte Financiero Mensual", estilos['Title'])
    elementos.append(titulo)
    elementos.append(Spacer(1, 12))

    # Fecha
    fecha = Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", estilos['Normal'])
    elementos.append(fecha)
    elementos.append(Spacer(1, 24))

    # Resumen
    resumen_texto = Paragraph("Resumen del Mes", estilos['Heading2'])
    elementos.append(resumen_texto)
    elementos.append(Spacer(1, 12))

    if resumen:
        datos_resumen = [
            ["Concepto", "Monto"],
            ["Total Ingresos", f"${resumen[0] or 0:.2f}"],
            ["Total Gastos", f"${resumen[1] or 0:.2f}"],
            ["Saldo Neto", f"${(resumen[0] or 0) - (resumen[1] or 0):.2f}"]
        ]

        tabla_resumen = Table(datos_resumen, colWidths=[200, 100])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elementos.append(tabla_resumen)
        elementos.append(Spacer(1, 24))

    # Top categorías
    if top_categorias:
        categorias_texto = Paragraph("Top 5 Categorías de Gastos", estilos['Heading2'])
        elementos.append(categorias_texto)
        elementos.append(Spacer(1, 12))

        datos_categorias = [["Categoría", "Total Gastado"]]
        for categoria in top_categorias:
            datos_categorias.append([categoria[0], f"${categoria[1]:.2f}"])

        tabla_categorias = Table(datos_categorias, colWidths=[300, 100])
        tabla_categorias.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elementos.append(tabla_categorias)

    # Generar PDF
    doc.build(elementos)
    return ruta_archivo