from PyQt5.QtWidgets import (
    QApplication, QComboBox, QLineEdit, QPushButton, QLabel,
    QVBoxLayout, QGridLayout, QMessageBox, QWidget
)
from PyQt5.QtCore import pyqtSignal, QObject
from model.json_logic import load_db, load_settings_data, save_db 


class AddToDatabaseWindow(QWidget):
    # Define a custom signal to notify when data is added
    data_added = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("ADD NEW")
        layout = QVBoxLayout()
        grid_layout = QGridLayout()

        # Load data and add keys to ComboBox
        data = load_settings_data()
        brand_keys = list(data["Settings"]["Brands"].keys())
        types_keys = list(data["Settings"]["Types"].keys())
        windows_version_keys = list(data["Settings"]["WindowsVersions"].keys())

        grid_layout.addWidget(QLabel("Brand:"), 0, 0)
        self.brand_combobox = QComboBox() 
        self.brand_combobox.setEditable(True) # Search by typing 
        self.brand_combobox.addItems([""] + brand_keys)
        grid_layout.addWidget(self.brand_combobox, 0, 1)

        grid_layout.addWidget(QLabel("Model:"), 1, 0)
        self.model_entry = QLineEdit()
        self.model_entry.setToolTip("Enter the device model (e.g., EliteBook 840 G3)")
        self.model_entry.setPlaceholderText("Example: EliteBook 840 G3")
        grid_layout.addWidget(self.model_entry, 1, 1)

        # Types Combobox
        grid_layout.addWidget(QLabel("Type:"), 2, 0)
        self.type_combobox = QComboBox()
        self.type_combobox.addItems(["" + types_keys])
        grid_layout.addWidget(self.type_combobox, 2, 1)

        # Windows Combobox
        grid_layout.addWidget(QLabel("Windows Version:"), 3, 0)
        self.windows_version_combobox = QComboBox()
        self.windows_version_combobox.addItems(["" + windows_version_keys])
        grid_layout.addWidget(self.windows_version_combobox, 3, 1)

        grid_layout.addWidget(QLabel("Image:"), 4, 0)
        self.image_combobox = QComboBox()
        self.image_combobox.addItems(["", "Done", "Not Done"])
        grid_layout.addWidget(self.image_combobox, 4, 1)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_data)
        layout.addLayout(grid_layout)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.beautify_json_file_save()

    def submit_data(self):
        brand = self.brand_combobox.currentText()
        model = self.model_entry.text()
        type_ = self.type_combobox.currentText()
        windows_version = self.windows_version_combobox.currentText()
        image = self.image_combobox.currentText()

        if not all([brand, model, type_, windows_version, image]):
            QMessageBox.critical(self, "Error", "All fields must be filled!")
            return

        data = load_db()

        if brand not in data:
            data[brand] = []

        existing_entry = next(
            (item for item in data[brand] if item["Model"] == model and item["Type"] == type_ and item["Windows Version"] == windows_version),
            None
        )

        if existing_entry:
            reply = QMessageBox.question(
                self, "Overwrite Confirmation",
                f"An entry already exists for this model:\n\n"
                f"Model: {existing_entry['Model']}\n"
                f"Type: {existing_entry['Type']}\n"
                f"Windows Version: {existing_entry['windows_version']}\n"
                f"Image: {existing_entry['Image']}\n\n"
                f"Do you want to overwrite this entry?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

            existing_entry["Image"] = image
            QMessageBox.information(self, "Success", "Entry updated successfully!")
        else:
            data[brand].append({
                "Model": model,
                "Type": type_,
                "Windows Version": windows_version,
                "Image": image
            })
            QMessageBox.information(self, "Success", "Data submitted successfully!")

        #save_db(data)
        self.beautify_json_file_save()
        self.clear_fields()
        # Emit the data_added signal to refresh table
        self.data_added.emit()

    """Reformat the JSON file to ensure consistency."""
    def beautify_json_file_save(self):
        data = load_db()
        save_db(data)

    def clear_fields(self):
        self.brand_combobox.setCurrentIndex(0)
        self.model_entry.clear()
        self.type_combobox.setCurrentIndex(0)
        self.windows_version_combobox.setCurrentIndex(0)
        self.image_combobox.setCurrentIndex(0)
