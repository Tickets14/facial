from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from kivymd.uix.card import MDCard
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from datetime import datetime
import sqlite3
from kivymd.toast import toast
from kivy.utils import get_color_from_hex
from shutil import rmtree
from kivy.metrics import dp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.picker import MDTimePicker


Builder.load_file('components/kv/dashboard.kv')

# To add the color in every section
class Header(BoxLayout):
    pass


# For Updating the database, subject and course_year
class UpdateContent(BoxLayout):
    new_subject = ObjectProperty(None)
    new_course_year = ObjectProperty(None)
    dialog = None

    # To initialize the menu for updating
    def __init__(self, **kwargs):
        super().__init__()
        date = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        new_menu_items = [
            {
                "viewclass": "DropDownIcon",
                "icon": "calendar",
                "height": dp(56),
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.set_item(x),
            } for i in date]

        new_menu_items1 = [
            {
                "viewclass": "DropDownIcon",
                "icon": "calendar",
                "height": dp(56),
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.set_item1(x),
            } for i in date]

        self.new_menu = MDDropdownMenu(
            caller=self.ids.new_sched,
            items=new_menu_items,
            position="auto",
            width_mult=4,
        )
        self.new_menu1 = MDDropdownMenu(
            caller=self.ids.new_sched1,
            items=new_menu_items1,
            position="auto",
            width_mult=4,
        )

    # To get the input
    def set_item(self, new_content_item):
        self.ids.new_sched.text = new_content_item
        self.new_menu.dismiss()

    def set_item1(self, new_content_item1):
        self.ids.new_sched1.text = new_content_item1
        self.new_menu1.dismiss()

    # To update the database
    def update_section(self):
        new_subject = self.new_subject.text
        new_course_year = self.new_course_year.text
        new_sched = self.ids.new_sched.text
        new_sched1 = self.ids.new_sched1.text
        new_time = self.ids.new_time.text
        date = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

        try:
            check = date.index(new_sched)
            check1 = date.index(new_sched1)

        except ValueError:
            Snackbar(text="Don't leave an empty field").open()

        else:

            if check > check1:
                toast('Double check your schedule')

            else:
                # Error Handling
                if new_subject == '' or new_course_year == '' or \
                        new_sched == '' or new_sched1 == '' or new_time is None:

                    Snackbar(text="Don't leave an empty field").open()

                else:
                    app = MDApp.get_running_app()
                    connection = sqlite3.connect("FacialRecognitionDB.db")
                    connect_data = connection.cursor()
                    connect_data.execute(f"SELECT * FROM section WHERE professor_ID={app.current_user}")

                    update = """
                    UPDATE section SET subject = ?, course_year = ?, sched =?, sched1 = ?, 
                    time_sched = ? WHERE professor_ID = ? AND section_id = ?
                    """

                    update_values = (new_subject, new_course_year, new_sched, new_sched1, app.updated_time,
                                     app.current_user, app.current_update)

                    connect_data.execute(update, update_values)
                    connection.commit()
                    connect_data.close()

                    toast('Section is updated')

    # To clear the input
    def reset_field(self):
        self.new_subject.text = ''
        self.new_course_year.text = ''
        self.ids.new_sched.text = ''
        self.ids.new_sched1.text = ''
        self.ids.new_time.text = "None"

    def close(self, obj):
        self.dialog.dismiss()

    # To show the time picker
    def update_show_time(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.new_get_time)
        time_dialog.open()

    # TO get the time
    def new_get_time(self, instance, time):
        print(time)
        app = MDApp.get_running_app()
        fix_time = datetime.strptime(str(time), "%H:%M:%S")
        correct_time = fix_time.strftime("%I:%M %p")

        app.updated_time = correct_time
        return time


