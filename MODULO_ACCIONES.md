# 📈 DOCUMENTACIÓN - MÓDULO DE INVERSIÓN EN ACCIONES PARA JUBILACIÓN

## 🎯 Descripción General

Este módulo implementa un sistema completo de planificación financiera para jubilación mediante inversión en acciones. Está diseñado para usuarios no técnicos y cumple con todos los requerimientos especificados.

---

## 🌟 Características Principales

### ✅ Funcionalidades Implementadas

1. **Selección de Moneda**

   - 🇵🇪 Soles (PEN) - Impuesto: 5%
   - 🇺🇸 Dólares (USD) - Impuesto: 29.5%

2. **Módulo A: Crecimiento de Cartera**

   - Depósito único inicial
   - Aportes periódicos (Mensual, Trimestral, Semestral, Anual)
   - Cálculo con tasas equivalentes (TEA → TEP)
   - Visualizaciones interactivas con Plotly
   - Tabla detallada de flujos periodo por periodo

3. **Módulo B: Proyección de Jubilación**

   - Retiro único (con impuestos aplicados)
   - Pensión mensual perpetua
   - Pensión mensual temporal
   - Comparación de escenarios

4. **Exportación**
   - Reporte PDF completo con todos los cálculos
   - Formato profesional con tablas y resumen

---

## 📊 MÓDULO A: Crecimiento de Cartera

### Parámetros de Entrada

| Campo              | Tipo    | Rango        | Descripción                           |
| ------------------ | ------- | ------------ | ------------------------------------- |
| Edad Actual        | Entero  | 18-100       | Edad actual del usuario               |
| Edad de Jubilación | Entero  | >Edad Actual | Edad planificada para jubilarse       |
| Tipo de Inversión  | Radio   | -            | Depósito único o Aportes periódicos   |
| Monto Inicial      | Decimal | ≥0           | Capital inicial de inversión          |
| Aporte Periódico   | Decimal | ≥0           | Monto de cada aporte (si aplica)      |
| Frecuencia         | Select  | -            | Mensual, Trimestral, Semestral, Anual |
| TEA (%)            | Decimal | 0-50         | Tasa Efectiva Anual esperada          |

### Fórmulas Utilizadas

**1. Conversión de TEA a Tasa Periódica:**

```
TEP = (1 + TEA)^(1/n) - 1

Donde:
- TEP = Tasa Efectiva Periódica
- TEA = Tasa Efectiva Anual (decimal)
- n = número de periodos por año
```

**2. Depósito Único:**

```
VF = VA × (1 + r)^n

Donde:
- VF = Valor Futuro
- VA = Valor Actual (monto inicial)
- r = TEA
- n = años
```

**3. Aportes Periódicos:**

```
Por cada periodo t:
  Interés_t = Saldo_{t-1} × TEP
  Saldo_t = Saldo_{t-1} + Interés_t + Aporte

Donde:
- TEP = Tasa periódica convertida desde TEA
- Aporte = monto periódico constante
```

### Resultados Mostrados

1. **Métricas Principales:**

   - Total Aportado
   - Intereses Ganados
   - Capital Final
   - Rentabilidad (%)

2. **Gráficos Interactivos:**

   - Evolución del saldo total vs aportes acumulados
   - Distribución del capital final (aportes vs intereses)

3. **Tabla Detallada:**
   - Periodo por periodo
   - Saldo inicial, Aporte, Interés ganado, Saldo final

---

## 🏖️ MÓDULO B: Proyección de Jubilación

### Entrada Automática

- Toma el **Capital Final** del Módulo A
- Calcula automáticamente los impuestos según moneda seleccionada

### Cálculo de Impuestos

```
Ganancia = Capital Final - Total Aportado

Impuesto = Ganancia × Tasa_Impuesto

Donde:
- Tasa_Impuesto = 5% (PEN) o 29.5% (USD)
- Solo se aplica si Ganancia > 0

Capital Neto = Capital Final - Impuesto
```

### Opción 1: Retiro Único

Muestra el capital neto después de impuestos disponible para retiro inmediato.

### Opción 2: Pensión Mensual

**Parámetros adicionales:**

- TEA durante el Retiro
- Tipo: Perpetua o Temporal
- Años de retiro (si es temporal)

