
import csv
import sys
import numpy as np
import pandas as pd
import tensorflow as tf
import keras
import cv2
from keras.layers import Input, Conv2D, Activation, MaxPooling2D, Dense, Dropout, Flatten, BatchNormalization
from keras.models import Sequential, Model
from sklearn.model_selection import train_test_split
from keras.optimizers import Adam
import matplotlib
import matplotlib.pyplot as plt
import itertools
from keras.preprocessing import image
import time
import os.path
from sklearn.externals import joblib
import pymysql
from sklearn import metrics, svm

batch_size = 128
num_epochs = 170
learning_rate = 0.001



capture_duration = 30 #al durtion bta3 al session kolha 1min


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


def Calculate_Final_Expression():
    df = pd.read_csv('Facial Expressions.csv')

    # get the column name of max values in every row
    maxValueIndexObj = df.mean()

    print("Max Probability of Each Expression are: ")
    print(maxValueIndexObj)

    # get the column name of max values in every row
    FinalExpressionName = maxValueIndexObj.idxmax(), maxValueIndexObj.max()

    # get the column number of max values in every row
   # FinalExpressionProbalilty = maxValueIndexObj.max()
    print("\nHighest Expression during the exam is:", FinalExpressionName)

    filename = "Final Expression2.csv"
    file_exists = os.path.isfile(filename)
    fields = ['Angry Expr', 'Disgust Expr', 'Fear Expr', 'Happy Expr', 'Sad Expr', 'Surprise Expr'
        , 'Neutral Expr']
    # csv.register_dialect('myDialect', delimiter='/', quoting=csv.QUOTE_NONE)
    # writing to csv file
    # "w" representing to writing
    with open(filename, 'a', newline='') as csvfile:
        # creating a csv dict writer object
        csvwriter1 = csv.DictWriter(csvfile, fieldnames=fields)

        # creating a csv writer object
        csvwriter = csv.writer(csvfile)

        # writing headers (field names)
        if not file_exists:
            csvwriter1.writeheader()

        # writing the data rows
        csvwriter.writerow(maxValueIndexObj)
        #csvwriter.writerow(FinalExpressionName)
        # csvwriter.writerow(FinalExpressionProbalilty)


def merge():
    web_df = pd.read_csv("insert_ans.csv")
    facial_df = pd.read_csv("Final Expression.csv")

    merge = pd.concat([web_df, facial_df], axis=1)  # 1 --> bybd2 mn col 1

    # Write DataFrame to CSV
    merge.to_csv('merge.csv', index=False)

def load_svm_classification():
    conn = pymysql.connect(host='localhost', user='root', password='', db='test')

    a = conn.cursor()

    sql = 'SELECT  `Answer_Validity`, `Test_Elapsed_Time`, `Current_Level` FROM `e-learning`;'

    a.execute(sql)

    controw = a.execute(sql)
    print("number of rows", controw)

    a.execute(sql)
    records = a.fetchall()
    print("Total number of rows in Laptop is: ", a.rowcount)

    print("\nPrinting each laptop record")
    for row in records:
        print("Answer_Validity = ", row[0], )
        print("Test_Elapsed_Time = ", row[1])
        print("Current_Level  = ", row[2], "\n")
    #data = pd.read_csv("merge.csv")

    # Load the model
    model = joblib.load("Save_Classification.pkl")

    pred = model.predict(records)
    print("The Next Level is: ",pred)

