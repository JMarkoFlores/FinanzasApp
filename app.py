import streamlit as st
from bono import mostrar_calculadora_bonos
from acciones import mostrar_calculadora_acciones

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Finanzas",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("💰 Dashboard de Finanzas")
st.markdown("Herramienta integral para análisis de bonos y acciones")

# Sidebar - Menú de navegación
st.sidebar.title("Navegación")
st.sidebar.markdown("---")

opcion = st.sidebar.radio(
    "Selecciona una opción:",
    ["🏠 Inicio", "📊 Bonos", "📈 Acciones"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Dashboard de Finanzas v1.0**

Esta aplicación te permite:
- Calcular el valor de bonos
- Analizar inversiones en acciones
- Tomar decisiones informadas
""")

# Contenido principal según la opción seleccionada
if opcion == "🏠 Inicio":
    st.header("Bienvenido al Dashboard de Finanzas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Calculadora de Bonos")
        st.markdown("""
        Herramienta especializada para:
        - Calcular el valor presente de bonos
        - Analizar flujos de efectivo
        - Determinar si un bono es una buena inversión
        - Comparar tasa cupón vs tasa de rendimiento
        
        **Características:**
        - Múltiples periodos (mensual, trimestral, semestral, anual)
        - Cálculo automático de cupones
        - Diagramas de flujo de caja
        - Recomendaciones de inversión
        """)
        
        if st.button("Ir a Bonos", use_container_width=True):
            st.sidebar.radio("Selecciona una opción:", ["🏠 Inicio", "📊 Bonos", "📈 Acciones"], index=1)
    
    with col2:
        st.subheader("📈 Calculadora de Acciones")
        st.markdown("""
        Herramienta completa para:
        - Valoración de acciones por dividendos
        - Análisis de retorno de inversión
        - Comparación entre múltiples acciones
        - Proyecciones de dividendos
        
        **Tipos de inversión:**
        - Inversiones locales en Perú (PEN)
        - Inversiones extranjeras (USD)
        
        **Modelos incluidos:**
        - Modelo de Gordon (crecimiento de dividendos)
        - Análisis de retorno total
        - Métricas comparativas
        """)
        
        if st.button("Ir a Acciones", use_container_width=True):
            st.sidebar.radio("Selecciona una opción:", ["🏠 Inicio", "📊 Bonos", "📈 Acciones"], index=2)
    
    st.markdown("---")
    
    # Información adicional
    st.subheader("📚 Conceptos Clave")
    
    with st.expander("¿Qué son los Bonos?"):
        st.markdown("""
        Los bonos son instrumentos de deuda emitidos por gobiernos o empresas para obtener financiamiento. 
        Al comprar un bono, estás prestando dinero al emisor a cambio de:
        
        - **Pagos periódicos** (cupones): Intereses pagados regularmente
        - **Valor nominal**: El monto principal devuelto al vencimiento
        
        El valor de un bono depende de:
        - La tasa cupón (tasa de interés del bono)
        - La tasa de rendimiento requerida por el mercado
        - El tiempo hasta el vencimiento
        """)
    
    with st.expander("¿Qué son las Acciones?"):
        st.markdown("""
        Las acciones representan una porción de propiedad en una empresa. Como accionista, tienes derecho a:
        
        - **Dividendos**: Parte de las ganancias distribuidas a los accionistas
        - **Apreciación del capital**: Ganancias cuando el precio de la acción sube
        - **Derechos de voto**: Participación en decisiones importantes de la empresa
        
        Factores que afectan el valor:
        - Desempeño financiero de la empresa
        - Dividendos pagados
        - Condiciones del mercado
        - Perspectivas de crecimiento
        """)
    
    with st.expander("Conceptos Financieros Importantes"):
        st.markdown("""
        - **TEA (Tasa Efectiva Anual)**: Tasa de rendimiento anual que considera la capitalización
        - **Valor Presente**: Valor actual de flujos de efectivo futuros
        - **Dividend Yield**: Rendimiento por dividendos (dividendo/precio)
        - **P/E Ratio**: Relación precio/ganancias de una acción
        - **Beta**: Medida de volatilidad en comparación con el mercado
        - **Valor Intrínseco**: Valor real estimado de un activo
        """)

elif opcion == "📊 Bonos":
    mostrar_calculadora_bonos()

elif opcion == "📈 Acciones":
    mostrar_calculadora_acciones()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>Dashboard de Finanzas | Desarrollado con Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
