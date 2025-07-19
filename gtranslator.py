import sys
import json
import os
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QStandardPaths
from deep_translator import GoogleTranslator

config_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
config_dir = os.path.join(config_path, "G-Translator")
if not os.path.exists(config_dir):
    os.makedirs(config_dir)

SETTINGS_FILE = os.path.join(config_dir, "settings.json")

default_settings = {
    "font_family": "Arial",
    "font_size": 10,
    "target_lang": "en",
    "theme": "dark"
}

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        return default_settings.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

class LoadingScreen(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            background-color: #1e1e1e;
            color: white;
            border-radius: 10px;
        """)
        self.center()

        layout = QtWidgets.QVBoxLayout(self)

        self.title = QtWidgets.QLabel("G-Translator", self)
        self.title.setFont(QtGui.QFont("Arial", 24, QtGui.QFont.Weight.Bold))
        self.title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 10px;
                text-align: center;
                color: white;
                background-color: #2e2e2e;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.loading_label = QtWidgets.QLabel("Loading", self)
        self.loading_label.setFont(QtGui.QFont("Arial", 12))
        self.loading_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.loading_label)

        self.progress = 0
        self.dot_count = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(40)

    def update_progress(self):
        if self.progress >= 100:
            self.timer.stop()
            QtCore.QTimer.singleShot(2000, self.finish_loading)
        else:
            self.progress += 2
            self.progress_bar.setValue(self.progress)
            self.dot_count = (self.dot_count + 1) % 50
            dots = '...' * self.dot_count
            self.loading_label.setText(f"{dots}")

    def finish_loading(self):
        self.close()
        self.main_window.center()
        self.main_window.show()

    def center(self):
        screen = QtWidgets.QApplication.primaryScreen()
        screen_geo = screen.availableGeometry()
        x = (screen_geo.width() - self.width()) // 2
        y = (screen_geo.height() - self.height()) // 2
        self.move(x, y)

class SettingsWidget(QtWidgets.QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setFixedSize(500, 400)
        self.setAutoFillBackground(True)
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.title = QtWidgets.QLabel("Settings")
        self.title.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Weight.Bold))
        self.layout.addWidget(self.title, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.font_label = QtWidgets.QLabel("Yazı Fontu:")
        self.layout.addWidget(self.font_label)
        self.font_combo = QtWidgets.QFontComboBox()
        self.font_combo.setCurrentFont(QtGui.QFont(self.settings.get("font_family", "Arial")))
        self.font_combo.currentFontChanged.connect(self.font_changed)
        self.layout.addWidget(self.font_combo)

        self.size_label = QtWidgets.QLabel(f"Font Boyutu: {self.settings.get('font_size', 12)}")
        self.layout.addWidget(self.size_label)
        self.size_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(8)
        self.size_slider.setMaximum(30)
        self.size_slider.setValue(self.settings.get("font_size", 12))
        self.size_slider.valueChanged.connect(self.size_changed)
        self.layout.addWidget(self.size_slider)

        self.lang_label = QtWidgets.QLabel("Çeviri Dili:")
        self.layout.addWidget(self.lang_label)
        self.lang_combo = QtWidgets.QComboBox()
        languages = {
            "en": "İngilizce",
            "tr": "Türkçe",
            "de": "Almanca",
            "fr": "Fransızca",
            "es": "İspanyolca",
            "ru": "Rusça",
            "ja": "Japonca",
            "zh-cn": "Çince (Basitleştirilmiş)"
        }
        self.lang_combo.addItems([f"{code} - {name}" for code, name in languages.items()])
        try:
            current_index = list(languages.keys()).index(self.settings.get("target_lang", "en"))
        except ValueError:
            current_index = 0
        self.lang_combo.setCurrentIndex(current_index)
        self.lang_combo.currentIndexChanged.connect(self.lang_changed)
        self.layout.addWidget(self.lang_combo)

        self.theme_label = QtWidgets.QLabel("Tema Seçimi:")
        self.layout.addWidget(self.theme_label)
        self.theme_light = QtWidgets.QRadioButton("Aydınlık Mod")
        self.theme_dark = QtWidgets.QRadioButton("Karanlık Mod")
        self.layout.addWidget(self.theme_light)
        self.layout.addWidget(self.theme_dark)
        if self.settings.get("theme", "light") == "light":
            self.theme_light.setChecked(True)
        else:
            self.theme_dark.setChecked(True)
        self.theme_light.toggled.connect(self.theme_changed)
        self.theme_dark.toggled.connect(self.theme_changed)

        self.btn_close = QtWidgets.QPushButton("Kapat")
        self.btn_close.clicked.connect(self.close_clicked)
        self.layout.addWidget(self.btn_close)

        self.status_label = QtWidgets.QLabel("")
        self.status_label.setStyleSheet("color: green;")
        self.layout.addWidget(self.status_label)

    def apply_theme(self):
        if self.settings.get("theme", "light") == "light":
            palette = self.palette()
            palette.setColor(self.backgroundRole(), QtGui.QColor("#201F1F"))
            self.setPalette(palette)

            self.setStyleSheet("""
                QDialog, QWidget {
                    background-color: #121212;
                }
                QLabel { color: white; }
                QComboBox, QFontComboBox {
                    color: white;
                    background-color: #333;
                    border: 1px solid #555;
                    padding: 5px;
                }
                QComboBox QAbstractItemView {
                    background-color: #333;
                    color: white;
                    selection-background-color: #555;
                    selection-color: white;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #444;
                    height: 8px;
                    background: #222;
                    margin: 2px 0;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #4caf50;
                    border: 1px solid #5c5c5c;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 9px;
                }
                QRadioButton {
                    color: white;
                    background-color: transparent;
                }
                QPushButton {
                    color: white;
                    background-color: #333;
                    border: none;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #444;
                }
            """)
        else:
            palette = self.palette()
            palette.setColor(self.backgroundRole(), QtGui.QColor("#201F1F"))
            self.setPalette(palette)
            self.setStyleSheet("")

    def font_changed(self, font):
        self.settings["font_family"] = font.family()
        save_settings(self.settings)
        self.status_label.setText(f"Font '{font.family()}' Seçildi.")
        self.parent().apply_theme()
        self.parent().set_font_to_widget(self.parent().txt_input)
        self.parent().set_font_to_widget(self.parent().txt_output)

    def size_changed(self, val):
        self.settings["font_size"] = val
        self.size_label.setText(f"Font Boyutu: {val}")
        save_settings(self.settings)
        self.status_label.setText(f"Font Boyutu '{val}' Seçildi.")
        self.parent().apply_theme()
        self.parent().set_font_to_widget(self.parent().txt_input)
        self.parent().set_font_to_widget(self.parent().txt_output)

    def lang_changed(self, idx):
        code = self.lang_combo.currentText().split(" - ")[0]
        self.settings["target_lang"] = code
        save_settings(self.settings)
        self.status_label.setText(f"Dil '{self.lang_combo.currentText()}' Seçildi.")
        self.parent().lbl_language.setText(f"Hedef Dil: {code}")

    def theme_changed(self):
        if self.theme_light.isChecked():
            self.settings["theme"] = "light"
        elif self.theme_dark.isChecked():
            self.settings["theme"] = "dark"
        save_settings(self.settings)
        self.status_label.setText(f"Tema '{self.settings['theme']}' Seçildi.")
        self.parent().apply_theme()

    def close_clicked(self):
        self.close()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings = load_settings()

        self.setWindowTitle("G-Translator")
        self.setFixedSize(900,500)
        self.setWindowIcon(QtGui.QIcon("g-translator.ico"))  
        self.center()

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.top_bar = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.top_bar)

        self.lbl_logo = QtWidgets.QLabel("G-Translator")
        font_logo = QtGui.QFont("Arial", 9, QtGui.QFont.Weight.Light)
        self.lbl_logo.setFont(font_logo)
        self.lbl_logo.setStyleSheet("color: gray;")
        self.top_bar.addWidget(self.lbl_logo)

        self.top_bar.addStretch()

        self.btn_close = QtWidgets.QPushButton("X")
        self.btn_close.setFixedSize(70, 30)
        self.btn_close.clicked.connect(self.confirm_exit)
        self.top_bar.addWidget(self.btn_close)

        self.translate_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.translate_layout)

        self.txt_input = QtWidgets.QTextEdit()
        self.txt_input.setPlaceholderText("Çeviri yapılacak metni buraya yazınız...")
        self.set_font_to_widget(self.txt_input)
        self.translate_layout.addWidget(self.txt_input)

        self.txt_output = QtWidgets.QTextEdit()
        self.txt_output.setReadOnly(True)
        self.txt_output.setPlaceholderText("Çeviri sonucu burada görünecek...")
        self.set_font_to_widget(self.txt_output)
        self.translate_layout.addWidget(self.txt_output)

        self.status_label = QtWidgets.QLabel("")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.layout.addWidget(self.status_label)

        self.bottom_bar = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.bottom_bar)

        self.lbl_language = QtWidgets.QLabel(f"Hedef Dil: {self.settings.get('target_lang', 'en')}")
        self.bottom_bar.addWidget(self.lbl_language)

        self.btn_settings = QtWidgets.QPushButton("Ayarlar")
        self.btn_settings.clicked.connect(self.open_settings)
        self.bottom_bar.addWidget(self.btn_settings)

        self.settings_widget = None

        self.translate_timer = QtCore.QTimer()
        self.translate_timer.setSingleShot(True)
        self.translate_timer.timeout.connect(self.auto_translate)

        self.txt_input.textChanged.connect(self.on_text_changed)

        self.apply_theme()

    def center(self):
        screen = QtWidgets.QApplication.primaryScreen()
        screen_geo = screen.availableGeometry()
        x = (screen_geo.width() - self.width()) // 2
        y = (screen_geo.height() - self.height()) // 2
        self.move(x, y)

    def set_font_to_widget(self, widget):
        font = QtGui.QFont(self.settings.get("font_family", "Arial"), self.settings.get("font_size", 12))
        widget.setFont(font)

    def apply_theme(self):
        if self.settings.get("theme", "light") == "dark":
            self.setStyleSheet("""
                QMainWindow { background-color: #121212; color: white;}
                QTextEdit { background-color: #222; color: white; font-style: italic; }
                QPushButton { background-color: #333; color: white; border: none; padding: 5px; }
                QPushButton:hover { background-color: #444; }
                QLabel { color: white; }
            """)
            self.txt_input.setStyleSheet("background-color: #222; color: white; font-style: italic;")
            self.txt_output.setStyleSheet("background-color: #222; color: white; font-style: italic;")
            self.status_label.setStyleSheet("color: white; font-weight: bold;")
            self.lbl_language.setStyleSheet("color: white;")
            self.lbl_logo.setStyleSheet("color: lightgray;")  
        else:
            self.setStyleSheet("")
            self.txt_input.setStyleSheet("color: #555555; font-style: italic;")
            self.txt_output.setStyleSheet("color: #333333; font-style: italic;")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.lbl_language.setStyleSheet("color: black;")
            self.lbl_logo.setStyleSheet("color: gray;")

    def on_text_changed(self):
        self.status_label.setText("")
        self.translate_timer.start(2200)

    def auto_translate(self):
        text = self.txt_input.toPlainText().strip()
        if text == "":
            self.txt_output.clear()
            self.status_label.setText("")
            return

        self.status_label.setText("Çeviri yapılıyor...")
        QtWidgets.QApplication.processEvents()

        try:
            tgt_lang = self.settings.get("target_lang", "en")
            translated = GoogleTranslator(source='auto', target=tgt_lang).translate(text)
            self.txt_output.setPlainText(translated)
            self.status_label.setText("Çeviri tamamlandı.")
        except Exception as e:
            self.status_label.setText(f"Çeviri hatası: {e}")

    def open_settings(self):
        if self.settings_widget is None:
            self.settings_widget = SettingsWidget(self.settings, self)
        self.settings_widget.show()

    def confirm_exit(self):
        dialog = QtWidgets.QMessageBox(self)
        dialog.setWindowTitle("Çıkış Onayı")
        dialog.setText("Uygulamayı sonlandıracaksınız, onaylıyor musunuz?")
        dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.NoButton)  

        btn_kapat = dialog.addButton("Kapat", QtWidgets.QMessageBox.ButtonRole.YesRole)
        btn_vazgec = dialog.addButton("Vazgeç", QtWidgets.QMessageBox.ButtonRole.NoRole)
        dialog.setDefaultButton(btn_vazgec)

        dialog.setIcon(QtWidgets.QMessageBox.Icon.Question) 

        if self.settings.get("theme", "light") == "dark":
            dialog.setStyleSheet("""
                QMessageBox {
                    background-color: #121212;
                    color: white;
                }
                QPushButton {
                    background-color: #333;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    min-width: 70px;
                }
                QPushButton:hover {
                    background-color: #444;
                }
            """)

        dialog.exec()

        if dialog.clickedButton() == btn_kapat:
            QtWidgets.QApplication.quit()

def main():
    app = QtWidgets.QApplication(sys.argv)

    main_window = MainWindow()
    main_window.hide()

    loading_screen = LoadingScreen(main_window)
    loading_screen.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

# Bu kod Gexnys tarafından yazılmıştır.
# Tüm hakları Gexnys'e aittir.
# Eklenmesi gereken kodlar için lütfen Gexnys ile iletişime geçin.
# E-posta adresi : developergokhan@proton.me
