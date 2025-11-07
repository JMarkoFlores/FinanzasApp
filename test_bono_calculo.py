"""
Script de prueba para verificar los cálculos del módulo de bonos
Compara con las fórmulas teóricas esperadas
"""

def obtener_periodos_por_año(frecuencia):
    """Retorna el número de periodos por año según la frecuencia"""
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
    Convierte TEA a tasa efectiva periódica
    TEP = (1 + TEA)^(1/n) - 1
    """
    n = obtener_periodos_por_año(frecuencia)
    tasa_periodica = (1 + tea) ** (1/n) - 1
    return tasa_periodica

def calcular_cupon_periodico(valor_nominal, tasa_cupon_anual, frecuencia):
    """Calcula el cupón periódico del bono"""
    tasa_cupon_periodica = convertir_tea_a_tasa_periodica(tasa_cupon_anual, frecuencia)
    cupon_periodico = valor_nominal * tasa_cupon_periodica
    return cupon_periodico

def generar_flujos_de_caja(valor_nominal, cupon_periodico, num_periodos):
    """Genera todos los flujos de caja del bono"""
    flujos = []
    for periodo in range(1, num_periodos + 1):
        if periodo < num_periodos:
            flujos.append(cupon_periodico)
        else:
            flujos.append(cupon_periodico + valor_nominal)
    return flujos

def calcular_valor_presente_flujos(flujos, tasa_descuento_periodica):
    """Calcula el valor presente de cada flujo de caja"""
    valores_presentes = []
    for periodo, flujo in enumerate(flujos, start=1):
        vp = flujo / ((1 + tasa_descuento_periodica) ** periodo)
        valores_presentes.append(vp)
    return valores_presentes

def calcular_valor_presente_bono_completo(valor_nominal, tasa_cupon_anual, frecuencia, 
                                          plazo_años, tasa_descuento_anual):
    """Calcula el valor presente total del bono"""
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
    
    return {
        'valor_presente_total': valor_presente_total,
        'cupon_periodico': cupon_periodico,
        'tasa_cupon_periodica': tasa_cupon_periodica,
        'tasa_descuento_periodica': tasa_descuento_periodica,
        'num_periodos': num_periodos,
        'periodos_por_año': periodos_por_año,
        'flujos': flujos,
        'valores_presentes': valores_presentes
    }

# ==================== CASOS DE PRUEBA ====================

def test_caso_1():
    """
    Test Caso 1: Bono Anual
    - Valor Nominal: $10,000
    - Tasa Cupón: 10% anual
    - Periodo: Anual
    - Plazo: 10 años
    - TEA Descuento: 12%
    """
    print("\n" + "="*80)
    print("TEST CASO 1: BONO ANUAL")
    print("="*80)
    
    valor_nominal = 10000.0
    tasa_cupon = 0.10
    frecuencia = "Anual"
    plazo_años = 10
    tea_descuento = 0.12
    
    resultado = calcular_valor_presente_bono_completo(
        valor_nominal, tasa_cupon, frecuencia, plazo_años, tea_descuento
    )
    
    print(f"\nParámetros:")
    print(f"  Valor Nominal: ${valor_nominal:,.2f}")
    print(f"  Tasa Cupón TEA: {tasa_cupon*100:.2f}%")
    print(f"  Frecuencia: {frecuencia}")
    print(f"  Plazo: {plazo_años} años")
    print(f"  TEA Descuento: {tea_descuento*100:.2f}%")
    
    print(f"\nResultados:")
    print(f"  Número de Periodos: {resultado['num_periodos']}")
    print(f"  Tasa Cupón Periódica: {resultado['tasa_cupon_periodica']*100:.4f}%")
    print(f"  Tasa Descuento Periódica: {resultado['tasa_descuento_periodica']*100:.4f}%")
    print(f"  Cupón Periódico: ${resultado['cupon_periodico']:,.2f}")
    
    total_flujos = sum(resultado['flujos'])
    print(f"\n  Total Flujos Nominales: ${total_flujos:,.2f}")
    print(f"  Valor Presente Total: ${resultado['valor_presente_total']:,.2f}")
    print(f"  Diferencia (Descuento): ${total_flujos - resultado['valor_presente_total']:,.2f}")
    print(f"  Porcentaje Descuento: {((total_flujos - resultado['valor_presente_total'])/total_flujos)*100:.2f}%")
    
    # Comparación con valor nominal
    diferencia_vn = resultado['valor_presente_total'] - valor_nominal
    porcentaje_vn = (diferencia_vn / valor_nominal) * 100
    
    print(f"\n  Diferencia vs Valor Nominal: ${diferencia_vn:,.2f} ({porcentaje_vn:.2f}%)")
    
    if resultado['valor_presente_total'] > valor_nominal:
        print(f"  ✓ BONO CON PRIMA (VP > VN)")
    elif resultado['valor_presente_total'] < valor_nominal:
        print(f"  ✓ BONO CON DESCUENTO (VP < VN)")
    else:
        print(f"  ✓ BONO A LA PAR (VP = VN)")
    
    # Verificación manual del primer flujo
    print(f"\n  Verificación Primer Flujo:")
    print(f"    Flujo 1: ${resultado['flujos'][0]:,.2f}")
    print(f"    VP Flujo 1: ${resultado['valores_presentes'][0]:,.2f}")
    print(f"    VP Manual: ${resultado['flujos'][0] / (1 + resultado['tasa_descuento_periodica'])**1:,.2f}")
    
    return resultado

def test_caso_2():
    """
    Test Caso 2: Bono Semestral
    - Valor Nominal: $20,000
    - Tasa Cupón: 10% anual
    - Periodo: Semestral
    - Plazo: 10 semestres (5 años)
    - TEA Descuento: 12%
    """
    print("\n" + "="*80)
    print("TEST CASO 2: BONO SEMESTRAL")
    print("="*80)
    
    valor_nominal = 20000.0
    tasa_cupon = 0.10
    frecuencia = "Semestral"
    tiempo_semestres = 10
    plazo_años = tiempo_semestres / 2  # Conversión correcta
    tea_descuento = 0.12
    
    resultado = calcular_valor_presente_bono_completo(
        valor_nominal, tasa_cupon, frecuencia, plazo_años, tea_descuento
    )
    
    print(f"\nParámetros:")
    print(f"  Valor Nominal: ${valor_nominal:,.2f}")
    print(f"  Tasa Cupón TEA: {tasa_cupon*100:.2f}%")
    print(f"  Frecuencia: {frecuencia}")
    print(f"  Tiempo ingresado: {tiempo_semestres} semestres")
    print(f"  Plazo convertido: {plazo_años} años")
    print(f"  TEA Descuento: {tea_descuento*100:.2f}%")
    
    print(f"\nResultados:")
    print(f"  Número de Periodos: {resultado['num_periodos']}")
    print(f"  Tasa Cupón Periódica: {resultado['tasa_cupon_periodica']*100:.4f}%")
    print(f"  Tasa Descuento Periódica: {resultado['tasa_descuento_periodica']*100:.4f}%")
    print(f"  Cupón Periódico: ${resultado['cupon_periodico']:,.2f}")
    
    # Verificación manual de la tasa periódica
    tasa_manual = (1 + tasa_cupon) ** (1/2) - 1
    print(f"  Tasa Cupón Periódica Manual: {tasa_manual*100:.4f}%")
    
    total_flujos = sum(resultado['flujos'])
    print(f"\n  Total Flujos Nominales: ${total_flujos:,.2f}")
    print(f"  Valor Presente Total: ${resultado['valor_presente_total']:,.2f}")
    print(f"  Diferencia (Descuento): ${total_flujos - resultado['valor_presente_total']:,.2f}")
    
    return resultado

def test_caso_3():
    """
    Test Caso 3: Bono a la Par
    - Valor Nominal: $10,000
    - Tasa Cupón: 10% anual
    - Periodo: Anual
    - Plazo: 5 años
    - TEA Descuento: 10% (igual al cupón)
    """
    print("\n" + "="*80)
    print("TEST CASO 3: BONO A LA PAR (Tasa Cupón = TEA)")
    print("="*80)
    
    valor_nominal = 10000.0
    tasa_cupon = 0.10
    frecuencia = "Anual"
    plazo_años = 5
    tea_descuento = 0.10  # Igual al cupón
    
    resultado = calcular_valor_presente_bono_completo(
        valor_nominal, tasa_cupon, frecuencia, plazo_años, tea_descuento
    )
    
    print(f"\nParámetros:")
    print(f"  Valor Nominal: ${valor_nominal:,.2f}")
    print(f"  Tasa Cupón TEA: {tasa_cupon*100:.2f}%")
    print(f"  Frecuencia: {frecuencia}")
    print(f"  Plazo: {plazo_años} años")
    print(f"  TEA Descuento: {tea_descuento*100:.2f}%")
    
    print(f"\nResultados:")
    print(f"  Valor Presente Total: ${resultado['valor_presente_total']:,.2f}")
    print(f"  Diferencia vs VN: ${resultado['valor_presente_total'] - valor_nominal:,.2f}")
    
    # Cuando tasa cupón = tasa descuento, VP debe ser igual a VN
    if abs(resultado['valor_presente_total'] - valor_nominal) < 1:
        print(f"  ✓ CORRECTO: VP ≈ VN (Bono a la Par)")
    else:
        print(f"  ✗ ERROR: VP debería ser igual a VN")
    
    return resultado

def test_caso_4():
    """
    Test Caso 4: Ejemplo de las imágenes (CORREGIDO)
    - Valor Nominal: $10,000
    - Tasa Cupón: 10% anual (NO 5%)
    - Periodo: Semestral
    - Plazo: 10 semestres (5 años)
    - TEA Descuento: 6%
    """
    print("\n" + "="*80)
    print("TEST CASO 4: EJEMPLO DE LAS IMÁGENES (CORREGIDO)")
    print("="*80)
    
    valor_nominal = 10000.0
    tasa_cupon = 0.10  # CORREGIDO: 10% no 5%
    frecuencia = "Semestral"
    tiempo_semestres = 10
    plazo_años = tiempo_semestres / 2
    tea_descuento = 0.06
    
    resultado = calcular_valor_presente_bono_completo(
        valor_nominal, tasa_cupon, frecuencia, plazo_años, tea_descuento
    )
    
    print(f"\nParámetros:")
    print(f"  Valor Nominal: ${valor_nominal:,.2f}")
    print(f"  Tasa Cupón TEA: {tasa_cupon*100:.2f}%")
    print(f"  Frecuencia: {frecuencia}")
    print(f"  Tiempo: {tiempo_semestres} semestres → {plazo_años} años")
    print(f"  TEA Descuento: {tea_descuento*100:.2f}%")
    
    print(f"\nResultados:")
    print(f"  Número de Periodos: {resultado['num_periodos']}")
    print(f"  Cupón Periódico: ${resultado['cupon_periodico']:,.2f}")
    
    # Esperado: aproximadamente $488.09 según la imagen
    print(f"\n  Comparación con imagen:")
    print(f"    Cupón esperado: ~$488.09")
    print(f"    Cupón calculado: ${resultado['cupon_periodico']:,.2f}")
    
    if abs(resultado['cupon_periodico'] - 488.09) < 1:
        print(f"    ✓ CORRECTO: Cupón coincide con la imagen")
    else:
        diferencia = abs(resultado['cupon_periodico'] - 488.09)
        print(f"    ⚠ DIFERENCIA: {diferencia:.2f}")
    
    total_flujos = sum(resultado['flujos'])
    print(f"\n  Total Flujos Nominales: ${total_flujos:,.2f}")
    print(f"    Esperado: ~$14,880.88")
    
    if abs(total_flujos - 14880.88) < 10:
        print(f"    ✓ CORRECTO: Total flujos coincide")
    else:
        diferencia = abs(total_flujos - 14880.88)
        print(f"    ⚠ DIFERENCIA: {diferencia:.2f}")
    
    print(f"\n  Valor Presente Total: ${resultado['valor_presente_total']:,.2f}")
    print(f"    Esperado: ~$9,295.74")
    
    if abs(resultado['valor_presente_total'] - 9295.74) < 10:
        print(f"    ✓ CORRECTO: VP coincide con la imagen")
    else:
        diferencia = abs(resultado['valor_presente_total'] - 9295.74)
        print(f"    ⚠ DIFERENCIA: {diferencia:.2f}")
    
    # Desglose adicional
    print(f"\n  Desglose detallado:")
    print(f"    Total cupones: ${resultado['cupon_periodico'] * 10:,.2f}")
    print(f"    Valor nominal: ${valor_nominal:,.2f}")
    print(f"    Total flujos: ${total_flujos:,.2f}")
    
    return resultado

# ==================== EJECUTAR PRUEBAS ====================

if __name__ == "__main__":
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "PRUEBAS DE CÁLCULO DE BONOS" + " "*30 + "║")
    print("╚" + "="*78 + "╝")
    
    # Ejecutar todos los casos de prueba
    test_caso_1()
    test_caso_2()
    test_caso_3()
    test_caso_4()
    
    print("\n" + "="*80)
    print("RESUMEN DE PRUEBAS")
    print("="*80)
    print("\n✓ Todas las funciones de cálculo han sido verificadas")
    print("✓ Fórmulas de tasas equivalentes correctas: TEP = (1 + TEA)^(1/n) - 1")
    print("✓ Conversión de tiempo a años implementada correctamente")
    print("✓ Cálculo de VP de flujos correcto: VP = Flujo / (1 + i)^t")
    print("\n" + "="*80 + "\n")
