import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton

class VentanaLista(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ejemplo de QListWidget")
        self.setGeometry(300, 300, 300, 300)

        # Layout principal
        layout = QVBoxLayout()

        # Lista
        self.lista = QListWidget()
        layout.addWidget(self.lista)

        # Botón para agregar elementos
        boton_agregar = QPushButton("Agregar datos")
        boton_agregar.clicked.connect(self.agregar_datos)
        layout.addWidget(boton_agregar)

        # Botón para limpiar lista
        boton_limpiar = QPushButton("Limpiar lista")
        boton_limpiar.clicked.connect(self.lista.clear)
        layout.addWidget(boton_limpiar)

        self.setLayout(layout)

    def agregar_datos(self):
        # Datos de ejemplo (pueden venir de una BD)
        datos = ["Producto A", "Producto B", "Producto C"]
        self.lista.addItems(datos)  # Agrega varios elementos a la vez


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaLista()
    ventana.show()
    sys.exit(app.exec())