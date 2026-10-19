# -*- coding: utf-8 -*-
"""
CAJERO AUTOMÁTICO WEB - Proyecto en Python con Flask
-----------------------------------------------------
Cómo ejecutarlo:
  1. Instalar Flask:        pip install flask
  2. Ejecutar el programa:  python app.py
  3. Abrir en el navegador: http://127.0.0.1:5000

Cuentas de prueba:
  Cuenta: 1001   PIN: 1234
  Cuenta: 1002   PIN: 4321
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "clave_secreta_del_cajero"  # necesaria para usar session y flash

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


# ---------------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------------
def formato_dinero(valor):
    """Convierte 1500000 en '$1.500.000'"""
    return "$" + f"{valor:,.0f}".replace(",", ".")


# Así podemos usar {{ saldo|dinero }} dentro de los HTML
app.add_template_filter(formato_dinero, "dinero")


def registrar_movimiento(cuenta, tipo, monto):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    cuenta["historial"].append({
        "fecha": fecha,
        "tipo": tipo,
        "monto": monto,
        "saldo": cuenta["saldo"],
    })


def obtener_cuenta():
    """Devuelve la cuenta de quien inició sesión (o None si nadie ha iniciado)"""
    numero = session.get("usuario")
    if numero in cuentas:
        return cuentas[numero]
    return None


# ---------------------------------------------------------------
# RUTA 1: INICIO DE SESIÓN
# ---------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        numero = request.form["cuenta"].strip()
        pin = request.form["pin"].strip()

        if numero not in cuentas:
            flash("El número de cuenta no existe.", "error")
            return redirect(url_for("login"))

        cuenta = cuentas[numero]

        if cuenta["bloqueada"]:
            flash("Esta cuenta está bloqueada por intentos fallidos. Comuníquese con el banco.", "error")
            return redirect(url_for("login"))

        if pin == cuenta["pin"]:
            cuenta["intentos"] = 0
            session["usuario"] = numero
            return redirect(url_for("menu"))

        # PIN incorrecto
        cuenta["intentos"] += 1
        restantes = 3 - cuenta["intentos"]
        if restantes <= 0:
            cuenta["bloqueada"] = True
            flash("Superó los 3 intentos. La cuenta fue bloqueada.", "error")
        else:
            flash("PIN incorrecto. Intentos restantes: " + str(restantes), "error")
        return redirect(url_for("login"))

    return render_template("login.html")


# ---------------------------------------------------------------
# RUTA 2: MENÚ PRINCIPAL
# ---------------------------------------------------------------
@app.route("/menu")
def menu():
    cuenta = obtener_cuenta()
    if cuenta is None:
        return redirect(url_for("login"))
    return render_template("menu.html", cuenta=cuenta)


# ---------------------------------------------------------------
# RUTA 3: CONSULTAR SALDO
# ---------------------------------------------------------------
@app.route("/saldo")
def saldo():
    cuenta = obtener_cuenta()
    if cuenta is None:
        return redirect(url_for("login"))
    return render_template("saldo.html", cuenta=cuenta, numero=session["usuario"])


# ---------------------------------------------------------------
# RUTA 4: DEPOSITAR / RETIRAR (misma ruta para los dos)
# ---------------------------------------------------------------
@app.route("/operacion/<tipo>", methods=["GET", "POST"])
def operacion(tipo):
    cuenta = obtener_cuenta()
    if cuenta is None:
        return redirect(url_for("login"))

    if tipo not in ["deposito", "retiro"]:
        return redirect(url_for("menu"))

    if request.method == "POST":
        texto = request.form["monto"].strip()

        if not texto.isdigit():
            flash("Ingrese solo números, sin puntos ni letras.", "error")
            return redirect(url_for("operacion", tipo=tipo))

        monto = int(texto)

        if monto <= 0:
            flash("El monto debe ser mayor que cero.", "error")
            return redirect(url_for("operacion", tipo=tipo))

        if tipo == "deposito":
            cuenta["saldo"] += monto
            registrar_movimiento(cuenta, "Depósito", monto)
            flash("Depósito exitoso de " + formato_dinero(monto), "exito")
            return redirect(url_for("menu"))

        # Si llegó aquí, es un retiro
        if monto % 10000 != 0:
            flash("El monto debe ser múltiplo de $10.000.", "error")
            return redirect(url_for("operacion", tipo=tipo))

        if monto > cuenta["saldo"]:
            flash("Saldo insuficiente.", "error")
            return redirect(url_for("operacion", tipo=tipo))

        cuenta["saldo"] -= monto
        registrar_movimiento(cuenta, "Retiro", monto)
        flash("Retiro exitoso. Recoja su dinero: " + formato_dinero(monto), "exito")
        return redirect(url_for("menu"))

    return render_template("operacion.html", cuenta=cuenta, tipo=tipo)


# ---------------------------------------------------------------
# RUTA 5: HISTORIAL
# ---------------------------------------------------------------
@app.route("/historial")
def historial():
    cuenta = obtener_cuenta()
    if cuenta is None:
        return redirect(url_for("login"))

    # Últimos 10 movimientos, el más reciente primero
    ultimos = cuenta["historial"][-10:]
    ultimos.reverse()
    return render_template("historial.html", movimientos=ultimos)


# ---------------------------------------------------------------
# RUTA 6: CAMBIAR PIN
# ---------------------------------------------------------------
@app.route("/cambiar-pin", methods=["GET", "POST"])
def cambiar_pin():
    cuenta = obtener_cuenta()
    if cuenta is None:
        return redirect(url_for("login"))

    if request.method == "POST":
        actual = request.form["actual"].strip()
        nuevo = request.form["nuevo"].strip()
        confirmar = request.form["confirmar"].strip()

        if actual != cuenta["pin"]:
            flash("El PIN actual es incorrecto.", "error")
        elif len(nuevo) != 4 or not nuevo.isdigit():
            flash("El PIN nuevo debe tener exactamente 4 números.", "error")
        elif nuevo != confirmar:
            flash("Los PIN nuevos no coinciden.", "error")
        else:
            cuenta["pin"] = nuevo
            flash("PIN cambiado correctamente.", "exito")
            return redirect(url_for("menu"))

        return redirect(url_for("cambiar_pin"))

    return render_template("cambiar_pin.html")


# ---------------------------------------------------------------
# RUTA 7: CERRAR SESIÓN
# ---------------------------------------------------------------
@app.route("/salir")
def salir():
    session.clear()
    flash("Sesión cerrada. ¡Hasta pronto!", "exito")
    return redirect(url_for("login"))


# ---------------------------------------------------------------
# INICIO DEL PROGRAMA
# ---------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
