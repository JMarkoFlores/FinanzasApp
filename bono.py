import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.units import inch
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# ==================== CONFIGURACIÓN DE ESTILOS ====================
COLORES = {
    'principal': '#1f4788',
    'secundario': '#2e5c8a',
    'exito': '#28a745',
    'peligro': '#dc3545',
    'advertencia': '#ffc107',
    'info': '#17a2b8',
    'inversion': '#e74c3c',
    'cupon': '#2ecc71',
    'valor_nominal': '#3498db'
}

# ==================== FUNCIONES DE CONVERSIÓN DE TASAS ====================

def obtener_periodos_por_año(frecuencia):
    """
    Retorna el número de periodos por año según la frecuencia de pago
    """
    frecuencias = {
        "Mensual": 12,
        "Bimestral": 6,
        "Trimestral": 4,
        "Cuatrimestral": 3,
        "Semestral": 2,
        "Anual": 1
    }
    return frecuencias.get(frecuencia, 1)

def convertir_tea_a_tasa_periodica(tea, frecuencia):
    """
    Convierte una Tasa Efectiva Anual (TEA) a tasa efectiva periódica
    usando la fórmula de tasas equivalentes:
    
    TEP = (1 + TEA)^(1/n) - 1
    
    donde n es el número de periodos por año
    
    Args:
        tea (float): Tasa Efectiva Anual en decimal (ej: 0.10 para 10%)
        frecuencia (str): Frecuencia de pago del cupón
    
    Returns:
        float: Tasa efectiva periódica en decimal
    """
    n = obtener_periodos_por_año(frecuencia)
    tasa_periodica = (1 + tea) ** (1/n) - 1
    return tasa_periodica

def validar_tasa(tasa, nombre_tasa):
    """
    Valida que la tasa esté en el rango permitido (0% - 50%)
    
    Args:
        tasa (float): Tasa en decimal
        nombre_tasa (str): Nombre de la tasa para mensajes de error
    
    Returns:
        tuple: (bool, str) - (es_valida, mensaje_error)
    """
    if tasa < 0:
        return False, f"❌ {nombre_tasa} no puede ser negativa"
    if tasa > 0.50:
        return False, f"❌ {nombre_tasa} no puede ser mayor a 50%"
    return True, ""

def validar_valor_positivo(valor, nombre_campo):
    """
    Valida que un valor sea positivo
    
    Args:
        valor (float): Valor a validar
        nombre_campo (str): Nombre del campo para mensajes de error
    
    Returns:
        tuple: (bool, str) - (es_valido, mensaje_error)
    """
    if valor <= 0:
        return False, f"❌ {nombre_campo} debe ser mayor a cero"
    return True, ""

def validar_valor_positivo(valor, nombre_campo):
    """
    Valida que un valor sea positivo
    
    Args:
        valor (float): Valor a validar
        nombre_campo (str): Nombre del campo para mensajes de error
    
    Returns:
        tuple: (bool, str) - (es_valido, mensaje_error)
    """
    if valor <= 0:
        return False, f"❌ {nombre_campo} debe ser mayor a cero"
    return True, ""

# ==================== FUNCIONES DE CÁLCULO DEL BONO ====================

def calcular_cupon_periodico(valor_nominal, tasa_cupon_anual, frecuencia):
    """
    Calcula el cupón periódico del bono
    
    Args:
        valor_nominal (float): Valor nominal del bono
        tasa_cupon_anual (float): TEA del cupón en decimal
        frecuencia (str): Frecuencia de pago del cupón
    
    Returns:
        float: Cupón periódico
    """
    tasa_cupon_periodica = convertir_tea_a_tasa_periodica(tasa_cupon_anual, frecuencia)
    cupon_periodico = valor_nominal * tasa_cupon_periodica
    return cupon_periodico

