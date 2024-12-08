from PyQt5.QtWidgets import (
    QApplication, QTableView, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QHBoxLayout
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QMouseEvent, QPalette, QBrush, QPixmap, QColor
from PyQt5.QtWidgets import QHeaderView
from helpers import confirm_msg, show_message
from model.json_logic import load_db, save_db
from plus import AddToDatabaseWindow
import random

class CustomFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_string = ""

    def setFilterString(self, text):
        self.filter_string = text.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        # Concatenate all column data for the row
        model = self.sourceModel()
        row_data = []
        for column in range(model.columnCount()):
            index = model.index(source_row, column, source_parent) # Grab Values
            row_data.append(model.data(index))
        concatenated_data = " ".join(row_data).lower()
        # Split the filter string into individual words
        filter_words = self.filter_string.split()

        # Check if all filter words are present as substrings in the concatenated data if so return valid answers
        return all(word in concatenated_data for word in filter_words)


class DataViewApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Remove borders and set always on top
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Images DB")  # Set the window title
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("assets/icons/icon.ico"))  # Path to your icon file

        # Set background image
        image_number = random.randint(1, 2)
        self.set_background_image(f"assets/image/background-{image_number}.png")
        # Layouts
        main_layout = QVBoxLayout()
        
        # Top Bar Layout
        top_bar_layout = QHBoxLayout()

        # Close Button
        self.close_button = QPushButton("X")
        self.close_button.setFixedSize(20, 20)
        self.close_button.setStyleSheet("""
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
        self.close_button.clicked.connect(self.close)
        top_bar_layout.addWidget(self.close_button, alignment=Qt.AlignRight)

        main_layout.addLayout(top_bar_layout)

        # Filter Layout
        filter_layout = QHBoxLayout()
        # Add Delete Button
        self.delete_button = QPushButton("Del Sel")
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)
        self.delete_button.clicked.connect(self.delete_selected_entry)
        filter_layout.addWidget(self.delete_button)

        # Refresh Button with Icon
        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(QIcon("assets/icons/refresh.svg"))  # Path to refresh icon
        self.refresh_button.setToolTip("Refresh Data")
        self.refresh_button.clicked.connect(self.load_data_GUI)
        filter_layout.addWidget(self.refresh_button)

        # Add Button with Icon
        self.add_button = QPushButton()
        self.add_button.setIcon(QIcon("assets/icons/add.svg"))  # Path to add icon
        self.add_button.setToolTip("Add New Entry")
        self.add_button.clicked.connect(self.open_add_window)
        filter_layout.addWidget(self.add_button)
        main_layout.addLayout(filter_layout)
        #filter_layout.addWidget(QLabel("Filter:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Type to filter...")
        self.filter_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_input)


        # Table View
        self.table_view = QTableView()
        self.table_view.setSortingEnabled(True)  # Enable sorting
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch columns
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)  # Resize rows
        self.table_view.horizontalHeader().setStretchLastSection(True)  # Stretch the last column
        main_layout.addWidget(self.table_view)

        self.setLayout(main_layout)

        # Data Model and Proxy Model
        self.model = QStandardItemModel()
        self.proxy_model = CustomFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.table_view.setModel(self.proxy_model)

        self.load_data_GUI()  # Load data initially

    def load_data_GUI(self):
        """Load JSON data and populate the table with ordered columns."""
        self.model.clear()  # Clear existing data in the model
        data = load_db()

        # Define ordered headers with Brand first and Model second
        ordered_headers = ["Brand", "Model"]

        # Dynamically add remaining headers
        for brand, items in data.items():
            for item in items:
                for key in item.keys():
                    if key not in ordered_headers:
                        ordered_headers.append(key)

        # Set headers for the table
        self.model.setHorizontalHeaderLabels(ordered_headers)

        # Populate the table with data
        for brand, items in data.items():
            for item in items:
                row = []
                for header in ordered_headers:
                    if header == "Brand":
                        row.append(QStandardItem(brand))  # Add the brand from the outer key
                    else:
                        # Add item data or an empty string if the key is missing
                        row.append(QStandardItem(item.get(header, "")))
                self.model.appendRow(row)

    def delete_selected_entry(self):
        """Delete the currently selected entry."""
        selected_index = self.table_view.currentIndex()

        if not selected_index.isValid():
            show_message("warning", "No Selection", "Please select an entry to delete.")
            return

        # Extract row data
        row_index = selected_index.row()
        brand = self.model.item(row_index, 0).text()  # First column is "Brand"

        # Extract all headers correctly
        headers = [self.model.headerData(col, Qt.Horizontal) for col in range(self.model.columnCount())]

        # Collect data from the row, excluding the "Brand" header
        item_data = {
            header: self.model.item(row_index, col).text() 
            for col, header in enumerate(headers) 
            if header != "Brand"
        }
        # Format data into a readable string
        formatted_data = "\n".join(f"{key}: {value}" for key, value in item_data.items())

        # Confirm Deletion
        if not confirm_msg(
            "Delete Entry", 
            f"Are you sure you want to delete this entry?\n\n"
            f"Brand: {brand}\n\n"
            f"{formatted_data}",
            parent=self
        ):return

        # Update the data and remove the entry
        data = load_db()

        if brand in data:
            for index, entry in enumerate(data[brand]):
                if all(str(entry.get(key, "")) == item_data[key] for key in item_data):
                    del data[brand][index]
                    break

            if not data[brand]:  # Remove the brand if empty
                del data[brand]

        save_db(data)
        self.load_data_GUI()  # Refresh the view
        show_message("information", "Success", "Entry deleted successfully!")


    def apply_filter(self):
        """Apply filter based on user input."""
        filter_text = self.filter_input.text()
        self.proxy_model.setFilterString(filter_text)

    def open_add_window(self):
        """Open Add Window"""
        self.add_window = AddToDatabaseWindow()
        self.add_window.data_added_signal.connect(self.load_data_GUI)  # Connect the signal        
        self.add_window.show()

    # Override mouse events for dragging
    def mousePressEvent(self, event: QMouseEvent):
        """ Capture the initial mouse click position """
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """ Move the window while dragging """
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
    window = DataViewApp()
    window.show()
    app.exec_()