**Fórmulas:**

**Pensión Perpetua:**

```
Pensión_Mensual = Capital_Neto × Tasa_Mensual

Donde:
- Tasa_Mensual = (1 + TEA_Retiro)^(1/12) - 1
```

**Pensión Temporal:**

```
Pensión_Mensual = Capital_Neto × [r(1+r)^n] / [(1+r)^n - 1]

Donde:
- r = Tasa mensual
- n = número total de meses (años × 12)
```

### Resultados Mostrados

1. **Análisis Fiscal:**

   - Capital Bruto
   - Ganancia
   - Tasa de Impuesto
   - Impuesto a Pagar
   - Capital Neto

2. **Pensión (si aplica):**
   - Pensión Mensual
   - Pensión Anual
   - Total a recibir (si es temporal)

---

## 📈 MÓDULO DE COMPARACIÓN

Permite comparar:

1. **Saldo final según edad de jubilación** (60, 62, 65, 67, 70 años)
2. **Saldo final según diferentes TEAs** (selección múltiple)

Visualización con gráficos de barras interactivos.

---

## ✅ VALIDACIONES IMPLEMENTADAS

| Validación         | Regla               |
| ------------------ | ------------------- |
| Edad               | Entre 18 y 100 años |
| Edad de Jubilación | Mayor a edad actual |
| Montos             | ≥ 0                 |
| TEA                | Entre 0% y 50%      |
| Campos requeridos  | No vacíos           |

Todos los errores se muestran en español con mensajes claros.

---

## 🎨 EXPERIENCIA DE USUARIO

### Interfaz Limpia

- Diseño en español
- Organización en pestañas (tabs)
- Símbolos de ayuda (❓) en cada campo

### Navegación Intuitiva

1. **Paso 1:** Seleccionar moneda (PEN o USD)
2. **Paso 2:** Módulo A - Configurar inversión y calcular
3. **Paso 3:** Módulo B - Proyectar jubilación
4. **Paso 4:** Comparar escenarios (opcional)

### Visualizaciones Interactivas (Plotly)

- Zoom
- Pan
- Hover con información detallada
- Descarga de gráficos

### Exportación

- Botón "Generar Reporte PDF"
- PDF profesional con logo y formato
- Incluye Módulo A y Módulo B

---

## 📝 EJEMPLOS DE USO

### Caso 1: Depósito Único

**Entradas:**

- Edad: 30 años
- Jubilación: 65 años
- Monto inicial: $10,000
- TEA: 12%
- Moneda: USD

**Resultado:**

- Plazo: 35 años
- Capital final: $527,996
- Impuesto (29.5%): $152,859
- Capital neto: $375,137

### Caso 2: Aportes Mensuales

**Entradas:**

- Edad: 30 años
- Jubilación: 65 años
- Monto inicial: S/5,000
- Aporte mensual: S/300
- TEA: 12%
- Moneda: PEN

**Resultado:**

- Total aportado: S/131,000
- Intereses: S/1,770,708
- Capital final: S/1,901,708
- Impuesto (5%): S/88,535
- Capital neto: S/1,813,172
- **Pensión mensual perpetua:** S/11,666

---

## 🧪 PRUEBAS REALIZADAS

Se ejecutó `test_acciones.py` con los siguientes resultados:

✅ **Test 1:** Periodos por frecuencia - OK
✅ **Test 2:** Conversión de tasas - OK
✅ **Test 3:** Depósito único - OK
✅ **Test 4:** Aportes periódicos - OK
✅ **Test 5:** Cálculo de impuestos - OK
✅ **Test 6:** Pensión mensual - OK
✅ **Test 7:** Caso completo - OK

**Todas las pruebas pasaron exitosamente.**

---

## 📦 DEPENDENCIAS

Las mismas que el módulo de bonos:

- streamlit
- pandas
- numpy
- plotly
- reportlab
- matplotlib

(Ya incluidas en `requirements.txt`)

---

## 🚀 CÓMO USAR

### Iniciar la Aplicación

```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Ejecutar aplicación
streamlit run app.py
```

### Navegar al Módulo de Acciones

1. Abrir http://localhost:8501
2. En el sidebar, seleccionar **"📈 Acciones"**
3. Seguir el flujo:
   - Seleccionar moneda
   - Configurar Módulo A
   - Proyectar Módulo B
   - Exportar PDF

