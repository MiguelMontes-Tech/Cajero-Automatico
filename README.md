# Cajero Automático Web

Proyecto de un cajero automático hecho con **Python** y **Flask**.

## Funciones
- Inicio de sesión con número de cuenta y PIN (se bloquea tras 3 intentos fallidos)
- Consultar saldo
- Depositar dinero
- Retirar dinero (solo múltiplos de $10.000)
- Historial de los últimos 10 movimientos
- Cambiar PIN
- Cerrar sesión

## Cómo ejecutarlo
1. Instalar Flask:
   ```
   pip install flask
   ```
2. Ejecutar el programa:
   ```
   python app.py
   ```
3. Abrir en el navegador: http://127.0.0.1:5000

## Cuentas de prueba
| Cuenta | PIN  |
|--------|------|
| 1001   | 1234 |
| 1002   | 4321 |

## Estructura del proyecto
```
cajero_web/
├── app.py              # Lógica del programa (Python / Flask)
├── requirements.txt    # Dependencias
├── templates/          # Páginas HTML
└── static/
    └── estilos.css     # Diseño de la página
```

> Los datos se guardan en memoria: al reiniciar el programa, los saldos y PIN vuelven a sus valores iniciales.