# To create a design for every section
class Section(MDCard):
    header = ObjectProperty(None)
    subject = StringProperty('')
    course_year = StringProperty('')
    index = NumericProperty()
    color = ListProperty([1, 1, 1, 1])
    count = NumericProperty()
    schedule = StringProperty('')
    schedule1 = StringProperty('')
    dialog = None

    def add_update_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Update Section",
                type="custom",
                content_cls=UpdateContent(),
            )

        self.dialog.open()

    # To delete the section in the database
    def delete_section(self):
        app = MDApp.get_running_app()
        connection = sqlite3.connect('FacialRecognitionDB.db')
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS section(
                                "professor_ID" INTEGER,
                                "section_id" INTEGER NOT NULL,
                                "subject"	TEXT NOT NULL,
                                "course_year"	TEXT NOT NULL,
                                "sched" TEXT NOT NULL,
                                "sched1" TEXT NOT NULL,
                                'time_sched' TEXT NOT NULL,
                                PRIMARY KEY ("section_id" AUTOINCREMENT)
                            )"""
                        )
        connection.commit()

        cursor.execute(f'DELETE FROM section WHERE section_id = {app.current_delete}')
        cursor.execute(f'DELETE FROM student WHERE section_id = {app.current_delete}')

        connection.commit()
        cursor.close()

        try:
            image_name = f"./references/{app.current_user}/{app.current_delete}/"
            thumbnails1 = f"./thumbnails/{app.current_user}/{app.current_delete}/"
            rmtree(image_name)
            rmtree(thumbnails1)
        except FileNotFoundError:
            Snackbar(text='Section Deleted class ').open()

        self.parent.remove_widget(self)
        Snackbar(text='Section Deleted class ').open()


class LobbyScreen(Screen):
    dialog = None
    x = NumericProperty(0)
    y = NumericProperty(0)

    def __init__(self, **kwargs):
        super(LobbyScreen, self).__init__(**kwargs)

    def add_class_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Add Section",
                type="custom",
                content_cls=Content(),
            )
        self.dialog.open()

    # Built in method where the details appear when you enter the lobby screen
    def on_enter(self, *args):
        data_items = self.get_section()
        change_color = ['#DC143C', '#88ABE3', '#d0a8c9', '#c36f31', '#cab39f', '#242726', '#eb826b', '#551825',
                        '#ed7d48', '#e9c68a']

        connection = sqlite3.connect('FacialRecognitionDB.db')
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS student(
        "id" INTEGER UNIQUE,
        "professor_ID" INTEGER,
        "section_id" INTEGER,
        "student_name" TEXT NOT NULL,
        "student_id" INTEGER,
        "present_count" INTEGER,
        PRIMARY KEY ("id" AUTOINCREMENT)
        ) 
        """)

        for info in data_items:
            cursor.execute(f"SELECT COUNT(id) FROM student WHERE section_id = {info[1]} ")
            student_count = cursor.fetchall()
            section_list = Section(index=info[1], subject=info[2], course_year=info[3], count=student_count[0][0],
                                   schedule=info[4], schedule1=info[5], color=get_color_from_hex(change_color[info[1] % 10]))

            self.ids.content.add_widget(section_list)

    # To update the data in the screen
    def refresh_callback(self, *args):

        def refresh_callback(interval):
            self.ids.content.clear_widgets()

            if self.x == 0:
                self.x, self.y = 1, 1
            else:
                self.x, self.y = 0, 0
            self.on_enter()
            self.ids.refresh_layout.refresh_done()
            self.tick = 0
        Clock.schedule_once(refresh_callback, 1)

    def on_leave(self, *args):
        self.ids.content.clear_widgets()

    # To get the data in the database
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
                                "sched" TEXT NOT NULL,
                                "sched1" TEXT NOT NULL,
                                'time_sched' TEXT NOT NULL,
                                PRIMARY KEY ("section_id" AUTOINCREMENT)
                            )"""
                        )
        connection.commit()

        cursor.execute(f"SELECT * FROM section WHERE professor_ID={app.current_user}")
        rows = cursor.fetchall()

        for row in rows:
            reset_data.append(row)
        data_items = reset_data

        cursor.close()
        return data_items

    # Closing the dialog
    def close(self, *args):
        self.dialog.dismiss()


class DropDownIcon(OneLineIconListItem):
    icon = StringProperty()


# For adding subject, course and year, sched, sched1, and time sched
class Content(BoxLayout):
    subject = ObjectProperty(None)
    course_year = ObjectProperty(None)
    dialog = None

    def __init__(self, **kwargs):
        super().__init__()
        date = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        menu_items = [
            {
                "viewclass": "DropDownIcon",
                "icon": "calendar",
                "height": dp(56),
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.set_item(x),
            } for i in date]

        menu_items1 = [
            {
                "viewclass": "DropDownIcon",
                "icon": "calendar",
                "height": dp(56),
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.set_item1(x),
            } for i in date]

        self.menu = MDDropdownMenu(
            caller=self.ids.sched,
            items=menu_items,
            position="auto",
            width_mult=4,
        )
        self.menu1 = MDDropdownMenu(
            caller=self.ids.sched1,
            items=menu_items1,
            position="auto",
            width_mult=4,
        )

    def set_item(self, content_item):
        self.ids.sched.text = content_item
        self.menu.dismiss()

    def set_item1(self, content_item1):
        self.ids.sched1.text = content_item1
        self.menu1.dismiss()

    def add_section(self):
        # To get the user's input
        subject = self.subject.text
        course_year = self.course_year.text
        sched = self.ids.sched.text
        sched1 = self.ids.sched1.text
        time = self.ids.time.text

        date = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        app = MDApp.get_running_app()
        # Error handling
        try:
            check = date.index(sched)
            check1 = date.index(sched1)
        except ValueError:
            Snackbar(text="Don't leave an empty field").open()
        else:

            if check > check1:
                toast('Double check your schedule')

            else:
                # If the user leave an empty field it will give a popup
                if subject == '' or course_year == '' or sched == '' or sched1 == '' or time is None:
                    toast("Don't leave an empty field")

                else:

                    connection = sqlite3.connect('FacialRecognitionDB.db')
                    cursor = connection.cursor()
                    cursor.execute("""CREATE TABLE IF NOT EXISTS section(
                                        "professor_ID" INTEGER,
                                        "section_id" INTEGER NOT NULL,
                                        "subject"	TEXT NOT NULL,
                                        "course_year"	TEXT NOT NULL,
                                        "sched" TEXT NOT NULL,
                                        "sched1" TEXT NOT NULL,
                                        'time_sched' TEXT NOT NULL,
                                        PRIMARY KEY ("section_id" AUTOINCREMENT)
                                    )"""
                                   )
                    connection.commit()

                    connection = sqlite3.connect('FacialRecognitionDB.db')
                    cursor = connection.cursor()
                    # Inserting the user's input into the database
                    cursor.execute('INSERT INTO section(professor_ID, subject, course_year, sched, sched1, time_sched) '
                                   'VALUES (?,?,?,?,?,?)', (app.current_user, subject, course_year, sched,
                                                           sched1, app.pick_time))

                    connection.commit()
                    cursor.close()
                    toast('Subject save')

    # To reset the field in the dialog
    def reset_field(self):
        self.subject.text = ''
        self.course_year.text = ''
        self.ids.sched.text = ''
        self.ids.sched1.text = ''
        self.ids.time.text = "None"

    def close(self, *args):
        self.dialog.dismiss()

    # To show the date picker
    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_time)
        time_dialog.open()

    # To get the time in the date picker
    def get_time(self, instance, time):
        print(time)
        app = MDApp.get_running_app()
        fix_time = datetime.strptime(str(time), "%H:%M:%S")
        correct_time = fix_time.strftime("%I:%M %p")
        app.pick_time = correct_time
        return time
