"""
Script para calcular VP del bono EXACTAMENTE como lo describe bonos_page.py
Separando VP de cupones y VP del valor nominal
"""

def calcular_vp_bono_formula_exacta(valor_nominal, tasa_cupon_anual, frecuencia_anual, 
                                     plazo_años, tea_descuento):
    """
    Implementación EXACTA de la fórmula de bonos_page.py
    
    VP_total = VP_cupones + VP_nominal
    
    Donde:
    - VP_cupones = Σ(C / (1+i)^t) para t=1 hasta n
    - VP_nominal = VN / (1+i)^n
    - C = Cupón periódico = VN × tasa_cupón_periodo
    - i = Tasa de descuento por periodo
    """
    
    # Calcular número de periodos
    n = int(plazo_años * frecuencia_anual)
    
    # Convertir TEA a tasa periódica usando: tasa_periodo = (1 + TEA)^(1/f) - 1
    tasa_cupon_periodo = (1 + tasa_cupon_anual) ** (1/frecuencia_anual) - 1
    tasa_descuento_periodo = (1 + tea_descuento) ** (1/frecuencia_anual) - 1
    
    # Calcular cupón periódico: C = VN × tasa_cupón_periodo
    cupon_periodico = valor_nominal * tasa_cupon_periodo
    
    print(f"\n{'='*80}")
    print(f"PARÁMETROS:")
    print(f"{'='*80}")
    print(f"  Valor Nominal (VN): ${valor_nominal:,.2f}")
    print(f"  Tasa Cupón TEA: {tasa_cupon_anual*100:.2f}%")
    print(f"  Frecuencia anual (f): {frecuencia_anual} pagos/año")
    print(f"  Plazo: {plazo_años} años")
    print(f"  Número de periodos (n): {n}")
    print(f"  TEA Descuento: {tea_descuento*100:.2f}%")
    
    print(f"\n{'='*80}")
    print(f"TASAS PERIÓDICAS:")
    print(f"{'='*80}")
    print(f"  Tasa Cupón Periodo: {tasa_cupon_periodo*100:.4f}%")
    print(f"  Tasa Descuento Periodo (i): {tasa_descuento_periodo*100:.4f}%")
    print(f"  Cupón Periódico (C): ${cupon_periodico:,.2f}")
    
    # Calcular VP de cupones: Σ(C / (1+i)^t) para t=1 hasta n
    vp_cupones_total = 0
    print(f"\n{'='*80}")
    print(f"VP DE CUPONES (primeros 5 y último):")
    print(f"{'='*80}")
    
    for t in range(1, n + 1):
        vp_cupon_t = cupon_periodico / ((1 + tasa_descuento_periodo) ** t)
        vp_cupones_total += vp_cupon_t
        
        if t <= 5 or t == n:
            print(f"  Periodo {t}: C/(1+i)^{t} = {cupon_periodico:,.2f} / (1+{tasa_descuento_periodo:.6f})^{t} = ${vp_cupon_t:,.2f}")
    
    print(f"\n  VP Total de Cupones: ${vp_cupones_total:,.2f}")
    
    # Calcular VP del valor nominal: VN / (1+i)^n
    vp_nominal = valor_nominal / ((1 + tasa_descuento_periodo) ** n)
    
    print(f"\n{'='*80}")
    print(f"VP DEL VALOR NOMINAL:")
    print(f"{'='*80}")
    print(f"  VP_nominal = VN / (1+i)^n")
    print(f"  VP_nominal = {valor_nominal:,.2f} / (1+{tasa_descuento_periodo:.6f})^{n}")
    print(f"  VP_nominal = ${vp_nominal:,.2f}")
    
    # VP TOTAL
    vp_total = vp_cupones_total + vp_nominal
    
    print(f"\n{'='*80}")
    print(f"VALOR PRESENTE TOTAL DEL BONO:")
    print(f"{'='*80}")
    print(f"  VP_total = VP_cupones + VP_nominal")
    print(f"  VP_total = ${vp_cupones_total:,.2f} + ${vp_nominal:,.2f}")
    print(f"  VP_total = ${vp_total:,.2f}")
    
    # Totales de flujos
    total_flujos_nominales = (cupon_periodico * n) + valor_nominal
    descuento_temporal = total_flujos_nominales - vp_total
    
    print(f"\n{'='*80}")
    print(f"RESUMEN:")
    print(f"{'='*80}")
    print(f"  Total Flujos Nominales: ${total_flujos_nominales:,.2f}")
    print(f"  Valor Presente Total: ${vp_total:,.2f}")
    print(f"  Descuento Temporal: ${descuento_temporal:,.2f} ({descuento_temporal/total_flujos_nominales*100:.2f}%)")
    
    # Clasificación
    diferencia_vn = vp_total - valor_nominal
    if vp_total > valor_nominal:
        clasificacion = "BONO CON PRIMA (VP > VN)"
    elif vp_total < valor_nominal:
        clasificacion = "BONO CON DESCUENTO (VP < VN)"
    else:
        clasificacion = "BONO A LA PAR (VP = VN)"
    
    print(f"\n  Diferencia vs Valor Nominal: ${diferencia_vn:,.2f} ({diferencia_vn/valor_nominal*100:.2f}%)")
    print(f"  Clasificación: {clasificacion}")
    print(f"{'='*80}\n")
    
    return {
        'vp_total': vp_total,
        'vp_cupones': vp_cupones_total,
        'vp_nominal': vp_nominal,
        'cupon_periodico': cupon_periodico,
        'total_flujos': total_flujos_nominales
    }


