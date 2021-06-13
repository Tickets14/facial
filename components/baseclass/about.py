from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder


Builder.load_file('components/kv/about.kv')


class AboutScreen(Screen):
    # For introduction in screen
    intro = 'Facial Recognition Student Attendance System is a Student Application for android.' \
            ' Send us your Feedbacks Bug Reports, and Suggestion for further development of the application'
