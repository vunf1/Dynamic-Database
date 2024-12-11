from PyQt5.QtWidgets import (
    QApplication, QComboBox, QLineEdit, QPushButton, QLabel,
    QVBoxLayout, QGridLayout, QWidget
)
from PyQt5.QtGui import QFont, QMouseEvent, QPalette, QBrush, QPixmap, QColor, QIcon
from PyQt5.QtCore import pyqtSignal, Qt, QPoint

from model.json_logic import load_db, load_settings_data, save_db
from helpers.messages_dialog import confirm_message, show_message

import random


class AddToDatabaseWindow(QWidget):
    data_added_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.drag_position = QPoint()
        self.init_ui()

    def init_ui(self):
        self.setup_window()
        self.setup_layout()

    def setup_window(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Add New")
        self.setWindowIcon(QIcon("assets/icons/icon.ico"))
        self.set_background_image(f"assets/image/background-{random.randint(1, 2)}.png")
        self.setStyleSheet("QLabel { color: white; }")
        self.setMinimumSize(500, 300)

    def setup_layout(self):
        main_layout = QVBoxLayout()
        grid_layout = QGridLayout()

        font_settings = QFont()
        font_settings.setPointSize(12)
        input_height = 35

        # Close Button
        close_button = self.create_button("X", "red", self.close, font_settings, (20, 20))
        close_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;  /* White Text */
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)
        grid_layout.addWidget(close_button, 0, 2, Qt.AlignRight)

        # Load Settings Data
        settings_data = load_settings_data()
        brand_keys = settings_data["Settings"]["Brands"].keys()
        types_keys = settings_data["Settings"]["Types"].keys()
        windows_version_keys = settings_data["Settings"]["WindowsVersions"].keys()

        # Form Fields
        self.brand_combobox = self.create_combobox("Brand", grid_layout, 1, brand_keys, font_settings, input_height)
        self.model_entry = self.create_lineedit("Model", "Example: 840 G3", grid_layout, 2, font_settings, input_height)
        self.model_entry.textChanged.connect(lambda: self.force_uppercase(self.model_entry))

        self.type_combobox = self.create_combobox("Type", grid_layout, 3, types_keys, font_settings, input_height)
        self.windows_version_combobox = self.create_combobox(
            "Windows Version", grid_layout, 4, windows_version_keys, font_settings, input_height
        )
        self.image_combobox = self.create_combobox(
            "Image", grid_layout, 5, ["Done", "Not Done"], font_settings, input_height
        )

        # Submit Button
        self.submit_button = self.create_button(
            "Submit", "orange", self.submit_data, font_settings, (input_height + 5, input_height + 10)
        )
        self.submit_button.setMinimumHeight(45)
        self.submit_button.setMinimumWidth(180)
        self.submit_button.setSizePolicy(self.submit_button.sizePolicy().Expanding, self.submit_button.sizePolicy().Fixed)
        # Add layouts
        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.submit_button, alignment=Qt.AlignCenter)
        self.setLayout(main_layout)

    def create_combobox(self, label_text, layout, row, items, font, height):
        label = QLabel(f"{label_text}:")
        label.setFont(font)
        layout.addWidget(label, row, 0)

        combobox = QComboBox()
        combobox.addItems([""] + list(items))
        combobox.setFont(font)
        combobox.setEditable(True)
        combobox.setFixedHeight(height)
        combobox.currentIndexChanged.connect(self.update_submit_button_color)
        layout.addWidget(combobox, row, 1)
        return combobox

    def create_lineedit(self, label_text, placeholder, layout, row, font, height):
        label = QLabel(f"{label_text}:")
        label.setFont(font)
        layout.addWidget(label, row, 0)

        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setFont(font)
        line_edit.setFixedHeight(height)
        line_edit.textChanged.connect(self.update_submit_button_color)
        layout.addWidget(line_edit, row, 1)
        return line_edit

    def create_button(self, text, color, action, font, size=None):
        button = QPushButton(text)
        button.setFont(font)
        if size:
            button.setFixedSize(*size)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: dark{color};
            }}
        """)
        button.clicked.connect(action)
        return button

    def submit_data(self):
        form_data = self.get_form_data()

        if not all(form_data.values()):
            show_message("critical", "Error", "All fields must be filled!")
            return
        
        form_data = {key: value.upper() if isinstance(value, str) else value for key, value in form_data.items()}

        brand = form_data.pop("Brand")
        data = load_db()

        if brand not in data:
            data[brand] = []

        existing_entry = self.find_existing_entry(data[brand], form_data)

        if existing_entry:
            if not self.confirm_overwrite(existing_entry):
                return
            existing_entry.update(form_data)
            show_message("information", "Success", "Entry updated successfully!")
        else:
            data[brand].append(form_data)
            show_message("information", "Success", "Data submitted successfully!")

        save_db(data)
        self.data_added_signal.emit()
        self.clear_fields()

    def find_existing_entry(self, brand_data, form_data):
        return next(
            (entry for entry in brand_data if
             entry.get("Model") == form_data.get("Model") and
             entry.get("Type") == form_data.get("Type")),
            None
        )

    def confirm_overwrite(self, existing_entry):
        message = (
            f"An entry already exists for this model:\n\n"
            f"Model: {existing_entry['Model']}\n"
            f"Type: {existing_entry['Type']}\n"
            f"Windows Version: {existing_entry['Windows Version']}\n"
            f"Image: {existing_entry['Image']}\n\n"
            f"Do you want to overwrite this entry?"
        )
        return confirm_message("Overwrite Confirmation", message)

    def get_form_data(self):
        return {
            "Brand": self.brand_combobox.currentText(),
            "Model": self.model_entry.text(),
            "Type": self.type_combobox.currentText(),
            "Windows Version": self.windows_version_combobox.currentText(),
            "Image": self.image_combobox.currentText(),
        }

    def update_submit_button_color(self):
        form_data = self.get_form_data()
        color = "green" if all(form_data.values()) else "orange"
        self.submit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-weight: bold;
            }}
        """)

    def force_uppercase(self, line_edit):
        line_edit.setText(line_edit.text().upper())

    def clear_fields(self):
        self.brand_combobox.setCurrentIndex(0)
        self.model_entry.clear()
        self.type_combobox.setCurrentIndex(0)
        self.windows_version_combobox.setCurrentIndex(0)
        self.image_combobox.setCurrentIndex(0)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def set_background_image(self, image_path):
        palette = QPalette()
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            random_color = QColor(*(random.randint(0, 255) for _ in range(3)))
            palette.setColor(QPalette.Background, random_color)
        else:
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            palette.setBrush(QPalette.Background, QBrush(scaled_pixmap))

        self.setPalette(palette)
'''
# Debug

if __name__ == "__main__":    
    app = QApplication([])
    window = AddToDatabaseWindow()
    window.show()
    app.exec_()

'''