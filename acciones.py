import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime

# ==================== CONFIGURACIÓN ====================
COLORES = {
    'aportes': '#3498db',
    'interes': '#2ecc71',
    'total': '#e74c3c',
    'pension': '#f39c12'
}

IMPUESTOS = {
    'USD': 0.295,  # 29.5% para extranjera
    'PEN': 0.05    # 5% para local
}

# ==================== FUNCIONES DE CONVERSIÓN DE TASAS ====================

def obtener_periodos_por_año(frecuencia):
    """Retorna el número de periodos por año según la frecuencia"""
    frecuencias = {
        "Mensual": 12,
        "Trimestral": 4,
        "Semestral": 2,
        "Anual": 1
    }
    return frecuencias.get(frecuencia, 12)

def convertir_tea_a_tasa_periodica(tea, frecuencia):
    """
    Convierte TEA a tasa efectiva periódica usando fórmula de tasas equivalentes:
    TEP = (1 + TEA)^(1/n) - 1
    """
    n = obtener_periodos_por_año(frecuencia)
    tasa_periodica = (1 + tea) ** (1/n) - 1
    return tasa_periodica

# ==================== VALIDACIONES ====================

def validar_tasa(tasa, nombre_tasa):
    """Valida que la tasa esté en el rango permitido (0% - 50%)"""
    if tasa < 0:
        return False, f"❌ {nombre_tasa} no puede ser negativa"
    if tasa > 0.50:
        return False, f"❌ {nombre_tasa} no puede ser mayor a 50%"
    return True, ""

def validar_valor_positivo(valor, nombre_campo):
    """Valida que un valor sea positivo o cero"""
    if valor < 0:
        return False, f"❌ {nombre_campo} no puede ser negativo"
    return True, ""

def validar_edad(edad):
    """Valida que la edad esté en un rango razonable"""
    if edad < 18:
        return False, "❌ La edad debe ser mayor a 18 años"
    if edad > 100:
        return False, "❌ La edad debe ser menor a 100 años"
    return True, ""

# ==================== MÓDULO A: CRECIMIENTO DE CARTERA ====================

def calcular_crecimiento_deposito_unico(monto_inicial, tea, plazo_años):
    """
    Calcula el crecimiento con un único depósito inicial
    VF = VA × (1 + r)^n
    """
    periodos = list(range(0, int(plazo_años) + 1))
    saldos = []
    aportes_acum = []
    intereses_acum = []
    
    for año in periodos:
        saldo = monto_inicial * ((1 + tea) ** año)
        interes_ganado = saldo - monto_inicial
        
        saldos.append(saldo)
        aportes_acum.append(monto_inicial)
        intereses_acum.append(interes_ganado)
    
    return {
        'periodos': periodos,
        'saldos': saldos,
        'aportes_acumulados': aportes_acum,
        'intereses_acumulados': intereses_acum,
        'saldo_final': saldos[-1],
        'total_aportado': monto_inicial,
        'interes_total': saldos[-1] - monto_inicial
    }

def calcular_crecimiento_aportes_periodicos(monto_inicial, aporte_periodico, tea, 
                                            frecuencia, plazo_años):
    """
    Calcula el crecimiento con aportes periódicos
    Fórmula de anualidad con valor presente
    """
    n_periodos_año = obtener_periodos_por_año(frecuencia)
    tasa_periodica = convertir_tea_a_tasa_periodica(tea, frecuencia)
    total_periodos = int(plazo_años * n_periodos_año)
    
    # Generar tabla detallada
    periodos = []
    saldos_iniciales = []
    aportes = []
    intereses = []
    saldos_finales = []
    aportes_acumulados = []
    intereses_acumulados = []
    
    saldo_actual = monto_inicial
    total_aportado = monto_inicial
    total_interes = 0
    
    for periodo in range(0, total_periodos + 1):
        periodos.append(periodo)
        saldos_iniciales.append(saldo_actual)
        
        if periodo == 0:
            # Periodo 0: solo inversión inicial
            aportes.append(monto_inicial)
            intereses.append(0)
            saldos_finales.append(monto_inicial)
            aportes_acumulados.append(monto_inicial)
            intereses_acumulados.append(0)
        else:
            # Calcular interés sobre saldo anterior
            interes_periodo = saldo_actual * tasa_periodica
            # Agregar aporte periódico
            saldo_actual = saldo_actual + interes_periodo + aporte_periodico
            total_aportado += aporte_periodico
            total_interes += interes_periodo
            
            aportes.append(aporte_periodico)
            intereses.append(interes_periodo)
            saldos_finales.append(saldo_actual)
            aportes_acumulados.append(total_aportado)
            intereses_acumulados.append(total_interes)
    
    return {
        'periodos': periodos,
        'saldos_iniciales': saldos_iniciales,
        'aportes': aportes,
        'intereses': intereses,
        'saldos_finales': saldos_finales,
        'aportes_acumulados': aportes_acumulados,
        'intereses_acumulados': intereses_acumulados,
        'saldo_final': saldo_actual,
        'total_aportado': total_aportado,
        'interes_total': total_interes,
        'tasa_periodica': tasa_periodica,
        'frecuencia': frecuencia,
        'n_periodos_año': n_periodos_año
    }

# ==================== MÓDULO B: PROYECCIÓN DE JUBILACIÓN ====================

def calcular_impuestos(capital_final, total_aportado, moneda):
    """Calcula los impuestos según la moneda elegida"""
    ganancia = capital_final - total_aportado
    
    if ganancia <= 0:
        return 0, ganancia
    
    tasa_impuesto = IMPUESTOS.get(moneda, 0)
    impuesto = ganancia * tasa_impuesto
    
    return impuesto, ganancia

