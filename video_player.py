import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QFileDialog, QWidget, QDockWidget
from PyQt5.QtCore import Qt

import subprocess
import os  # Import the os module for path manipulation

class ControlPanel(QWidget):
    def __init__(self, video_player):
        super().__init__()
        self.video_player = video_player
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        play_button = QPushButton('Play Video')
        play_button.clicked.connect(self.video_player.playVideo)
        layout.addWidget(play_button)

        vsf_button = QPushButton('Start Jack VSF')
        vsf_button.clicked.connect(self.video_player.startVSF)
        layout.addWidget(vsf_button)

        self.setLayout(layout)

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.playlist = []
        self.current_video = 0

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.add_button = QPushButton('Add Video File(s)')
        self.add_button.clicked.connect(self.addVideo)
        self.layout.addWidget(self.add_button)

        self.clear_button = QPushButton('Clear Playlist')
        self.clear_button.clicked.connect(self.clearPlaylist)
        self.layout.addWidget(self.clear_button)

        self.setLayout(self.layout)

    def addVideo(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_names, _ = QFileDialog.getOpenFileNames(self, "Select Video File(s)", "", "Video Files (*.mkv *.mp4);;All Files (*)", options=options)
        self.playlist.extend(file_names)

    def playVideo(self):
        if self.current_video < len(self.playlist):
            video_file = self.playlist[self.current_video]
            subprocess.run(['mpv', '--ao=jack', '--vo=gpu', '--gpu-context=x11egl', '--gpu-api=opengl', video_file])
            self.current_video += 1

    def clearPlaylist(self):
        self.playlist = []
        self.current_video = 0

    def startVSF(self):
        vsf_executable_path = os.path.join(os.path.dirname(__file__), 'vsf', 'jack-vsf')  # Use the relative path
        hrir_file_path = os.path.join(os.path.dirname(__file__), 'vsf', 'hrir_kemar', 'hrir-kemar-48000.wav')  # Use the relative path
        subprocess.run([vsf_executable_path, hrir_file_path])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    video_player = VideoPlayer()
    control_panel = ControlPanel(video_player)
    
    main_window = QMainWindow()
    main_window.setCentralWidget(video_player)

    # Add a dock widget for the control panel
    dock_widget = QDockWidget()
    dock_widget.setWidget(control_panel)
    main_window.addDockWidget(Qt.RightDockWidgetArea, dock_widget)

    main_window.setWindowTitle('PyQt Video Player')
    main_window.setGeometry(100, 100, 400, 200)
    main_window.show()
    
    sys.exit(app.exec_())
