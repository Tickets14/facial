from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from components.baseclass.dashboard import LobbyScreen


Builder.load_file('components/kv/dummy.kv')


class DummyScreen(Screen):

    def on_pre_leave(self, *args):
        LobbyScreen().ids.content.clear_widgets()

