import os
import sys
import subprocess
import multiprocessing
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QPushButton,
                             QFileDialog, QWidget, QDockWidget, QLabel, QSlider, QMessageBox)
from PyQt5.QtCore import Qt

def setPipeWireBuffer(buffer_size):
    subprocess.run(['pw-metadata', '-n', 'settings', '0', f'clock.force-quantum', str(buffer_size)])

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

        pause_button = QPushButton('Pause/Resume Video')
        pause_button.clicked.connect(self.video_player.pauseResumeVideo)
        layout.addWidget(pause_button)

        vsf_button = QPushButton('Start Jack VSF')
        vsf_button.clicked.connect(self.video_player.startVSF)
        layout.addWidget(vsf_button)

        self.setLayout(layout)

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.playlist = []
        self.current_video = 0
        self.mpv_process = None

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.add_button = QPushButton('Add Video File(s)')
        self.add_button.clicked.connect(self.addVideo)
        self.layout.addWidget(self.add_button)

        self.clear_button = QPushButton('Clear Playlist')
        self.clear_button.clicked.connect(self.clearPlaylist)
        self.layout.addWidget(self.clear_button)

        self.volume_label = QLabel('Volume:')
        self.layout.addWidget(self.volume_label)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)  # Default volume
        self.volume_slider.valueChanged.connect(self.changeVolume)
        self.layout.addWidget(self.volume_slider)

        self.setLayout(self.layout)

    def addVideo(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_names, _ = QFileDialog.getOpenFileNames(self, "Select Video File(s)", "", "Video Files (*.mkv *.mp4);;All Files (*)", options=options)
        self.playlist.extend(file_names)


    def pauseResumeVideo(self):
        if self.mpv_process and self.mpv_process.poll() is None:
            self.mpv_process.send_signal(subprocess.signal.SIGSTOP)
        else:
            QMessageBox.warning(self, "Playback Error", "No video is currently playing.")

    def changeVolume(self, value):
        # Implement volume change functionality here
        pass

    def playVideo(self):
        if self.current_video < len(self.playlist):
            video_file = self.playlist[self.current_video]
            self.setPipeWireBuffer(512)  # Example buffer size, adjust as needed
            self.mpv_process = subprocess.Popen(['mpv', '--ao=jack', '--vo=gpu', '--gpu-context=x11egl', '--gpu-api=opengl', video_file])
            self.current_video += 1

    def clearPlaylist(self):
        self.playlist = []
        self.current_video = 0

    def setPipeWireBuffer(self, buffer_size):
        subprocess.run(['pw-metadata', '-n', 'settings', '0', f'clock.force-quantum', str(buffer_size)])

    def startVSF(self):
        vsf_process = multiprocessing.Process(target=self.runVSF)
        vsf_process.start()

    def runVSF(self):
        vsf_executable_path = os.path.join(os.path.dirname(__file__), 'vsf', 'jack-vsf')
        hrir_file_path = os.path.join(os.path.dirname(__file__), 'vsf', 'hrir_kemar', 'hrir-kemar-48000.wav')
        subprocess.run([vsf_executable_path, hrir_file_path])


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = QMainWindow()
    main_window.setWindowTitle('PyQt Video Player')
    main_window.setGeometry(100, 100, 600, 300)

    video_player = VideoPlayer()
    main_window.setCentralWidget(video_player)

    control_panel = ControlPanel(video_player)
    dock_widget = QDockWidget()
    dock_widget.setWidget(control_panel)
    main_window.addDockWidget(Qt.RightDockWidgetArea, dock_widget)

    main_window.show()
    sys.exit(app.exec_())
