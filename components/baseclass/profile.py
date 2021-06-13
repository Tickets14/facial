from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import TwoLineAvatarListItem, ILeftBodyTouch
from kivymd.uix.button import MDIconButton
import sqlite3
from kivy.properties import StringProperty
from kivymd.app import MDApp


Builder.load_file('components/kv/profile.kv')


# For design of every list
class SectionCourse(TwoLineAvatarListItem):
    icon = StringProperty('folder-account')


# For adding icons in list
class IconLeftIcon(ILeftBodyTouch, MDIconButton):
    pass


# For creating the user's profile
class ProfileScreen(Screen):

    # To make the data appear
    def on_enter(self, *args):
        data_items = self.get_section()

        for info in data_items:
            section_list = SectionCourse(text=f'{info[2].upper()}', secondary_text=f'{info[3].upper()}')
            self.ids.content.add_widget(section_list)

    # To get the section handle of the user
    def get_section(self):
        app = MDApp.get_running_app()
        reset_data = []

        connection = sqlite3.connect('FacialRecognitionDB.db')
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS section(
                            "professor_ID" INTEGER,
                            "section_id" INTEGER NOT NULL,
                            "subject"	TEXT NOT NULL,
                            "course_year"	TEXT NOT NULL, 
                            PRIMARY KEY ("section_id" AUTOINCREMENT)
                        )"""
                       )
        connection.commit()

        # To select all the section
        cursor.execute(f"SELECT * FROM section WHERE professor_ID={app.current_user}")
        rows = cursor.fetchall()

        for row in rows:
            reset_data.append(row)

        data_items = reset_data
        cursor.close()

        return data_items
