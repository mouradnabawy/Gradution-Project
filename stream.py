import csv
import time

import cv2
import keras
import numpy as np
import pandas as pd
import pymysql
import tensorflow as tf
from flask import Flask, render_template
from keras.layers import Conv2D, Activation, MaxPooling2D, Dense, Dropout, Flatten, BatchNormalization
from keras.models import Sequential
from keras.optimizers import Adam
from keras.preprocessing import image
from sklearn.externals import joblib

batch_size = 128
num_epochs = 170
learning_rate = 0.001

capture_duration = 30  # al durtion bta3 al session kolha 1min
app = Flask(__name__)

webcam = cv2.VideoCapture(0)


@app.route('/')
def index():
    return render_template('Result.html')


def construct_cnn():
    model = Sequential()
    model.add(Conv2D(64, (3, 3), padding='same', input_shape=(48, 48, 1)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(128, (3, 3), padding='same'))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    #
    model.add(Conv2D(128, (3, 3), padding='same'))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Dropout(0.20))
    model.add(Flatten())
    model.add(Dense(256))
    model.add(Activation("relu"))
    model.add(BatchNormalization())
    model.add(Dropout(0.30))
    model.add(Dense(7, activation='softmax'))

    model.compile(optimizer=Adam(lr=learning_rate), loss='categorical_crossentropy', metrics=['accuracy'])
    model.summary()

    return model


def load_existing_model_weights():
    model = construct_cnn()
    import os
    from pathlib import Path
    user_home = str(Path.home())
    model.load_weights(os.path.join(user_home, "model_weights.h5"))
    return model


def startCapturing():
    expressions_category = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
    model = load_existing_model_weights()
    graph = tf.get_default_graph()
    import os
    from pathlib import Path
    user_home = str(Path.home())

    # copy haarcascade_frontalface_default.xml file to your user home directory.
    face_cascade = cv2.CascadeClassifier(os.path.join(user_home, "haarcascade_frontalface_default.xml"))

    while True:
        # returns a float value which represents the time in seconds since the epoch("trainning period") .
        start_time = time.time()
        while ((time.time() - start_time) < capture_duration):
            rval, frame = webcam.read()
            if rval == True:
                frame = cv2.flip(frame, 1, 0)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_index = 0
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    face = gray[y:y + h, x:x + w]
                    detected_face = cv2.resize(face, (48, 48), interpolation=cv2.INTER_AREA)
                    x = image.img_to_array(detected_face)
                    x = np.expand_dims(x, axis=0)
                    x /= 255
                    with graph.as_default():
                        detected_expression = model.predict(x)[0]
                        # print("predicted expressions model=", detected_expression)

                        # creating dataframe using DataFrame constructor
                        df = pd.DataFrame(detected_expression)

                        # Get a series containing maximum value of each row
                        predictFE = df.max(axis=1)  # axis = 1 for cols
                        print('\nFacial Expressions Model : ')
                        print(predictFE)

                        # name of csv file
                        filename = "Facial Expressions.csv"
                        file_exists = os.path.isfile(filename)
                        fields = ['Angry Expr', 'Disgust Expr', 'Fear Expr', 'Happy Expr', 'Sad Expr',
                                  'Surprise Expr'
                            , 'Neutral Expr']

                        # writing to csv file
                        # "a" representing to append
                        with open(filename, 'a', newline='') as csvfile:
                            # creating a csv dict writer object
                            field_writer_facial = csv.DictWriter(csvfile, fieldnames=fields)

                            # creating a csv writer object
                            row_writer = csv.writer(csvfile)

                            # writing headers (field names)
                            if not file_exists:
                                field_writer_facial.writeheader()

                            # writing the data rows
                            row_writer.writerow(predictFE)

                        for index, emotion in enumerate(expressions_category):
                            cv2.putText(frame, emotion, (10, index * 20 + 20), cv2.FONT_HERSHEY_PLAIN, 0.8,
                                        (0, 255, 0),
                                        lineType=cv2.LINE_AA)
                            cv2.rectangle(frame, (70, index * 20 + 10),
                                          (70 + int(detected_expression[index] * 100), (index + 1) * 20 + 4),
                                          (0, 255, 0),
                                          -1)

                cv2.imshow('Facial Expression Model', frame)
                cv2.waitKey(3000)  # kol kam snya ya5od frame (millisecond)



        # webcam.release()
        cv2.destroyAllWindows()

        readfile = pd.read_csv('Facial Expressions.csv')

        # get the column name of max values in every row
        MeanOfEachExpression = readfile.mean()

        print("\nMax Probability of Each Expression are: ")
        print(MeanOfEachExpression)

        arr_of_facial = np.array(MeanOfEachExpression)

        # get the column name of max values in every row
        FinalExpression_Name_Probalilty = MeanOfEachExpression.idxmax(), MeanOfEachExpression.max()
        print("\nHighest Expression during the exam is:", FinalExpression_Name_Probalilty, '\n')

        filename = "Final Expression.csv"
        file_exists = os.path.isfile(filename)
        fields = ['Angry Expr', 'Disgust Expr', 'Fear Expr', 'Happy Expr', 'Sad Expr', 'Surprise Expr'
            , 'Neutral Expr']

        # writing to csv file
        # "a" representing to append
        with open(filename, 'a', newline='') as csvfile:
            # creating a csv dict writer object
            field_writer_mean_expression = csv.DictWriter(csvfile, fieldnames=fields)

            # creating a csv writer object
            row_writer_mean_expression = csv.writer(csvfile)

            # writing headers (field names)
            if not file_exists:
                field_writer_mean_expression.writeheader()

            # writing the data rows
            row_writer_mean_expression.writerow(MeanOfEachExpression)

        conn = pymysql.connect(host='localhost', user='root', password='', db='test')
        a = conn.cursor()
        sql = 'SELECT  `Answer_Validity`, `Test_Elapsed_Time`, `Current_Level` FROM `e-learning`'

        controw = a.execute(sql)
        print("number of rows", controw)

        records = a.fetchone()  # it returns a list of all databases present
        arr_of_web = np.array(records)
        print(records)

        merge = np.append(arr_of_facial, arr_of_web).reshape(-10, 10)

        # Load the model svm
        model = joblib.load("Save_Classification.pkl")

        pred = model.predict(merge)
        print("The Next Level is: ", pred)

        break


def finishx():
    # webcam.release()
    cv2.destroyAllWindows()


@app.route('/start')
def start():
    # al mfrod swa2 das End aw 5las lma al quiz ynthy hywdena ll page bta3t elly hywreh feh next level
    Start = (render_template('Result.html'), startCapturing())
    return Start


@app.route('/end')
def end():
    End = (render_template('Result.html'), finishx())
    return End


if __name__ == '__main__':
    app.run(host='localhost', debug=True)
    cfg = tf.ConfigProto(device_count={'GPU': 0, 'CPU': 56})
    sess = tf.Session(config=cfg)
    sess.graph.as_default()
    keras.backend.set_session(sess)
