
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont, QTextCharFormat, QIcon, QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import datetime
import sys
import weather.current
import weather.historical
import re
import threading

flag = 0
class Window(QWidget):

    def __init__(self):
        super(Window, self).__init__()


        layout = QVBoxLayout()  #using QVBoxLayout for GUI.  forces each widget to have its own vertical space

        self.setLayout(layout)      #apply layout to window
        self.setFixedSize(400,450)  #using fixed size to avoid messing up scaling
        icon = QIcon()
        icon.addPixmap(QPixmap("icon.png"), QIcon.Normal, QIcon.Off)   #apply Sun Icon to upper left
        self.setWindowIcon(icon)
        button = QPushButton('Update weather', self)    #define button
        time2 = QTime()
        dateTest = QDate()
        time = QTimeEdit()
        Param1 = QLineEdit()
        Param2 = QLineEdit()
        Param3 = QLineEdit()
        Param4 = QLineEdit()        #define widgets for main panel
        Param1.setReadOnly(True)
        Param2.setReadOnly(True)
        Param3.setReadOnly(True)
        Param4.setReadOnly(True)    #force text boxes to read only, used for outputs
        calendar = QCalendarWidget()    #define calendar
        calendar.setMinimumDate(QDate(1998,1,1))    #force minimum date for calendar
        calendar.setMaximumDate(dateTest.currentDate()) #force maximum date for calendar as current date
        calendar.setGridVisible(True)
        layout.addWidget(calendar)      #add calendar to panel
        layout.addWidget(button)        #add button to panel
        layout.addWidget(time)          #add time selector to panel
        time.setTime(time2.currentTime())   #grab current time, change time selector to it as default
        layout.addWidget(Param1)          #add text output 1
        layout.addWidget(Param2)          #add text output 2
        layout.addWidget(Param3)          #add text output 3
        layout.addWidget(Param4)          #add text output 4
        button.clicked.connect(lambda: self.on_click(calendar.selectedDate(),time,Param1,Param2,Param3,Param4))  #setup event for button press, lambda in arguments
        self.setWindowTitle("AmesWeather.py")   #set title for main screen


    def on_click(self,date,time,Param1,Param2,Param3,Param4): #on click function, happens when button is pressed
        global flag     #pass in global flag to keep people from breaking program by spamming the button before the action is complete
        if (flag == 0):
            flag = 1
            thread = threading.Thread(target = (lambda: self.doCheck(date,time,Param1,Param2,Param3,Param4)))   #define a thread to take the processing attached to the button press action
            thread.start()  #start the thread.  this keeps the front-end gui from locking up while the processing takes place


    def doCheck(self,date,time,Param1,Param2,Param3,Param4):
        global flag          #Code inside this event should match up with the code inside amesweather.py
        a = ""               #functionality is the same, just outputs are not printing, they are appended to
        b = ""               #four string variables, which are written to the four outputs
        c = ""
        d = ""
        testStr = date.toPyDate().strftime("%m/%d/%Y")
        testStr = (testStr+ ":"+time.time().toString("hh:mm"))
        sys.argv.append("T")
        sys.argv.append("WS")
        sys.argv.append("P")
        sys.argv.append("WD")           #spoof in sys.argv values, to function with existing code from amesweather.py
        #te.setText(testStr)
        sys.argv.append("--time-offset=" + testStr)

        metric = False
        delta = None
        # TimeOffset is now a datetime object.
        timeOffset = None
        isTimeOffset = False
        flags = []
        arglist = sys.argv[1::]
        # Change args to know that the -- peramitors are in the list before ding the retreiving.

        place = 0
        while place < len(arglist):
            if arglist[place].startswith('--'):
                flags.append(arglist[place])
                del arglist[place]
            else:
                place += 1

        # Take care of the flags
        for i in range(len(flags)):
            arg = flags[i]
            if arg.startswith('--time-offset'):
                cmdtime = arg[arg.find('=') + 1::]
                # Split the command line arg up, and place in the datetime method.
                t = re.split('[/ :]', cmdtime)
                timeOffset = datetime.datetime(int(t[2]), int(t[0]), int(t[1]), int(t[3]), int(t[4]))
                isTimeOffset = True
            elif arg == '--metric':
                metric = True

        if timeOffset is None:
            timeOffset = datetime.datetime.now()

        # arglist = [a.upper() for a in arglist]

        for i in range(len(arglist)):
                arg = arglist[i]
                if arg.startswith('T'):
                    if arg == 'T':
                        if isTimeOffset:
                            if metric:
                                a+=str((weather.historical.getTemperature('C', tme=int((timeOffset).timestamp()))))
                            else:
                                a+=str((weather.historical.getTemperature('F', tme=int((timeOffset).timestamp()))))
                        else:
                            a+=(weather.current.getTemperature(metric))
                    elif arg == 'T-D':
                        delta = datetime.timedelta(days=1)
                        if metric:
                            a+=str((weather.historical.getTemperature('C', tme=int((timeOffset - delta).timestamp()))))
                        else:
                            a+=str((weather.historical.getTemperature('F', tme=int((timeOffset - delta).timestamp()))))
                    elif arg == 'T-W':
                        delta = datetime.timedelta(days=7)
                        if metric:
                            a+=str((weather.historical.getTemperature('C', tme=int((timeOffset - delta).timestamp()))))
                        else:
                            a+=str((weather.historical.getTemperature('F', tme=int((timeOffset - delta).timestamp()))))
                    elif arg == 'T-M':
                        delta = datetime.timedelta(days=28)
                        if metric:
                            a+=str((weather.historical.getTemperature('C', tme=int((timeOffset - delta).timestamp()))))
                        else:
                            a+=str((weather.historical.getTemperature('F', tme=int((timeOffset - delta).timestamp()))))
                    elif arg == 'T-Y':
                        delta = datetime.timedelta(days=365.25)
                        if metric:
                            a+=str((weather.historical.getTemperature('C', tme=int((timeOffset - delta).timestamp()))))
                        else:
                            a+=str((weather.historical.getTemperature('F', tme=int((timeOffset - delta).timestamp()))))
                elif arg.startswith('WS'):
                    if arg == 'WS':
                        if isTimeOffset:
                            if metric:
                                b+=str((weather.historical.getWindSpeed('KMH', tme=int(timeOffset.timestamp()))))
                            else:
                                b+=str((weather.historical.getWindSpeed('MPH', tme=int(timeOffset.timestamp()))))
                        else:
                            a+=(weather.current.getWindSpeed(metric))
                    elif arg == 'WS-D':
                        delta = datetime.timedelta(days=1)
                        if metric:
                            b+=str((weather.historical.getWindSpeed('KMH', tme=int((timeOffset - delta).timestamp()))))
                        else:
                            b+=str((weather.historical.getWindSpeed('MPH', tme=int((timeOffset - delta).timestamp()))))
                    elif arg == 'WS-W':
                        delta = datetime.timedelta(days=7)
                        if metric:
                            b+=str((weather.historical.getWindSpeed('KMH', tme=int((timeOffset - delta).timestamp()))))
                        else:
                            b+=str((weather.historical.getWindSpeed('MPH', tme=int((timeOffset - delta).timestamp()))))
                    elif arg == 'WS-M':
                        delta = datetime.timedelta(days=28)
                        if metric:
                            b+=str((weather.historical.getWindSpeed('KMH', tme=int((timeOffset - delta).timestamp()))))
                        else:
                            b+=str((weather.historical.getWindSpeed('MPH', tme=int((timeOffset - delta).timestamp()))))
                    elif arg == 'WS-Y':
                        delta = datetime.timedelta(days=365.25)
                        if metric:
                            b+=str((weather.historical.getWindSpeed('KMH', tme=int((timeOffset - delta).timestamp()))))
                        else:
                            b+=str((weather.historical.getWindSpeed('MPH', tme=int((timeOffset - delta).timestamp()))))
                elif arg.startswith('P'):
                    if arg == 'P':
                        if isTimeOffset:
                            if metric:
                                c+=str((weather.historical.getPressure('mbar', tme=int(timeOffset.timestamp()))))
                            else:
                                c+=str((weather.historical.getPressure('inHg', tme=int(timeOffset.timestamp()))))
                        else:
                            c+=(weather.current.getPressure(metric))
                    elif arg == 'P-D':
                        delta = datetime.timedelta(days=1)
                        if metric:
                            c+=str((weather.historical.getPressure('mbar', tme=int((timeOffset - delta).timestamp()))))
                        else:
                            c+=str((weather.historical.getPressure('inHg', tme=int((timeOffset - delta).timestamp()))))
                    elif arg == 'P-W':
                        delta = datetime.timedelta(days=7)
                        if metric:
                            c+=str((weather.historical.getPressure('mbar', tme=int((timeOffset - delta).timestamp()))))
                        else:
                            c+=str((weather.historical.getPressure('inHg', tme=int((timeOffset - delta).timestamp()))))
                    elif arg == 'P-M':
                        delta = datetime.timedelta(days=28)
                        if metric:
                            c+=str((weather.historical.getPressure('mbar', tme=int((timeOffset - delta).timestamp()))))
                        else:
                            c+=str((weather.historical.getPressure('inHg', tme=int((timeOffset - delta).timestamp()))))
                    elif arg == 'P-Y':
                        delta = datetime.timedelta(days=365.25)
                        if metric:
                            c+=str((weather.historical.getPressure('mbar', tme=int((timeOffset - delta).timestamp()))))
                        else:
                            c+=str((weather.historical.getPressure('inHg', tme=int((timeOffset - delta).timestamp()))))
                elif arg.startswith('WD'):
                    if arg == 'WD':
                        if isTimeOffset:
                            d+=str((weather.historical.getWindDirection(tme=int(timeOffset.timestamp()))))
                        else:
                            d+=str((weather.current.getWindDirection()))
                    elif arg == 'WD-D':
                        delta = datetime.timedelta(days=1)
                        d+=str((weather.historical.getWindDirection(tme=int((timeOffset - delta).timestamp()))))
                    elif arg == 'WD-W':
                        delta = datetime.timedelta(days=7)
                        d+=str((weather.historical.getWindDirection(tme=int((timeOffset - delta).timestamp()))))
                    elif arg == 'WD-M':
                        delta = datetime.timedelta(days=28)
                        d+=str((weather.historical.getWindDirection(tme=int((timeOffset - delta).timestamp()))))
                    elif arg == 'WD-Y':
                        delta = datetime.timedelta(days=365.25)
                        d+=str((weather.historical.getWindDirection(tme=int((timeOffset - delta).timestamp()))))

                if i != (len(arglist) - 1) and arg not in ['--metric', '--time-offset']:
                    a = a
        Param1.setText(a + " Degrees Fahrenheit")
        Param2.setText(b + " MPH")
        Param3.setText(c + " inHG")
        Param4.setText(d)       #print the four values to the text outputs
        a=""
        b=""
        c=""
        d=""

        del sys.argv[1:]        #remove the spoofed sys.argv values
        flag = 0                #unset flag








        #QMessageBox.information(self, 'a',date.toString(), QMessageBox.Ok, QMessageBox.Ok)

app = QApplication(sys.argv)

screen = Window()

screen.show()

sys.exit(app.exec_())
