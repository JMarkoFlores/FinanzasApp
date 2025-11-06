import streamlit as st
import pandas as pd
import numpy as np

def calcular_valor_accion_dividendos(dividendo, tasa_crecimiento, tasa_descuento):
    """
    Modelo de Gordon para valoración de acciones con dividendos crecientes
    """
    if tasa_descuento <= tasa_crecimiento:
        return None
    
    valor = dividendo * (1 + tasa_crecimiento) / (tasa_descuento - tasa_crecimiento)
    return valor

def calcular_retorno_esperado(precio_compra, precio_venta, dividendos, tiempo):
    """
    Calcula el retorno esperado de una inversión en acciones
    """
    ganancia_capital = precio_venta - precio_compra
    ganancia_total = ganancia_capital + dividendos
    retorno = (ganancia_total / precio_compra) * 100
    retorno_anualizado = ((1 + ganancia_total/precio_compra) ** (1/tiempo) - 1) * 100
    
    return retorno, retorno_anualizado

def mostrar_calculadora_acciones():
    st.header("Calculadora de Acciones")
    
    # Selector de tipo de inversión
    tipo_inversion = st.radio(
        "Tipo de Inversión",
        ["Inversión Local (Perú - PEN)", "Inversión Extranjera (USD)"],
        horizontal=True
    )
    
    moneda = "S/" if "Local" in tipo_inversion else "$"
    moneda_texto = "Soles (PEN)" if "Local" in tipo_inversion else "Dólares (USD)"
    
    st.markdown(f"**Moneda: {moneda_texto}**")
    st.markdown("---")
    
    # Tabs para diferentes tipos de análisis
    tab1, tab2, tab3 = st.tabs(["Valoración por Dividendos", "Análisis de Retorno", "Comparación de Acciones"])
    
    with tab1:
        st.subheader("Modelo de Valoración por Dividendos (Gordon)")
        st.markdown("Este modelo es útil para acciones que pagan dividendos constantes o crecientes.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dividendo_actual = st.number_input(
                f"Dividendo Actual por Acción ({moneda})",
                min_value=0.0,
                value=2.0 if "Local" in tipo_inversion else 0.5,
                step=0.1,
                format="%.2f"
            )
            
            tasa_crecimiento = st.number_input(
                "Tasa de Crecimiento de Dividendos (%)",
                min_value=0.0,
                value=5.0,
                step=0.5,
                format="%.2f"
            ) / 100
        
        with col2:
            tasa_descuento = st.number_input(
                "Tasa de Descuento/Rendimiento Requerido (%)",
                min_value=0.0,
                value=12.0 if "Local" in tipo_inversion else 10.0,
                step=0.5,
                format="%.2f",
                help="Tasa de rendimiento que esperas obtener"
            ) / 100
            
            precio_mercado = st.number_input(
                f"Precio Actual de Mercado ({moneda})",
                min_value=0.0,
                value=30.0 if "Local" in tipo_inversion else 25.0,
                step=1.0,
                format="%.2f"
            )
        
        if tasa_descuento > tasa_crecimiento:
            valor_intrinseco = calcular_valor_accion_dividendos(dividendo_actual, tasa_crecimiento, tasa_descuento)
            
            st.markdown("### Resultados del Análisis")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Valor Intrínseco", f"{moneda}{valor_intrinseco:.2f}")
            with col2:
                st.metric("Precio de Mercado", f"{moneda}{precio_mercado:.2f}")
            with col3:
                diferencia = valor_intrinseco - precio_mercado
                porcentaje = (diferencia / precio_mercado) * 100
                st.metric("Diferencia", f"{moneda}{diferencia:.2f}", delta=f"{porcentaje:.2f}%")
            
            st.markdown("---")
            
            # Recomendación
            if valor_intrinseco > precio_mercado:
                margen = ((valor_intrinseco - precio_mercado) / precio_mercado) * 100
                st.success(f"**RECOMENDACIÓN: COMPRAR**")
                st.markdown(f"""
                La acción está **subvalorada** en el mercado.
                
                - **Valor intrínseco**: {moneda}{valor_intrinseco:.2f}
                - **Precio de mercado**: {moneda}{precio_mercado:.2f}
                - **Margen de seguridad**: {margen:.2f}%
                
                Esta podría ser una buena oportunidad de compra, ya que el precio de mercado está por debajo 
                del valor calculado según los dividendos esperados.
                """)
            elif valor_intrinseco < precio_mercado:
                sobrevalorada = ((precio_mercado - valor_intrinseco) / valor_intrinseco) * 100
                st.error(f"**RECOMENDACIÓN: NO COMPRAR / VENDER**")
                st.markdown(f"""
                La acción está **sobrevalorada** en el mercado.
                
                - **Valor intrínseco**: {moneda}{valor_intrinseco:.2f}
                - **Precio de mercado**: {moneda}{precio_mercado:.2f}
                - **Sobrevaloración**: {sobrevalorada:.2f}%
                
                El precio actual está por encima de su valor intrínseco. Considera esperar a que el precio baje
                o buscar otras oportunidades de inversión.
                """)
            else:
                st.info(f"**RECOMENDACIÓN: MANTENER**")
                st.markdown(f"""
                La acción está **correctamente valorada**.
                
                - **Valor intrínseco**: {moneda}{valor_intrinseco:.2f}
                - **Precio de mercado**: {moneda}{precio_mercado:.2f}
                
                El precio de mercado refleja adecuadamente el valor de la acción según los dividendos esperados.
                """)
            
            # Proyección de dividendos
            st.markdown("---")
            st.subheader("Proyección de Dividendos (Próximos 10 años)")
            
            años = list(range(1, 11))
            dividendos_proyectados = [dividendo_actual * (1 + tasa_crecimiento) ** año for año in años]
            
            df_proyeccion = pd.DataFrame({
                'Año': años,
                f'Dividendo por Acción ({moneda})': dividendos_proyectados
            })
            
            st.dataframe(
                df_proyeccion.style.format({f'Dividendo por Acción ({moneda})': '{:.2f}'}),
                use_container_width=True
            )
            
        else:
            st.error("⚠️ La tasa de descuento debe ser mayor que la tasa de crecimiento para aplicar este modelo.")
    
    with tab2:
        st.subheader("Análisis de Retorno de Inversión")
        st.markdown("Calcula el retorno esperado de una inversión en acciones.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            precio_compra = st.number_input(
                f"Precio de Compra ({moneda})",
                min_value=0.0,
                value=100.0 if "Local" in tipo_inversion else 50.0,
                step=1.0,
                format="%.2f"
            )
            
            precio_venta_esperado = st.number_input(
                f"Precio de Venta Esperado ({moneda})",
                min_value=0.0,
                value=120.0 if "Local" in tipo_inversion else 60.0,
                step=1.0,
                format="%.2f"
            )
        
        with col2:
            dividendos_totales = st.number_input(
                f"Dividendos Totales Recibidos ({moneda})",
                min_value=0.0,
                value=10.0 if "Local" in tipo_inversion else 5.0,
                step=0.5,
                format="%.2f"
            )
            
            tiempo_inversion = st.number_input(
                "Tiempo de Inversión (años)",
                min_value=0.1,
                value=2.0,
                step=0.5,
                format="%.1f"
            )
        
        cantidad_acciones = st.number_input(
            "Cantidad de Acciones",
            min_value=1,
            value=100,
            step=10
        )
        
        # Calcular resultados
        inversion_total = precio_compra * cantidad_acciones
        ganancia_capital = (precio_venta_esperado - precio_compra) * cantidad_acciones
        dividendos_total = dividendos_totales * cantidad_acciones
        ganancia_total = ganancia_capital + dividendos_total
        valor_final = precio_venta_esperado * cantidad_acciones + dividendos_total
        
        retorno_total = (ganancia_total / inversion_total) * 100
        retorno_anualizado = ((1 + ganancia_total/inversion_total) ** (1/tiempo_inversion) - 1) * 100
        
        st.markdown("### Resultados del Análisis")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Inversión Inicial", f"{moneda}{inversion_total:,.2f}")
        with col2:
            st.metric("Valor Final", f"{moneda}{valor_final:,.2f}")
        with col3:
            st.metric("Ganancia Total", f"{moneda}{ganancia_total:,.2f}")
        with col4:
            st.metric("Retorno Total", f"{retorno_total:.2f}%")
        
        st.markdown(f"#### Retorno Anualizado: **{retorno_anualizado:.2f}%**")
        
        # Desglose de ganancias
        st.markdown("---")
        st.subheader("Desglose de Ganancias")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Ganancia de Capital", f"{moneda}{ganancia_capital:,.2f}", 
                     delta=f"{(ganancia_capital/inversion_total)*100:.2f}%")
        with col2:
            st.metric("Ganancias por Dividendos", f"{moneda}{dividendos_total:,.2f}",
                     delta=f"{(dividendos_total/inversion_total)*100:.2f}%")
        
        # Interpretación
        st.markdown("---")
        st.subheader("Interpretación")
        
        if retorno_anualizado > 15:
            st.success("**Excelente retorno de inversión**")
            st.markdown(f"""
            Con un retorno anualizado de {retorno_anualizado:.2f}%, esta inversión supera ampliamente 
            las expectativas típicas del mercado. Es una inversión muy rentable.
            """)
        elif retorno_anualizado > 8:
            st.success("**Buen retorno de inversión**")
            st.markdown(f"""
            Con un retorno anualizado de {retorno_anualizado:.2f}%, esta inversión ofrece un rendimiento 
            sólido y atractivo para el perfil de riesgo de acciones.
            """)
        elif retorno_anualizado > 0:
            st.info("**Retorno moderado**")
            st.markdown(f"""
            Con un retorno anualizado de {retorno_anualizado:.2f}%, esta inversión genera ganancias positivas, 
            aunque podrías considerar si hay mejores alternativas en el mercado.
            """)
        else:
            st.error("**Retorno negativo**")
            st.markdown(f"""
            Con un retorno anualizado de {retorno_anualizado:.2f}%, esta inversión genera pérdidas. 
            Revisa tu estrategia de inversión y considera vender si las perspectivas no mejoran.
            """)
    
    with tab3:
        st.subheader("Comparación de Acciones")
        st.markdown("Compara múltiples acciones para tomar mejores decisiones de inversión.")
        
        num_acciones = st.number_input("Número de acciones a comparar", min_value=2, max_value=5, value=3)
        
        datos_acciones = []
        
        for i in range(num_acciones):
            with st.expander(f"Acción {i+1}", expanded=(i==0)):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    nombre = st.text_input(f"Nombre", value=f"Acción {i+1}", key=f"nombre_{i}")
                    precio = st.number_input(f"Precio ({moneda})", min_value=0.0, value=50.0, step=1.0, key=f"precio_{i}")
                
                with col2:
                    dividendo = st.number_input(f"Dividendo Anual ({moneda})", min_value=0.0, value=2.0, step=0.1, key=f"div_{i}")
                    crecimiento = st.number_input(f"Crecimiento (%)", min_value=0.0, value=5.0, step=0.5, key=f"crec_{i}")
                
                with col3:
                    pe_ratio = st.number_input(f"P/E Ratio", min_value=0.0, value=15.0, step=0.5, key=f"pe_{i}")
                    beta = st.number_input(f"Beta", min_value=0.0, value=1.0, step=0.1, key=f"beta_{i}")
                
                dividend_yield = (dividendo / precio) * 100 if precio > 0 else 0
                
                datos_acciones.append({
                    'Acción': nombre,
                    f'Precio ({moneda})': precio,
                    f'Dividendo ({moneda})': dividendo,
                    'Dividend Yield (%)': dividend_yield,
                    'Crecimiento (%)': crecimiento,
                    'P/E Ratio': pe_ratio,
                    'Beta': beta
                })
        
        df_comparacion = pd.DataFrame(datos_acciones)
        
        st.markdown("### Tabla Comparativa")
        st.dataframe(
            df_comparacion.style.format({
                f'Precio ({moneda})': '{:.2f}',
                f'Dividendo ({moneda})': '{:.2f}',
                'Dividend Yield (%)': '{:.2f}',
                'Crecimiento (%)': '{:.2f}',
                'P/E Ratio': '{:.2f}',
                'Beta': '{:.2f}'
            }).highlight_max(subset=['Dividend Yield (%)', 'Crecimiento (%)'], color='lightgreen')
              .highlight_min(subset=['P/E Ratio', 'Beta'], color='lightblue'),
            use_container_width=True
        )
        
        st.markdown("---")
        st.markdown("""
        **Guía de interpretación:**
        - **Dividend Yield**: Mayor es mejor (más ingresos por dividendos)
        - **Crecimiento**: Mayor es mejor (mayor potencial de apreciación)
        - **P/E Ratio**: Menor suele ser mejor (menos sobrevalorada)
        - **Beta**: Menor es menos volátil (menos riesgo), mayor es más volátil (más riesgo)
        """)
