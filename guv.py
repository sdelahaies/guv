#!/usr/bin/python3

import os
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QLineEdit,
    QMessageBox,
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton

import subprocess
import shutil
import datetime

from config import INSTALL_PATH


class MyUVGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyUV Manager")
        self.resize(900, 600)
        # self.env_list_path = Path.home() / ".myuv" / "env_list"
        self.env_list_path = Path(INSTALL_PATH) / "env_list"
        self.envs = self.load_envs()

        self.init_ui()

    def load_envs(self):
        """Load and return virtual environment paths from env_list."""
        if not self.env_list_path.exists():
            return []
        with open(self.env_list_path, "r") as f:
            return [line.strip() for line in f if line.strip()]

    def filter_env_list(self, query):
        query = query.strip().lower()

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            name = item.text().lower()
            path = str(item.data(Qt.UserRole)).lower()

            # Show only if query matches name or path
            item.setHidden(query not in name and query not in path)

    def read_env_list(self):
        envs = []
        # env_file = Path.home() / ".myuv" / "env_list"
        env_file = Path(INSTALL_PATH) / "env_list"
        if env_file.exists():
            with env_file.open("r") as f:
                for line in f:
                    path = Path(line.strip()).expanduser().resolve()
                    if path.exists():
                        envs.append(path)
        return envs

    def reload_env_list(self):
        # Run the find_venv.sh script
        try:
            # script_path = str(Path.home() / ".myuv" / "find_venv.sh")
            # script_path = str(f"{working_dir}/scripts/get_venv.sh")
            script_path = str(f"{INSTALL_PATH}/get_venv.sh")
            subprocess.run(["bash", script_path], check=True, cwd=INSTALL_PATH)
        except subprocess.CalledProcessError as e:
            print(f"Error running get_venv.sh: {e}")
            return

        # Clear current list and reload
        self.list_widget.clear()
        self.envs = self.read_env_list()
        for env_path in self.envs:
            self.add_env_item(env_path)
        pass

    def delete_env(self):
        item = self.list_widget.currentItem()
        if not item:
            return

        env_path = Path(item.data(Qt.UserRole))
        env_root = env_path.parent
        env_name = env_root.name

        # Optional: save env details to a backup text file
        backup_file = env_root / "venv.txt"
        with open(backup_file, "w") as f:
            f.write(self.details_area.toPlainText())

        # Confirmation dialog
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"You are about to delete the virtual environment for:\n\n{env_name}\n\nThis action cannot be undone.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                shutil.rmtree(env_path)
                print(f"Deleted: {env_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {e}")
                return

            # Remove from list widget
            self.list_widget.takeItem(self.list_widget.row(item))
            self.details_area.clear()

            # Update ~/.myuv/env_list
            self.envs = [p for p in self.envs if p != env_path]
            self.write_env_list()

    def write_env_list(self):
        env_file = Path(INSTALL_PATH) / "env_list"
        with env_file.open("w") as f:
            for env in self.envs:
                f.write(f"{env}\n")

    def init_ui(self):
        self.setWindowTitle("MyUV Environment Manager")
        self.setMinimumSize(800, 600)

        # Top toolbar layout
        toolbar = QHBoxLayout()
        self.shell_button = QPushButton("⬛ Open Shell in Env")
        self.shell_button.clicked.connect(self.open_shell_for_selected_env)
        self.delete_button = QPushButton("🗑️ Delete")
        self.delete_button.clicked.connect(self.delete_env)
        self.reload_button = QPushButton("🔄 Reload")
        self.reload_button.clicked.connect(self.reload_env_list)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search environments...")
        self.search_bar.textChanged.connect(self.filter_env_list)

        toolbar.addWidget(self.shell_button)
        # toolbar.addStretch()
        toolbar.addWidget(self.delete_button)
        toolbar.addWidget(self.reload_button)
        toolbar.addWidget(self.search_bar)

        # Left: List of envs
        self.list_widget = QListWidget()
        for env_path in self.envs:
            self.add_env_item(env_path)
        self.list_widget.currentItemChanged.connect(self.display_env_details)

        left_panel = QVBoxLayout()
        left_panel.addWidget(self.list_widget)
        left_container = QWidget()
        left_container.setLayout(left_panel)

        # Details area (right)
        self.details_area = QTextEdit()
        self.details_area.setReadOnly(True)

        right_panel = QVBoxLayout()
        right_panel.addWidget(self.details_area)
        right_container = QWidget()
        right_container.setLayout(right_panel)

        # Horizontal content area (list + details)
        content_layout = QHBoxLayout()
        content_layout.addWidget(left_container, 2)
        content_layout.addWidget(right_container, 5)

        # Final layout with toolbar on top
        main_layout = QVBoxLayout()
        main_layout.addLayout(toolbar)
        main_layout.addLayout(content_layout)

        # ✅ Set the layout on self
        self.setLayout(main_layout)

    def add_env_item(self, env_path):
        path_obj = Path(env_path)
        display_name = (
            path_obj.parent.name if path_obj.name == ".venv" else path_obj.name
        )
        relative_path = str(path_obj).replace(str(Path.home()), "~")

        # Create widget with name and relative path
        widget = QWidget()
        vbox = QVBoxLayout()
        vbox.setContentsMargins(10, 4, 10, 4)

        label_name = QLabel(display_name)
        label_name.setFont(QFont("Arial", 12, QFont.Bold))
        label_name.setStyleSheet("color: white;")

        label_path = QLabel(relative_path)
        label_path.setFont(QFont("Arial", 8))
        label_path.setStyleSheet("color: gray;")

        vbox.addWidget(label_name)
        vbox.addWidget(label_path)
        widget.setLayout(vbox)

        # Wrap in QListWidgetItem with proper size
        item = QListWidgetItem()
        item.setSizeHint(QSize(200, 50))  # Explicit size so it's visible
        item.setData(Qt.UserRole, env_path)

        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)

    def display_env_details(self, current, previous):
        if not current:
            return

        env_path = Path(current.data(Qt.UserRole))
        details = []

        # 1. Path
        details.append(f"📁 Path: {env_path}")

        # 2. Python version (use .venv/bin/python or Scripts/python.exe)
        python_bin = env_path / "bin" / "python"
        if not python_bin.exists():  # Windows fallback
            python_bin = env_path / "Scripts" / "python.exe"

        if python_bin.exists():
            try:
                version = subprocess.check_output(
                    [str(python_bin), "--version"], text=True
                ).strip()
                details.append(f"🐍 Python Version: {version}")
            except subprocess.SubprocessError:
                details.append("🐍 Python Version: <error fetching>")
        else:
            details.append("🐍 Python Version: <not found>")

        # 3. Creation date
        try:
            stat = env_path.stat()
            created = datetime.datetime.fromtimestamp(stat.st_ctime)
            details.append(f"📅 Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception:
            details.append("📅 Created: <unavailable>")

        # 4. Size on disk
        def get_size(path):
            total = 0
            for dirpath, _, filenames in os.walk(path):
                for f in filenames:
                    try:
                        fp = os.path.join(dirpath, f)
                        total += os.path.getsize(fp)
                    except Exception:
                        pass
            return total

        size_bytes = get_size(env_path)
        size_mb = size_bytes / (1024 * 1024)
        details.append(f"💾 Size: {size_mb:.2f} MB")
        details.append("")
        # 5. Installed packages (via source + uv pip list)
        try:
            command = f"cd '{env_path}' && source bin/activate && uv pip list"
            output = subprocess.check_output(["bash", "-c", command], text=True)
            packages = output.strip().splitlines()
            if packages:
                details.append("📦 Packages:")
                details.extend(f"   {line}" for line in packages)
            else:
                details.append("📦 Packages: <none>")
        except subprocess.SubprocessError as e:
            details.append(f"📦 Packages: <error fetching>\n{e}")

        self.details_area.setPlainText("\n".join(details))

    def open_shell_for_selected_env(self):
        item = self.list_widget.currentItem()
        if not item:
            return

        env_path = Path(item.data(Qt.UserRole))
        activate_path = env_path / "bin" / "activate"

        if not activate_path.exists():
            print("Activation script not found")
            return

        # Build command
        # bash_command = f"cd '{env_path}' && source bin/activate && exec bash"
        project_dir = env_path.parent
        bash_command = f"cd '{project_dir}' && exec bash --rcfile ~/.bashrc_uv"

        try:
            # GNOME Terminal (Linux)
            subprocess.Popen(
                ["gnome-terminal", "--tab", "--", "bash", "-c", bash_command]
            )
        except FileNotFoundError:
            print("gnome-terminal not found. Trying x-terminal-emulator...")
            try:
                subprocess.Popen(
                    ["x-terminal-emulator", "-e", f'bash -c "{bash_command}"']
                )
            except Exception as e:
                print(f"Terminal launch failed: {e}")

    def load_env_list(self):
        self.list_widget.clear()
        # env_file = Path.home() / ".myuv" / "env_list"
        env_file = Path(INSTALL_PATH) / "env_list"

        if not env_file.exists():
            return

        with env_file.open("r") as f:
            for line in f:
                path = Path(line.strip()).expanduser().resolve()
                if not path.exists():
                    continue  # skip broken entries

                # Display format
                project_name = path.parent.name  # folder containing .venv
                rel_path = str(path).replace(str(Path.home()), "~")

                # Create list item
                item = QListWidgetItem()
                item.setText(project_name)
                item.setData(Qt.UserRole, str(path))  # full .venv path for logic

                # Rich display: bold name + gray subpath
                item.setToolTip(rel_path)
                self.list_widget.addItem(item)


if __name__ == "__main__":
    import sys

    print("\033[1;38;5;11m        __  ___   __\033[0;0m")
    print("\033[1;38;5;11m  ___ _/ / / / | / /\033[0;0m")
    print("\033[1;38;5;11m / _ `/ /_/ /| |/ / \033[0;0m")
    print("\033[1;38;5;11m \_, /\____/ |___/  \033[0;0m")
    print("\033[1;38;5;11m/___/               \033[0;0m")
    print()

    print(
        "\033[96mrepository: \033[00m\033[1;38;5;11mhttps://github.com/sdelahaies/guv\033[0;0m"
    )
    print()
    print("\033[92mready... \033[0;0m")
    print()
    app = QApplication(sys.argv)
    window = MyUVGUI()
    window.show()
    sys.exit(app.exec())
