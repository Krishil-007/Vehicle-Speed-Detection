from tkinter import filedialog
import cv2
import dlib
import time
import math
from tkinter.ttk import Progressbar
from tkinter import *
import tkinter as tk

bgclr = '#11EEED'
fclr = '#EE1112'
btnclr = '#6E7376'
btnFclr = 'white'
Splash_Screen = Tk()
Splash_Screen.attributes("-fullscreen", True)
Splash_Screen.configure(background=bgclr)
l1 = Label(Splash_Screen, text='Welcome To Vehicle Speed ', fg=fclr, bg=bgclr)
lst1 = ('Monotype Corsiva', 82, 'bold')
l1.config(font=lst1)
l1.place(x=115, y=50)
l2 = Label(Splash_Screen, text='Detection Program ', fg=fclr, bg=bgclr)
lst2 = ('Monotype Corsiva', 82, 'bold')
l2.config(font=lst2)
l2.place(x=295,y=180)
def bar():
    l3=Label(Splash_Screen,text='Loading...',fg=fclr,bg=bgclr)
    lst3=('Calibri (Body)',25)
    l3.config(font=lst3)
    l3.place(x=18,y=650)
    
    import time
    r=0
    for i in range(50):
        Splash_Screen.update_idletasks()
        time.sleep(0.02)
        r=r+1
    Splash_Screen.destroy()
    Next_Screen()
lst4 = ('Monotype Corsiva', 28, 'bold')
b1 = Button(Splash_Screen, width=50, height=1, text='Get Started', command=bar,
            font=lst4, border=0, fg=btnFclr, bg=btnclr)
b1.place(x=130, y=510)
def Next_Screen():
    File_Selection_Screen = tk.Tk()
    File_Selection_Screen.geometry("1365x730")  
    File_Selection_Screen.configure(bg=bgclr) 
    File_Selection_Screen.title('Vehicle Speed Detection')
    l5 = Label(File_Selection_Screen, text='Select File', fg=fclr, bg=bgclr)
    lst5 = ('Monotype Corsiva', 82, 'bold')
    l5.config(font=lst5)
    l5.place(x=430,y=100)
    b2 = tk.Button(File_Selection_Screen, text='Browse', bg=btnclr, fg=btnFclr,height=2,
    width=50,command = lambda:openFile())
    b2.place(x=470,y=300) 


    def openFile():
        filepath = filedialog.askopenfilename(initialdir="C:\\Users\\Admin\\Desktop",title="Open file okay?",filetypes=(("video", "*.mp4"),("all files", ".")))
        print(filepath)
        file = open(filepath, 'r')
        File_Selection_Screen.destroy()
        runmaincode(filepath)
        file.close()
    File_Selection_Screen.mainloop()

def runmaincode(f1):
    carCascade = cv2.CascadeClassifier('vech.xml')
    video = cv2.VideoCapture(f1)

    WIDTH = 1280
    HEIGHT = 720

    def estimateSpeed(location1, location2):
        d_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
        ppm = 8.8
        d_meters = d_pixels / ppm
        fps = 18
        speed = d_meters * fps * 3.6
        return speed

    def trackMultipleObjects():
        rectangleColor = (0, 253, 59)
        frameCounter = 0
        currentCarID = 0
        fps = 0

        carTracker = {}
        carNumbers = {}
        carLocation1 = {}
        carLocation2 = {}
        speed = [None] * 1000

        out = cv2.VideoWriter('outNew.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 10, (WIDTH, HEIGHT))

        while True:
            start_time = time.time()
            rc, image = video.read()
            if type(image) == type(None):
                break

            image = cv2.resize(image, (WIDTH, HEIGHT))
            resultImage = image.copy()

            frameCounter = frameCounter + 1
            carIDtoDelete = []

            for carID in carTracker.keys():
                trackingQuality = carTracker[carID].update(image)

                if trackingQuality < 7:
                    carIDtoDelete.append(carID)

            
            for carID in carIDtoDelete:
                print("Removing carID " + str(carID) + ' from list of trackers. ')
                print("Removing carID " + str(carID) + ' previous location. ')
                print("Removing carID " + str(carID) + ' current location. ')
                carTracker.pop(carID, None)
                carLocation1.pop(carID, None)
                carLocation2.pop(carID, None)

            
            if not (frameCounter % 10):
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                cars = carCascade.detectMultiScale(gray, 1.1, 13, 18, (24, 24))

                for (_x, _y, _w, _h) in cars:
                    x = int(_x)
                    y = int(_y)
                    w = int(_w)
                    h = int(_h)

                    x_bar = x + 0.5 * w
                    y_bar = y + 0.5 * h

                    matchCarID = None

                    for carID in carTracker.keys():
                        trackedPosition = carTracker[carID].get_position()

                        t_x = int(trackedPosition.left())
                        t_y = int(trackedPosition.top())
                        t_w = int(trackedPosition.width())
                        t_h = int(trackedPosition.height())

                        t_x_bar = t_x + 0.5 * t_w
                        t_y_bar = t_y + 0.5 * t_h

                        if ((t_x <= x_bar <= (t_x + t_w)) and (t_y <= y_bar <= (t_y + t_h)) and (x <= t_x_bar <= (x + w)) and (y <= t_y_bar <= (y + h))):
                            matchCarID = carID

                    if matchCarID is None:
                        print(' Creating new tracker' + str(currentCarID))

                        tracker = dlib.correlation_tracker()
                        tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))

                        carTracker[currentCarID] = tracker
                        carLocation1[currentCarID] = [x, y, w, h]

                        currentCarID = currentCarID + 1

            for carID in carTracker.keys():
                trackedPosition = carTracker[carID].get_position()

                t_x = int(trackedPosition.left())
                t_y = int(trackedPosition.top())
                t_w = int(trackedPosition.width())
                t_h = int(trackedPosition.height())

                cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), rectangleColor, 4)

                carLocation2[carID] = [t_x, t_y, t_w, t_h]

            end_time = time.time()

            if not (end_time == start_time):
                fps = 1.0/(end_time - start_time)

            for i in carLocation1.keys():
                if frameCounter % 1 == 0:
                    [x1, y1, w1, h1] = carLocation1[i]
                    [x2, y2, w2, h2] = carLocation2[i]

                    carLocation1[i] = [x2, y2, w2, h2]

                    if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
                        if (speed[i] == None or speed[i] == 0) and y1 >= 275 and y1 <= 285:
                            speed[i] = estimateSpeed([x1, y1, w1, h1], [x1, y2, w2, h2])

                        if speed[i] != None and y1 >= 180:
                            cv2.putText(resultImage, str(int(speed[i])) + "km/h", (int(x1 + w1/2), int(y1-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 100) ,2)

            cv2.imshow('Vehicle Speed Detection', resultImage)

            out.write(resultImage)

            if cv2.waitKey(1) == 27:
                break

        
        cv2.destroyAllWindows()
        out.release()


    trackMultipleObjects()

Splash_Screen.mainloop()