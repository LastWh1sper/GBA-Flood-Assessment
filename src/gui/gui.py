import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QFileDialog, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shapefile Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.project_name = ""
        self.shapefile_path = ""

        self.layout = QVBoxLayout()
        self.central_widget = QWidget(self)
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.label = QLabel("No shapefile selected")
        self.layout.addWidget(self.label)

        self.select_button = QPushButton("Select Shapefile")
        self.select_button.clicked.connect(self.select_shapefile)
        self.layout.addWidget(self.select_button)

        self.project_button = QPushButton("Select Project Name")
        self.project_button.clicked.connect(self.select_project_name)
        self.layout.addWidget(self.project_button)

    def select_shapefile(self):
        file_dialog = QFileDialog(self)
        self.shapefile_path, _ = file_dialog.getOpenFileName(self, "Select Shapefile", "", "Shapefile (*.shp)")
        if self.shapefile_path:
            self.label.setText(f"Selected shapefile: {self.shapefile_path}")

    def select_project_name(self):
        project_dialog = QFileDialog(self)
        self.project_name, _ = project_dialog.getSaveFileName(self, "Select Project Name", "", "Project Name (*.proj)")
        if self.project_name:
            self.label.setText(f"Selected project name: {self.project_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())