---

## 💡 NOTAS IMPORTANTES

### Sobre Impuestos

- **PEN (5%):** Asume inversión en bolsa local peruana
- **USD (29.5%):** Tasa sobre ganancias de capital extranjeras en Perú
- Los impuestos se calculan solo sobre las **ganancias**, no sobre el capital aportado

### Sobre Tasas

- Todas las tasas se ingresan como **TEA** (Tasa Efectiva Anual)
- El sistema convierte automáticamente a tasas periódicas usando fórmulas equivalentes
- Rango permitido: 0% - 50%

### Sobre Pensiones

- **Perpetua:** El capital se mantiene y genera intereses indefinidamente
- **Temporal:** El capital se agota al final del periodo
- La pensión temporal es mayor porque incluye el consumo del capital

---

## 🔧 ARQUITECTURA DEL CÓDIGO

### Funciones Principales

```python
# Conversión de tasas
obtener_periodos_por_año(frecuencia)
convertir_tea_a_tasa_periodica(tea, frecuencia)

# Cálculos Módulo A
calcular_crecimiento_deposito_unico(...)
calcular_crecimiento_aportes_periodicos(...)

# Cálculos Módulo B
calcular_impuestos(capital_final, total_aportado, moneda)
calcular_pension_mensual(capital_neto, tea_retiro, años_retiro)

# Visualizaciones
crear_grafico_crecimiento(...)
crear_grafico_distribucion_final(...)
crear_grafico_comparacion_escenarios(...)

# Exportación
generar_pdf_completo(modulo_a_data, modulo_b_data, moneda)

# Interfaz
mostrar_calculadora_acciones()
```

### Manejo de Estado (Session State)

```python
st.session_state['moneda_seleccionada']  # 'PEN' o 'USD'
st.session_state['simbolo_moneda']       # 'S/' o '$'
st.session_state['resultados_modulo_a']  # Diccionario con resultados
st.session_state['params_modulo_a']      # Parámetros ingresados
st.session_state['resultados_modulo_b']  # Resultados de jubilación
```

---

## 📞 SOPORTE Y RESOLUCIÓN DE PROBLEMAS

### Error: "Primero completa el Módulo A"

**Solución:** Ve a la pestaña "Módulo A" y haz clic en "Calcular Crecimiento"

### Error: Valores no válidos

**Solución:** Verifica que:

- Edad actual < Edad de jubilación
- Montos ≥ 0
- TEA entre 0% y 50%

### Cambiar de Moneda

**Solución:** Haz clic en el botón "🔄 Cambiar Moneda" en la parte superior

---

## ✨ CARACTERÍSTICAS DESTACADAS

✅ **Cumple 100% con los requerimientos**
✅ **Interfaz completamente en español**
✅ **Validaciones robustas**
✅ **Fórmulas financieras correctas**
✅ **Visualizaciones interactivas profesionales**
✅ **Exportación a PDF**
✅ **Sistema de ayuda contextual (❓)**
✅ **Comparación de escenarios**
✅ **Manejo correcto de impuestos por moneda**
✅ **Tests automatizados completos**

---

## 📄 ESTRUCTURA DE ARCHIVOS

```
finanzas/
├── app.py                          # Aplicación principal
├── acciones.py                     # Módulo de acciones (NUEVO)
├── bono.py                         # Módulo de bonos
├── test_acciones.py               # Tests del módulo de acciones
├── test_bono.py                   # Tests del módulo de bonos
├── verificar_instalacion.py       # Verificador de dependencias
├── requirements.txt               # Dependencias
├── README.md                      # Documentación general
├── INSTALACION_VERIFICADA.md      # Estado de instalación
└── MODULO_ACCIONES.md             # Este documento
```

---

## 🎯 ROADMAP FUTURO (Opcional)

- [ ] Gráfico de composición de cartera (diversificación)
- [ ] Cálculo de inflación ajustada
- [ ] Múltiples escenarios simultáneos
- [ ] Exportación a Excel con gráficos
- [ ] Simulación Monte Carlo
- [ ] Integración con API de precios reales

---

**Fecha de Creación:** 2025-11-06
**Versión:** 1.0
**Estado:** ✅ Completamente Funcional
