"""
SISTEMA DE RESERVAS DE HOTEL 
Alcance: solo reservas en septiembre (30 días).
Anticipación mínima: 7 días.
Se valida restando directamente números de día (sin librerías).
"""

import random

def main():
    # parámetros hotel
    TIPOS = ["ESTANDAR", "PREMIUM", "KING"]     # columnas 0..2
    PISOS = [3, 2, 1]                           # alineado a TIPOS
    TARIFAS_BASE = [60000.0, 90000.0, 120000.0] # base por tipo
    COCHERA_VALOR = 10000.0
    HABITACIONES = 5
    TIPOS_CANT = 3
    DIAS_SEPTIEMBRE = 30
    hoy_dia = 3
    print("===== SISTEMA RESERVA HOTEL (SEPTIEMBRE 2025) =====")
    print("Hoy es 3 de septiembre de 2025 (día fijo = " + str(hoy_dia) + ")")

    Vendedor = HABITACIONES
    Sucursal = TIPOS_CANT
    ventaXHabitacion = [0] * Vendedor
    VTAxTIPO = [0] * Sucursal
    m = [[0] * Sucursal for _ in range(Vendedor)]

    # --- Carga ---
    hubo_venta = cargar_importes(m, TIPOS, PISOS, TARIFAS_BASE, COCHERA_VALOR, HABITACIONES, DIAS_SEPTIEMBRE, hoy_dia)
    if not hubo_venta:
        print("No se registraron reservas.")
        return

    # --- 1) Mostrar matriz ---
    mostrar_matriz(m)
    print("\n=== (1) Listado matriz ===")
    listado_puntoA(m, Vendedor, Sucursal)

    # --- 2) Total por habitación ---
    SumaMatrizxFila(m, ventaXHabitacion, Vendedor)
    print("\n=== (2) Total por habitación ===")
    i = 0
    while i < len(ventaXHabitacion):
        print("Habitación ".ljust(12) + str(i+1).rjust(2) + ": $" + str(int(ventaXHabitacion[i])).rjust(10))
        i += 1

    # --- 3) Total por tipo ---
    sumaMatrizXCOL(m, VTAxTIPO, Sucursal, Vendedor)
    print("\n=== (3) Total por tipo ===")
    print("Tipo".ljust(10) + "Total $".rjust(12))
    i = 0
    while i < len(VTAxTIPO):
        tipo_str = str(i+1).rjust(2) + " (" + TIPOS[i].ljust(8) + ")"
        total_str = "$" + str(int(VTAxTIPO[i])).rjust(10)
        print(tipo_str + "\t" + total_str)
        i += 1

    # --- 4) Tipo/s con mayor venta ---
    ventaMaxima = max(VTAxTIPO)
    print("\n=== (4) Tipo/s con mayor venta ===")
    print("Mayor venta: $" + str(int(ventaMaxima)).rjust(10))
    mejores_tipos = []
    i = 0
    while i < len(VTAxTIPO):
        if VTAxTIPO[i] == ventaMaxima:
            mejores_tipos.append(i+1)
        i += 1
    print("Tipo/s: " + str(mejores_tipos))

    # --- 4b) Tipo/s con menor venta ---
    ventaMinima = min(VTAxTIPO)
    print("\n=== (4b) Tipo/s con menor venta ===")
    print("Menor venta: $" + str(int(ventaMinima)).rjust(10))
    peores_tipos = []
    i = 0
    while i < len(VTAxTIPO):
        if VTAxTIPO[i] == ventaMinima:
            peores_tipos.append(i+1)
        i += 1
    print("Tipo/s: " + str(peores_tipos))

    # --- 5) Promedio por habitación por tipo ---
    print("\n=== (5) Promedio por habitación por tipo ===")
    print("Tipo".ljust(10) + "Promedio $".rjust(12))
    i = 0
    while i < len(VTAxTIPO):
        prom = VTAxTIPO[i] / HABITACIONES
        tipo_str = str(i+1).rjust(2) + " (" + TIPOS[i].ljust(8) + ")"
        total_str = "$" + str(int(prom)).rjust(10)
        print(tipo_str + "\t" + total_str)
        i += 1
        
    # --- 6) Habitaciones sin reservas por tipo ---
    print("\n=== (6) Habitaciones sin reservas por tipo ===")
    for i in range(Sucursal):   # recorre los tipos de habitación
        print(TIPOS[i] + ":")
        sin_reserva = False

        for j in range(Vendedor):   # recorre las habitaciones de ese tipo
            if m[j][i] == 0:        # si no hay reserva en esa posición
                print("  Habitación " + str(j+1))
                sin_reserva = True

        if not sin_reserva:         # si todas tenían reservas
            print("  Todas las habitaciones reservadas")


    # --- 7) Venta total ---
    total_periodo = sumarMatriz(m, Vendedor)
    print("\n=== (7) Venta total del período ===")
    print("Total: $" + str(int(total_periodo)).rjust(10))

    # --- 8) Porcentaje de habitaciones no reservadas ---
    porc, libres, total = porcentaje_no_reservadas(m, Vendedor, Sucursal)
    print("\n=== (8) Porcentaje de habitaciones no reservadas ===")
    print(f"Libres: {libres} de {total} ({porc:.2f}%)")

    # --- 9) Número total de reservas ---
    total_reservas = 0
    for i in range(Vendedor):
        for j in range(Sucursal):
            if m[i][j] > 0:
                total_reservas += 1
    print(f"\nNúmero total de reservas realizadas: {total_reservas}")

