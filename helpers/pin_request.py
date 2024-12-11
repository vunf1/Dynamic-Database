import hashlib
import os
from cryptography.fernet import Fernet
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt


# File paths
PLAIN_PIN_FILE = os.path.join(os.getcwd(), "database/pin.txt")
SECURE_PIN_FILE = os.path.join(os.getcwd(), "database/secure_pin.bin")
HASH_FILE = os.path.join(os.getcwd(), "database/pin_hash.txt")


# Generate file hash for validation
def generate_file_hash(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


# Save the encrypted PIN securely and protect the file
def save_encrypted_pin():
    if not os.path.exists(PLAIN_PIN_FILE):
        raise FileNotFoundError("Application is misconfigured. Missing PIN file.")
    
    # Generate encryption key and encrypt the PIN
    key = Fernet.generate_key()
    fernet = Fernet(key)

    with open(PLAIN_PIN_FILE, "r") as file:
        plain_pin = file.read().strip()

    encrypted_pin = fernet.encrypt(plain_pin.encode())

    # Save the encrypted PIN and key
    with open(SECURE_PIN_FILE, "wb") as pin_file:
        pin_file.write(key + b"\n" + encrypted_pin)

    # Generate and save the file hash
    file_hash = generate_file_hash(SECURE_PIN_FILE)
    with open(HASH_FILE, "w") as hash_file:
        hash_file.write(file_hash)

    # Make the file read-only
    os.chmod(SECURE_PIN_FILE, 0o400)  # Read-only for owner
    os.system(f"attrib +R {SECURE_PIN_FILE}") # Read-only for owner
    os.chmod(HASH_FILE, 0o400) # Read-only for owner
    os.system(f"attrib +R {HASH_FILE}") # Read-only for owner
    # Delete the plaintext PIN file
    os.remove(PLAIN_PIN_FILE)


# Load the encrypted PIN and check for tampering
def load_encrypted_pin():
    if not os.path.exists(SECURE_PIN_FILE):
        save_encrypted_pin()

    # Validate file integrity
    expected_hash = open(HASH_FILE, "r").read().strip()
    current_hash = generate_file_hash(SECURE_PIN_FILE)

    if current_hash != expected_hash:
        raise PermissionError("PIN file tampering detected!")

    # Load encrypted PIN
    with open(SECURE_PIN_FILE, "rb") as pin_file:
        key, encrypted_pin = pin_file.read().split(b"\n", 1)
        fernet = Fernet(key)
        return fernet, encrypted_pin


class PinDialog(QDialog):
    # Load and store the encrypted PIN in memory (one-time initialization)
    FERNET, ENCRYPTED_PIN = load_encrypted_pin()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter PIN")
        self.setFixedSize(200, 75)
        self.setWindowIcon(QIcon("assets/icons/lock.svg"))
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)  # Always on top
        
        # Layout
        layout = QVBoxLayout()        
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(0)  # Remove spacing between widgets

        # Label for feedback
        self.label = QLabel("")
        font = QFont("Arial")
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)  # Attach to top-center
        self.label.setStyleSheet("font-size: 15px; font-weight: bold; color: darkred;")        
        layout.addWidget(self.label, alignment=Qt.AlignHCenter)
        
        # PIN input field
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.Password)
        self.pin_input.setFixedHeight(50)  # Larger input field
        self.pin_input.setStyleSheet("font-size: 40px; padding: 0px; margin: 0px;")
        '''
        Not able to hide blinking cursor......
        '''
        self.pin_input.returnPressed.connect(self.check_pin)  # Trigger validation on Enter
        layout.addWidget(self.pin_input, alignment=Qt.AlignHCenter)
        
        self.setLayout(layout)
    
    def check_pin(self):
        # Decrypt the encrypted PIN and compare
        decrypted_pin = self.FERNET.decrypt(self.ENCRYPTED_PIN).decode()
        if self.pin_input.text() == decrypted_pin:
            print("Success")
            self.accept()  # Close dialog on success
        else:
            self.label.setText("INCORRECT PIN.")  # Display error message


'''
Debug

if __name__ == "__main__":    
    app = QApplication([])
    window = PinDialog()
    window.show()
    app.exec_()


'''