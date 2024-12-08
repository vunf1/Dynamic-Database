from PyQt5.QtWidgets import (
    QApplication, QComboBox, QLineEdit, QPushButton, QLabel,
    QVBoxLayout, QGridLayout, QWidget
)

from PyQt5.QtGui import QFont, QMouseEvent, QPalette, QBrush, QPixmap, QColor
from PyQt5.QtCore import pyqtSignal, Qt, QPoint
from model.json_logic import load_db, load_settings_data, save_db 
from helpers import MessageBox, confirm_msg, show_message
import random

class AddToDatabaseWindow(QWidget):
    data_added_signal = pyqtSignal()# Define a custom signal to notify when data is added
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.drag_position = QPoint()

    def init_ui(self):
        # Remove window borders and keep always on top
        self.setWindowFlags(Qt.FramelessWindowHint| Qt.WindowStaysOnTopHint)
        self.setWindowTitle("ADD NEW")
        # Set background image
        image_number = random.randint(1, 2)
        self.set_background_image(f"assets/image/background-{image_number}.png")
        self.setStyleSheet("QLabel { color: white; }")
        self.setMinimumSize(500, 300)

        layout = QVBoxLayout()
        grid_layout = QGridLayout()

        # Load data and add keys to ComboBox
        data = load_settings_data()
        brand_keys = list(data["Settings"]["Brands"].keys())
        types_keys = list(data["Settings"]["Types"].keys())
        windows_version_keys = list(data["Settings"]["WindowsVersions"].keys())

        # Define font
        font_settings = QFont()
        font_settings.setPointSize(12)
        # Define input height
        input_height = 35
        
        # Close Button
        close_button = QPushButton("X")
        close_button.setFont(font_settings)
        close_button.setFixedSize(20, 20)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)
        close_button.clicked.connect(self.close)
        grid_layout.addWidget(close_button, 0, 2, Qt.AlignRight)

        # Connect signals for real-time validation

        # Brand ComboBox
        brand_label = QLabel("Brand:")
        brand_label.setFont(font_settings)
        grid_layout.addWidget(brand_label, 1, 0)
        self.brand_combobox = QComboBox()
        self.brand_combobox.currentIndexChanged.connect(self.update_submit_button_color) 
        self.brand_combobox.setFont(font_settings)
        self.brand_combobox.setPlaceholderText("Example: HP")
        self.brand_combobox.setEditable(True) # Search by typing 
        self.brand_combobox.setFixedHeight(input_height)
        self.brand_combobox.addItems(brand_keys)
        grid_layout.addWidget(self.brand_combobox, 1, 1)
        
        # Model Entry
        model_label = QLabel("Model:")
        model_label.setFont(font_settings)
        grid_layout.addWidget(model_label, 2, 0)
        self.model_entry = QLineEdit()
        self.model_entry.textChanged.connect(self.update_submit_button_color)
        self.model_entry.setFixedHeight(input_height)
        self.model_entry.setFont(font_settings)
        self.model_entry.setFixedHeight(input_height)        
        # Connect textChanged signal to enforce uppercase
        self.model_entry.textChanged.connect(self.force_uppercase)
        self.model_entry.setToolTip("Enter the device model (e.g.,840 G3)")
        self.model_entry.setPlaceholderText("Example:840 G3")
        grid_layout.addWidget(self.model_entry, 2, 1)

        # Type ComboBox
        type_label = QLabel("Type:")
        type_label.setFont(font_settings)
        grid_layout.addWidget(type_label, 3, 0)
        self.type_combobox = QComboBox()
        self.type_combobox.currentIndexChanged.connect(self.update_submit_button_color)
        self.type_combobox.setFont(font_settings)
        self.type_combobox.setFixedHeight(input_height)
        self.type_combobox.setEditable(True) # Search by typing    
        # Add a default placeholder item 
        #self.placeholder_text = "Example: Laptop"
        #self.type_combobox.addItem(self.placeholder_text)
        #self.type_combobox.setItemData(0, 0, 0)  # Disable the placeholder remove "[""] + "
        self.type_combobox.addItems([""]+types_keys)
        # Connect signal for selection change 
        # Connect focus and cursor position events
        #self.type_combobox.lineEdit().cursorPositionChanged.connect(self.clear_placeholder)
        #self.type_combobox.lineEdit().focusInEvent = self.focus_event_clear_field
        grid_layout.addWidget(self.type_combobox, 3, 1)

        # Windows Version ComboBox Initialization
        windows_label = QLabel("Windows Version:")
        windows_label.setFont(font_settings)
        grid_layout.addWidget(windows_label, 4, 0)
        self.windows_version_combobox = QComboBox()
        self.windows_version_combobox.setFont(font_settings)
        self.windows_version_combobox.setFixedHeight(input_height)
        self.windows_version_combobox.addItems([""] + windows_version_keys)
        
        self.windows_version_combobox.currentIndexChanged.connect(self.update_submit_button_color)
        grid_layout.addWidget(self.windows_version_combobox, 4, 1)

        # Image ComboBox
        image_label = QLabel("Image:")
        image_label.setFont(font_settings)
        grid_layout.addWidget(image_label, 5, 0)
        self.image_combobox = QComboBox()
        self.image_combobox.setFont(font_settings)
        self.image_combobox.setFixedHeight(input_height)
        self.image_combobox.setEditable(True)
        self.image_combobox.addItems(["", "Done", "Not Done"])
        self.image_combobox.currentIndexChanged.connect(self.update_submit_button_color)
        grid_layout.addWidget(self.image_combobox, 5, 1)

        self.submit_button = QPushButton("Submit")
        self.submit_button.setFont(font_settings)
        self.submit_button.setFixedHeight(input_height + 5)
        self.submit_button.setStyleSheet("background-color: orange; color: white; font-weight: bold;")
        self.submit_button.clicked.connect(self.submit_data)
        layout.addLayout(grid_layout)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.beautify_json_file_save()

    def update_submit_button_color(self):
        """Update the submit button's color based on form validation."""    
        # Ensure the form fields are initialized
        if not hasattr(self, 'windows_version_combobox'): # Error handler where combobox isnt init until late so trigger error, return empty then when needed is initialized
            return
        form_data = self.get_form_data()
        if all(form_data.values()):
            # All fields are filled - set to green
            self.submit_button.setStyleSheet("""
                background-color: green;
                color: white;
                font-weight: bold;
            """)
        else:
            # Incomplete fields - set to orange
            self.submit_button.setStyleSheet("""
                background-color: orange;
                color: white;
                font-weight: bold;
            """)
    def force_uppercase(self, text):
        """Enforces uppercase input."""
        self.model_entry.setText(text.upper())

    def focus_event_clear_field(self, event):
        """Clear, only if is, placeholder when the combo box is focused."""
        if self.type_combobox.currentText() == self.placeholder_text:
            self.type_combobox.setCurrentIndex(-1)
            self.type_combobox.lineEdit().clear()
        # Call the original focus event
        QComboBox.lineEdit(self.type_combobox).focusInEvent(event)

    def clear_placeholder(self):
        """Clears the placeholder if it's selected."""
        if self.type_combobox.currentText() == self.placeholder_text:
            self.type_combobox.setCurrentIndex(-1)  # Clear selection
            self.type_combobox.lineEdit().clear()

    def submit_data(self):
        """Submit data to the JSON file."""
        # Collect form data
        form_data = self.get_form_data()
        if not all(form_data.values()):
            show_message("critical","Error", "All fields must be filled!")
            #QMessageBox.critical(self, "Error", "All fields must be filled!")
            return

        brand = form_data.pop("Brand")  # Extract brand and remove it from form_data
        data = load_db()

        # Ensure brand list exists
        if brand not in data:
            data[brand] = []

        # Check for an existing entry
        existing_entry = self.find_existing_entry(data[brand], form_data)

        if existing_entry:
            if not self.confirm_overwrite(existing_entry):
                return
            existing_entry.update(form_data)
            show_message("Success", "Entry updated successfully!")
        else:
            data[brand].append(form_data)
            show_message("Success", "Data submitted successfully!")

        # Save changes and clear fields
        save_db(data)
        self.data_added_signal.emit()
        self.clear_fields()




        # Helper Methods
    def get_form_data(self):
        """Retrieve and return form data as a dictionary."""
        return {
            "Brand": self.brand_combobox.currentText(),
            "Model": self.model_entry.text(),
            "Type": self.type_combobox.currentText(),
            "Windows Version": self.windows_version_combobox.currentText(),
            "Image": self.image_combobox.currentText(),
        }

    def find_existing_entry(self, brand_data, form_data):
        """Find an existing entry matching the form data."""
        return next(
            (item for item in brand_data if 
            item["Model"] == form_data["Model"] and 
            item["Type"] == form_data["Type"] and 
            item["Windows Version"] == form_data["Windows Version"]),
            None
        )

    def confirm_overwrite(self, existing_entry):
        """Ask for overwrite confirmation and return the user's choice."""
        message = (
            f"An entry already exists for this model:\n\n"
            f"Model: {existing_entry['Model']}\n"
            f"Type: {existing_entry['Type']}\n"
            f"Windows Version: {existing_entry['Windows Version']}\n"
            f"Image: {existing_entry['Image']}\n\n"
            f"Do you want to overwrite this entry?"
        )
        return confirm_msg("Overwrite Confirmation", message)


    def show_message(self, title, message):
        """Display an information message box."""
        show_message("information", title, message)
    
    def beautify_json_file_save(self):
        """Reformat the JSON file to ensure consistency."""
        data = load_db()
        save_db(data)

    def clear_fields(self):
        """Clear Input Fields"""
        self.brand_combobox.setCurrentIndex(0)
        self.model_entry.clear()
        self.type_combobox.setCurrentIndex(0)
        self.windows_version_combobox.setCurrentIndex(0)
        self.image_combobox.setCurrentIndex(0)
    
    # Override mouse events for dragging
    def mousePressEvent(self, event: QMouseEvent):
        """ Capture the initial click position """
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """ Move the window when dragging """
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def set_background_image(self, image_path):
        """Sets the background image or falls back to a random color."""
        palette = QPalette()
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            show_message("warning","background image",f"Warning: Could not load background image from {image_path}. Using random color.")
            # Generate a random color
            random_color = QColor(
                random.randint(0, 255), 
                random.randint(0, 255), 
                random.randint(0, 255)
            )
            palette.setColor(QPalette.Background, random_color)
        else:
            # Scale the pixmap to fit the window size
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,  # Keeps aspect ratio but covers the entire window
                Qt.SmoothTransformation         # Smooth scaling
            )
            palette.setBrush(QPalette.Background, QBrush(scaled_pixmap))

        self.setPalette(palette)


if __name__ == "__main__":
    app = QApplication([])
    window = AddToDatabaseWindow()
    window.show()
    app.exec_()
