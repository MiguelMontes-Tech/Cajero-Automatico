# -*- coding: utf-8 -*-
"""
CAJERO AUTOMÁTICO - Proyecto en Python con tkinter
---------------------------------------------------
Funciones:
  - Inicio de sesión con número de cuenta y PIN (3 intentos, luego se bloquea)
  - Consultar saldo
  - Depositar dinero
  - Retirar dinero (solo múltiplos de $10.000)
  - Ver historial de movimientos
  - Cambiar PIN
  - Cerrar sesión

Cuentas de prueba:
  Cuenta: 1001   PIN: 1234
  Cuenta: 1002   PIN: 4321

Para ejecutar:  python cajero_automatico.py
(tkinter ya viene instalado con Python, no hay que instalar nada)
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# ---------------------------------------------------------------
# DATOS DEL SISTEMA (base de datos sencilla usando un diccionario)
# ---------------------------------------------------------------
cuentas = {
    "1001": {
        "nombre": "Cliente Uno",
        "pin": "1234",
        "saldo": 500000,
        "historial": [],
        "intentos": 0,
        "bloqueada": False,
    },
    "1002": {
        "nombre": "Cliente Dos",
        "pin": "4321",
        "saldo": 1200000,
        "historial": [],
        "intentos": 0,
        "bloqueada": False,
    },
}

usuario_actual = None  # guarda el número de cuenta que inició sesión

# ---------------------------------------------------------------
# COLORES Y FUENTES
# ---------------------------------------------------------------
COLOR_FONDO = "#0b3d91"
COLOR_PANEL = "#ffffff"
COLOR_BOTON = "#1565c0"
COLOR_BOTON_VERDE = "#2e7d32"
COLOR_BOTON_ROJO = "#c62828"
FUENTE_TITULO = ("Arial", 20, "bold")
FUENTE_NORMAL = ("Arial", 12)
FUENTE_BOTON = ("Arial", 12, "bold")

# ---------------------------------------------------------------
# VENTANA PRINCIPAL
# ---------------------------------------------------------------
ventana = tk.Tk()
ventana.title("Cajero Automático")
ventana.geometry("480x600")
ventana.resizable(False, False)
ventana.configure(bg=COLOR_FONDO)

# Contenedor donde se dibuja cada pantalla
contenedor = tk.Frame(ventana, bg=COLOR_PANEL)
contenedor.pack(fill="both", expand=True, padx=20, pady=20)


# ---------------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------------
def formato_dinero(valor):
    """Convierte 1500000 en '$1.500.000'"""
    return "$" + f"{valor:,.0f}".replace(",", ".")


def limpiar_pantalla():
    """Borra todo lo que hay en el contenedor para dibujar otra pantalla"""
    for elemento in contenedor.winfo_children():
        elemento.destroy()


def crear_titulo(texto):
    etiqueta = tk.Label(contenedor, text=texto, font=FUENTE_TITULO,
                        bg=COLOR_PANEL, fg=COLOR_FONDO)
    etiqueta.pack(pady=(25, 15))


def crear_texto(texto):
    etiqueta = tk.Label(contenedor, text=texto, font=FUENTE_NORMAL,
                        bg=COLOR_PANEL, fg="#333333")
    etiqueta.pack(pady=4)
    return etiqueta


def crear_boton(texto, comando, color=COLOR_BOTON):
    boton = tk.Button(contenedor, text=texto, command=comando,
                      font=FUENTE_BOTON, bg=color, fg="white",
                      activebackground="#0d47a1", activeforeground="white",
                      width=26, pady=6, relief="flat", cursor="hand2")
    boton.pack(pady=6)
    return boton


def registrar_movimiento(tipo, monto):
    """Guarda un movimiento en el historial de la cuenta actual"""
    cuenta = cuentas[usuario_actual]
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    cuenta["historial"].append((fecha, tipo, monto, cuenta["saldo"]))


# ---------------------------------------------------------------
# PANTALLA 1: INICIO DE SESIÓN
# ---------------------------------------------------------------
def pantalla_login():
    global usuario_actual
    usuario_actual = None
    limpiar_pantalla()

    crear_titulo("BIENVENIDO")
    crear_texto("Ingrese sus datos para continuar")

    crear_texto("Número de cuenta:")
    entrada_cuenta = tk.Entry(contenedor, font=FUENTE_NORMAL, justify="center", width=20)
    entrada_cuenta.pack(pady=4)

    crear_texto("PIN (4 dígitos):")
    entrada_pin = tk.Entry(contenedor, font=FUENTE_NORMAL, justify="center",
                           width=20, show="*")
    entrada_pin.pack(pady=4)

    def intentar_ingreso(evento=None):
        iniciar_sesion(entrada_cuenta.get().strip(), entrada_pin.get().strip())

    crear_boton("INGRESAR", intentar_ingreso, COLOR_BOTON_VERDE)
    entrada_pin.bind("<Return>", intentar_ingreso)  # tecla Enter
    entrada_cuenta.focus()


def iniciar_sesion(numero, pin):
    global usuario_actual

    if numero not in cuentas:
        messagebox.showerror("Error", "El número de cuenta no existe.")
        return

    cuenta = cuentas[numero]

    if cuenta["bloqueada"]:
        messagebox.showerror("Cuenta bloqueada",
                             "Esta cuenta está bloqueada por intentos fallidos.\n"
                             "Comuníquese con el banco.")
        return

    if pin == cuenta["pin"]:
        cuenta["intentos"] = 0
        usuario_actual = numero
        pantalla_menu()
    else:
        cuenta["intentos"] += 1
        restantes = 3 - cuenta["intentos"]
        if restantes <= 0:
            cuenta["bloqueada"] = True
            messagebox.showerror("Cuenta bloqueada",
                                 "Superó los 3 intentos. La cuenta fue bloqueada.")
        else:
            messagebox.showerror("PIN incorrecto",
                                 "PIN incorrecto. Intentos restantes: " + str(restantes))


# ---------------------------------------------------------------
# PANTALLA 2: MENÚ PRINCIPAL
# ---------------------------------------------------------------
def pantalla_menu():
    limpiar_pantalla()
    cuenta = cuentas[usuario_actual]

    crear_titulo("MENÚ PRINCIPAL")
    crear_texto("Hola, " + cuenta["nombre"])

    crear_boton("Consultar saldo", pantalla_saldo)
    crear_boton("Depositar dinero", lambda: pantalla_operacion("deposito"))
    crear_boton("Retirar dinero", lambda: pantalla_operacion("retiro"))
    crear_boton("Historial de movimientos", pantalla_historial)
    crear_boton("Cambiar PIN", pantalla_cambiar_pin)
    crear_boton("Cerrar sesión", pantalla_login, COLOR_BOTON_ROJO)


# ---------------------------------------------------------------
# PANTALLA 3: CONSULTAR SALDO
# ---------------------------------------------------------------
def pantalla_saldo():
    limpiar_pantalla()
    cuenta = cuentas[usuario_actual]

    crear_titulo("SALDO DISPONIBLE")
    crear_texto("Cuenta: " + usuario_actual)

    etiqueta_saldo = tk.Label(contenedor, text=formato_dinero(cuenta["saldo"]),
                              font=("Arial", 30, "bold"), bg=COLOR_PANEL,
                              fg=COLOR_BOTON_VERDE)
    etiqueta_saldo.pack(pady=40)

    crear_boton("Volver al menú", pantalla_menu)


# ---------------------------------------------------------------
# PANTALLA 4: DEPOSITAR / RETIRAR (misma pantalla para los dos)
# ---------------------------------------------------------------
def pantalla_operacion(tipo):
    limpiar_pantalla()

    if tipo == "deposito":
        crear_titulo("DEPOSITAR")
    else:
        crear_titulo("RETIRAR")
        crear_texto("Solo múltiplos de $10.000")

    crear_texto("Saldo actual: " + formato_dinero(cuentas[usuario_actual]["saldo"]))
    crear_texto("Digite el monto:")

    entrada_monto = tk.Entry(contenedor, font=("Arial", 16), justify="center", width=15)
    entrada_monto.pack(pady=8)
    entrada_monto.focus()

    # Botones rápidos con montos comunes
    marco_rapido = tk.Frame(contenedor, bg=COLOR_PANEL)
    marco_rapido.pack(pady=6)

    def poner_monto(valor):
        entrada_monto.delete(0, "end")
        entrada_monto.insert(0, str(valor))

    for valor in [20000, 50000, 100000, 200000]:
        boton_rapido = tk.Button(marco_rapido, text=formato_dinero(valor),
                                 command=lambda v=valor: poner_monto(v),
                                 font=("Arial", 10), bg="#e3f2fd", relief="flat",
                                 cursor="hand2")
        boton_rapido.pack(side="left", padx=3)

    def confirmar():
        texto = entrada_monto.get().strip()

        if not texto.isdigit():
            messagebox.showerror("Error", "Ingrese solo números, sin puntos ni letras.")
            return

        monto = int(texto)
        if monto <= 0:
            messagebox.showerror("Error", "El monto debe ser mayor que cero.")
            return

        cuenta = cuentas[usuario_actual]

        if tipo == "deposito":
            cuenta["saldo"] += monto
            registrar_movimiento("Depósito", monto)
            messagebox.showinfo("Listo", "Depósito exitoso de " + formato_dinero(monto))
        else:
            if monto % 10000 != 0:
                messagebox.showerror("Error", "El monto debe ser múltiplo de $10.000.")
                return
            if monto > cuenta["saldo"]:
                messagebox.showerror("Error", "Saldo insuficiente.")
                return
            cuenta["saldo"] -= monto
            registrar_movimiento("Retiro", monto)
            messagebox.showinfo("Listo", "Retire su dinero: " + formato_dinero(monto))

        pantalla_menu()

    crear_boton("CONFIRMAR", confirmar, COLOR_BOTON_VERDE)
    crear_boton("Cancelar", pantalla_menu, COLOR_BOTON_ROJO)


# ---------------------------------------------------------------
# PANTALLA 5: HISTORIAL
# ---------------------------------------------------------------
def pantalla_historial():
    limpiar_pantalla()
    cuenta = cuentas[usuario_actual]

    crear_titulo("HISTORIAL")
    crear_texto("Últimos 10 movimientos")

    lista = tk.Listbox(contenedor, font=("Courier", 10), width=52, height=12)
    lista.pack(pady=10)

    if len(cuenta["historial"]) == 0:
        lista.insert("end", "No hay movimientos todavía.")
    else:
        ultimos = cuenta["historial"][-10:]
        for movimiento in reversed(ultimos):
            fecha, tipo, monto, saldo = movimiento
            linea = fecha + " " + tipo.ljust(9) + formato_dinero(monto)
            lista.insert("end", linea)

    crear_boton("Volver al menú", pantalla_menu)


# ---------------------------------------------------------------
# PANTALLA 6: CAMBIAR PIN
# ---------------------------------------------------------------
def pantalla_cambiar_pin():
    limpiar_pantalla()
    crear_titulo("CAMBIAR PIN")

    crear_texto("PIN actual:")
    entrada_actual = tk.Entry(contenedor, font=FUENTE_NORMAL, justify="center", show="*")
    entrada_actual.pack(pady=3)

    crear_texto("PIN nuevo (4 dígitos):")
    entrada_nuevo = tk.Entry(contenedor, font=FUENTE_NORMAL, justify="center", show="*")
    entrada_nuevo.pack(pady=3)

    crear_texto("Confirmar PIN nuevo:")
    entrada_confirmar = tk.Entry(contenedor, font=FUENTE_NORMAL, justify="center", show="*")
    entrada_confirmar.pack(pady=3)

    def guardar_pin():
        cuenta = cuentas[usuario_actual]
        actual = entrada_actual.get().strip()
        nuevo = entrada_nuevo.get().strip()
        confirmar = entrada_confirmar.get().strip()

        if actual != cuenta["pin"]:
            messagebox.showerror("Error", "El PIN actual es incorrecto.")
        elif len(nuevo) != 4 or not nuevo.isdigit():
            messagebox.showerror("Error", "El PIN nuevo debe tener exactamente 4 números.")
        elif nuevo != confirmar:
            messagebox.showerror("Error", "Los PIN nuevos no coinciden.")
        else:
            cuenta["pin"] = nuevo
            messagebox.showinfo("Listo", "PIN cambiado correctamente.")
            pantalla_menu()

    crear_boton("GUARDAR", guardar_pin, COLOR_BOTON_VERDE)
    crear_boton("Cancelar", pantalla_menu, COLOR_BOTON_ROJO)


# ---------------------------------------------------------------
# INICIO DEL PROGRAMA
# ---------------------------------------------------------------
pantalla_login()
ventana.mainloop()