def calcular_pension_mensual(capital_neto, tea_retiro, años_retiro=None):
    """
    Calcula la pensión mensual sostenible
    Si años_retiro es None, asume anualidad perpetua
    Si años_retiro está definido, calcula anualidad temporal
    """
    tasa_mensual = convertir_tea_a_tasa_periodica(tea_retiro, "Mensual")
    
    if años_retiro is None or años_retiro >= 100:
        # Anualidad perpetua: P = C × r
        pension_mensual = capital_neto * tasa_mensual
    else:
        # Anualidad temporal: P = C × [r(1+r)^n] / [(1+r)^n - 1]
        n_meses = int(años_retiro * 12)
        if tasa_mensual > 0:
            factor = (tasa_mensual * (1 + tasa_mensual) ** n_meses) / \
                     ((1 + tasa_mensual) ** n_meses - 1)
            pension_mensual = capital_neto * factor
        else:
            pension_mensual = capital_neto / n_meses
    
    return pension_mensual, tasa_mensual

# ==================== VISUALIZACIONES ====================

def crear_grafico_crecimiento(resultados, moneda, tipo_inversion):
    """Crea gráfico interactivo de crecimiento de cartera"""
    
    if tipo_inversion == "Depósito único":
        periodos = resultados['periodos']
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=periodos,
            y=resultados['aportes_acumulados'],
            mode='lines',
            name='Aportes Acumulados',
            line=dict(color=COLORES['aportes'], width=2),
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.2)'
        ))
        
        fig.add_trace(go.Scatter(
            x=periodos,
            y=resultados['saldos'],
            mode='lines+markers',
            name='Saldo Total',
            line=dict(color=COLORES['total'], width=3),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title='<b>Crecimiento de Cartera - Depósito Único</b>',
            xaxis_title='Años',
            yaxis_title=f'Monto ({moneda})',
            hovermode='x unified',
            plot_bgcolor='white',
            height=500
        )
        
    else:  # Aportes periódicos
        # Convertir periodos a años para mejor visualización
        periodos_array = np.array(resultados['periodos'])
        años = periodos_array / resultados['n_periodos_año']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=años,
            y=resultados['aportes_acumulados'],
            mode='lines',
            name='Aportes Acumulados',
            line=dict(color=COLORES['aportes'], width=2),
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.2)',
            hovertemplate=f'Años: %{{x:.1f}}<br>Aportes: {moneda}%{{y:,.2f}}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=años,
            y=resultados['intereses_acumulados'],
            mode='lines',
            name='Intereses Acumulados',
            line=dict(color=COLORES['interes'], width=2),
            fill='tonexty',
            fillcolor='rgba(46, 204, 113, 0.2)',
            hovertemplate=f'Años: %{{x:.1f}}<br>Intereses: {moneda}%{{y:,.2f}}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=años,
            y=resultados['saldos_finales'],
            mode='lines+markers',
            name='Saldo Total',
            line=dict(color=COLORES['total'], width=3),
            marker=dict(size=5),
            hovertemplate=f'Años: %{{x:.1f}}<br>Saldo: {moneda}%{{y:,.2f}}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Crecimiento de Cartera - Aportes Periódicos</b>',
            xaxis_title='Años',
            yaxis_title=f'Monto ({moneda})',
            hovermode='x unified',
            plot_bgcolor='white',
            height=500,
            yaxis=dict(tickformat=',')
        )
    
    fig.update_xaxes(gridcolor='lightgray')
    fig.update_yaxes(gridcolor='lightgray')
    
    return fig

