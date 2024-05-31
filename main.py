from kivy.app import App
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.utils import platform
from kivy.properties import ListProperty
from plyer import filechooser
import os
import sys
import subprocess
import re
#IMPORTING jnius
from jnius import autoclass
from jnius import * 
#Declaring Variable so it can be used
FFMPEG = autoclass('com.sahib.pyff.ffpy')

# python3 -m PyInstaller --hidden-import=kivy --hidden-import=plyer.platforms.macosx.filechooser --hidden-import=pyobjus --hidden-import=subprocess main.py

if platform == "android":
    from android.permissions import request_permissions, Permission, check_permission  # pylint: disable=import-error # type: ignore
    request_permissions([Permission.READ_EXTERNAL_STORAGE,
                        Permission.WRITE_EXTERNAL_STORAGE])

# widgets
class ImageBtn(ButtonBehavior, Image):

    def convert_video_on_win(self, input_file, output_file, subs_track_number=0):
        print("FFMPEG started...")
        print(f"Input file ... {input_file}")
        print(f"Output file ... {output_file}")

        performance_setting = App.get_running_app().performance_setting
        audio_track = App.get_running_app().audio_track
        final_audio_track = int(audio_track[-1])

        script_path = os.path.realpath(sys.argv[0])
        directory_path = os.path.dirname(script_path)
        quoted_input_file = f'"{input_file}"'
        
        print(quoted_input_file)
        ffmpegCommand = FFMPEG.Run("ffmpeg")
        print(ffmpegCommand)

        # try:
        #     subprocess.run("ffmpeg", check=True, shell=True)
        #     print(f"Sucessfully converted! New file: {output_file}")
        # except subprocess.CalledProcessError as e:
        #     print("Conversion failed")

        # try:
        #     stream = ffmpeg.input(quoted_input_file)
        #     stream = ffmpeg.output(stream, 'output.mp4')
        #     ffmpeg.run(stream)
        # except subprocess.CalledProcessError as e:
        #     print("Conversion failed")
            

        systype = ["win", "macosx", "linux"]

        if performance_setting == "BEST QUALITY":
            ffmpeg_command = f"{directory_path}/ffmpeg/{systype[0]}/ffmpeg -y -i {quoted_input_file} -vcodec libx264 -preset veryfast -pix_fmt yuv420p -acodec aac -movflags +faststart -map 0:v:0 -map 0:a:{final_audio_track - 1} {output_file}"
        if performance_setting == "BALANCED":
            ffmpeg_command = f"{directory_path}/ffmpeg/{systype[0]}/ffmpeg -y -i {quoted_input_file} -vcodec libx264 -preset superfast -pix_fmt yuv420p -acodec aac -movflags +faststart -map 0:v:0 -map 0:a:{final_audio_track - 1} -vf scale=1280:720 {output_file}"
        if performance_setting == "BEST PERFORMANCE":
            ffmpeg_command = f"{directory_path}/ffmpeg/{systype[0]}/ffmpeg -y -i {quoted_input_file} -vcodec libx264 -preset ultrafast -pix_fmt yuv420p -acodec aac -movflags +faststart -map 0:v:0 -map 0:a:{final_audio_track - 1} -vf scale=960:540 {output_file}"
        if performance_setting == "AUDIO":
            ffmpeg_command = f"{directory_path}/ffmpeg/{systype[0]}/ffmpeg -y -i {quoted_input_file} -vcodec copy -pix_fmt yuv420p -acodec aac -movflags +faststart -map 0:v:0 -map 0:a:{final_audio_track - 1} {output_file}"
        if performance_setting == "SUBTITLES":
            ffmpeg_command = f"{directory_path}/ffmpeg/{systype[0]}/ffmpeg -y -i {quoted_input_file} -map 0:{subs_track_number} subs{subs_track_number}.srt"

        try:
            subprocess.run(ffmpeg_command, check=True, shell=True)
            print(f"Sucessfully converted! New file: {output_file}")
        except subprocess.CalledProcessError as e:
            print("Conversion failed")

    def convert_file(self):
        performance_setting = App.get_running_app().performance_setting

        print("Conversion started...!")
        if performance_setting == "SUBTITLES":
            for i in range(50):
                self.convert_video_on_win(FileTextInput.Instance.text, "subs_{i}.srt", subs_track_number=i)
        else:
            self.convert_video_on_win(FileTextInput.Instance.text, "converted_video.mp4")

    def load_file(self):
        filters = [
            ('Video Files', '*.mp4', '*.flv', '*.avi', '*.mkv', '*.webm', '*.mov', '*.wmv', '*.m4v', '*.f4v', '*.vob', '*.ogg', '*.qt', '*.mxf', '*.roq', '*.nsv', '*.3g2', '*.m2ts', '*.mts', '*.ts', '*.m2t', '*.m2v', '*.m4p', '*.m4b', '*.m4r', '*.m4v', '*.mpg', '*.mp2', '*.mpeg', '*.mpe', '*.mpv', '*.mpg', '*.mpeg', '*.m2v', '*.svi', '*.3gp', '*.3g2', '*.mxf', '*.roq', '*.nsv', '*.flv', '*.f4v', '*.f4p', '*.f4a', '*.f4b'),
        ]
        file_location = filechooser.open_file(title="Choose video file...", filters=filters, multiple=False)

        if file_location:
            print(file_location)
            file_path = file_location[0]
            SetLocation(file_path)
            self.check_audio_track(file_path)

    def check_audio_track(self, file_path):
            script_path = os.path.realpath(sys.argv[0])
            directory_path = os.path.dirname(script_path)
            quoted_input_file = f'"{file_path}"'
            systype = ["win", "macosx", "linux"]
            ffmpeg_command = f"{directory_path}/ffmpeg/{systype[0]}/ffmpeg -i {quoted_input_file} -hide_banner"
            # Execute the ffmpeg command to check for audio tracks
            result = subprocess.run(
                ffmpeg_command,
                shell=True,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            output = result.stdout.decode('utf-8')

            # Regular expression pattern to match language track names
            pattern = r'Stream #\d:\d+\((\w+)\): Audio'
            id_Pattern = r'Stream #(\d+:\d+)\(\w+\): Audio'


            # Find all matches using re.findall
            language_tracks = re.findall(pattern, output, re.MULTILINE)
            language_tracks_id = re.findall(id_Pattern, output, re.MULTILINE)

            track_info = {}
            for track_id, language in zip(language_tracks_id, language_tracks):
                track_info[track_id] = language

            App.get_running_app().audio_tracks_info = [lang for key, lang in track_info.items()]
            App.get_running_app().audio_tracks_data = track_info


def SetLocation(text):
    FileTextInput.Instance.text = text


class FileTextInput(TextInput):
    Instance = None

    def __init__(self, **kwargs):
        super(FileTextInput, self).__init__(**kwargs)
        FileTextInput.Instance = self

        SetLocation("Select file...")


class Interface(BoxLayout):
    pass


class MainApp(App):
    performance_setting = StringProperty('BALANCED')  # Default value can be set here
    audio_track = StringProperty('0:a:1')  # Default value can be set here
    audio_tracks_info = ListProperty()
    audio_tracks_data = {}

    def set_audio_track(self, audio_track):
        self.audio_track = audio_track
        for key, value in self.audio_tracks_data.items():
            if value == audio_track:
                print(key)
                self.audio_track = key
                break
    def set_performance(self, setting_value):
        self.performance_setting = setting_value
    def build(self):
        self.title = "YarukiLingo Video Converter"
        self.icon = "img/yaruki.ico"
        Window.borderless = False
        if platform == 'android' or platform == 'ios':
            Window.maximize()
        else:
            Window.size = (1460 * 0.6, 820 * 0.6)


MainApp().run()
