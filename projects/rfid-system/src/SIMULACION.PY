# app_single_file.py
import sys
import time
import random
import string
from datetime import datetime
from typing import Optional, List, Tuple

from dotenv import load_dotenv
import os

# lee archivo .env y carga variables en os.environ
load_dotenv(override=True,dotenv_path=r"C:\Users\wilso\Desktop\x\x\matplotlib_vscode\SIMULACION PROTEUS\Variables.env")

# Instalaciones: pip install pyqt6 mysql-connector-python pyserial python-dotenv twilio
# (si no usas .env, define las variables directamente abajo antes de usar Twilio)

try:
    import serial
except Exception:
    serial = None  # si no hay pyserial instalado, el hilo detectará y generará error

import mysql.connector
from mysql.connector import Error
from twilio.rest import Client

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QListWidget,
    QPushButton, QHBoxLayout, QMessageBox, QFrame, QLineEdit,
    QDialog, QFormLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

# ---------------------------
# CONFIG: ajusta estas variables
# ---------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root", 
    "password": "WILSONTARRIFA1900",
    "database": "reservas",
    "port": 3306,
}

DB_CONFIG1 = {
    "host": "localhost",
    "user": "root",
    "password": "WILSONTARRIFA1900",
    "port":3306,
}

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")



# Usuarios locales (ejemplo). Mejor guardarlos en DB o archivo seguro en producción.
usuarios = {"wilson": "1234"}

# Puerto serial por defecto
DEFAULT_SERIAL_PORT = os.environ.get("RFID_PORT", "COM2")
DEFAULT_BAUDRATE = int(os.environ.get("RFID_BAUD", "9600"))

# ---------------------------
# UTIL: generador de tokens
# ---------------------------
def generar_token(lon: int = 8) -> str:
    token_chars = string.ascii_letters + string.digits
    return ''.join(random.choice(token_chars) for _ in range(lon))