def generar_flujos_de_caja(valor_nominal, cupon_periodico, num_periodos):
    """
    Genera todos los flujos de caja del bono
    
    Args:
        valor_nominal (float): Valor nominal del bono
        cupon_periodico (float): Cupón periódico
        num_periodos (int): Número total de periodos
    
    Returns:
        list: Lista de flujos de caja por periodo
    """
    flujos = []
    
    for periodo in range(1, num_periodos + 1):
        if periodo < num_periodos:
            # Periodos intermedios: solo cupón
            flujos.append(cupon_periodico)
        else:
            # Último periodo: cupón + valor nominal
            flujos.append(cupon_periodico + valor_nominal)
    
    return flujos

def calcular_valor_presente_flujos(flujos, tasa_descuento_periodica):
    """
    Calcula el valor presente de cada flujo de caja
    
    Args:
        flujos (list): Lista de flujos de caja
        tasa_descuento_periodica (float): Tasa de descuento periódica en decimal
    
    Returns:
        list: Lista de valores presentes de cada flujo
    """
    valores_presentes = []
    
    for periodo, flujo in enumerate(flujos, start=1):
        vp = flujo / ((1 + tasa_descuento_periodica) ** periodo)
        valores_presentes.append(vp)
    
    return valores_presentes

def calcular_valor_presente_bono_completo(valor_nominal, tasa_cupon_anual, frecuencia, 
                                          plazo_años, tasa_descuento_anual):
    """
    Calcula el valor presente total del bono y genera desglose completo
    
    Args:
        valor_nominal (float): Valor nominal del bono en USD
        tasa_cupon_anual (float): TEA del cupón en decimal
        frecuencia (str): Frecuencia de pago
        plazo_años (float): Plazo al vencimiento en años
        tasa_descuento_anual (float): TEA de descuento en decimal
    
    Returns:
        dict: Diccionario con todos los cálculos y resultados
    """
    # Calcular número de periodos
    periodos_por_año = obtener_periodos_por_año(frecuencia)
    num_periodos = int(plazo_años * periodos_por_año)
    
    # Convertir tasas anuales a periódicas
    tasa_cupon_periodica = convertir_tea_a_tasa_periodica(tasa_cupon_anual, frecuencia)
    tasa_descuento_periodica = convertir_tea_a_tasa_periodica(tasa_descuento_anual, frecuencia)
    
    # Calcular cupón periódico
    cupon_periodico = calcular_cupon_periodico(valor_nominal, tasa_cupon_anual, frecuencia)
    
    # Generar flujos de caja
    flujos = generar_flujos_de_caja(valor_nominal, cupon_periodico, num_periodos)
    
    # Calcular valores presentes
    valores_presentes = calcular_valor_presente_flujos(flujos, tasa_descuento_periodica)
    
    # Valor presente total del bono
    valor_presente_total = sum(valores_presentes)
    
    # Calcular VP acumulado
    vp_acumulado = []
    suma = 0
    for vp in valores_presentes:
        suma += vp
        vp_acumulado.append(suma)
    
    # Retornar diccionario con todos los resultados
    return {
        'valor_presente_total': valor_presente_total,
        'cupon_periodico': cupon_periodico,
        'tasa_cupon_periodica': tasa_cupon_periodica,
        'tasa_descuento_periodica': tasa_descuento_periodica,
        'num_periodos': num_periodos,
        'periodos_por_año': periodos_por_año,
        'flujos': flujos,
        'valores_presentes': valores_presentes,
        'vp_acumulado': vp_acumulado
    }

# ==================== FUNCIONES DE VISUALIZACIÓN ====================

