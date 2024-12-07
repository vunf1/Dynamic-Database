from PyQt5.QtWidgets import (
    QApplication, QTableView, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QHBoxLayout
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QHeaderView
from model.json_logic import load_db
from plus import AddToDatabaseWindow


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
        self.setWindowTitle("View Data Table")
        self.setGeometry(100, 100, 800, 600)

        # Layouts
        main_layout = QVBoxLayout()

        # Filter Layout
        filter_layout = QHBoxLayout()
        #filter_layout.addWidget(QLabel("Filter:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Type to filter...")
        self.filter_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_input)

        # Refresh Button with Icon
        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(QIcon("icons/refresh.svg"))  # Path to refresh icon
        self.refresh_button.setToolTip("Refresh Data")
        self.refresh_button.clicked.connect(self.load_data_GUI)
        filter_layout.addWidget(self.refresh_button)

        # Add Button with Icon
        self.add_button = QPushButton()
        self.add_button.setIcon(QIcon("icons/add.svg"))  # Path to add icon
        self.add_button.setToolTip("Add New Entry")
        self.add_button.clicked.connect(self.open_add_window)
        filter_layout.addWidget(self.add_button)
        main_layout.addLayout(filter_layout)

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
        self.model.clear()  # Clear existing data in the model
        """Load JSON data and populate the table dynamically."""
        data = load_db()

        # Determine headers dynamically
        headers = set()
        for brand, items in data.items():
            headers.add("Brand")  # Ensure "Brand" is always included because is the name of the collection
            for item in items:
                headers.update(item.keys())  # Add all keys from the JSON objects

        #headers = sorted(headers)  # Sort headers 
        self.model.setHorizontalHeaderLabels(headers)  # Set headers

        # Populate the table with data, make sure start loop again (data.items) to grab 1st Brand
        for brand, items in data.items():
            for item in items:
                row = []
                for header in headers:
                    if header == "Brand":
                        row.append(QStandardItem(brand))  # Add "Brand" from the outer key
                    else:
                        row.append(QStandardItem(item.get(header, "")))  # Add item data or an empty string
                self.model.appendRow(row)

    def apply_filter(self):
        """Apply filter based on user input."""
        filter_text = self.filter_input.text()
        self.proxy_model.setFilterString(filter_text)

    def open_add_window(self):
        """Open Add Window"""
        self.add_window = AddToDatabaseWindow()
        self.add_window.data_added.connect(self.load_data_GUI)  # Connect the signal        
        self.add_window.show()


if __name__ == "__main__":
    app = QApplication([])
    window = DataViewApp()
    window.show()
    app.exec_()
