
# **Image Database Manager**

This project is a **PyQt5-based GUI application** that manages an image database by extracting data from a table, checking for folder paths based on specific patterns, and opening corresponding folders in the file explorer.

---

## **Features**
- Extracts data from json file.
- Dynamically create table with data.
- Dynamically constructs folder paths using:
  - **Space-separated format**: `Model Type`
  - **Underscore-separated format**: `Model_Type`
  - **Concatenated format**: `ModelType`
  - **Model only format**: `Model`
- Opens the correct folder if found.
- Displays detailed error messages.
- Customizable settings stored in `settings.json`.
- Responsive GUI with sorting, filtering, and data management.

---


1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## **Project Structure**
```
image-db-manager/
│
├── assets/                   # Icons and images for the UI
│   ├── icons/
│   └── image/
│
├── database/
│   └── local_database.json   # Database for storing records
│
├── model/                    # Data models and logic
│   └── json_logic.py         # Handles JSON-based logic
│
├── requirements.txt          # Project dependencies
├── settings.json             # Configuration file for folder locations
├── show.py                   # Main entry point for the application
├── show.spec                 # Spec file for building executables
└── helpers.py                # Utility functions
```

---

## **settings.json Example**
```json
{
  "Settings": {
    "Location": {
      "E:/Images": {}
    }
  }
}
```

---

## **Technologies Used**
- **Programming Language:** Python 3.8+
- **GUI Framework:** PyQt5
- **Libraries:** 
  - `os` - File system interaction
  - `json` - Settings management
  - `sys` - System-specific parameters

Sources:

[PyQt5](https://www.riverbankcomputing.com/static/Docs/PyQt5/) Reference for QTableView, QStandardItemModel, QMessageBox, and QWidget.

[Qt Documentation](https://doc.qt.io/) Reference for QTableView, QStandardItem, QColor, QFileDialog, etc.

[Python3](https://docs.python.org/3/library/)

[Real Python](https://realpython.com/)

[Python GUIs](https://www.pythonguis.com/)
## **License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