def crear_diagrama_flujo_interactivo(resultados, valor_nominal, frecuencia):
    """
    Crea un diagrama de flujo de efectivo interactivo usando Plotly
    """
    num_periodos = resultados['num_periodos']
    flujos = resultados['flujos']
    cupon = resultados['cupon_periodico']
    vp_total = resultados['valor_presente_total']
    
    # Preparar datos
    periodos = list(range(0, num_periodos + 1))
    valores_flujo = [-vp_total] + flujos
    
    # Crear figura
    fig = go.Figure()
    
    # Agregar línea de tiempo
    fig.add_trace(go.Scatter(
        x=periodos,
        y=[0] * len(periodos),
        mode='lines+markers',
        line=dict(color='black', width=3),
        marker=dict(size=10, color='black'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Agregar flechas de flujo
    colors_flujo = []
    texts_flujo = []
    
    for i, periodo in enumerate(periodos):
        if periodo == 0:
            # Inversión inicial (negativa)
            color = COLORES['inversion']
            text = f'Inversión<br>${vp_total:,.2f}'
            colors_flujo.append(color)
            texts_flujo.append(text)
        elif periodo < num_periodos:
            # Cupones
            color = COLORES['cupon']
            text = f'Cupón<br>${cupon:,.2f}'
            colors_flujo.append(color)
            texts_flujo.append(text)
        else:
            # Último flujo (cupón + principal)
            color = COLORES['valor_nominal']
            text = f'Cupón + Principal<br>${flujos[-1]:,.2f}'
            colors_flujo.append(color)
            texts_flujo.append(text)
    
    # Agregar barras de flujo
    fig.add_trace(go.Bar(
        x=periodos,
        y=valores_flujo,
        marker=dict(
            color=colors_flujo,
            line=dict(color='black', width=1)
        ),
        text=texts_flujo,
        textposition='outside',
        hovertemplate='<b>Periodo %{x}</b><br>Flujo: $%{y:,.2f}<extra></extra>',
        showlegend=False
    ))
    
    # Configurar layout
    fig.update_layout(
        title=dict(
            text=f'<b>Diagrama de Flujo de Efectivo del Bono</b><br><sub>Frecuencia: {frecuencia}</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=20, color=COLORES['principal'])
        ),
        xaxis=dict(
            title='Periodo',
            tickmode='linear',
            tick0=0,
            dtick=1 if num_periodos <= 20 else max(1, num_periodos // 20),
            gridcolor='lightgray',
            showline=True,
            linewidth=2,
            linecolor='black'
        ),
        yaxis=dict(
            title='Flujo de Efectivo (USD)',
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',
            tickformat='$,.0f'
        ),
        plot_bgcolor='white',
        height=500,
        hovermode='x unified',
        font=dict(size=12)
    )
    
    return fig

def crear_grafico_vp_acumulado(resultados):
    """
    Crea un gráfico de evolución del VP acumulado
    """
    num_periodos = resultados['num_periodos']
    vp_acumulado = resultados['vp_acumulado']
    
    periodos = list(range(1, num_periodos + 1))
    
    fig = go.Figure()
    
    # Línea de VP acumulado
    fig.add_trace(go.Scatter(
        x=periodos,
        y=vp_acumulado,
        mode='lines+markers',
        name='VP Acumulado',
        line=dict(color=COLORES['principal'], width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor=f'rgba(31, 71, 136, 0.2)',
        hovertemplate='<b>Periodo %{x}</b><br>VP Acumulado: $%{y:,.2f}<extra></extra>'
    ))
    
    # Línea de referencia en cero
    fig.add_hline(
        y=0, 
        line_dash="dash", 
        line_color="red",
        annotation_text="Punto de equilibrio",
        annotation_position="right"
    )
    
    fig.update_layout(
        title='<b>Evolución del Valor Presente Acumulado</b>',
        xaxis_title='Periodo',
        yaxis_title='Valor Presente Acumulado (USD)',
        plot_bgcolor='white',
        height=400,
        hovermode='x unified',
        yaxis=dict(tickformat='$,.0f', gridcolor='lightgray'),
        xaxis=dict(gridcolor='lightgray')
    )
    
    return fig

def crear_grafico_composicion_flujos(resultados, valor_nominal):
    """
    Crea un gráfico de pie mostrando la composición del valor presente
    """
    cupon = resultados['cupon_periodico']
    num_periodos = resultados['num_periodos']
    valores_presentes = resultados['valores_presentes']
    
    # Calcular VP de cupones y VP del principal
    vp_cupones = sum(valores_presentes[:-1])
    vp_principal = valores_presentes[-1] - (cupon / ((1 + resultados['tasa_descuento_periodica']) ** num_periodos))
    vp_ultimo_cupon = cupon / ((1 + resultados['tasa_descuento_periodica']) ** num_periodos)
    
    # Ajustar para que sume correctamente
    vp_cupones_total = vp_cupones + vp_ultimo_cupon
    
    fig = go.Figure(data=[go.Pie(
        labels=['Valor Presente de Cupones', 'Valor Presente del Principal'],
        values=[vp_cupones_total, vp_principal],
        marker=dict(colors=[COLORES['cupon'], COLORES['valor_nominal']]),
        textinfo='label+percent+value',
        texttemplate='<b>%{label}</b><br>%{percent}<br>$%{value:,.2f}',
        hovertemplate='<b>%{label}</b><br>Valor: $%{value:,.2f}<br>Porcentaje: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title='<b>Composición del Valor Presente del Bono</b>',
        height=400,
        font=dict(size=12)
    )
    
    return fig

def crear_grafico_sensibilidad_tasa(valor_nominal, tasa_cupon_anual, frecuencia, 
                                     plazo_años, tasa_descuento_base):
    """
    Crea un gráfico de sensibilidad del precio del bono ante cambios en la tasa de descuento
    """
    # Rango de tasas de descuento (+/- 5% de la tasa base)
    tasas = np.linspace(max(0.01, tasa_descuento_base - 0.05), 
                       min(0.50, tasa_descuento_base + 0.05), 50)
    
    valores_bono = []
    
    for tasa in tasas:
        resultado = calcular_valor_presente_bono_completo(
            valor_nominal, tasa_cupon_anual, frecuencia, plazo_años, tasa
        )
        valores_bono.append(resultado['valor_presente_total'])
    
    fig = go.Figure()
    
    # Línea de sensibilidad
    fig.add_trace(go.Scatter(
        x=tasas * 100,
        y=valores_bono,
        mode='lines',
        name='Valor del Bono',
        line=dict(color=COLORES['info'], width=3),
        hovertemplate='<b>TEA: %{x:.2f}%</b><br>Valor del Bono: $%{y:,.2f}<extra></extra>'
    ))
    
    # Punto actual
    resultado_actual = calcular_valor_presente_bono_completo(
        valor_nominal, tasa_cupon_anual, frecuencia, plazo_años, tasa_descuento_base
    )
    
    fig.add_trace(go.Scatter(
        x=[tasa_descuento_base * 100],
        y=[resultado_actual['valor_presente_total']],
        mode='markers',
        name='Tasa Actual',
        marker=dict(size=15, color='red', symbol='star'),
        hovertemplate='<b>Tasa Actual</b><br>TEA: %{x:.2f}%<br>Valor: $%{y:,.2f}<extra></extra>'
    ))
    
    # Línea de referencia del valor nominal
    fig.add_hline(
        y=valor_nominal,
        line_dash="dash",
        line_color="green",
        annotation_text=f"Valor Nominal (${valor_nominal:,.0f})",
        annotation_position="left"
    )
    
    fig.update_layout(
        title='<b>Análisis de Sensibilidad: Precio del Bono vs Tasa de Descuento</b>',
        xaxis_title='Tasa de Descuento (TEA %)',
        yaxis_title='Valor Presente del Bono (USD)',
        plot_bgcolor='white',
        height=450,
        hovermode='x unified',
        yaxis=dict(tickformat='$,.0f', gridcolor='lightgray'),
        xaxis=dict(tickformat='.2f', gridcolor='lightgray', ticksuffix='%')
    )
    
    return fig
    
    # Valor presente total
    vp_total = vp_cupones + vp_nominal
    
    return vp_total, cupon

def crear_diagrama_flujo_efectivo(tiempo, cupon, valor_nominal, vp_bono, periodo):
    """
    Crea un diagrama visual de flujo de efectivo similar a la imagen proporcionada
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Configurar límites y estilo
    ax.set_xlim(-0.5, tiempo + 0.5)
    ax.set_ylim(-vp_bono * 1.5, max(cupon, valor_nominal) * 1.5)
    
    # Línea de tiempo horizontal
    ax.axhline(y=0, color='black', linewidth=2, zorder=1)
    
    # Etiqueta del periodo
    if periodo == "Mensual":
        periodo_label = "Mes"
    elif periodo == "Trimestral":
        periodo_label = "Trimestre"
    elif periodo == "Semestral":
        periodo_label = "Semestre"
    else:
        periodo_label = "Año"
    
    # Marcar periodos en la línea de tiempo
    for i in range(tiempo + 1):
        ax.plot(i, 0, 'ko', markersize=8, zorder=2)
        ax.text(i, -vp_bono * 0.15, str(i), ha='center', va='top', fontsize=10, fontweight='bold')
    
    # Etiqueta del eje
    ax.text(tiempo + 0.3, -vp_bono * 0.15, periodo_label, ha='left', va='top', fontsize=10, style='italic')
    
    # Flujo inicial (salida - inversión)
    ax.arrow(0, 0, 0, -vp_bono * 0.8, head_width=0.2, head_length=vp_bono * 0.1, 
             fc='red', ec='red', linewidth=2, zorder=3)
    ax.text(0, -vp_bono * 0.9, f'P₃ = ${vp_bono:,.2f}', ha='center', va='top', 
            fontsize=11, fontweight='bold', color='red')
    ax.text(0.3, -vp_bono * 0.5, 'Inversión\nInicial', ha='left', va='center', 
            fontsize=9, color='red', style='italic')
    
    # Cupones periódicos (entradas)
    for i in range(1, tiempo + 1):
        altura = cupon * 0.8 if i < tiempo else cupon * 0.5
        ax.arrow(i, 0, 0, altura, head_width=0.2, head_length=cupon * 0.1, 
                 fc='green', ec='green', linewidth=2, zorder=3)
        
        if i == 1 or i == tiempo:
            ax.text(i, altura + cupon * 0.15, f'${cupon:,.2f}', ha='center', va='bottom', 
                    fontsize=9, fontweight='bold', color='green')
    
    # Etiqueta de cupones
    ax.text(tiempo/2, cupon * 1.2, f'Cupones = ${cupon:,.2f}', ha='center', va='bottom', 
            fontsize=11, fontweight='bold', color='green',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7))
    
    # Valor nominal al final (entrada adicional)
    ax.arrow(tiempo, cupon * 0.5, 0, valor_nominal * 0.6, head_width=0.2, 
             head_length=valor_nominal * 0.05, fc='blue', ec='blue', linewidth=2.5, zorder=3)
    ax.text(tiempo, cupon * 0.5 + valor_nominal * 0.7, f'Principal\n${valor_nominal:,.2f}', 
            ha='center', va='bottom', fontsize=11, fontweight='bold', color='blue',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.7))
    
    # Eliminar ejes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Título
    ax.set_title('Diagrama de Flujo de Efectivo del Bono', fontsize=14, fontweight='bold', pad=20)
    
    # Leyenda
    legend_elements = [
        mpatches.Patch(color='red', label='Inversión Inicial (Salida)'),
        mpatches.Patch(color='green', label='Cupones Periódicos (Entrada)'),
        mpatches.Patch(color='blue', label='Valor Nominal (Entrada)')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    plt.tight_layout()
    return fig

def generar_excel_pagos(df_detalle, valor_nominal, tasa_cupon, tea, vp_bono, periodo):
    """
    Genera un archivo Excel con los detalles de los pagos periódicos
    """
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja 1: Resumen
        resumen_data = {
            'Parámetro': [
                'Valor Nominal',
                'Tasa Cupón Anual',
                'Periodo de Pago',
                'TEA (Tasa Requerida)',
                'Valor Presente del Bono',
                'Fecha de Generación'
            ],
            'Valor': [
                f'${valor_nominal:,.2f}',
                f'{tasa_cupon*100:.2f}%',
                periodo,
                f'{tea*100:.2f}%',
                f'${vp_bono:,.2f}',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        df_resumen = pd.DataFrame(resumen_data)
        df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
        
        # Hoja 2: Detalle de Pagos
        df_detalle.to_excel(writer, sheet_name='Detalle de Pagos', index=False)
        
        # Ajustar anchos de columna
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
    
    output.seek(0)
    return output

def generar_pdf_pagos(df_detalle, valor_nominal, tasa_cupon, tea, vp_bono, periodo, cupon):
    """
    Genera un archivo PDF con los detalles de los pagos periódicos
    """
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=1  # Centrado
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2e5c8a'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Título
    title = Paragraph("REPORTE DE ANÁLISIS DE BONO", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Fecha
    fecha = Paragraph(f"<b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
                     styles['Normal'])
    elements.append(fecha)
    elements.append(Spacer(1, 0.3*inch))
    
    # Resumen de parámetros
    resumen_heading = Paragraph("Parámetros del Bono", heading_style)
    elements.append(resumen_heading)
    
    resumen_data = [
        ['Parámetro', 'Valor'],
        ['Valor Nominal', f'${valor_nominal:,.2f}'],
        ['Tasa Cupón Anual', f'{tasa_cupon*100:.2f}%'],
        ['Cupón Periódico', f'${cupon:,.2f}'],
        ['Periodo de Pago', periodo],
        ['TEA (Tasa de Rendimiento Requerida)', f'{tea*100:.2f}%'],
        ['Valor Presente del Bono', f'${vp_bono:,.2f}'],
        ['Diferencia (VP - VN)', f'${vp_bono - valor_nominal:,.2f}']
    ]
    
    resumen_table = Table(resumen_data, colWidths=[3.5*inch, 2.5*inch])
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(resumen_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Detalle de pagos
    detalle_heading = Paragraph("Detalle de Pagos Periódicos", heading_style)
    elements.append(detalle_heading)
    
    # Preparar datos de la tabla
    table_data = [df_detalle.columns.tolist()] + df_detalle.values.tolist()
    
    # Formatear los valores numéricos
    for i in range(1, len(table_data)):
        for j in range(1, len(table_data[i])):
            if isinstance(table_data[i][j], (int, float)):
                table_data[i][j] = f'${table_data[i][j]:,.2f}'
    
    detalle_table = Table(table_data, colWidths=[0.8*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1.5*inch])
    detalle_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(detalle_table)
    
    # Construir PDF
    doc.build(elements)
    output.seek(0)
    return output

def mostrar_calculadora_bonos():
    st.header("Calculadora de Bonos")
    st.markdown("**Moneda: Dólares (USD)**")
    
    # Parámetros de entrada
    col1, col2 = st.columns(2)
    
    with col1:
        valor_nominal = st.number_input(
            "Valor Nominal ($)", 
            min_value=0.0, 
            value=20000.0, 
            step=1000.0,
            format="%.2f"
        )
        
        periodo = st.selectbox(
            "Periodo de Pago",
            ["Mensual", "Trimestral", "Semestral", "Anual"],
            index=3
        )
    
    with col2:
        tasa_cupon = st.number_input(
            "Tasa Cupón (%)", 
            min_value=0.0, 
            value=10.0, 
            step=0.1,
            format="%.2f"
        ) / 100
        
        # Etiqueta del tiempo según el periodo
        if periodo == "Mensual":
            tiempo_label = "Tiempo (meses)"
        elif periodo == "Trimestral":
            tiempo_label = "Tiempo (trimestres)"
        elif periodo == "Semestral":
            tiempo_label = "Tiempo (semestres)"
        else:
            tiempo_label = "Tiempo (años)"
        
        tiempo = st.number_input(
            tiempo_label, 
            min_value=1, 
            value=10, 
            step=1
        )
    
    # Calcular cupón periódico
    if periodo == "Anual":
        cupon_periodico = valor_nominal * tasa_cupon
    elif periodo == "Semestral":
        cupon_periodico = valor_nominal * tasa_cupon / 2
    elif periodo == "Trimestral":
        cupon_periodico = valor_nominal * tasa_cupon / 4
    elif periodo == "Mensual":
        cupon_periodico = valor_nominal * tasa_cupon / 12
    
    st.markdown(f"### Cupón Periódico: **${cupon_periodico:,.2f}**")
    
    st.markdown("---")
    
    # TEA - Tasa de Rendimiento Requerida
    st.subheader("Tasa de Rendimiento Requerida")
    
    tea = st.number_input(
        "TEA - Tasa Efectiva Anual (%)", 
        min_value=0.0, 
        value=12.0, 
        step=0.1,
        format="%.2f",
        help="Tasa de rendimiento que deseas obtener como inversionista"
    ) / 100
    
    # Alerta de comparación con tasa cupón
    if tea < tasa_cupon:
        st.error("⚠️ La TEA es menor que la tasa cupón. Esto significa que pagarás más por el bono de lo que recibirás, resultando en una pérdida.")
    elif tea > tasa_cupon:
        st.success("✓ La TEA es mayor que la tasa cupón. Pagarás menos por el bono, obteniendo una ganancia.")
    else:
        st.info("La TEA es igual a la tasa cupón. El bono se valorará a la par.")
    
    st.markdown("---")
    
    # Calcular valor presente usando la función correcta
    resultados = calcular_valor_presente_bono_completo(
        valor_nominal, tasa_cupon, periodo, tiempo, tea
    )
    vp_bono = resultados['valor_presente_total']
    cupon_calc = resultados['cupon_periodico']
    
    # Mostrar resultados
    st.subheader("Resultados del Análisis")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Valor Nominal", f"${valor_nominal:,.2f}")
    with col2:
        st.metric("Valor Presente del Bono", f"${vp_bono:,.2f}")
    with col3:
        diferencia = vp_bono - valor_nominal
        st.metric("Diferencia", f"${diferencia:,.2f}", delta=f"{(diferencia/valor_nominal)*100:.2f}%")
    
    # Diagrama de flujo de efectivo
    st.subheader("Flujo de Efectivo")
    
    # Crear y mostrar el diagrama visual
    fig = crear_diagrama_flujo_efectivo(tiempo, cupon_periodico, valor_nominal, vp_bono, periodo)
    st.pyplot(fig)
    plt.close()
    
    # Interpretación del diagrama de flujo
    total_cupones = cupon_periodico * tiempo

    st.info(
        f"""**📖 Interpretación:** Este diagrama muestra todos los flujos de efectivo del bono a lo largo del tiempo.
    La flecha roja hacia abajo representa tu inversión inicial.
    Las flechas verdes hacia arriba son los cupones que recibirás periódicamente (**{cupon_periodico:.2f}** cada **{periodo.lower()}**), totalizando **{total_cupones:,.2f}**.
    La flecha azul al final representa la devolución del valor nominal (**{valor_nominal:.2f}**).
    En total recibirás **{total_cupones + valor_nominal:.2f}**.
    """, icon="💡"
    )
    
    st.markdown("---")
    
    # Crear tabla de flujos detallada
    periodos_list = list(range(0, tiempo + 1))
    flujos = []
    flujos_actualizados = []
    vp_acumulado_list = []
    
    # Usar la tasa de descuento periódica de los resultados
    tasa_descuento = resultados['tasa_descuento_periodica']
    
    for t in periodos_list:
        if t == 0:
            flujo = -vp_bono
            flujo_actualizado = flujo
            vp_acum = flujo
        elif t == tiempo:
            flujo = cupon_periodico + valor_nominal
            flujo_actualizado = flujo / ((1 + tasa_descuento) ** t)
            vp_acum = vp_acumulado_list[-1] + flujo_actualizado
        else:
            flujo = cupon_periodico
            flujo_actualizado = flujo / ((1 + tasa_descuento) ** t)
            vp_acum = vp_acumulado_list[-1] + flujo_actualizado
        
        flujos.append(flujo)
        flujos_actualizados.append(flujo_actualizado)
        vp_acumulado_list.append(vp_acum)
    
    df_flujos = pd.DataFrame({
        'Periodo': periodos_list,
        'Flujo de Efectivo': flujos,
        'Flujo Actualizado': flujos_actualizados,
        'VP Acumulado': vp_acumulado_list,
        'Tipo de Flujo': ['Inversión Inicial'] + ['Cupón'] * (tiempo - 1) + ['Cupón + Principal']
    })
    
    # Mostrar tabla
    st.subheader("Tabla Detallada de Flujos")
    st.dataframe(
        df_flujos.style.format({
            'Flujo de Efectivo': '${:,.2f}',
            'Flujo Actualizado': '${:,.2f}',
            'VP Acumulado': '${:,.2f}'
        }).background_gradient(subset=['VP Acumulado'], cmap='RdYlGn', vmin=df_flujos['VP Acumulado'].min(), vmax=0),
        use_container_width=True,
        height=400
    )
    
    st.markdown("---")
    
    # Opciones de descarga
    st.subheader("📥 Descargar Reportes")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Generar Excel
        excel_file = generar_excel_pagos(df_flujos, valor_nominal, tasa_cupon, tea, vp_bono, periodo)
        st.download_button(
            label="📊 Descargar Excel",
            data=excel_file,
            file_name=f"reporte_bono_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        # Generar PDF
        pdf_file = generar_pdf_pagos(df_flujos, valor_nominal, tasa_cupon, tea, vp_bono, periodo, cupon_periodico)
        st.download_button(
            label="📄 Descargar PDF",
            data=pdf_file,
            file_name=f"reporte_bono_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    with col3:
        # Generar CSV
        csv_data = df_flujos.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📋 Descargar CSV",
            data=csv_data,
            file_name=f"reporte_bono_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Análisis y recomendación
    st.markdown("---")
    st.subheader("Análisis y Recomendación")
    
    # Calcular métricas adicionales
    rendimiento_real = ((valor_nominal + cupon_periodico * tiempo) / vp_bono - 1) * 100
    
    if tea > tasa_cupon:
        recomendacion = f"""
        **Recomendación: COMPRAR**
        
        Este bono representa una oportunidad de inversión atractiva:
        
        - **Precio de compra**: ${vp_bono:,.2f} (descuento de ${valor_nominal - vp_bono:,.2f})
        - **Tasa de rendimiento esperada**: {tea*100:.2f}% anual
        - **Ventaja**: Estás comprando el bono por debajo de su valor nominal, lo que te permite obtener un rendimiento superior a la tasa cupón
        - **Retorno total estimado**: Recibirás ${cupon_periodico * tiempo + valor_nominal:,.2f} durante la vida del bono
        
        Esta inversión es adecuada si buscas un rendimiento de {tea*100:.2f}% y confías en la capacidad del emisor para pagar.
        """
    elif tea < tasa_cupon:
        recomendacion = f"""
        **Recomendación: NO COMPRAR**
        
        Este bono no es una inversión favorable en las condiciones actuales:
        
        - **Precio de compra**: ${vp_bono:,.2f} (prima de ${vp_bono - valor_nominal:,.2f})
        - **Tasa de rendimiento esperada**: {tea*100:.2f}% anual
        - **Desventaja**: Pagarías más que el valor nominal del bono, obteniendo un rendimiento inferior a la tasa cupón
        - **Pérdida potencial**: ${vp_bono - valor_nominal:,.2f}
        
        Considera buscar alternativas de inversión con mejor rendimiento o esperar a que el precio del bono baje.
        """
    else:
        recomendacion = f"""
        **Recomendación: NEUTRAL**
        
        Este bono se cotiza a la par:
        
        - **Precio de compra**: ${vp_bono:,.2f} (igual al valor nominal)
        - **Tasa de rendimiento esperada**: {tea*100:.2f}% anual
        - **Observación**: El bono está correctamente valorado según tu tasa requerida
        
        La decisión de compra dependerá de otros factores como la solidez del emisor y tus objetivos de inversión.
        """
    
    st.markdown(recomendacion)