def crear_grafico_distribucion_final(total_aportado, interes_total, moneda):
    """Crea gráfico de pie con la distribución final"""
    
    fig = go.Figure(data=[go.Pie(
        labels=['Aportes Totales', 'Intereses Ganados'],
        values=[total_aportado, interes_total],
        hole=0.4,
        marker=dict(colors=[COLORES['aportes'], COLORES['interes']]),
        textinfo='label+percent+value',
        texttemplate=f'%{{label}}<br>%{{percent}}<br>{moneda}%{{value:,.2f}}',
        hovertemplate='<b>%{label}</b><br>Monto: ' + moneda + '%{value:,.2f}<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title='<b>Distribución del Capital Final</b>',
        height=400
    )
    
    return fig

def crear_grafico_comparacion_escenarios(capital_actual, edad_actual, tea, moneda):
    """Crea gráfico comparativo de diferentes edades de jubilación"""
    
    edades_jubilacion = [60, 62, 65, 67, 70]
    saldos_finales = []
    
    for edad_jub in edades_jubilacion:
        if edad_jub > edad_actual:
            plazo = edad_jub - edad_actual
            saldo = capital_actual * ((1 + tea) ** plazo)
            saldos_finales.append(saldo)
        else:
            saldos_finales.append(0)
    
    fig = go.Figure(data=[
        go.Bar(
            x=[f"{edad} años" for edad in edades_jubilacion],
            y=saldos_finales,
            marker=dict(
                color=saldos_finales,
                colorscale='Blues',
                showscale=True,
                colorbar=dict(title=f"Saldo<br>({moneda})")
            ),
            text=[f"{moneda}{s:,.0f}" for s in saldos_finales],
            textposition='outside',
            hovertemplate='<b>Edad: %{x}</b><br>Saldo: ' + moneda + '%{y:,.2f}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title='<b>Comparación: Saldo Final según Edad de Jubilación</b>',
        xaxis_title='Edad de Jubilación',
        yaxis_title=f'Saldo Final ({moneda})',
        height=450,
        showlegend=False,
        yaxis=dict(tickformat=',')
    )
    
    return fig

# ==================== EXPORTACIÓN A PDF ====================

def generar_pdf_completo(modulo_a_data, modulo_b_data, moneda, tipo_inversion_nombre="Inversión Nacional"):
    """Genera un reporte PDF completo con ambos módulos"""
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter, topMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=20,
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2e5c8a'),
        spaceAfter=12
    )
    
    # Título principal
    elements.append(Paragraph(f"REPORTE DE INVERSIÓN EN ACCIONES", title_style))
    elements.append(Paragraph(f"Tipo de Inversión: {tipo_inversion_nombre}", styles['Normal']))
    elements.append(Paragraph(f"Moneda: Dólares (USD)", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
                             styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # ===== MÓDULO A: CRECIMIENTO DE CARTERA =====
    elements.append(Paragraph("MÓDULO A: CRECIMIENTO DE CARTERA", subtitle_style))
    
    modulo_a_table_data = [
        ['Parámetro', 'Valor'],
        ['Edad Actual', f"{modulo_a_data['edad_actual']} años"],
        ['Edad de Jubilación', f"{modulo_a_data['edad_jubilacion']} años"],
        ['Plazo', f"{modulo_a_data['plazo']} años"],
        ['Tipo de Inversión', modulo_a_data['tipo_inversion']],
        ['Monto Inicial', f"{moneda}{modulo_a_data['monto_inicial']:,.2f}"],
    ]
    
    if modulo_a_data['tipo_inversion'] == 'Aportes periódicos':
        modulo_a_table_data.extend([
            ['Aporte Periódico', f"{moneda}{modulo_a_data['aporte_periodico']:,.2f}"],
            ['Frecuencia', modulo_a_data['frecuencia']]
        ])
    
    modulo_a_table_data.extend([
        ['TEA Esperada', f"{modulo_a_data['tea']*100:.2f}%"],
        ['Total Aportado', f"{moneda}{modulo_a_data['total_aportado']:,.2f}"],
        ['Intereses Ganados', f"{moneda}{modulo_a_data['interes_total']:,.2f}"],
        ['Capital Final', f"{moneda}{modulo_a_data['capital_final']:,.2f}"]
    ])
    
    tabla_a = Table(modulo_a_table_data, colWidths=[3*inch, 3*inch])
    tabla_a.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    
    elements.append(tabla_a)
    elements.append(Spacer(1, 0.3*inch))
    
    # ===== MÓDULO B: PROYECCIÓN DE JUBILACIÓN =====
    if modulo_b_data:
        elements.append(Paragraph("MÓDULO B: PROYECCIÓN DE JUBILACIÓN", subtitle_style))
        
        modulo_b_table_data = [
            ['Concepto', 'Valor'],
            ['Capital Acumulado (Bruto)', f"{moneda}{modulo_b_data['capital_bruto']:,.2f}"],
            ['Ganancias', f"{moneda}{modulo_b_data['ganancias']:,.2f}"],
            ['Tasa de Impuesto', f"{modulo_b_data['tasa_impuesto']*100:.2f}%"],
            ['Impuesto a Pagar', f"{moneda}{modulo_b_data['impuesto']:,.2f}"],
            ['Capital Neto (después de impuestos)', f"{moneda}{modulo_b_data['capital_neto']:,.2f}"],
        ]
        
        if modulo_b_data['opcion_retiro'] == 'Pensión mensual':
            modulo_b_table_data.extend([
                ['Opción de Retiro', 'Pensión Mensual'],
                ['TEA durante Retiro', f"{modulo_b_data['tea_retiro']*100:.2f}%"],
                ['Años de Retiro', modulo_b_data['años_retiro'] if modulo_b_data['años_retiro'] else 'Perpetuo'],
                ['Pensión Mensual', f"{moneda}{modulo_b_data['pension_mensual']:,.2f}"],
            ])
        else:
            modulo_b_table_data.append(['Opción de Retiro', 'Retiro Único'])
        
        tabla_b = Table(modulo_b_table_data, colWidths=[3*inch, 3*inch])
        tabla_b.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        
        elements.append(tabla_b)
    
    doc.build(elements)
    output.seek(0)
    return output

# ==================== INTERFAZ PRINCIPAL ====================

def mostrar_calculadora_acciones():
    """Interfaz principal de la calculadora de inversión en acciones"""
    
    st.header("📈 Calculadora de Inversión en Acciones para Jubilación")
    st.markdown("**Sistema de Planificación Financiera Integral**")
    st.markdown("---")
    
    # ===== SELECCIÓN DE TIPO DE INVERSIÓN =====
    if 'moneda_seleccionada' not in st.session_state:
        st.session_state['moneda_seleccionada'] = None
    
    if st.session_state['moneda_seleccionada'] is None:
        st.subheader("🌎 Paso 1: Selecciona el Tipo de Inversión")
        st.info("👉 Define si tu inversión es nacional o extranjera. Todas las cantidades se manejarán en dólares ($).")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🇵🇪 Inversión Nacional", use_container_width=True, type="primary"):
                st.session_state['moneda_seleccionada'] = 'PEN'
                st.session_state['simbolo_moneda'] = '$'
                st.rerun()
        
        with col2:
            if st.button("� Inversión Extranjera", use_container_width=True, type="primary"):
                st.session_state['moneda_seleccionada'] = 'USD'
                st.session_state['simbolo_moneda'] = '$'
                st.rerun()
        
        st.markdown("---")
        st.markdown("""
        **📌 Nota sobre Impuestos:**
        - **Inversión Nacional:** Aplica 5% de impuesto sobre ganancias de capital
        - **Inversión Extranjera:** Aplica 29.5% de impuesto sobre ganancias de capital
        
        *Todas las inversiones se manejan en dólares ($USD)*
        """)
        
        return
    
    # Tipo de inversión ya seleccionado
    moneda_codigo = st.session_state['moneda_seleccionada']
    moneda = st.session_state['simbolo_moneda']
    tipo_inversion_nombre = "Inversión Nacional" if moneda_codigo == 'PEN' else "Inversión Extranjera"
    tasa_impuesto_display = "5%" if moneda_codigo == 'PEN' else "29.5%"
    
    # Botón para cambiar tipo de inversión
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.success(f"💰 **Tipo de Inversión:** {tipo_inversion_nombre} (Impuesto: {tasa_impuesto_display})")
    with col_header2:
        if st.button("🔄 Cambiar Tipo"):
            st.session_state['moneda_seleccionada'] = None
            st.session_state.clear()
            st.rerun()
    
    st.markdown("---")
    
    # ===== NAVEGACIÓN ENTRE MÓDULOS =====
    tab_modulo_a, tab_modulo_b, tab_comparacion = st.tabs([
        "📊 Módulo A: Crecimiento de Cartera",
        "🏖️ Módulo B: Proyección de Jubilación",
        "📈 Comparación de Escenarios"
    ])
    
    # ==================== MÓDULO A ====================
    with tab_modulo_a:
        st.subheader("📊 Módulo A: Crecimiento de Cartera en Acciones")
        st.markdown("Simula el crecimiento de tu inversión hasta la jubilación.")
        
        # Parámetros de entrada
        col1, col2, col3 = st.columns(3)
        
        with col1:
            edad_actual = st.number_input(
                "Edad Actual ❓",
                min_value=18,
                max_value=100,
                value=30,
                step=1,
                help="Tu edad actual en años"
            )
            
            edad_jubilacion = st.number_input(
                "Edad de Jubilación ❓",
                min_value=edad_actual + 1,
                max_value=100,
                value=65,
                step=1,
                help="Edad a la que planeas jubilarte"
            )
            
            plazo_años = edad_jubilacion - edad_actual
            st.info(f"⏱️ **Plazo de inversión:** {plazo_años} años")
        
        with col2:
            tipo_inversion = st.radio(
                "Tipo de Inversión ❓",
                ["Depósito único", "Aportes periódicos"],
                help="Elige cómo invertirás: una sola vez o con aportes regulares"
            )
            
            monto_inicial = st.number_input(
                f"Monto Inicial ({moneda}) ❓",
                min_value=0.0,
                value=3000.0,
                step=100.0,
                format="%.2f",
                help="Capital con el que iniciarás tu inversión en dólares"
            )
        
        with col3:
            if tipo_inversion == "Aportes periódicos":
                frecuencia = st.selectbox(
                    "Frecuencia de Aportes ❓",
                    ["Mensual", "Trimestral", "Semestral", "Anual"],
                    help="Con qué frecuencia realizarás los aportes"
                )
                
                aporte_periodico = st.number_input(
                    f"Aporte Periódico ({moneda}) ❓",
                    min_value=0.0,
                    value=150.0,
                    step=10.0,
                    format="%.2f",
                    help="Monto que aportarás en cada periodo (en dólares)"
                )
            else:
                frecuencia = "Anual"
                aporte_periodico = 0.0
            
            tea_pct = st.number_input(
                "Tasa Efectiva Anual (TEA %) ❓",
                min_value=0.0,
                max_value=50.0,
                value=12.0,
                step=0.5,
                format="%.2f",
                help="Rendimiento anual esperado de tu inversión (0% - 50%)"
            )
            tea = tea_pct / 100
        
        # Botón de cálculo
        if st.button("🔄 Calcular Crecimiento", type="primary", use_container_width=True):
            # Validaciones
            errores = []
            
            es_valida, msg = validar_edad(edad_actual)
            if not es_valida:
                errores.append(msg)
            
            es_valida, msg = validar_edad(edad_jubilacion)
            if not es_valida:
                errores.append(msg)
            
            if edad_jubilacion <= edad_actual:
                errores.append("❌ La edad de jubilación debe ser mayor a la edad actual")
            
            es_valida, msg = validar_valor_positivo(monto_inicial, "Monto inicial")
            if not es_valida:
                errores.append(msg)
            
            if tipo_inversion == "Aportes periódicos":
                es_valida, msg = validar_valor_positivo(aporte_periodico, "Aporte periódico")
                if not es_valida:
                    errores.append(msg)
            
            es_valida, msg = validar_tasa(tea, "TEA")
            if not es_valida:
                errores.append(msg)
            
            if errores:
                for error in errores:
                    st.error(error)
            else:
                # Realizar cálculos
                if tipo_inversion == "Depósito único":
                    resultados = calcular_crecimiento_deposito_unico(monto_inicial, tea, plazo_años)
                else:
                    resultados = calcular_crecimiento_aportes_periodicos(
                        monto_inicial, aporte_periodico, tea, frecuencia, plazo_años
                    )
                
                # Guardar en session_state
                st.session_state['resultados_modulo_a'] = resultados
                st.session_state['params_modulo_a'] = {
                    'edad_actual': edad_actual,
                    'edad_jubilacion': edad_jubilacion,
                    'plazo': plazo_años,
                    'tipo_inversion': tipo_inversion,
                    'monto_inicial': monto_inicial,
                    'aporte_periodico': aporte_periodico,
                    'frecuencia': frecuencia,
                    'tea': tea,
                    'moneda': moneda,
                    'moneda_codigo': moneda_codigo
                }
                
                st.success("✅ Cálculos completados exitosamente!")
        
        # Mostrar resultados si existen
        if 'resultados_modulo_a' in st.session_state:
            resultados = st.session_state['resultados_modulo_a']
            params = st.session_state['params_modulo_a']
            
            st.markdown("---")
            st.subheader("📊 Resultados del Análisis")
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Aportado",
                    f"{moneda}{resultados['total_aportado']:,.2f}"
                )
            
            with col2:
                st.metric(
                    "Intereses Ganados",
                    f"{moneda}{resultados['interes_total']:,.2f}"
                )
            
            with col3:
                st.metric(
                    "Capital Final",
                    f"{moneda}{resultados['saldo_final']:,.2f}"
                )
            
            with col4:
                rentabilidad = (resultados['interes_total'] / resultados['total_aportado']) * 100
                st.metric(
                    "Rentabilidad",
                    f"{rentabilidad:.2f}%"
                )
            
            st.markdown("---")
            
            # Visualizaciones
            st.subheader("📈 Visualización del Crecimiento")
            
            fig_crecimiento = crear_grafico_crecimiento(resultados, moneda, params['tipo_inversion'])
            st.plotly_chart(fig_crecimiento, use_container_width=True)
            
            # Interpretación del gráfico de crecimiento
            if params['tipo_inversion'] == "Aportes periódicos":
                st.info("""
                **📖 Interpretación:** Este gráfico muestra la evolución de tu inversión a lo largo del tiempo. 
                La línea azul representa tus aportes acumulados (el dinero que TÚ pones), mientras que el área verde 
                muestra los intereses generados (el dinero que tu dinero genera). Note cómo los intereses crecen de forma 
                exponencial gracias al interés compuesto: ¡ganas intereses sobre intereses!
                """, icon="💡")
            else:
                st.info("""
                **📖 Interpretación:** Este gráfico muestra cómo crece tu inversión inicial a lo largo del tiempo 
                gracias al interés compuesto. Aunque no agregas más dinero, tu capital trabaja para ti y se multiplica 
                año tras año. La curva ascendente refleja el poder del tiempo en las inversiones.
                """, icon="💡")
            
            # Gráfico de distribución
            fig_distribucion = crear_grafico_distribucion_final(
                resultados['total_aportado'],
                resultados['interes_total'],
                moneda
            )
            st.plotly_chart(fig_distribucion, use_container_width=True)
            
            # Interpretación del gráfico de distribución
            porcentaje_interes = (resultados['interes_total'] / resultados['saldo_final']) * 100
            st.info(f"""
            **📖 Interpretación:** Este gráfico circular muestra de dónde proviene tu capital final. 
            El **{porcentaje_interes:.1f}%** de tu dinero proviene de los intereses ganados, mientras que 
            solo el **{100-porcentaje_interes:.1f}%** es dinero que tú aportaste directamente. 
            Esto demuestra el poder del interés compuesto: ¡tu dinero trabaja más que tú!
            """, icon="💡")
            
            # Tabla detallada
            if params['tipo_inversion'] == "Aportes periódicos":
                st.markdown("---")
                st.subheader("📋 Tabla Detallada de Flujos")
                
                # Crear DataFrame para mostrar
                df_display = pd.DataFrame({
                    'Periodo': resultados['periodos'],
                    'Saldo Inicial': resultados['saldos_iniciales'],
                    'Aporte': resultados['aportes'],
                    'Interés Ganado': resultados['intereses'],
                    'Saldo Final': resultados['saldos_finales']
                })
                
                # Mostrar solo primeros 20 periodos y últimos 5
                total_periodos = len(df_display)
                if total_periodos > 25:
                    # Crear fila de puntos suspensivos como diccionario
                    fila_puntos = pd.DataFrame([{
                        'Periodo': '...',
                        'Saldo Inicial': '...',
                        'Aporte': '...',
                        'Interés Ganado': '...',
                        'Saldo Final': '...'
                    }])
                    df_mostrar = pd.concat([
                        df_display.head(15),
                        fila_puntos,
                        df_display.tail(10)
                    ], ignore_index=True)
                    # Convertir columna Periodo a string para evitar errores de conversión
                    df_mostrar['Periodo'] = df_mostrar['Periodo'].astype(str)
                else:
                    df_mostrar = df_display
                
                # Función para formatear solo valores numéricos
                def format_valor(val, formato):
                    if isinstance(val, str):
                        return val
                    try:
                        return formato.format(val)
                    except:
                        return str(val)
                
                st.dataframe(
                    df_mostrar.style.format({
                        'Periodo': lambda x: str(x),
                        'Saldo Inicial': lambda x: format_valor(x, f'{moneda}{{:,.2f}}'),
                        'Aporte': lambda x: format_valor(x, f'{moneda}{{:,.2f}}'),
                        'Interés Ganado': lambda x: format_valor(x, f'{moneda}{{:,.2f}}'),
                        'Saldo Final': lambda x: format_valor(x, f'{moneda}{{:,.2f}}')
                    }),
                    height=400,
                    use_container_width=True
                )
                
                st.info(f"📊 **Total de periodos:** {total_periodos} ({params['frecuencia'].lower()})")
    
    # ==================== MÓDULO B ====================
    with tab_modulo_b:
        st.subheader("🏖️ Módulo B: Proyección de Jubilación")
        st.markdown("Calcula tu pensión mensual o retiro único al jubilarte.")
        
        if 'resultados_modulo_a' not in st.session_state:
            st.warning("⚠️ Primero debes completar el **Módulo A** para proyectar tu jubilación.")
            st.info("👈 Ve a la pestaña **Módulo A: Crecimiento de Cartera** para comenzar.")
            return
        
        # Obtener datos del Módulo A
        resultados_a = st.session_state['resultados_modulo_a']
        params_a = st.session_state['params_modulo_a']
        
        capital_acumulado = resultados_a['saldo_final']
        total_aportado = resultados_a['total_aportado']
        
        st.success(f"✅ **Capital acumulado a los {params_a['edad_jubilacion']} años:** {moneda}{capital_acumulado:,.2f}")
        
        st.markdown("---")
        
        # Opciones de retiro
        st.subheader("💼 Opciones de Retiro")
        
        opcion_retiro = st.radio(
            "¿Cómo deseas retirar tu dinero? ❓",
            ["Retiro único", "Pensión mensual"],
            help="Elige si retirarás todo de una vez o recibirás una pensión mensual"
        )
        
        # Calcular impuestos
        impuesto, ganancias = calcular_impuestos(
            capital_acumulado,
            total_aportado,
            params_a['moneda_codigo']
        )
        capital_neto = capital_acumulado - impuesto
        
        st.markdown("---")
        st.subheader("💰 Análisis Fiscal")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Capital Bruto",
                f"{moneda}{capital_acumulado:,.2f}"
            )
        
        with col2:
            tasa_impuesto = IMPUESTOS[params_a['moneda_codigo']]
            st.metric(
                f"Impuesto ({tasa_impuesto*100:.1f}%)",
                f"{moneda}{impuesto:,.2f}",
                delta=f"-{(impuesto/capital_acumulado)*100:.2f}%",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                "Capital Neto",
                f"{moneda}{capital_neto:,.2f}",
                delta=f"Después de impuestos"
            )
        
        st.info(f"""
        **📌 Detalle Fiscal:**
        - Ganancias: {moneda}{ganancias:,.2f}
        - Tasa de impuesto: {tasa_impuesto*100:.1f}% ({tipo_inversion_nombre})
        - Impuesto a pagar: {moneda}{impuesto:,.2f}
        """)
        
        st.markdown("---")
        
        # Configuración según opción de retiro
        if opcion_retiro == "Retiro único":
            st.subheader("💵 Retiro Único")
            st.success(f"**Recibirás un pago único de:** {moneda}{capital_neto:,.2f}")
            
            # Guardar datos del módulo B
            st.session_state['resultados_modulo_b'] = {
                'opcion_retiro': 'Retiro único',
                'capital_bruto': capital_acumulado,
                'ganancias': ganancias,
                'tasa_impuesto': tasa_impuesto,
                'impuesto': impuesto,
                'capital_neto': capital_neto
            }
        
        else:  # Pensión mensual
            st.subheader("📅 Pensión Mensual")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Valor por defecto: mitad de la TEA del Módulo A
                tea_default = (params_a['tea'] * 100) / 2
                tea_retiro_pct = st.number_input(
                    "TEA durante el Retiro (%) ❓",
                    min_value=0.0,
                    max_value=50.0,
                    value=tea_default,
                    step=0.5,
                    format="%.2f",
                    help="Rendimiento anual esperado durante tu jubilación (por defecto: mitad de la TEA del Módulo A)"
                )
                tea_retiro = tea_retiro_pct / 100
            
            with col2:
                tipo_anualidad = st.radio(
                    "Tipo de Pensión ❓",
                    ["Perpetua (hasta que el capital dure)", "Temporal (por años definidos)"],
                    help="Perpetua: pensión indefinida. Temporal: pensión por un tiempo limitado"
                )
                
                if tipo_anualidad == "Temporal (por años definidos)":
                    años_retiro = st.number_input(
                        "Años de Retiro ❓",
                        min_value=1,
                        max_value=50,
                        value=25,
                        step=1,
                        help="¿Por cuántos años quieres recibir la pensión?"
                    )
                else:
                    años_retiro = None
            
            # Calcular pensión
            pension_mensual, tasa_mensual = calcular_pension_mensual(
                capital_neto,
                tea_retiro,
                años_retiro
            )
            
            st.markdown("---")
            st.success(f"**💵 Pensión Mensual:** {moneda}{pension_mensual:,.2f}")
            
            # Información adicional
            pension_anual = pension_mensual * 12
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Pensión Mensual", f"{moneda}{pension_mensual:,.2f}")
            
            with col2:
                st.metric("Pensión Anual", f"{moneda}{pension_anual:,.2f}")
            
            with col3:
                st.metric("Tasa Mensual", f"{tasa_mensual*100:.4f}%")
            
            if años_retiro:
                total_recibir = pension_mensual * años_retiro * 12
                st.info(f"""
                **📊 Proyección:**
                - Duración: {años_retiro} años
                - Total a recibir: {moneda}{total_recibir:,.2f}
                - Promedio anual: {moneda}{total_recibir/años_retiro:,.2f}
                """)
            else:
                st.info(f"""
                **♾️ Pensión Perpetua:**
                - Tu capital generará {moneda}{pension_mensual:,.2f} mensuales indefinidamente
                - Basado en una tasa de retorno de {tea_retiro*100:.2f}% anual
                - El capital principal se mantiene intacto
                """)
            
            # Guardar datos del módulo B
            st.session_state['resultados_modulo_b'] = {
                'opcion_retiro': 'Pensión mensual',
                'capital_bruto': capital_acumulado,
                'ganancias': ganancias,
                'tasa_impuesto': tasa_impuesto,
                'impuesto': impuesto,
                'capital_neto': capital_neto,
                'tea_retiro': tea_retiro,
                'años_retiro': str(años_retiro) if años_retiro else 'Perpetuo',
                'pension_mensual': pension_mensual,
                'tasa_mensual': tasa_mensual
            }
        
        # Botón de exportación
        st.markdown("---")
        st.subheader("📥 Exportar Reporte")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 PDF", type="primary", use_container_width=True):
                try:
                    # Preparar datos para PDF
                    modulo_a_data = {
                        'edad_actual': params_a['edad_actual'],
                        'edad_jubilacion': params_a['edad_jubilacion'],
                        'plazo': params_a['plazo'],
                        'tipo_inversion': params_a['tipo_inversion'],
                        'monto_inicial': params_a['monto_inicial'],
                        'aporte_periodico': params_a.get('aporte_periodico', 0),
                        'frecuencia': params_a.get('frecuencia', 'N/A'),
                        'tea': params_a['tea'],
                        'total_aportado': resultados_a['total_aportado'],
                        'interes_total': resultados_a['interes_total'],
                        'capital_final': resultados_a['saldo_final']
                    }
                    
                    modulo_b_data = st.session_state.get('resultados_modulo_b', None)
                    
                    pdf_file = generar_pdf_completo(modulo_a_data, modulo_b_data, moneda, tipo_inversion_nombre)
                    
                    st.download_button(
                        label="⬇️ Descargar PDF",
                        data=pdf_file,
                        file_name=f"Reporte_Inversion_Acciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        type="secondary"
                    )
                except Exception as e:
                    st.error(f"❌ Error al generar PDF: {str(e)}")
        
        with col2:
            if st.button("📊 Excel", type="primary", use_container_width=True):
                try:
                    # Crear DataFrame con resumen
                    data_summary = {
                        'Concepto': [
                            'Edad Actual',
                            'Edad Jubilación',
                            'Plazo (años)',
                            'Tipo Inversión',
                            'Monto Inicial',
                            'Aporte Periódico',
                            'Frecuencia',
                            'TEA',
                            'Total Aportado',
                            'Intereses Ganados',
                            'Capital Final'
                        ],
                        'Valor': [
                            f"{params_a['edad_actual']} años",
                            f"{params_a['edad_jubilacion']} años",
                            f"{params_a['plazo']} años",
                            params_a['tipo_inversion'],
                            f"{moneda}{params_a['monto_inicial']:,.2f}",
                            f"{moneda}{params_a.get('aporte_periodico', 0):,.2f}",
                            params_a.get('frecuencia', 'N/A'),
                            f"{params_a['tea']*100:.2f}%",
                            f"{moneda}{resultados_a['total_aportado']:,.2f}",
                            f"{moneda}{resultados_a['interes_total']:,.2f}",
                            f"{moneda}{resultados_a['saldo_final']:,.2f}"
                        ]
                    }
                    
                    df_summary = pd.DataFrame(data_summary)
                    
                    # Si hay datos de módulo B, agregarlos
                    modulo_b_data = st.session_state.get('resultados_modulo_b', None)
                    if modulo_b_data:
                        df_modulo_b = pd.DataFrame({
                            'Concepto': [
                                'Opción Retiro',
                                'Capital Bruto',
                                'Impuesto',
                                'Capital Neto',
                                'TEA Retiro',
                                'Pensión Mensual'
                            ],
                            'Valor': [
                                modulo_b_data['opcion_retiro'],
                                f"{moneda}{modulo_b_data['capital_bruto']:,.2f}",
                                f"{moneda}{modulo_b_data['impuesto']:,.2f}",
                                f"{moneda}{modulo_b_data['capital_neto']:,.2f}",
                                f"{modulo_b_data['tea_retiro']*100:.2f}%",
                                f"{moneda}{modulo_b_data.get('pension_mensual', 0):,.2f}"
                            ]
                        })
                        df_summary = pd.concat([df_summary, df_modulo_b], ignore_index=True)
                    
                    # Convertir a Excel
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_summary.to_excel(writer, sheet_name='Resumen', index=False)
                        
                        # Si hay aportes periódicos, agregar tabla detallada
                        if params_a['tipo_inversion'] == "Aportes periódicos":
                            df_detalle = pd.DataFrame({
                                'Periodo': resultados_a['periodos'],
                                'Aportes Acumulados': resultados_a['aportes'],
                                'Intereses Acumulados': resultados_a['intereses'],
                                'Saldo': resultados_a['saldos']
                            })
                            df_detalle.to_excel(writer, sheet_name='Detalle', index=False)
                    
                    excel_data = output.getvalue()
                    
                    st.download_button(
                        label="⬇️ Descargar Excel",
                        data=excel_data,
                        file_name=f"Reporte_Inversion_Acciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        type="secondary"
                    )
                except Exception as e:
                    st.error(f"❌ Error al generar Excel: {str(e)}")
        
        with col3:
            if st.button("📋 CSV", type="primary", use_container_width=True):
                try:
                    # Crear DataFrame con resumen
                    data_summary = {
                        'Concepto': [
                            'Edad Actual',
                            'Edad Jubilación',
                            'Plazo (años)',
                            'Tipo Inversión',
                            'Monto Inicial',
                            'Aporte Periódico',
                            'Frecuencia',
                            'TEA',
                            'Total Aportado',
                            'Intereses Ganados',
                            'Capital Final'
                        ],
                        'Valor': [
                            f"{params_a['edad_actual']} años",
                            f"{params_a['edad_jubilacion']} años",
                            f"{params_a['plazo']} años",
                            params_a['tipo_inversion'],
                            f"{moneda}{params_a['monto_inicial']:,.2f}",
                            f"{moneda}{params_a.get('aporte_periodico', 0):,.2f}",
                            params_a.get('frecuencia', 'N/A'),
                            f"{params_a['tea']*100:.2f}%",
                            f"{moneda}{resultados_a['total_aportado']:,.2f}",
                            f"{moneda}{resultados_a['interes_total']:,.2f}",
                            f"{moneda}{resultados_a['saldo_final']:,.2f}"
                        ]
                    }
                    
                    df_summary = pd.DataFrame(data_summary)
                    
                    # Si hay datos de módulo B, agregarlos
                    modulo_b_data = st.session_state.get('resultados_modulo_b', None)
                    if modulo_b_data:
                        df_modulo_b = pd.DataFrame({
                            'Concepto': [
                                'Opción Retiro',
                                'Capital Bruto',
                                'Impuesto',
                                'Capital Neto',
                                'TEA Retiro',
                                'Pensión Mensual'
                            ],
                            'Valor': [
                                modulo_b_data['opcion_retiro'],
                                f"{moneda}{modulo_b_data['capital_bruto']:,.2f}",
                                f"{moneda}{modulo_b_data['impuesto']:,.2f}",
                                f"{moneda}{modulo_b_data['capital_neto']:,.2f}",
                                f"{modulo_b_data['tea_retiro']*100:.2f}%",
                                f"{moneda}{modulo_b_data.get('pension_mensual', 0):,.2f}"
                            ]
                        })
                        df_summary = pd.concat([df_summary, df_modulo_b], ignore_index=True)
                    
                    # Convertir a CSV
                    csv_data = df_summary.to_csv(index=False, encoding='utf-8-sig')
                    
                    st.download_button(
                        label="⬇️ Descargar CSV",
                        data=csv_data,
                        file_name=f"Reporte_Inversion_Acciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        type="secondary"
                    )
                except Exception as e:
                    st.error(f"❌ Error al generar CSV: {str(e)}")
    
    # ==================== COMPARACIÓN DE ESCENARIOS ====================
    with tab_comparacion:
        st.subheader("📈 Comparación de Escenarios")
        st.markdown("Compara diferentes opciones de jubilación y tasas de retorno.")
        
        if 'params_modulo_a' not in st.session_state:
            st.warning("⚠️ Primero completa el **Módulo A** para ver comparaciones.")
            return
        
        params_a = st.session_state['params_modulo_a']
        resultados_a = st.session_state['resultados_modulo_a']
        
        st.markdown("### 🎯 Comparación por Edad de Jubilación")
        
        fig_comparacion = crear_grafico_comparacion_escenarios(
            resultados_a['saldo_final'],
            params_a['edad_actual'],
            params_a['tea'],
            moneda
        )
        st.plotly_chart(fig_comparacion, use_container_width=True)
        
        # Interpretación del gráfico
        st.info("""
        **📖 Interpretación:** Este gráfico muestra cómo crece tu capital si sigues invirtiendo hasta diferentes edades de jubilación. 
        Mientras más años mantengas tu inversión, mayor será el monto acumulado debido al interés compuesto. 
        Por ejemplo, jubilarse a los 70 años en lugar de los 60 puede significar tener el doble o más de capital disponible.
        """, icon="💡")
        
        st.markdown("---")
        st.markdown("### 📊 Comparación por TEA")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tea_comparar = st.multiselect(
                "Selecciona TEAs a comparar (%)",
                options=[6, 8, 10, 12, 15, 18, 20],
                default=[10, 12, 15]
            )
        
        with col2:
            años_comparar = st.slider(
                "Años de inversión",
                min_value=5,
                max_value=40,
                value=params_a['plazo']
            )
        
        if tea_comparar:
            comparacion_data = []
            
            for tea_pct in tea_comparar:
                tea = tea_pct / 100
                
                if params_a['tipo_inversion'] == "Depósito único":
                    saldo = params_a['monto_inicial'] * ((1 + tea) ** años_comparar)
                else:
                    # Simplificación para aportes periódicos
                    tasa_periodica = convertir_tea_a_tasa_periodica(tea, params_a['frecuencia'])
                    n = obtener_periodos_por_año(params_a['frecuencia'])
                    total_periodos = años_comparar * n
                    
                    # Valor futuro de anualidad
                    if tasa_periodica > 0:
                        vf_aportes = params_a['aporte_periodico'] * \
                                    (((1 + tasa_periodica) ** total_periodos - 1) / tasa_periodica)
                        vf_inicial = params_a['monto_inicial'] * ((1 + tasa_periodica) ** total_periodos)
                        saldo = vf_inicial + vf_aportes
                    else:
                        saldo = params_a['monto_inicial'] + (params_a['aporte_periodico'] * total_periodos)
                
                comparacion_data.append({
                    'TEA': f"{tea_pct}%",
                    'Saldo Final': saldo
                })
            
            df_comparacion = pd.DataFrame(comparacion_data)
            
            fig_tea = go.Figure(data=[
                go.Bar(
                    x=df_comparacion['TEA'],
                    y=df_comparacion['Saldo Final'],
                    marker=dict(
                        color=df_comparacion['Saldo Final'],
                        colorscale='Viridis',
                        showscale=True
                    ),
                    text=[f"{moneda}{s:,.0f}" for s in df_comparacion['Saldo Final']],
                    textposition='outside'
                )
            ])
            
            fig_tea.update_layout(
                title=f'<b>Comparación de Saldos Finales por TEA ({años_comparar} años)</b>',
                xaxis_title='Tasa Efectiva Anual (TEA)',
                yaxis_title=f'Saldo Final ({moneda})',
                height=450,
                showlegend=False
            )
            
            st.plotly_chart(fig_tea, use_container_width=True)
            
            # Interpretación del gráfico de TEA
            if len(tea_comparar) > 0:
                tea_min = min(tea_comparar)
                tea_max = max(tea_comparar)
                saldo_min = df_comparacion.loc[df_comparacion['TEA'] == f"{tea_min}%", 'Saldo Final'].values[0]
                saldo_max = df_comparacion.loc[df_comparacion['TEA'] == f"{tea_max}%", 'Saldo Final'].values[0]
                diferencia_pct = ((saldo_max - saldo_min) / saldo_min) * 100
                
                st.info(f"""
                **📖 Interpretación:** Este gráfico compara cómo diferentes tasas de retorno (TEA) impactan tu capital final 
                después de {años_comparar} años. Una diferencia de solo {tea_max-tea_min} puntos porcentuales en la TEA 
                (de {tea_min}% a {tea_max}%) puede resultar en {diferencia_pct:.1f}% más de capital. 
                Esto resalta la importancia de buscar inversiones con mejores rendimientos y mantenerlas a largo plazo.
                """, icon="💡")
            
            # Tabla de comparación
            st.dataframe(
                df_comparacion.style.format({
                    'Saldo Final': f'{moneda}{{:,.2f}}'
                }),
                use_container_width=True
            )
