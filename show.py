from PyQt5.QtWidgets import (
    QApplication, QTableView, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget, QHBoxLayout, QHeaderView
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QMouseEvent, QPalette, QBrush, QPixmap, QColor

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
        model = self.sourceModel()
        row_data = " ".join(
            model.data(model.index(source_row, col, source_parent)) or "" 
            for col in range(model.columnCount())
        ).lower()
        return all(word in row_data for word in self.filter_string.split())


class DataViewApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Images DB")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("assets/icons/icon.ico"))
        self.set_background_image(f"assets/image/background-{random.randint(1, 2)}.png")

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.create_top_bar())
        main_layout.addLayout(self.create_filter_bar())

        self.model = QStandardItemModel()
        self.proxy_model = CustomFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)

        self.table_view = QTableView()
        self.table_view.setModel(self.proxy_model)
        self.setup_table_view(self.table_view)
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

        self.delete_button = self.create_button("Del Sel", "red", self.delete_selected_entry)
        filter_layout.addWidget(self.delete_button)

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
        header = table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStretchLastSection(True)
        table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def load_data_GUI(self):
        self.model.clear()
        data = load_db()

        ordered_headers = ["Brand", "Model"] + list(
            {key for items in data.values() for item in items for key in item.keys()} - {"Brand", "Model"}
        )

        self.model.setHorizontalHeaderLabels(ordered_headers)
        for brand, items in data.items():
            for item in items:
                row = [
                    QStandardItem(str(item.get(header, ""))) if header != "Brand" else QStandardItem(brand)
                    for header in ordered_headers
                ]
                self.model.appendRow(row)

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
        self.add_window = AddToDatabaseWindow()
        self.add_window.data_added_signal.connect(self.load_data_GUI)
        self.add_window.show()

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


if __name__ == "__main__":
    app = QApplication([])
    window = DataViewApp()
    window.show()
    app.exec_()
