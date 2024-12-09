import os
from PyQt5.QtWidgets import (
    QApplication, QTableView, QVBoxLayout, QLineEdit, QPushButton, QWidget, QHBoxLayout, QHeaderView
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QPoint
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QMouseEvent, QPalette, QBrush, QPixmap, QColor

from helpers.helpers import confirm_msg, show_message
from model.json_logic import load_db, save_db, load_settings_data
from plus import AddToDatabaseWindow
import random


class CustomFilterProxyModel(QSortFilterProxyModel):
    """Custom filter model class inheriting from QSortFilterProxyModel"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_position = QPoint()
        self.filter_string = ""

    def setFilterString(self, text):
        self.filter_string = text.lower()
        self.invalidateFilter()
 
    def filterAcceptsRow(self, source_row, source_parent):
        """Method to check if a row meets the filter criteria"""
        # Access the source model
        model = self.sourceModel()        
        # Concatenate all column data from the row into a single lowercase string
        row_data = " ".join(
            model.data(model.index(source_row, col, source_parent)) or "" 
            for col in range(model.columnCount())
        ).lower()
        # Check if all words/letters from the filter string are present in the row data
        return all(word in row_data for word in self.filter_string.split())

class DataViewApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("Images DB")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("assets/icons/icon.ico"))
        self.set_background_image(f"assets/image/background-{random.randint(1, 3)}.png")

        main_layout = QVBoxLayout()
        # main_layout.addLayout(self.create_top_bar())
        main_layout.addLayout(self.create_filter_bar())

        self.model = QStandardItemModel()
        self.proxy_model = CustomFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)

        self.table_view = QTableView()
        self.table_view.setModel(self.proxy_model)
        self.setup_table_view(self.table_view)
        # Connect cell click signal
        self.table_view.doubleClicked.connect(self.cell_double_clicked)

        main_layout.addWidget(self.table_view)

        self.setLayout(main_layout)
        self.load_data_GUI()

    def create_top_bar(self):
        top_bar_layout = QHBoxLayout()
        self.close_button = self.create_button("X", "red", self.close, fixed_size=(20, 20))
        top_bar_layout.addWidget(self.close_button, alignment=Qt.AlignRight)
        return top_bar_layout

    def create_filter_bar(self):
        filter_layout = QHBoxLayout()

        self.delete_button = self.create_icon_button("delete.svg", "Select Row to Delete", self.delete_selected_entry)
        filter_layout.addWidget(self.delete_button)

        self.edit_button = self.create_icon_button("edit.svg", "Select Row to Edit", self.edit_selected_entry)
        filter_layout.addWidget(self.edit_button)

        self.refresh_button = self.create_icon_button("refresh.svg", "Refresh Data", self.load_data_GUI)
        filter_layout.addWidget(self.refresh_button)

        self.add_button = self.create_icon_button("add.svg", "Add New Entry", self.open_add_window)
        filter_layout.addWidget(self.add_button)

        self.filter_input = QLineEdit(placeholderText="Type to filter...")
        self.filter_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_input)

        return filter_layout

    def setup_table_view(self, table_view):
        table_view.setSortingEnabled(True)
        table_view.verticalHeader().setVisible(False)
        table_view.setStyleSheet("""
            QTableView {
                background-color: rgba(255, 255, 255, 180);  /* Light background */
                alternate-background-color: rgba(173, 216, 230, 150); /* LightBlue */
                selection-background-color: rgba(65, 105, 225, 220); /* RoyalBlue */
                selection-color: white;
                gridline-color: lightgray;
                font-size: 14px;
                font-weight: bold;
                border-radius: 15px;  /* Fully rounded corners for the entire table */
                border: 1px solid lightgray;
            }

            QHeaderView::section {
                background-color: rgba(65, 105, 225, 180);  /* RoyalBlue with transparency */
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
                border: 1px solid lightgray;
                text-align: center;  /* Center header text */
                border-top-left-radius: 15px;  /* Rounded top corners */
                border-top-right-radius: 15px;
            }

            QTableView::item:selected {
                background-color: rgba(173, 216, 230, 150);  /* Selection color */
                color: white;
                border-radius: 5px;  /* Slightly rounded selection */
            }

            QTableView QScrollBar:horizontal, QTableView QScrollBar:vertical {
                background: rgba(245, 245, 245, 180); /* Light background for scrollbars */
                border-radius: 5px;
            }

            QTableCornerButton::section {
                background-color: rgba(65, 105, 225, 180);  /* Corner header */
                border: 1px solid lightgray;
                border-top-left-radius: 15px;  /* Match table rounding */
            }
        """)
        header = table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStretchLastSection(True)
        table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def load_data_GUI(self):
        self.model.clear()
        data = load_db()
        # Define the priority headers
        priority_headers = ["Brand", "Model", "Type"]

        # Collect all unique keys from the data, excluding the priority headers
        additional_headers = sorted(
            {key for items in data.values() for item in items for key in item.keys()} - set(priority_headers)
        )

        # Combine priority headers with additional headers
        ordered_headers = priority_headers + additional_headers

        self.model.setHorizontalHeaderLabels(ordered_headers)
        # Populate rows in the model
        for brand, items in data.items():
            for item in items:
                row = []
                for header in ordered_headers:
                    value = str(item.get(header, brand if header == "Brand" else ""))
                    # Create a QStandardItem for each cell, better for custom profiles
                    item_cell = QStandardItem(value)
                    item_cell.setTextAlignment(Qt.AlignCenter)
                    # Make cells non-editable
                    item_cell.setFlags(item_cell.flags() & ~Qt.ItemIsEditable)
                    # Apply conditional formatting for the 'Image' column
                    if header == "Image":
                        if value == "Done":
                            item_cell.setBackground(QColor("#5f8244"))
                        else:
                            item_cell.setBackground(QColor("#bd4613"))
                    row.append(item_cell)
                self.model.appendRow(row)


    def edit_selected_entry(self):
        """
        Opens AddToDatabaseWindow populated with the selected row's values.
        """
        selected_index = self.table_view.currentIndex()
        if not selected_index.isValid():
            show_message("warning", "No Selection", "Please select an entry to edit.")
            return

        # Close the previous window if it exists
        if hasattr(self, "edit_window") and self.edit_window is not None:
            self.edit_window.close()
            """
            self.edit_window.deleteLater() is a method in PyQt5 that schedules the deletion 
            of the edit_window object when control returns to the event loop. 
            This is useful because deleting a QWidget immediately 
            while it’s still being used can cause crashes or undefined behavior.
            """
            self.edit_window.deleteLater()

        # Extract row data
        row_index = selected_index.row()
        headers = [self.model.headerData(col, Qt.Horizontal) for col in range(self.model.columnCount())]
        item_data = {
            header: self.model.item(row_index, col).text()
            for col, header in enumerate(headers)
        }

        # Create a new instance of AddToDatabaseWindow and populate fields
        self.edit_window = AddToDatabaseWindow()
        self.edit_window.brand_combobox.setCurrentText(item_data.get("Brand", ""))
        self.edit_window.model_entry.setText(item_data.get("Model", ""))
        self.edit_window.type_combobox.setCurrentText(item_data.get("Type", ""))
        self.edit_window.windows_version_combobox.setCurrentText(item_data.get("Windows Version", ""))
        self.edit_window.image_combobox.setCurrentText(item_data.get("Image", ""))
        
        # Refresh data and close window after successful edit
        self.edit_window.data_added_signal.connect(self.load_data_GUI)
        self.edit_window.data_added_signal.connect(self.edit_window.close)

        # Connect the signal to refresh data after editing
        self.edit_window.data_added_signal.connect(self.load_data_GUI)

        # Show the edit window
        self.edit_window.show()

    def delete_selected_entry(self):
        selected_index = self.table_view.currentIndex()
        if not selected_index.isValid():
            show_message("warning", "No Selection", "Please select an entry to delete.")
            return

        row_index = selected_index.row()
        brand = self.model.item(row_index, 0).text()
        headers = [self.model.headerData(col, Qt.Horizontal) for col in range(self.model.columnCount())]

        item_data = {
            header: self.model.item(row_index, col).text() 
            for col, header in enumerate(headers) 
            if header != "Brand"
        }

        formatted_data = "\n".join(f"{key}: {value}" for key, value in item_data.items())

        if not confirm_msg(
            "Delete Entry", f"Are you sure you want to delete this entry?\n\nBrand: {brand}\n\n{formatted_data}", parent=self
        ):
            return

        data = load_db()
        if brand in data:
            data[brand] = [entry for entry in data[brand] if not all(str(entry.get(k, "")) == v for k, v in item_data.items())]
            if not data[brand]:
                del data[brand]

        save_db(data)
        self.load_data_GUI()
        show_message("information", "Success", "Entry deleted successfully!")

    def apply_filter(self):
        self.proxy_model.setFilterString(self.filter_input.text())

    def open_add_window(self):
        if not hasattr(self, 'add_window') or self.add_window is None: # Allow just one instance 
            self.add_window = AddToDatabaseWindow()
            self.add_window.setAttribute(Qt.WA_DeleteOnClose)  # Ensure window is deleted on close
            self.add_window.data_added_signal.connect(self.load_data_GUI)
            self.add_window.show()
            self.add_window.destroyed.connect(self.clear_add_window_instance) # Clear instance when window is closed
        else:
            self.add_window.raise_() # Bring the existing window to the front
            self.add_window.activateWindow()

    def clear_add_window_instance(self):
        """Clear the instance of add_window when it is closed."""
        self.add_window = None

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

    def create_button(self, text, color, action, fixed_size=None):
        button = QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: dark{color};
            }}
        """)
        if fixed_size:
            button.setFixedSize(*fixed_size)
        button.clicked.connect(action)
        return button

    def create_icon_button(self, icon_path, tooltip, action):
        button = QPushButton()
        button.setIcon(QIcon(f"assets/icons/{icon_path}"))
        button.setToolTip(tooltip)
        button.clicked.connect(action)
        return button
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def cell_double_clicked(self, index):
        """
        Handles double-click events in the table view.
        Extracts location, model, and type, and opens the corresponding folder.
        """
        if not index.isValid():
            return

        # Get source index from proxy model
        source_index = self.proxy_model.mapToSource(index)

        # Extract row data
        row_data = {
            self.model.headerData(col, Qt.Horizontal): self.model.item(source_index.row(), col).text().strip()
            for col in range(self.model.columnCount())
        }

        # Validate required fields
        brand, model, device_type = row_data.get("Brand"), row_data.get("Model"), row_data.get("Type")
        if not all([brand, model, device_type]):
            show_message("warning", "Error", "Brand, Model, or Type is missing.")
            return

        # Load main location from settings
        location = list(load_settings_data()["Settings"]["Location"].keys())[0]

        folder_patterns = [
            # Brand and model with device type
            f"{brand} {model} {device_type}",   # Space-separated
            f"{brand}_{model}_{device_type}",   # Underscore-separated
            f"{brand}{model}{device_type}",     # Concatenated
            f"{brand} {model}_{device_type}",   # Model and device type, underscore-separated
            f"{brand}_{model} {device_type}",   # Brand and model underscore-separated, device type space-separated

            # Brand and model only
            f"{brand} {model}",                 # Space-separated
            f"{brand}_{model}",                 # Underscore-separated
            f"{brand}{model}",                  # Concatenated

            # Brand and model with prefixed device type
            f"{brand} {model} {device_type}",   # Space-separated
            f"{brand}_{model}_{device_type}",   # Underscore-separated
            f"{brand}{model}{device_type}",     # Concatenated

            # Prefixed with hash (#)
            f"#{brand} {model} {device_type}",  # #Brand, space-separated
            f"#{brand}_{model}_{device_type}",  # #Brand, underscore-separated
            f"#{brand}{model}{device_type}",    # #Brand concatenated
            f"#{brand} {model}",                # #Brand and model, space-separated
            f"#{brand}_{model}",                # #Brand and model, underscore-separated
            f"#{brand}{model}",                 # #Brand and model concatenated
            
            # Brand and model, prefixed with model and device type
            f"{model} {device_type}",           # Model and device type, space-separated
            f"{model}_{device_type}",           # Model and device type, underscore-separated
            f"{model}{device_type}",            # Model and device type concatenated
            f"{model}",                         # Model only
            f"#{model} {device_type}",          # #Model and device type, space-separated
            f"#{model}_{device_type}",          # #Model and device type, underscore-separated
            f"#{model}{device_type}",           # #Model and device type concatenated
            f"#{model}"                         # #Model only
        ]
        # Open the first existing folder or show an error
        # Search for the first matching folder
        for pattern in folder_patterns:
            folder_path = os.path.join(location, brand, pattern)
            if os.path.isdir(folder_path):
                os.startfile(folder_path)
                return

        # Show error if no folder exists
        show_message(
            "warning", 
            "Folder Not Found", 
            f"No folder found at:\n" + "\n".join(f"'{path}'" for path in folder_patterns)
        )
if __name__ == "__main__":
    app = QApplication([])
    window = DataViewApp()
    window.show()
    app.exec_()
