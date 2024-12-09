from PyQt5.QtWidgets import QMessageBox

from PyQt5.QtCore import Qt

class MessageBox:
    def __init__(self, parent=None):
        self.parent = parent

    def show(self, msg_type, title, message):
        """Display a message box based on the specified type."""
        print(f"DEBUG: Showing Message - Title: {title}, Message: {message}")
        
        msg_box = QMessageBox(self.parent)
        msg_box.setWindowTitle(title)
        msg_box.setInformativeText(str(message))  # Use this for detailed text
        
        # Customize message box based on the type
        if msg_type.lower() == "information":
            msg_box.setIcon(QMessageBox.Information)
        elif msg_type.lower() == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif msg_type.lower() == "critical":
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.NoIcon)

        msg_box.exec_()
    def confirm(self, title, message):
        """Ask the user for confirmation and return the response."""
        reply = QMessageBox.question(
            self.parent, title, message, QMessageBox.Yes | QMessageBox.No
        )
        return reply == QMessageBox.Yes

"""

# Initialize the message box class
self.message_box = MessageBox(self)

# Display different types of messages
self.message_box.show("information", "Success", "Data saved successfully!")
self.message_box.show("warning", "Warning", "Some fields are missing!")
self.message_box.show("critical", "Error", "Failed to save data!")


"""

def show_message(msg_type, title, message, parent=None):
    """Display a message box based on the specified type."""

    msg_box = QMessageBox(parent)
    msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
    msg_box.setWindowTitle(title)
    msg_box.setInformativeText(str(message))  # Use for detailed text

    # Customize message box based on the type
    if msg_type.lower() == "information":
        msg_box.setIcon(QMessageBox.Information)
    elif msg_type.lower() == "warning":
        msg_box.setIcon(QMessageBox.Warning)
    elif msg_type.lower() == "critical":
        msg_box.setIcon(QMessageBox.Critical)
    else:
        msg_box.setIcon(QMessageBox.NoIcon)

    msg_box.exec_()


def confirm_msg(title, message, parent=None):
    """Ask the user for confirmation and return the response."""
    reply = QMessageBox.question(
        parent, title, message, QMessageBox.Yes | QMessageBox.No
    )
    return reply == QMessageBox.Yes
