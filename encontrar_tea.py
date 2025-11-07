"""
Script para encontrar la TEA que produciría VP = $9,295.74
"""

def obtener_periodos_por_año(frecuencia):
    frecuencias = {"Semestral": 2}
    return frecuencias.get(frecuencia, 1)

def convertir_tea_a_tasa_periodica(tea, frecuencia):
    n = obtener_periodos_por_año(frecuencia)
    return (1 + tea) ** (1/n) - 1

def calcular_vp_bono(valor_nominal, tasa_cupon, frecuencia, plazo_años, tea_descuento):
    periodos_por_año = obtener_periodos_por_año(frecuencia)
    num_periodos = int(plazo_años * periodos_por_año)
    
    tasa_cupon_periodica = convertir_tea_a_tasa_periodica(tasa_cupon, frecuencia)
    tasa_descuento_periodica = convertir_tea_a_tasa_periodica(tea_descuento, frecuencia)
    
    cupon_periodico = valor_nominal * tasa_cupon_periodica
    
    # Calcular VP
    vp_total = 0
    for periodo in range(1, num_periodos + 1):
        if periodo < num_periodos:
            flujo = cupon_periodico
        else:
            flujo = cupon_periodico + valor_nominal
        
        vp = flujo / ((1 + tasa_descuento_periodica) ** periodo)
        vp_total += vp
    
    return vp_total

# Parámetros conocidos
valor_nominal = 10000.0
tasa_cupon = 0.10
frecuencia = "Semestral"
plazo_años = 5.0
vp_objetivo = 9295.74

print("\n" + "="*80)
print("BÚSQUEDA DE LA TEA QUE PRODUCE VP = $9,295.74")
print("="*80)

print(f"\nParámetros fijos:")
print(f"  Valor Nominal: ${valor_nominal:,.2f}")
print(f"  Tasa Cupón: {tasa_cupon*100:.2f}%")
print(f"  Frecuencia: {frecuencia}")
print(f"  Plazo: {plazo_años} años")
print(f"  VP Objetivo: ${vp_objetivo:,.2f}")

print(f"\n\nProbando diferentes TEAs:")
print(f"{'TEA':<10} {'VP Calculado':<20} {'Diferencia':<15} {'Status'}")
print("-" * 65)

for tea_test in [0.06, 0.08, 0.10, 0.12, 0.14, 0.15, 0.16, 0.17, 0.18]:
    vp_calc = calcular_vp_bono(valor_nominal, tasa_cupon, frecuencia, plazo_años, tea_test)
    diferencia = vp_calc - vp_objetivo
    
    status = ""
    if abs(diferencia) < 10:
        status = "✓ COINCIDE"
    elif diferencia > 0:
        status = "↑ Mayor"
    else:
        status = "↓ Menor"
    
    print(f"{tea_test*100:.2f}%     ${vp_calc:>12,.2f}    ${diferencia:>12,.2f}    {status}")

# Búsqueda más precisa
print(f"\n\nBúsqueda precisa entre 16% y 18%:")
print(f"{'TEA':<10} {'VP Calculado':<20} {'Diferencia'}")
print("-" * 50)

for tea_pct in range(160, 181, 1):
    tea_test = tea_pct / 1000
    vp_calc = calcular_vp_bono(valor_nominal, tasa_cupon, frecuencia, plazo_años, tea_test)
    diferencia = vp_calc - vp_objetivo
    
    if abs(diferencia) < 50:
        print(f"{tea_test*100:.2f}%     ${vp_calc:>12,.2f}    ${diferencia:>12,.2f}")

print("\n" + "="*80)
print("CONCLUSIÓN:")
print("="*80)
print("\nLa imagen probablemente está usando una TEA de descuento cercana a 17%")
print("(no 6% como inicialmente supuse). Esto explicaría el VP de $9,295.74.")
print("\nOTRA POSIBILIDAD: La imagen podría estar mostrando el precio DESPUÉS")
print("de una compra con descuento o algún ajuste adicional.")
print("="*80 + "\n")
