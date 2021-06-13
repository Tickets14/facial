from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from components.baseclass import splash, login,  dashboard, register, studentlist, profile, about, studentinfo, dummy
from kivy.config import Config
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.toast import toast


class ContentNavigationDrawer(BoxLayout):
    nav_drawer = ObjectProperty()

    @staticmethod
    def soon():
        toast('This app is not yet available')


class MyScreenManager(ScreenManager):
    pass


sm = MyScreenManager()


class MyApp(MDApp):
    current_button = NumericProperty()  # Index of pressed button in dashboard
    current_user = NumericProperty()  # Index of PROF/USER
    current_subject = StringProperty('')  # Subject name
    current_course_year = StringProperty('')  # Course and year
    current_prof = StringProperty('')  # Name of prof
    current_prof_email = StringProperty('')  # Email of prof
    current_student = StringProperty('')  # Name of student
    current_student_id = NumericProperty()  # Index of student in student list
    current_update = NumericProperty()  # Index of a section when updating it
    current_delete = NumericProperty()  # Index of a section when deleting it
    dialog = None
    pick_time = ObjectProperty()
    updated_time = ObjectProperty()

    def __init__(self, **kwargs):
        self.title = "Facial Recognition"
        self.icon = 'logo.png'
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = 'Blue'

    def build(self):
        self.mainkv = Builder.load_file("main.kv")
        return self.mainkv

    def show_screen(self, name):
        self.root.current = 'nav_layout_screen'
        self.root.get_screen('nav_layout_screen').ids.sm.current = name


if __name__ == "__main__":
    Config.set('graphics', 'resizable', 1)
    Config.set("graphics", "width", "380")
    Config.set("graphics", "height", "620")
    Config.write()
    MyApp().run()
