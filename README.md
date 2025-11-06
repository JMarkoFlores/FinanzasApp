# 💰 Dashboard de Finanzas

Aplicación web desarrollada con Streamlit para análisis financiero de bonos y acciones.

## � Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 📦 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd c:\Users\jeanm\Documents\finanzas
```

### 2. Crear entorno virtual (Recomendado)

```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows CMD
python -m venv venv
venv\Scripts\activate.bat

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Verificar instalación

```bash
python verificar_instalacion.py
```

Este script verificará que todas las librerías estén correctamente instaladas.

## �🚀 Ejecución

Para ejecutar la aplicación:

```bash
streamlit run app.py
```

La aplicación estará disponible en: http://localhost:8501

## � Librerías Utilizadas

| Librería        | Versión | Propósito                 |
| --------------- | ------- | ------------------------- |
| streamlit       | ≥1.28.0 | Framework web principal   |
| pandas          | ≥2.0.0  | Manipulación de datos     |
| numpy           | ≥1.24.0 | Cálculos numéricos        |
| matplotlib      | ≥3.7.0  | Visualización estática    |
| plotly          | ≥5.0.0  | Visualización interactiva |
| openpyxl        | ≥3.1.0  | Exportación a Excel       |
| reportlab       | ≥4.0.0  | Generación de PDF         |
| pillow          | ≥10.0.0 | Procesamiento de imágenes |
| python-dateutil | ≥2.8.0  | Manejo de fechas          |

## 🏗️ Estructura del Proyecto

```
finanzas/
│
├── app.py                      # Aplicación principal (punto de entrada)
├── bono.py                     # Módulo de calculadora de bonos
├── acciones.py                 # Módulo de calculadora de acciones
├── requirements.txt            # Dependencias del proyecto
├── verificar_instalacion.py   # Script de verificación
├── test_bono.py               # Tests del módulo de bonos
└── README.md                  # Este archivo
```

## 📊 Módulo de Bonos

### Características Principales:

1. **Parámetros Configurables:**

   - Valor nominal (default: $20,000)
   - Periodo de pago: Mensual, Bimestral, Trimestral, Cuatrimestral, Semestral, Anual
   - Tiempo de inversión en años
   - Tasa cupón anual (TEA) (default: 10%)
   - Tasa de retorno esperada (TEA) (default: 12%)

2. **Cálculos Automáticos:**

   - Cupón periódico usando tasas equivalentes
   - Conversión de TEA a tasa efectiva periódica: TEP = (1 + TEA)^(1/n) - 1
   - Valor presente del bono
   - Flujos de efectivo actualizados
   - VP acumulado periodo por periodo

3. **Visualizaciones Interactivas (Plotly):**

   - Diagrama de flujo de efectivo
   - Gráfico de VP acumulado
   - Análisis de sensibilidad (precio vs tasa de descuento)
   - VP acumulado

4. **Diagrama de Flujo de Efectivo Visual:**

   - Representación gráfica de ingresos y egresos
   - Flechas rojas para inversión inicial (salida)
   - Flechas verdes para cupones periódicos (entradas)
   - Flechas azules para valor nominal al vencimiento (entrada)
   - Línea de tiempo con todos los periodos

5. **Tabla Detallada:**

   - Periodo
   - Flujo de efectivo
   - Flujo actualizado (valor presente)
   - VP acumulado
   - Tipo de flujo
   - Formato con gradiente de colores

6. **Alertas Inteligentes:**

   - Alerta verde cuando TEA > Tasa Cupón (oportunidad de ganancia)
   - Alerta roja cuando TEA < Tasa Cupón (pérdida potencial)
   - Mensaje informativo cuando son iguales

7. **Recomendaciones de Inversión:**

   - Análisis automático COMPRAR/NO COMPRAR/MANTENER
   - Explicación detallada de la decisión
   - Cálculo de margen de seguridad o sobrevaloración

8. **Opciones de Descarga:**

   **📊 Descarga en Excel (.xlsx):**

   - Hoja 1: Resumen con todos los parámetros del bono
   - Hoja 2: Detalle completo de pagos periódicos
   - Formato profesional con anchos de columna ajustados
   - Fecha y hora de generación

   **📄 Descarga en PDF:**

   - Reporte profesional con encabezados estilizados
   - Tabla resumen de parámetros del bono
   - Tabla detallada de todos los pagos periódicos
   - Formato con colores corporativos
   - Fecha y hora de generación

## 📈 Módulo de Acciones

### Características:

1. **Tipos de Inversión:**

   - Inversión Local (Perú - PEN)
   - Inversión Extranjera (USD)

2. **Tres Secciones de Análisis:**

   **Valoración por Dividendos (Modelo de Gordon):**

   - Cálculo de valor intrínseco
   - Comparación con precio de mercado
   - Recomendación COMPRAR/VENDER/MANTENER
   - Proyección de dividendos para 10 años

   **Análisis de Retorno:**

   - Cálculo de ganancia de capital
   - Ganancias por dividendos
   - Retorno total y anualizado
   - Interpretación del rendimiento

   **Comparación de Acciones:**

   - Comparar hasta 5 acciones simultáneamente
   - Métricas: Precio, Dividendo, Dividend Yield, P/E Ratio, Beta
   - Tabla con resaltado de mejores valores

## 🔧 Tecnologías Utilizadas

- **Streamlit**: Framework de aplicación web
- **Pandas**: Manipulación de datos
- **NumPy**: Cálculos numéricos
- **Matplotlib**: Generación de gráficos
- **OpenPyXL**: Generación de archivos Excel
- **ReportLab**: Generación de archivos PDF

## 📝 Fórmulas Financieras

### Conversión de TEA a Tasa Periódica:

```
Tasa_Periodo = (1 + TEA)^(1/n) - 1
```

Donde n es el número de periodos en un año:

- Anual: n = 1
- Semestral: n = 2
- Trimestral: n = 4
- Mensual: n = 12

### Valor Presente de un Bono:

```
VP = Σ(Cupón_t / (1 + r)^t) + VN / (1 + r)^n
```

Donde:

- Cupón_t = Pago de cupón en el periodo t
- r = Tasa de descuento por periodo
- VN = Valor nominal
- n = Número total de periodos

### Modelo de Gordon (Valoración de Acciones):

```
Valor = D₁ / (r - g)
```

Donde:

- D₁ = Dividendo esperado del próximo periodo
- r = Tasa de descuento
- g = Tasa de crecimiento de dividendos

## 🎨 Interfaz de Usuario

- **Sidebar**: Navegación entre módulos (Inicio, Bonos, Acciones)
- **Layout de 2 columnas**: Para organizar inputs
- **Métricas visuales**: Para mostrar resultados clave
- **Tablas interactivas**: Con formato y colores
- **Botones de descarga**: Para exportar reportes
- **Diseño responsive**: Se adapta a diferentes tamaños de pantalla

## 📌 Notas Importantes

- Todos los cálculos usan **tasas efectivas** para mayor precisión
- El sistema de alertas es en **tiempo real** al modificar parámetros
- Los reportes incluyen **fecha y hora** de generación
- El diagrama de flujo usa **convención financiera**: salidas en rojo (negativo), entradas en verde/azul (positivo)

## 🤝 Contribuciones

Este proyecto es una herramienta educativa y profesional para análisis financiero.

## 📄 Licencia

Libre para uso educativo y profesional.

---

**Desarrollado con Streamlit** | Última actualización: Noviembre 2025