# ==================== CASO DE LA IMAGEN ====================

print("\n" + "█"*80)
print("█" + " "*26 + "CASO DE LA IMAGEN DEL USUARIO" + " "*24 + "█")
print("█"*80 + "\n")

# Según la imagen mostrada:
# - Valor Nominal: $10,000
# - Cupón Periódico: $488.09
# - Número de Pagos: 10
# - Total en Cupones: $4,880.88
# - Valor Presente del Bono: $9,295.74

print("DATOS DE LA IMAGEN:")
print("  Cupón Periódico mostrado: $488.09")
print("  Número de pagos: 10")
print("  Total en cupones: $4,880.88")
print("  Valor Presente mostrado: $9,295.74")

print("\n" + "▼"*80)
print("INTENTANDO CON DIFERENTES TEAs DE DESCUENTO:")
print("▼"*80)

# Caso 1: Con TEA 6% (como aparece en algunas interfaces)
print("\n" + "─"*80)
print("PRUEBA 1: TEA Descuento = 6%")
print("─"*80)
resultado_6 = calcular_vp_bono_formula_exacta(
    valor_nominal=10000.0,
    tasa_cupon_anual=0.10,
    frecuencia_anual=2,  # Semestral
    plazo_años=5.0,
    tea_descuento=0.06
)

if abs(resultado_6['vp_total'] - 9295.74) < 1:
    print("✅ COINCIDE CON LA IMAGEN!")
else:
    print(f"⚠️  NO COINCIDE. Diferencia: ${abs(resultado_6['vp_total'] - 9295.74):.2f}")

# Caso 2: Con TEA 12%
print("\n" + "─"*80)
print("PRUEBA 2: TEA Descuento = 12%")
print("─"*80)
resultado_12 = calcular_vp_bono_formula_exacta(
    valor_nominal=10000.0,
    tasa_cupon_anual=0.10,
    frecuencia_anual=2,  # Semestral
    plazo_años=5.0,
    tea_descuento=0.12
)

if abs(resultado_12['vp_total'] - 9295.74) < 1:
    print("✅ COINCIDE CON LA IMAGEN!")
else:
    print(f"⚠️  NO COINCIDE. Diferencia: ${abs(resultado_12['vp_total'] - 9295.74):.2f}")

# Buscar la TEA correcta
print("\n" + "─"*80)
print("BÚSQUEDA PRECISA DE LA TEA:")
print("─"*80)

mejor_tea = None
menor_diferencia = float('inf')

for tea_test in [i/100 for i in range(1, 20)]:  # 1% a 19%
    resultado = calcular_vp_bono_formula_exacta(
        valor_nominal=10000.0,
        tasa_cupon_anual=0.10,
        frecuencia_anual=2,
        plazo_años=5.0,
        tea_descuento=tea_test
    )
    
    diferencia = abs(resultado['vp_total'] - 9295.74)
    
    if diferencia < menor_diferencia:
        menor_diferencia = diferencia
        mejor_tea = tea_test
    
    if diferencia < 1:
        print(f"\n✅ ¡ENCONTRADA! TEA = {tea_test*100:.2f}% produce VP = ${resultado['vp_total']:,.2f}")
        break

print("\n" + "█"*80)
print("█" + " "*32 + "CONCLUSIÓN FINAL" + " "*32 + "█")
print("█"*80)
print(f"\nLa TEA de descuento que produce VP = $9,295.74 es: {mejor_tea*100:.2f}%")
print(f"Con esta TEA, la diferencia es: ${menor_diferencia:.2f}")
print("\n" + "█"*80 + "\n")
