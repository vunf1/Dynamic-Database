import os
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon



def show_message(msg_type, title, message, parent=None):
    """Display a message box based on the specified type with error handling."""
    try:
        if not title or not message:
            raise ValueError("Both title and message must be provided and cannot be empty.")
        
        print(f"DEBUG: Showing Message - Title: {title}, Message: {message}")
        
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(str(message))  # Use setText for the main message content

        # Customize message box based on the type
        if msg_type.lower() == "information":
            body_icon = QMessageBox.Information
            border_icon = os.path.join(os.getcwd(), "assets/icons/information.svg")
        elif msg_type.lower() == "warning":
            body_icon = QMessageBox.Warning
            border_icon = os.path.join(os.getcwd(), "assets/icons/warning.svg")
        elif msg_type.lower() == "critical":
            body_icon = QMessageBox.Critical
            border_icon = os.path.join(os.getcwd(), "assets/icons/critical.svg")
        else:
            body_icon = QMessageBox.NoIcon
            border_icon = os.path.join(os.getcwd(), "assets/icons/default.svg")
        
        # Set the message box icon
        msg_box.setIcon(body_icon)

        # Attempt to set a custom window icon
        if os.path.exists(border_icon):
            msg_box.setWindowIcon(QIcon(border_icon))
        else:
            print(f"WARNING: Icon file not found at {border_icon}. Using default icon.")
        
        print(f"DEBUG: Displaying Message - Title: {title}, Message: {message}")
        msg_box.exec_()
    except ValueError as ve:
        print(f"ERROR: {ve}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred in 'show_message' function: {e}")


def confirm_message(title, message, parent=None):
    """
    Ask the user for confirmation and return the response with error handling.
    """
    try:
        if not title or not message:
            raise ValueError("Both title and message must be provided and cannot be empty.")
        
        print(f"DEBUG: Asking for Confirmation - Title: {title}, Message: {message}")
        
        # Create a QMessageBox instance
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(str(message))  # Set the message text
        
        # Set the QMessageBox buttons
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # Find the standard buttons and style them
        yes_button = msg_box.button(QMessageBox.Yes)
        no_button = msg_box.button(QMessageBox.No)

        # Apply styles
        yes_button.setStyleSheet("""
            QPushButton {
                min-width: 50px;
                min-height: 20px;
                font-size: 14px;
                color: white;
                background-color: #4CAF50;  /* Green */
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #388E3C;  /* Dark Green */
            }
        """)

        no_button.setStyleSheet("""
            QPushButton {
                min-width: 50px;
                min-height: 20px;
                font-size: 14px;
                color: white;
                background-color: #F44336;  /* Red */
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #D32F2F;  /* Dark Red */
            }
        """)

        # Set the QMessageBox icon
        icon_path = os.path.join(os.getcwd(), "assets/icons/question.svg")
        if os.path.exists(icon_path):
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setWindowIcon(QIcon(icon_path))
        else:
            print(f"WARNING: Icon file not found at {icon_path}. Using default icon.")

        # Display the message box and get the user's response
        reply = msg_box.exec_()
        return reply == QMessageBox.Yes
    except ValueError as ve:
        print(f"ERROR: {ve}")
        return False
    except Exception as e:
        print(f"ERROR: An unexpected error occurred in 'confirm_message' function: {e}")
        return False