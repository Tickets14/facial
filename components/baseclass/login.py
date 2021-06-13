from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.lang.builder import Builder
import sqlite3
from kivymd.toast import toast
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog


Builder.load_file('components/kv/login.kv')


class LoginScreen(Screen):
    usr_email = ObjectProperty(None)
    usr_pass = ObjectProperty(None)
    dialog = None
    lobby = ObjectProperty(None)

    def saving(self, obj):  # close the dialog
        self.dialog.dismiss()

    # To check the credentials of user
    def usr_login(self):
        global usr_index
        app = MDApp.get_running_app()
        self.temp_username = []
        conn = sqlite3.connect('FacialRecognitionDB.db')
        cursor = conn.cursor()
        # For creating a table of professor
        cursor.execute('''CREATE TABLE IF NOT EXISTS professor (
                         "professor_ID"	INTEGER NOT NULL,
                         "email"	TEXT NOT NULL,
                         "name"	TEXT NOT NULL,
                         "password1"	TEXT NOT NULL,
                         "password2"	TEXT NOT NULL,
                         PRIMARY KEY("professor_ID" AUTOINCREMENT)
                     )''')

        # Selecting all column in professor table
        cursor.execute('SELECT * FROM professor')
        rows = cursor.fetchall()

        # Error handling
        for usernames in rows:
            self.temp_username.append(usernames[1])

        if self.usr_email.text == '' or self.usr_pass.text == '':
            toast("OOPS. Don't leave an empty field")

        else:

            if self.usr_email.text in self.temp_username:
                usr_index = self.temp_username.index(self.usr_email.text)
                app.current_user = usr_index
                app.current_prof = rows[usr_index][2].title()
                app.current_prof_email = rows[usr_index][1]

                if self.usr_pass.text == rows[usr_index][4]:
                    return True
                else:
                    toast('Double check your password')
            else:
                toast("Email doesn't exist")
        self.reset_field()

    # To get the index of the current user
    def get_index(self):
        return usr_index

    # To reset the user's input
    def reset_field(self):
        self.usr_email.text = ''
        self.usr_pass.text = ''




