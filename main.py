import sys
import pygame
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QPixmap
from PyQt5.QtCore import Qt, QRect
import json


class MenuWindow(QWidget):
    def __init__(self, start_callback, load_callback, background_path):
        super().__init__()
        self.start_callback = start_callback
        self.load_callback = load_callback

        self.setWindowTitle("Меню")
        self.setGeometry(100, 100, 1000, 600)  # Увеличенный размер окна

        # Фон меню
        self.background = QPixmap(background_path)

        layout = QVBoxLayout()

        # Добавляем пространство перед кнопками
        layout.addStretch()

        # Кнопка "Начать"
        self.start_button = QPushButton("Начать")
        self.start_button.setFixedSize(300, 60)
        self.start_button.clicked.connect(self.start_game)
        layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        # Кнопка "Загрузить параметры"
        self.load_button = QPushButton("Загрузить параметры")
        self.load_button.setFixedSize(300, 60)
        self.load_button.clicked.connect(self.load_and_start)
        layout.addWidget(self.load_button, alignment=Qt.AlignCenter)

        # Добавляем пространство после кнопок
        layout.addStretch()

        self.setLayout(layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.background.isNull():
            painter.drawPixmap(self.rect(), self.background)

    def start_game(self):
        self.start_callback()

    def load_and_start(self):
        self.load_callback()


class PianoApp(QMainWindow):
    def __init__(self, save_callback):
        super().__init__()
        self.setWindowTitle("Виртуальное пианино")
        self.setGeometry(100, 100, 1000, 600)

        self.volume = 0.5  # Громкость по умолчанию
        self.volume_step = 0.1  # Шаг изменения громкости
        self.save_callback = save_callback

        # Звуковые файлы
        self.white_sounds = [
            "1.wav", "2.wav", "3.wav", "4.wav", "5.wav", "6.wav", "7.wav", "8.wav",
            "222.wav", "333.wav", "444.wav", "555.wav", "666.wav", "777.wav", "888.wav"
        ]
        self.black_sounds = [
            "1#.wav", "2#.wav", None, "4#.wav", "5#.wav", "6#.wav", None,
            "111#.wav", "222#.wav", None, "444#.wav", "555#.wav", "666#.wav", None
        ]
        self.white_keys = [
            'Q', 'W', 'E', 'R', 'T', 'Y', 'U',
            'Z', 'X', 'C', 'V', 'B', 'N', 'M'
        ]
        self.black_keys = [
            '2', '3', None, '5', '6', '7', None,
            'S', 'D', None, 'G', 'H', 'J', None
        ]

        self.sounds = {}
        self.key_states = {}

        pygame.mixer.init()
        self.load_sounds()

        self.background = QPixmap("background.png")

        # Кнопка "Сохранить"
        self.save_button = QPushButton("Сохранить")
        self.save_button.setFixedSize(120, 40)
        self.save_button.move(10, 550)
        self.save_button.setParent(self)
        self.save_button.clicked.connect(self.save_volume)

        # Кнопка "Выход"
        self.exit_button = QPushButton("Выход")
        self.exit_button.setFixedSize(120, 40)
        self.exit_button.move(140, 550)  # Расположим кнопку рядом с кнопкой "Сохранить"
        self.exit_button.setParent(self)
        self.exit_button.clicked.connect(self.close_application)

    def load_sounds(self):
        for i, key in enumerate(self.white_keys):
            if i < len(self.white_sounds):
                sound = pygame.mixer.Sound(self.white_sounds[i])
                sound.set_volume(self.volume)
                self.sounds[key] = sound
                self.key_states[key] = False
        for i, key in enumerate(self.black_keys):
            if key and i < len(self.black_sounds) and self.black_sounds[i]:
                sound = pygame.mixer.Sound(self.black_sounds[i])
                sound.set_volume(self.volume)
                self.sounds[key] = sound
                self.key_states[key] = False

    def keyPressEvent(self, event):
        key = event.text().upper()
        if key in self.sounds and not self.key_states[key]:
            self.key_states[key] = True
            self.sounds[key].play()
            self.update()

        # Управление громкостью
        if key == '=':
            self.change_volume(self.volume_step)
        elif key == '-':
            self.change_volume(-self.volume_step)

    def keyReleaseEvent(self, event):
        key = event.text().upper()
        if key in self.key_states:
            self.key_states[key] = False
            self.update()

    def change_volume(self, step):
        self.volume = max(0.0, min(1.0, self.volume + step))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
        self.update()

    def save_volume(self):
        self.save_callback(self.volume)

    def close_application(self):
        QApplication.instance().quit()

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.background.isNull():
            painter.drawPixmap(self.rect(), self.background)

        # Рисуем подсказку по громкости
        painter.setFont(QFont("Arial", 12))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(10, 30, f"Громкость: {int(self.volume * 100)}% (Увеличить: '=', Уменьшить: '-')")


        # Рисуем белые клавиши
        x = 20
        for i, key in enumerate(self.white_keys):
            color = QColor(238, 203, 137) if self.key_states.get(key, False) else QColor(255, 255, 255)
            painter.setBrush(color)
            painter.setPen(QColor(0, 0, 0))  # Черная рамка для белых клавиш
            painter.drawRect(x, 250, 40, 150)

            # Изменим цвет текста (белый)
            painter.setPen(QColor(0, 0, 0))  # Белый цвет для текста
            painter.setFont(QFont('Arial', 10))
            painter.drawText(QRect(x, 320, 40, 50), Qt.AlignCenter, key)
            x += 50

        # Рисуем черные клавиши
        x = 50
        for i, key in enumerate(self.black_keys):
            if not key:
                x += 50
                continue
            color = QColor(238, 203, 137) if self.key_states.get(key, False) else QColor(0, 0, 0)
            painter.setBrush(color)
            painter.setPen(QColor(255, 255, 255) if self.key_states.get(key, False) else QColor(0, 0, 0))
            painter.drawRect(x, 250, 30, 100)

            # Белый цвет для текста на черных клавишах
            painter.setPen(QColor(255, 255, 255))  # Белый цвет для текста
            painter.setFont(QFont('Arial', 12))
            painter.drawText(QRect(x, 230, 30, 20), Qt.AlignCenter, key)
            x += 50



class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.piano = None

        # Загружаем меню
        self.menu = MenuWindow(self.start_piano, self.load_and_start_piano, "background.png")
        self.menu.show()

    def start_piano(self):
        if not self.piano:
            self.piano = PianoApp(self.save_settings)
        self.menu.close()
        self.piano.show()

    def load_and_start_piano(self):
        if not self.piano:
            self.piano = PianoApp(self.save_settings)
        self.load_settings()
        self.menu.close()
        self.piano.show()

    def load_settings(self):
        try:
            with open("settings.json", "r") as file:
                settings = json.load(file)
                volume = settings.get("volume", 0.5)
                if self.piano:
                    self.piano.volume = volume
        except FileNotFoundError:
            print("Файл настроек не найден.")

    def save_settings(self, volume):
        with open("settings.json", "w") as file:
            json.dump({"volume": volume}, file)
        print(f"Настройки сохранены: громкость {int(volume * 100)}%")

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    app = MainApp()
    app.run()
