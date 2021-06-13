from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.lang.builder import Builder
from kivymd.toast import toast
import sqlite3


Builder.load_file('components/kv/register.kv')


class RegisterScreen(Screen):
    # Attributes of register screen
    usr_email = ObjectProperty(None)
    usr_name = ObjectProperty(None)
    usr_pass1 = ObjectProperty(None)
    usr_pass2 = ObjectProperty(None)

    # To check the credentials
    def register(self):
        # Error handling
        if self.usr_email.text == '' or self.usr_name.text == '' or self.usr_pass1.text == '' or \
                self.usr_pass2.text == '':
            toast("OOOPSS... Don't leave an empty field")

            return False

        # To insert the user's credential to the database
        if self.usr_pass1.text == self.usr_pass2.text:
            # To connect to the database
            conn = sqlite3.connect('FacialRecognitionDB.db')
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            # To create a table
            cursor.execute('''CREATE TABLE IF NOT EXISTS professor (
                            "professor_ID"	INTEGER NOT NULL,
                            "email"	TEXT NOT NULL,
                            "name"	TEXT NOT NULL,
                            "password1"	TEXT NOT NULL,
                            "password2"	TEXT NOT NULL,
                            PRIMARY KEY("professor_ID" AUTOINCREMENT)
                        )''')

            insert_query = 'INSERT INTO professor (email,name, password1, password2) VALUES (?,?,?,?)'
            cursor.execute(insert_query, (self.usr_email.text, self.usr_name.text, self.usr_pass1.text,
                                          self.usr_pass2.text))
            conn.commit()
            cursor.close()
            # To reset the field after the program add the credentials
            self.reset_field()

            return True

        else:
            # Error handling
            toast('Password does not match')

            return False

    # To reset the user's input
    def reset_field(self):
        self.usr_email.text = ''
        self.usr_name.text = ''
        self.usr_pass1.text = ''
        self.usr_pass2.text = ''