def cargar_importes(matriz, TIPOS, PISOS, TARIFAS_BASE, COCHERA_VALOR, HABITACIONES, DIAS_SEPTIEMBRE, hoy_dia):
    """
    Carga reservas en la matriz:
    - Pide tipo (1..3), o -99 para salir.
    - Verifica disponibilidad (máx 5 por tipo).
    - Calcula total (base + cochera) multiplicado por cantidad de días.
    - Asigna en la primera habitación libre.
    """
    hubo_venta = False
    print("\n(Para finalizar, ingrese tipo = -99)")
    tipo = int(input("Tipo de habitación (1=Estandar, 2=Premium, 3=King): "))

    while tipo != -99:
        while tipo < 1 or tipo > 3:
            print("Error: tipo válido 1..3")
            tipo = int(input("Tipo de habitación (1=Estandar, 2=Premium, 3=King): "))

        # --- Día de reserva ---
        dia_reserva = int(input("Ingrese el día de septiembre para la reserva (1-30): "))
        if dia_reserva < 1 or dia_reserva > DIAS_SEPTIEMBRE:
            print("❌ Día inválido. Debe estar entre 1 y 30.")
        else:
            dif = dia_reserva - hoy_dia
            if dif < 0:
                print("❌ Esa fecha ya pasó.")
            elif dif < 7:
                print("❌ Anticipación insuficiente (" + str(dif) + " días). Se requieren 7 o más.")
            else:
                # Preguntar por cantidad de días
                dias_estadia = int(input("¿Cuántos días desea reservar? "))
                if dia_reserva + dias_estadia - 1 > DIAS_SEPTIEMBRE:
                    print("❌ La estadía se pasa de septiembre. Máximo permitido: " + str(DIAS_SEPTIEMBRE - dia_reserva + 1) + " días")
                else:
                    col = tipo - 1  #-1 para asi ir en 0,1,2 y no en 1,2,3
                    # mostrar habitaciones libres
                    print("Habitaciones disponibles: ")
                    hab_disponibles = []
                    for i in range(HABITACIONES):
                        if matriz[i][col] == 0:
                            hab_disponibles.append(i)
                            print("  Habitación " + str(i+1))


                    # elegir habitación
                    eleccion = input("Ingrese número de habitación o 'A' para aleatoria: ").strip().upper()
                    if eleccion == 'A':
                        fila_libre = random.randint(0, len(hab_disponibles)-1)
                        fila_libre = hab_disponibles[fila_libre]
                    else:
                        fila_libre = int(eleccion) - 1
                        if fila_libre not in hab_disponibles:
                            print("⚠️ Habitación no disponible, se asignará aleatoria")
                            fila_libre = random.randint(0, len(hab_disponibles)-1)
                            fila_libre = hab_disponibles[fila_libre]

                    coch = input("¿Cochera? (SI/NO): ").strip().upper()
                    coch_flag = 1 if coch == "SI" else 0
                    base = TARIFAS_BASE[col]
                    cochera_costo = COCHERA_VALOR if coch_flag == 1 else 0
                    total = (base + cochera_costo) * dias_estadia
                    matriz[fila_libre][col] = total
                    hubo_venta = True
                    print("ℹ️ Por el momento no contamos con cargos extras.")
                    print("Reserva realizada con exito!✅ A continuacion le dejamos los datos de su reserva= " + TIPOS[col] + " (Piso " + str(PISOS[col]) + ") | Hab " + str(fila_libre+1) + " | Día " + str(dia_reserva) + " por " + str(dias_estadia) + " días | Total $" + str(int(total)))

        tipo = int(input("\nTipo (1..3) o -99 para terminar: "))

    return hubo_venta


def mostrar_matriz(matriz):
    print("\nMatriz (filas=Hab 1..5, cols=Tipos 1..3):")
    for i in range(len(matriz)):  
        print(f"Vendedor {i+1}: {matriz[i]}")


def SumaMatrizxFila(matriz, lista, cantidadFilas):
    for i in range(cantidadFilas):
        lista[i]=sum(matriz[i])


def sumarMatriz(matriz, cantidadFilas):
    resultado = 0.0
    f = 0
    while f < cantidadFilas:
        resultado += sum(matriz[f])
        f += 1
    return resultado


def listado_puntoA(matriz, cantidadfilas, cantidadcolumnas):
    print("\nHABITACION/TIPO \t 01\t\t 02\t\t 03")

    for i in range(cantidadfilas):  # recorre las filas (habitaciones)
        print(str(i+1).rjust(2), end="\t\t   ")

        for j in range(cantidadcolumnas):  # recorre las columnas (tipos)
            print("$" + str(int(matriz[i][j])).rjust(10), end="\t")

        print()  # salto de línea al terminar cada fila



def sumaMatrizXCOL(matriz, lista, cantidadcolumnas, cantidadfilas):
    for i in range(cantidadcolumnas):
        for j in range(cantidadfilas):
            lista[i]+=matriz[j][i]

def porcentaje_no_reservadas(matriz, cantidadFilas, cantidadColumnas):
    total = cantidadFilas * cantidadColumnas
    libres = 0

    for i in range(cantidadFilas):
        for j in range(cantidadColumnas):
            if matriz[i][j] == 0:
                libres += 1

    porcentaje = (libres / total) * 100
    return porcentaje, libres, total



# Ejecutar
main()










