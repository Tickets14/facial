from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, StringProperty, NumericProperty
import sqlite3
from datetime import datetime
from time import localtime, strftime
import os
from kivymd.uix.list import TwoLineAvatarListItem
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar


Builder.load_file('components/kv/studentinfo.kv')


class StudentInfoScreen(Screen):
    # Attributes of student info
    personal_information = ListProperty([])
    name_student = StringProperty("")
    id_student = NumericProperty()
    class_student = StringProperty("")
    image_name = StringProperty("")
    status = StringProperty("Absent")
    dialog99 = None

    def __init__(self, **kwargs):
        super(StudentInfoScreen, self).__init__(**kwargs)

    # A dialog where ask question if you really want ot delete the student
    def delete_student_dialog(self):
        if not self.dialog99:
            self.dialog99 = MDDialog(
                title='[color=#f54029]Delete this Student?[/color]',
                text="If you delete this student you cannot retrieve it anymore ",
                buttons=[
                    MDFlatButton(
                        text="CANCEL", text_color=[1, 0, 1, 1], on_release=self.close
                    ),
                    MDRaisedButton(
                        text="DISCARD",
                        text_color=[1, 1, 1, 1],
                        md_bg_color=[1, 0, 0, 1],
                        on_release=lambda x: self.delete_student(),

                    ),
                ],
            )
        self.dialog99.open()

    # To close the dialog
    def close(self, *args):
        self.dialog99.dismiss(force=True)

    # This will fire if the user enter to the student info screen
    def on_enter(self, *args):
        app = MDApp.get_running_app()
        self.list_data = []
        connection = sqlite3.connect("FacialRecognitionDB.db")
        connect_data = connection.cursor()
        connect_data.execute(f"""
        SELECT * FROM student 
        WHERE professor_ID = {app.current_user} AND 
        section_id = {app.current_button} AND 
        id = {app.current_student_id}
        """)

        # To collect the data from the database
        self.data_collect = connect_data.fetchall()

        for row in self.data_collect:
            self.list_data.append(row)

        self.name_student = self.list_data[0][3]
        self.id_student = self.list_data[0][4]
        self.class_student = app.current_course_year
        self.image_name = f"thumbnails/{app.current_user}/{app.current_button}/" + str(
            app.current_student_id) + ".png"

        connect_data.close()
        reset_data = []

        # To get the student time log
        connection = sqlite3.connect("FacialRecognitionDB.db")
        cursor = connection.cursor()

        # To select all the details for a specific student
        student = "SELECT * FROM student_" + str(app.current_student_id)
        cursor.execute(student)
        student_log = cursor.fetchall()
        # print('STUDENT LOGGG', student_log[-1][0])
        for row in student_log:
            reset_data.append(row)
        data_log = reset_data

        # To get the section time
        cursor.execute(f"SELECT sched, sched1, time_sched FROM section WHERE professor_ID = {app.current_user} "
                       f"AND section_id = {app.current_button}")

        section_sched = cursor.fetchall()

        date = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

        print('SECTION SCHED',section_sched[0][0])
        print(section_sched[0][2])

        # To get the starting upto end of the date
        index_start = date.index(section_sched[0][0])
        index_end = date.index(section_sched[0][1])

        start = index_start
        end = index_end

        correct_date = date[start:end+1]

        print(correct_date)
        weekday = datetime.today().strftime('%A')

        # To get the details of the student log
        for details in data_log:
            details = list(details)
            details = ' '.join(details).split()

            list_students = DateTime(text=f'Date: {details[0]} {details[1]} {details[2]}',
                                     secondary_text=f'Time: {details[4]}')

            self.ids.logs.add_widget(list_students)

        # To get the localtime right now
        fix_time = localtime()
        date_today = strftime("%b %d, %Y", fix_time)
        print(date_today)
        print(student_log)

        # To check if the student is late, absent or present
        while True:
            for index in correct_date:
                if weekday != index:
                    self.status = 'Absent'

                else:
                    if not student_log:
                        self.status = 'Absent'
                        break
                    else:
                        student_fix = student_log[-1][0]
                        print('STUDENT FIX TIME', student_fix[15:20])
                        print(section_sched[0][2] > student_fix[15:20])
                        print('DATE TODAY', date_today)
                        if date_today == student_fix[0:12]:
                            if section_sched[0][2] > student_fix[15:20]:
                                self.status = 'Late'
                                break
                            else:
                                self.status = 'Present'
                                break

                        else:
                            self.status = 'Absent'
                            break
                            print('STUDENT INFO', student_fix)
            break

    # To delete the student
    def delete_student(self):
        app = MDApp.get_running_app()
        connection = sqlite3.connect("FacialRecognitionDB.db")
        connect_data = connection.cursor()

        connect_data.execute(f"""SELECT * FROM student 
        WHERE professor_ID = {app.current_user} 
        AND section_id = {app.current_button} 
        AND id = {app.current_student_id}
        """)
        take_data = connect_data.fetchall()
        print('TAKE_DATA', take_data[0][0])
        delete_data = "DELETE from student where id = ?"
        connect_data.execute(delete_data, (take_data[0][0],))

        connection.commit()
        connect_data.close()

        count = 0
        # To delete the image of students
        while True:
            try:
                count += 1
                references1 = f"references/{app.current_user}/{app.current_button}/" + self.name_student.replace('.', '') + "." + \
                             str(take_data[0][0]) + "." + str(count) + ".jpg"

                os.remove(references1)

            except FileNotFoundError:

                break

        # To delete the image of students in thumbnails
        while True:
            try:
                thumbnails1 = f"thumbnails/{app.current_user}/{app.current_button}/{app.current_student_id}.png"
                os.remove(thumbnails1)
            except FileNotFoundError:
                Snackbar(text='Student is Deleted')
                break

        # To show the student list screen after deleting the student
        app.show_screen('studentlist')
        self.close()


class DateTime(TwoLineAvatarListItem):
    pass
