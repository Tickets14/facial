from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from kivymd_extensions.akivymd import *

Builder.load_file('components/kv/splash.kv')


# This is the first thing the user will see
class SplashScreen(Screen):
    text = "This application is an integrated attendance system that uses facial recognition technology to match the " \
           "faces of every registered student"

    text1 = "Facial recognition is a way of identifying or confirming an individual’s identity using their face. " \
            "Facial recognition systems can be used to identify people in photos, videos, or in real-time."

    text2 = "Facial recognition is an easy, fast and secure way of taking down and collecting attendance for " \
            "everyday use."