# ---------------------------
# CLASE: Base de datos
# ---------------------------
class BaseDatos:
    """
    Clase simple que encapsula operaciones de MySQL.
    Reintenta la conexión si es necesario.
    """

    def __init__(self, config: dict):
        self.config = config

    def _get_conn(self):
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except Error as e:
            raise RuntimeError(f"Error conectando a la base de datos: {e}")

    def insertar_reserva(self, codigo: str, fecha: str, hora: str) -> Tuple[bool, str]:
        """
        Inserta una fila y devuelve (ok, mensaje).
        El id se calcula como MAX(id)+1 o inicia en 100 si no hay registros.
        """
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(id) FROM reservas")
            id_actual = cursor.fetchone()[0]
            nuevo_id = 100 if id_actual is None else id_actual + 1

            cursor.execute(
                "INSERT INTO reservas (id, codigo, fecha, hora) VALUES (%s, %s, %s, %s)",
                (nuevo_id, codigo, fecha, hora)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True, f"Reservado id={nuevo_id}"
        except Exception as e:
            return False, str(e)

    def obtener_reservas(self, limit: int = 100) -> List[Tuple]:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT id, codigo, fecha, hora FROM reservas ORDER BY id DESC LIMIT %s", (limit,))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except Exception as e:
            print("Error al obtener reservas:", e)
            return []


# ---------------------------
# CLASE: Hilo lector serial
# ---------------------------
class LectorSerial(QThread):
    dato_recibido = pyqtSignal(str)
    error_conexion = pyqtSignal(str)
    estado = pyqtSignal(str)

    def __init__(self, puerto: str = DEFAULT_SERIAL_PORT, baudrate: int = DEFAULT_BAUDRATE, poll_interval: float = 0.1):
        super().__init__()
        self.puerto = puerto
        self.baudrate = baudrate
        self.poll_interval = poll_interval
        self.running = True
        self.ser = None

    def run(self):
        # Intentar abrir puerto
        if serial is None:
            self.error_conexion.emit("Módulo pyserial no está instalado. 'pip install pyserial'")
            return

        try:
            self.ser = serial.Serial(self.puerto, self.baudrate, timeout=1)
            self.estado.emit(f"Puerto abierto: {self.puerto} @ {self.baudrate}")
        except Exception as e:
            self.error_conexion.emit(f"No se pudo abrir puerto {self.puerto}: {e}")
            return

        # Loop de lectura
        while self.running:
            try:
                if self.ser.in_waiting > 0:
                    raw = self.ser.readline().decode(errors="ignore").strip()
                    if raw:
                        self.dato_recibido.emit(raw)
                time.sleep(self.poll_interval)
            except Exception as e:
                self.error_conexion.emit(f"Error lectura serial: {e}")
                break

        # Cerrar puerto si está abierto
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
                self.estado.emit("Puerto serial cerrado")
        except Exception:
            pass

    def detener(self):
        self.running = False
        # Intentar desbloquear readline cerrando el puerto
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except Exception:
            pass


# ---------------------------
# VENTANA: Guardado (reutilizable)
# ---------------------------
class VentanaGuardado(QDialog):
    """
    Ventana de confirmación/revisión de guardado.
    Esta ventana se instancia una vez y se actualiza cuando llega
    un nuevo dato o cuando el usuario solicita ver el historial.
    """
    def __init__(self, db: BaseDatos, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("✅ Confirmación de guardado")
        self.setFixedSize(420, 320)
        self.setModal(False)  # no bloquear la app
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #e0e0e0; font-family: Segoe UI; }
            QLabel { font-size: 14px; padding: 4px; }
            QPushButton { background-color: #37474f; color: white; padding: 7px; border-radius: 6px; }
            QListWidget { background-color: #1e1e1e; border: 1px solid #333; }
        """)
        layout = QVBoxLayout(self)

        self.lbl_mensaje = QLabel("Esperando acción...")
        self.lbl_mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_mensaje)

        self.lista = QListWidget()
        layout.addWidget(self.lista)

        btns = QHBoxLayout()
        self.btn_refrescar = QPushButton("🔄 Refrescar lista")
        self.btn_refrescar.clicked.connect(self.cargar_lista)
        btns.addWidget(self.btn_refrescar)

        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.close)
        btns.addWidget(self.btn_cerrar)

        layout.addLayout(btns)

    def mostrar_guardado(self, codigo: str, fecha: str, hora: str, resultado_msg: str):
        """Actualizar texto y mostrar ventana"""
        self.lbl_mensaje.setText(resultado_msg.replace("\n", "<br>"))
        self.cargar_lista()
        if not self.isVisible():
            self.show()

    def cargar_lista(self):
        self.lista.clear()
        registros = self.db.obtener_reservas(limit=200)
        for reg in registros:
            self.lista.addItem(f"{reg[0]} - {reg[1]} - {reg[2]} {reg[3]}")


# ---------------------------
# VENTANA: Lector RFID principal
# ---------------------------
class VentanaRFID(QWidget):
    def __init__(self, db: BaseDatos, puerto: str = DEFAULT_SERIAL_PORT, baudrate: int = DEFAULT_BAUDRATE):
        super().__init__()
        self.db = db
        self.puerto = puerto
        self.baudrate = baudrate

        self.setWindowTitle("📡 Lector RFID - App")
        self.setFixedSize(640, 520)
        self.setStyleSheet(self.estilos())

        self.hilo_serial = None
        self.ventana_guardado = VentanaGuardado(self.db, parent=self)

        self.autosave = False  # si True guarda automáticamente (con debounce)
        self._last_auto_save_time = 0
        self._auto_save_cooldown = 1.0  # segundos entre auto-guardados

        self.setup_ui()
        self.iniciar_hilo_serial()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.titulo = QLabel("🛰️ Lector RFID Serial")
        self.titulo.setObjectName("Header")
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.titulo)

        linea = QFrame()
        linea.setObjectName("linea")
        linea.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(linea)

        self.sub = QLabel("Esperando datos del lector...")
        self.sub.setObjectName("Subtitulo")
        layout.addWidget(self.sub)

        self.lista = QListWidget()
        layout.addWidget(self.lista)

        botones = QHBoxLayout()
        botones.addStretch()

        self.boton_guardar = QPushButton("💾 Guardar seleccionado")
        self.boton_guardar.clicked.connect(self.guardar_seleccionado)
        botones.addWidget(self.boton_guardar)

        self.boton_refrescar = QPushButton("🧭 Mostrar datos (BD)")
        self.boton_refrescar.clicked.connect(self.mostrar_datos_bd)
        botones.addWidget(self.boton_refrescar)

        self.boton_limpiar = QPushButton("🧹 Limpiar Lista")
        self.boton_limpiar.clicked.connect(self.lista.clear)
        botones.addWidget(self.boton_limpiar)

        self.boton_autoguardado = QPushButton("🔁 Auto-guardar: OFF")
        self.boton_autoguardado.clicked.connect(self.toggle_autosave)
        botones.addWidget(self.boton_autoguardado)

        self.boton_salir = QPushButton("❌ Salir")
        self.boton_salir.clicked.connect(self.close)
        botones.addWidget(self.boton_salir)

        botones.addStretch()
        layout.addLayout(botones)

    def estilos(self):
        return """
        QWidget { background-color: #121212; font-family: Segoe UI; font-size: 14px; color: #e0e0e0; }
        QLabel#Header { font-size: 22px; font-weight: bold; color: #4fc3f7; margin: 10px 0; }
        QLabel#Subtitulo { font-size: 16px; color: #cfd8dc; padding-left: 20px; margin-bottom: 10px; }
        QListWidget { background-color: #1e1e1e; border: 1px solid #333; padding: 8px; margin: 0 20px; border-radius: 6px; }
        QPushButton { background-color: #37474f; color: white; border: none; padding: 8px 14px; border-radius: 6px; margin: 6px; }
        QPushButton:hover { background-color: #546e7a; }
        QFrame#linea { background-color: #263238; height: 2px; margin: 0 20px; }
        """

    def iniciar_hilo_serial(self):
        self.hilo_serial = LectorSerial(self.puerto, self.baudrate)
        self.hilo_serial.dato_recibido.connect(self.manejar_dato)
        self.hilo_serial.error_conexion.connect(self.mostrar_error)
        self.hilo_serial.estado.connect(self.actualizar_estado)
        self.hilo_serial.start()

    def actualizar_estado(self, texto: str):
        self.sub.setText(texto)

    def mostrar_error(self, mensaje: str):
        QMessageBox.critical(self, "Error de conexión serial", mensaje)

    def manejar_dato(self, dato: str):
        # Validación básica: alfanumérico y longitud razonable
        if not dato.isalnum() or not (4 <= len(dato) <= 20):
            self.sub.setText(f"⚠️ Dato inválido recibido: {dato}")
            return

        # Actualizar UI principal y encolar guardado (si corresponde)
        ts = datetime.now()
        self.sub.setText(f"📥 Último RFID leído: {dato}  ({ts.strftime('%H:%M:%S')})")
        self.lista.insertItem(0, f"{dato}  — {ts.strftime('%Y-%m-%d %H:%M:%S')}")

        # Si autosave activo, guardar con debounce para no abrir muchas ventanas
        if self.autosave:
            now = time.time()
            if now - self._last_auto_save_time >= self._auto_save_cooldown:
                self._last_auto_save_time = now
                # Guardado en background (no bloquear GUI)
                fecha = ts.strftime("%Y-%m-%d")
                hora = ts.strftime("%H:%M:%S")
                ok, msg = self.db.insertar_reserva(dato, fecha, hora)
                resultado_msg = f"✅ Guardado automático: {dato}" if ok else f"❌ Falló auto-guardar: {msg}"
                # Mostrar ventana reutilizable SOLO si ya está visible
                if self.ventana_guardado.isVisible():
                    self.ventana_guardado.mostrar_guardado(dato, fecha, hora, resultado_msg)

    def guardar_seleccionado(self):
        item = self.lista.currentItem()
        if item is None:
            QMessageBox.information(self, "Sin selección", "Selecciona un dato en la lista para guardar.")
            return
        # Extraer código (tipo 'codigo  — YYYY-MM-DD hh:mm:ss'), lo tomamos hasta el primer espacio o antes del '  —'
        texto = item.text()
        codigo = texto.split("  —")[0].strip()
        ts = datetime.now()
        fecha = ts.strftime("%Y-%m-%d")
        hora =  ts.strftime("%H:%M:%S")

        ok, msg = self.db.insertar_reserva(codigo, fecha, hora)
        resultado_msg = f"✅ Dato guardado:\n\n📄 Código: {codigo}\n📅 Fecha: {fecha}\n⏰ Hora: {hora}" if ok else f"❌ Error: {msg}"
        self.ventana_guardado.mostrar_guardado(codigo, fecha, hora, resultado_msg)

    def mostrar_datos_bd(self):
        # Muestra la ventana reutilizable y carga registros
        self.ventana_guardado.cargar_lista()
        self.ventana_guardado.show()

    def toggle_autosave(self):
        self.autosave = not self.autosave
        txt = "🔁 Auto-guardar: ON" if self.autosave else "🔁 Auto-guardar: OFF"
        self.boton_autoguardado.setText(txt)

    def closeEvent(self, event):
        # Pedimos detener el hilo antes de cerrar
        try:
            if self.hilo_serial:
                self.hilo_serial.detener()
                self.hilo_serial.wait(1000)
        except Exception:
            pass
        event.accept()


# ---------------------------
# VENTANA: Cambio de credenciales y envío TOKEN (Twilio)
# ---------------------------
class CambioCredenciales(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧶 Cambiar usuario / Enviar token")
        self.setFixedSize(420, 420)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #e0e0e0; font-family: Segoe UI; }
            QLineEdit { background-color: #1e1e1e; color: #e0e0e0; padding: 6px; border-radius: 4px; }
            QPushButton { background-color: #37474f; color: white; padding: 8px; border-radius: 6px; }
        """)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.usuario_viejo = QLineEdit()
        self.usuario_nuevo = QLineEdit()
        self.pass_vieja = QLineEdit()
        self.pass_vieja.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_nueva = QLineEdit()
        self.pass_nueva.setEchoMode(QLineEdit.EchoMode.Password)
        self.line_token_phone = QLineEdit()
        self.line_token_phone.setPlaceholderText("Ej: 3201234567 (sin +)")

        form.addRow("Usuario actual:", self.usuario_viejo)
        form.addRow("Contraseña actual:", self.pass_vieja)
        form.addRow("Nuevo usuario:", self.usuario_nuevo)
        form.addRow("Nueva contraseña:", self.pass_nueva)
        form.addRow("Teléfono (para token):", self.line_token_phone)

        layout.addLayout(form)

        self.btn_guardar = QPushButton("🪁 Guardar cambios")
        self.btn_guardar.clicked.connect(self.aplicar_cambio)
        self.btn_enviar = QPushButton("🪪 Enviar credencial (Twilio)")
        self.btn_enviar.clicked.connect(self.enviar_token)

        layout.addWidget(self.btn_guardar)
        layout.addWidget(self.btn_enviar)
        layout.addStretch()

    def aplicar_cambio(self):
        user_old = self.usuario_viejo.text().strip()
        pass_old = self.pass_vieja.text().strip()
        user_new = self.usuario_nuevo.text().strip()
        pass_new = self.pass_nueva.text().strip()

        if not user_old or not pass_old or not user_new or not pass_new:
            QMessageBox.warning(self, "Campos vacíos", "Completa todos los campos de usuario y contraseña.")
            return
        if user_old not in usuarios or usuarios[user_old] != pass_old:
            QMessageBox.warning(self, "Error", "Usuario o contraseña actual incorrectos.")
            return
        # Cambiar credenciales local
        usuarios.pop(user_old)
        usuarios[user_new] = pass_new
        QMessageBox.information(self, "Actualizado", f"Usuario cambiado a: {user_new}")

    def enviar_token(self):
        # Enviar token vía SMS usando Twilio
        phone = self.line_token_phone.text().strip()
        if not phone.isdigit() or len(phone) < 7:
            QMessageBox.warning(self, "Número inválido", "Ingresa un número de teléfono válido (solo dígitos).")
            return
        if not TWILIO_SID or not TWILIO_TOKEN:
            QMessageBox.critical(self, "Configuración Twilio", "No se configuraron las credenciales de Twilio.")
            return
        token = generar_token(6)
        try:
            client = Client(TWILIO_SID, TWILIO_TOKEN)
            mensaje = client.messages.create(
            body=f"Tu código de acceso es: {token}",
            from_=TWILIO_FROM,
            to=f"+57{phone}"
            )
            QMessageBox.information(self, "Mensaje enviado", f"Token enviado al +57{phone}. SID: {mensaje.sid}")
        except Exception as e:
            QMessageBox.critical(self, "Error al enviar SMS", str(e))


# ---------------------------
# VENTANA: Login simple
# ---------------------------
class LoginSimple(QWidget):
    def __init__(self , db:BaseDatos):
        super().__init__()
        self.db = db
        self.setWindowTitle("🔑 Login simple")
        self.setFixedSize(320, 280)
        self.setup_ui()
        

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #e0e0e0; font-family: Segoe UI; }
            QLineEdit { background-color: #1e1e1e; color: #e0e0e0; padding: 6px; border-radius: 4px; }
            QPushButton { background-color: #37474f; color: white; border: none; padding: 8px 20px; 
                           border-radius: 6px; margin-top: 20px; }
        """)
        layout = QVBoxLayout(self)

        self.line_user = QLineEdit()
        self.line_user.setPlaceholderText("Usuario")
        self.line_pass = QLineEdit()
        self.line_pass.setPlaceholderText("Contraseña")
        self.line_pass.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.btn_login = QPushButton("Entrar")
        self.btn_login.clicked.connect(self.verificar_login)

        self.btn_cambio= QPushButton("cambio-credenciales")
        self.btn_cambio.clicked.connect(self.cambiar_usuario)
        

        layout.addWidget(self.line_user)
        layout.addWidget(self.line_pass)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_cambio)

    def cambiar_usuario(self):

        self.CambioCredenciales=CambioCredenciales()
        self.CambioCredenciales.show()

    def verificar_login(self):
        user = self.line_user.text().strip()
        pwd = self.line_pass.text().strip()
        if not user or not pwd:
            QMessageBox.warning(self, "Campos vacíos", "Usuario o contraseña vacíos.")
            return
        if user not in usuarios or usuarios[user] != pwd:
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos.")
            return
        QMessageBox.information(self, "Login OK", f"Bienvenido, {user}!")
        # Aquí podrías ocultar esta ventana y mostrar la ventana principal
    
        self.ventana_rfid = VentanaRFID(self.db)
        self.ventana_rfid.show()
        self.close()  # cierra el login

        
# ------------------------------
# PUNTO DE ENTRADA
# ------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = BaseDatos(DB_CONFIG)
    login = LoginSimple(db)
    login.show()
    sys.exit(app.exec())

