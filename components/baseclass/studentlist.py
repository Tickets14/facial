from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivymd.uix.button import MDIconButton
from kivy.clock import Clock
import sqlite3
import cv2
import openpyxl
from pathlib import Path
from datetime import date
import os
from time import localtime, strftime
from kivymd.uix.list import TwoLineAvatarListItem, ILeftBodyTouch
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw
from components.baseclass import trainer
from kivymd.uix.snackbar import Snackbar


Builder.load_file('components/kv/studentlist.kv')


# To create a list
class CustomListItem(TwoLineAvatarListItem):
    index = NumericProperty()
    icon = StringProperty()


# To create an icon of the list
class IconLeftImage(ILeftBodyTouch, MDIconButton):
    pass


# To create a dialog where a user can add a student
class DialogContent(BoxLayout):
    student_name = ObjectProperty(None)
    student_id = ObjectProperty(None)
    get_func = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__()
        self.get_func = StudentListScreen()

    # This is where the student will take a photo for profile and for scanning
    def camera_add_student(self):
        app = MDApp.get_running_app()
        id_student = self.student_id.text
        name_student = self.student_name.text
        conn = sqlite3.connect('FacialRecognitionDB.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS student(
        "id" INTEGER UNIQUE,
        "professor_ID" INTEGER,
        "section_id" INTEGER,
        "student_name" TEXT NOT NULL,
        "student_id" INTEGER,
        "present_count" INTEGER,
        PRIMARY KEY ("id" AUTOINCREMENT)
        ) 
        """)

        conn.commit()

        # Error handling
        if name_student == '' or id_student == '':
            toast("Don't leave empty field")

        elif not id_student.isnumeric():
            toast('Student ID should only consist of numbers')

        else:
            conn = sqlite3.connect('FacialRecognitionDB.db')
            c = conn.cursor()
            # To insert the user's input
            c.execute("""INSERT INTO student(professor_ID, section_id, student_name, student_id, present_count) 
            VALUES (?,?,?,?,?)""", (app.current_user, app.current_button, name_student, id_student,  0))

            conn.commit()
            c.close()

            # Creating table for every student
            conn = sqlite3.connect("FacialRecognitionDB.db")
            c = conn.cursor()

            # To select the last student
            c.execute("SELECT max(id) FROM student")
            max_id = c.fetchone()[0]
            c.close()

            conn = sqlite3.connect("FacialRecognitionDB.db")
            c = conn.cursor()
            table_name = str(max_id)

            # To create a specific table for every student
            create_table = "CREATE TABLE IF NOT EXISTS student_" + table_name + "(Date_Time)"
            c.execute(create_table)
            c.close()

            # To open the camera
            cap = cv2.VideoCapture(0)

            # To check if the directory is existing
            assure_path_exists(f"thumbnails/{app.current_user}/{app.current_button}/")
            temp_name = f'./thumbnails/{app.current_user}/{app.current_button}/' + str(max_id) + '.png'

            confirm = True
            counts = 0

            # To capture the students' face
            while confirm:
                ret, img = cap.read()
                cv2.imshow('Capturing...', img)
                img = cv2.resize(img, (300, 300))
                k = cv2.waitKey(30)
                counts += 1

                if k >= 0 or counts >= 30:
                    cv2.imwrite(temp_name, img)
                    confirm = False

            cap.release()
            cv2.destroyAllWindows()

            # To make an image circle
            img = Image.open(f'./thumbnails/{app.current_user}/{app.current_button}/' + str(max_id) + '.png').convert("RGB")
            npImage = np.array(img)
            h, w = img.size
            alpha = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(alpha)
            draw.pieslice([0, 0, h, w], 0, 360, fill=255)
            npAlpha = np.array(alpha)
            # Add alpha layer to RGB
            npImage = np.dstack((npImage, npAlpha))
            # Save with alpha
            Image.fromarray(npImage).save(f'./thumbnails/{app.current_user}/{app.current_button}/' + str(max_id) + '.png')

            vid_cam = cv2.VideoCapture(0)
            # This is where the matching happens
            face_detector = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")

            count = 0
            assure_path_exists(f"references/{app.current_user}/{app.current_button}/")
            while True:
                _, image_frame = vid_cam.read()
                cv2.imshow('Scanning', image_frame)
                gray = cv2.cvtColor(image_frame, cv2.COLOR_BGR2GRAY)
                faces = face_detector.detectMultiScale(gray, 1.1, 5)

                # To make a square shape if the program detects a face
                for (x, y, w, h) in faces:
                    cv2.rectangle(image_frame, (x, y), (x + w - 10, y + h - 10), (255, 0, 0), 2)
                    font = cv2.FONT_HERSHEY_SIMPLEX

                    # If the face is detected it will take a picture automatically
                    if count >= 1:
                        cv2.putText(image_frame, 'Processing...', (0, 120),
                                    font, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    else:
                        cv2.putText(image_frame, 'Take picture', (0, 120), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.imshow('Scanning', image_frame)

                    count += 1

                    # This will insert an image to the folder named references
                    cv2.imwrite(
                        f"references/{app.current_user}/{app.current_button}/" + self.student_name.text.replace('.', '') + "." + str(max_id) + "." +
                        str(count) + ".jpg", gray[y:y + h, x:x + w]
                    )

                # To close the camera
                key = cv2.waitKey(1)
                if count == 10 or key >= 0:
                    vid_cam.release()
                    cv2.destroyAllWindows()
                    break

            conn.close()
            self.reset_field()

    # To reset the field
    def reset_field(self):
        self.student_name.text = ''
        self.student_id.text = ''

    # To close a dialog
    def close(self, obj):
        self.dialog.dismiss()


class StudentListScreen(Screen):
    x = NumericProperty(0)
    y = NumericProperty(0)
    dialog = None
    #app = MDApp.get_running_app()

    def __init__(self, **kwargs):
        super(StudentListScreen, self).__init__(**kwargs)

    def add_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Add Student",
                type="custom",
                content_cls=DialogContent(),

            )
        self.dialog.open()

    # To make a list of every student
    def on_enter(self, *args):
        # Icon for list of students
        app = MDApp.get_running_app()
        app.root.get_screen('nav_layout_screen').ids.toolbar.title = f'{app.current_subject} | {app.current_course_year}'
        app.root.get_screen('nav_layout_screen').ids.toolbar.right_action_items = [['account-plus', lambda x: self.add_dialog()]]
        data_items = self.get_users()

        for info in data_items:

            list_students = CustomListItem(index=info[0],
                                           text=f'{info[1].title()}',
                                           secondary_text=f'{info[2]}',
                                           icon=f'thumbnails/{app.current_user}/{app.current_button}/{info[0]}.png'
                                           )

            self.ids.content.add_widget(list_students)

    # A method that updates the state of your application while the spinner remains on the screen
    def refresh_callback(self, *args):

        def refresh_callback(interval):
            self.ids.content.clear_widgets()

            if self.x == 0:
                self.x, self.y = 0, 0
            else:
                self.x, self.y = 0, 0
            self.on_enter()
            self.ids.refresh_layout.refresh_done()
            self.tick = 0

        Clock.schedule_once(refresh_callback, 1)

    # To get every student
    def get_users(self):
        app = MDApp.get_running_app()

        reset_data = []
        data_items = []
        connection = sqlite3.connect("FacialRecognitionDB.db")
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS student(
        "id" INTEGER,
        "professor_ID" INTEGER,
        "section_id" INTEGER,
        "student_name" TEXT NOT NULL,
        "student_id" INTEGER,
        "present_count" INTEGER,
        PRIMARY KEY ("id" AUTOINCREMENT)
        ) 
        """)

        uid = cursor.lastrowid
        connection.commit()
        cursor = connection.cursor()

        cursor.execute(f"SELECT id, student_name, student_id FROM student WHERE professor_ID = {app.current_user} AND section_id = {app.current_button}")
        #cursor.execute(f"SELECT *, ROW_NUMBER() OVER(ORDER BY id) AS NoId FROM student WHERE professor_ID = {app.current_user} AND section_id = {app.current_button}")

        rows = cursor.fetchall()

        for row in rows:
            reset_data.append(row)
        data_items = reset_data


        cursor.close()

        return data_items

    def back_list(self):
        self.ids.content.clear_widgets()

    # This will scan and check if the user is already registered or not
    @staticmethod
    def attendance():

        app = MDApp.get_running_app()
        information_reset = []

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        path = f'./references/{app.current_user}/{app.current_button}/'
        if not os.path.exists('./trainer'):
            os.makedirs('./trainer')

        # Error handling
        try:
            Ids, faces = trainer.get_image(path)

        except FileNotFoundError:
            Snackbar(text='Add student first').open()

        else:
            recognizer.train(faces, Ids)
            recognizer.write('trainer/trainer.yml')
            cv2.destroyAllWindows()

            conn = sqlite3.connect('FacialRecognitionDB.db')

            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS student(
                    "id" INTEGER UNIQUE,
                    "professor_ID" INTEGER,
                    "section_id" INTEGER,
                    "student_name" TEXT NOT NULL,
                    "student_id" INTEGER,
                    "present_count" INTEGER,
                    PRIMARY KEY ("id" AUTOINCREMENT)
            ) 
            """)

            file_trainer = "trainer/trainer.yml"
            attend = "Attendance/"

            # Another error handling
            if not os.path.isfile(file_trainer):
                toast('File Error')

            else:

                if not os.path.exists(attend):
                    os.makedirs(f"Attendance/")
                else:
                    pass

                cap = cv2.VideoCapture(0)

                temp_name = 'Temporary Image.jpg'
                confirm = True
                count = 0
                while confirm:
                    ret, img = cap.read()
                    cv2.imshow('Face Recognizer', img)
                    k = cv2.waitKey(30)
                    count += 1
                    if k >= 0 or count >= 30:
                        cv2.imwrite(temp_name, img)
                        confirm = False
                cap.release()

                # To know the name of the user's face
                face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
                read_image = cv2.imread(temp_name)
                gray = cv2.cvtColor(read_image, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 5)
                recognizer = cv2.face.LBPHFaceRecognizer_create()
                recognizer.read(file_trainer)

                # Placing a square when the face is detected
                for (x, y, w, h) in faces:
                    cv2.rectangle(read_image, (x, y), (x + w - 10,
                                                       y + h - 10), (0, 255, 0), 3)

                    ids, conf = recognizer.predict(gray[y:y + h, x:x + w])

                    c.execute(f"SELECT student_name FROM student WHERE id = {ids}")

                    result = c.fetchall()

                    student_name = result[0][0]

                    if conf < 50:
                        cv2.putText(read_image, student_name, (x + 5, y + h - 12), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                    (150, 255, 0),
                                    2)
                        print('DONE IF')

                    else:
                        cv2.putText(read_image, 'No Match', (x + 5, y + h - 12),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        print('DONE ELSE')

                    cv2.imshow('Face Recognizer', read_image)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
                    c.execute('SELECT present_count FROM student WHERE id = (?);', (ids,))
                    count = c.fetchall()

                    to_add = 0
                    for count_num in count:

                        to_add = count_num[0]

                    # Updating the present count
                    if conf < 50:
                        add = int(to_add) + 1
                        update_attendance = "UPDATE student SET present_count =? WHERE id = ?"
                        data_values = (add, ids)
                        c.execute(update_attendance, data_values)
                        fix_time = localtime()
                        time_log = strftime("%b %d, %Y - %H:%M", fix_time)
                        c.execute('INSERT INTO student_' + str(ids) + '(Date_Time) VALUES (?)', (time_log,))

                        conn.commit()
                    c.execute(f'SELECT * FROM student WHERE id = {ids}')
                    result2 = c.fetchall()
                    today = str(date.today())

                    data_save = pd.DataFrame(result2, columns=[
                        'Student no.',
                        'Professor no.',
                        'Section name',
                        'Student name',
                        'Student ID',
                        'Number of Present'
                    ])
                    # Name of excel
                    file_name = f"Attendance/{app.current_subject} {app.current_course_year}.xlsx"
                    write_data = open('status_data.txt', 'a')

                    for info in result2:
                        for info_2 in info:
                            information_reset.append(info_2)

                    if conf < 50:
                        write_data.write(information_reset[3] + ':' + str(date.today()) + ';')
                        write_data.close()

                        # To input the data of database in excel file
                        if os.path.isfile(file_name):
                            file_path = Path(f"Attendance/{app.current_subject} {app.current_course_year}.xlsx")
                            load_sheet = openpyxl.load_workbook(file_path)
                            load_sheet.create_sheet(f'hello')

                            work_sheet = load_sheet.active
                            work_sheet.append(result2[0])
                            print(result2[0])
                            load_sheet.save(f"Attendance/{app.current_subject} {app.current_course_year}.xlsx")

                        else:
                            data_excel = pd.ExcelWriter(file_name, engine='xlsxwriter')
                            data_save.to_excel(data_excel, index=False, sheet_name=f"2021-06-09")
                            worksheet = data_excel.sheets[f"2021-06-09"]
                            worksheet.set_column('A:A', 7)
                            worksheet.set_column('B:B', 20)
                            worksheet.set_column('C:C', 20)
                            worksheet.set_column('D:D', 30)
                            data_excel.save()
                            print('SA else OS.PATH.ISFILE(FILE_NAME)')
                        break

                conn.close()
                cv2.destroyAllWindows()


# For checking if the directory is existing
def assure_path_exists(path):
    direct = os.path.dirname(path)
    if not os.path.exists(direct):
        os.makedirs(direct)
