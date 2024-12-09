import subprocess

pyinstaller_command = [
    "pyinstaller",
    "--clean",
    "--onefile",
    "--noconsole",
    "--add-data", "assets;assets",
    "--add-data", "database;database",
    "--icon", "assets/icons/icon.ico",
    "show.py"
]
try:
    subprocess.run(pyinstaller_command, check=True)
    print("Build completed successfully!")
except subprocess.CalledProcessError as e:
    print(f"Build failed: {e}")