def startCapturing():
    expressions_category = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
    model = load_existing_model_weights()
    graph = tf.get_default_graph()
    import os
    from pathlib import Path
    user_home = str(Path.home())
    #copy haarcascade_frontalface_default.xml file to your user home directory.
    face_cascade = cv2.CascadeClassifier(os.path.join(user_home, "haarcascade_frontalface_default.xml"))
    webcam = cv2.VideoCapture(0)
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
                        print('\nPredicted Expressions Model : ')
                        print(predictFE)

                        #fields = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

                        # name of csv file
                        filename = "Facial Expressions2.csv"
                        file_exists = os.path.isfile(filename)
                        fields = ['Angry Expr', 'Disgust Expr', 'Fear Expr', 'Happy Expr', 'Sad Expr', 'Surprise Expr'
                            , 'Neutral Expr']
                        # csv.register_dialect('myDialect', delimiter='/', quoting=csv.QUOTE_NONE)
                        # writing to csv file
                        # "a" representing to   append
                        with open(filename, 'a', newline='') as csvfile:
                            # creating a csv dict writer object
                            csvwriter1 = csv.DictWriter(csvfile, fieldnames=fields)

                            # creating a csv writer object
                            csvwriter = csv.writer(csvfile)

                            # writing headers (field names)
                            if not file_exists:
                                csvwriter1.writeheader()

                            # writing the data rows
                            csvwriter.writerow(predictFE)

                        # largest_var = max(predict)
                        # print("\nThe largest value is:\n", largest_var)

                        for index, emotion in enumerate(expressions_category):
                            cv2.putText(frame, emotion, (10, index * 20 + 20), cv2.FONT_HERSHEY_PLAIN, 0.8, (0, 255, 0),
                                        lineType=cv2.LINE_AA)
                            cv2.rectangle(frame, (70, index * 20 + 10),
                                          (70 + int(detected_expression[index] * 100), (index + 1) * 20 + 4),
                                          (0, 255, 0),
                                          -1)


                cv2.imshow('Facial Expression Model', frame)

                cv2.waitKey(3000)# kol kam snya ya5od frame (millisecond)
                # Load the model




                import connection as connection


               # if cv2.waitKey(1) & 0xFF == ord('q'):
               #     break

        webcam.release()
        cv2.destroyAllWindows()
        MEAN = df.mean(axis=1)
        dfff = pd.read_csv('Facial Expressions2.csv')
        #total = np.append(predictFE,axis=1)
        #print(total)

        # get the column name of max values in every row
        MEAN = dfff.mean()

        print("Max Probability of Each Expression are: ")

        print(MEAN)

        aa = np.array(MEAN)

        # get the column name of max values in every row
        FinalExpressionName = MEAN.idxmax(), MEAN.max()
        print("\nHighest Expression during the exam is:", FinalExpressionName,'\n')

        filename = "Final Expression.csv"
        file_exists = os.path.isfile(filename)
        fields = ['Angry Expr', 'Disgust Expr', 'Fear Expr', 'Happy Expr', 'Sad Expr', 'Surprise Expr'
            , 'Neutral Expr']
        # csv.register_dialect('myDialect', delimiter='/', quoting=csv.QUOTE_NONE)
        # writing to csv file
        # "w" representing to writing
        with open(filename, 'a', newline='') as csvfile:
            # creating a csv dict writer object
            csvwriter1 = csv.DictWriter(csvfile, fieldnames=fields)

            # creating a csv writer object
            csvwriter = csv.writer(csvfile)

            # writing headers (field names)
            if not file_exists:
               csvwriter1.writeheader()

            # writing the data rows
            csvwriter.writerow(MEAN)
           # csvwriter.writerow(FinalExpressionName)
            # csvwriter.writerow(FinalExpressionProbalilty)

        #load_svm_classification()
        conn = pymysql.connect(host='localhost', user='root', password='', db='test')

        a = conn.cursor()

        sql = 'SELECT  `Answer_Validity`, `Test_Elapsed_Time`, `Current_Level` FROM `e-learning`'

        controw = a.execute(sql)
        print("number of rows", controw)

        records = a.fetchone()  # it returns a list of all databases present
        b = np.array(records)
        print(records)
        merge = np.append(aa, b).reshape(-10,10)
        # Load the model
        model = joblib.load("Save_Classification.pkl")

        pred = model.predict(merge)
        print("The Next Level is: ", pred)

        break

if __name__ == "__main__":
    cfg = tf.ConfigProto(device_count={'GPU': 0, 'CPU': 56})
    sess = tf.Session(config=cfg)
    sess.graph.as_default()
    keras.backend.set_session(sess)
    startCapturing()



