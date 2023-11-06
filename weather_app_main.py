import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QThread, QTimer, Qt

import time
import datetime

import weather
from weather import DAYS

W_show = [300, 301, 303, 305, 315, 325, 330, 350, 400, 480, 560, 580, 600, 620, 650]
W_hide = [300, 369, 458, 500, 525, 550, 580, 600, 620, 650]


class WeatherData(QThread):
    def __init__(self):
        QThread.__init__(self)

    req = weather.today()
    temp = req['temp']
    feels = req['feels']
    humidity = req['humidity']
    speed = str(req['wind']['speed'])
    city = req['city']
    type = req['dis']
    icon = req['icon']

    week = weather.week()

    def run(self):
        while True:
            # weather today
            try:
                req = weather.today()
            except:
                req['temp'] = self.temp
                req['feels'] = self.feels
                req['humidity'] = self.humidity
                req['wind']['speed'] = self.speed
                req['city'] = self.city
                req['dis'] = self.type
                req['icon'] = self.icon
            # weather for the week
            try:
                req_week = weather.week()
                self.week = req_week
            except:
                self.week = DAYS
            self.temp = req['temp']
            self.feels = req['feels']
            self.humidity = req['humidity']
            self.speed = str(req['wind']['speed'])
            self.city = req['city']
            self.type = req['dis']
            self.icon = req['icon']
            time.sleep(300)


class App(QMainWindow):
    show_more = True
    tic = False

    def __init__(self, app):
        QMainWindow.__init__(self)
        self.weather = WeatherData()
        self.weather.start()
        self.app = app
        self.set()
        self.setData()
        self.setMore()
        self.timer = QTimer()
        self.timer.timeout.connect(self.setData)
        self.timer.start(500)
        self.old_pos = None

    def set(self):
        self.w_root = uic.loadUi('weather_app.ui', self)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.w_root.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.w_root.btn_more.clicked.connect(self.setWidth)
        self.w_root.show()

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            self.end = self.mapToGlobal(event.pos())
            self.movement = self.end - self.start
            self.setGeometry(self.mapToGlobal(self.movement).x(),
                             self.mapToGlobal(self.movement).y(),
                             self.width(),
                             self.height())
            self.start = self.end

    def mouseReleaseEvent(self, QMouseEvent):
        self.pressing = False

    def setData(self):
        """setting weather parameters on today"""
        self.w_root.l_temp.setText(str(self.weather.temp) + "°C")
        self.w_root.l_feel.setText(self.weather.feels)
        self.w_root.l_hum.setText(self.weather.humidity)
        self.w_root.l_wind.setText(self.weather.speed + " м/с")
        self.w_root.l_city.setText(self.weather.city)
        self.w_root.l_type.setText(self.weather.type)

        """setting icons to the main window"""
        # f"img/{self.weather.type}.png"
        px_logo = QPixmap(f"img/{self.weather.icon}.png")
        self.w_root.l_logo.setPixmap(px_logo)

        self.w_root.l_feeling.setPixmap(QPixmap('img/temperature.png'))
        self.w_root.l_humidity.setPixmap(QPixmap('img/water.png'))
        self.w_root.l_speed.setPixmap(QPixmap('img/wind.png'))

        """day of the week"""
        today = DAYS[datetime.datetime.today().weekday()]
        self.w_root.l_day.setText(today['title'])
        color = today['color']
        self.w_root.l_day.setStyleSheet(f"color:{color};\n"
                                        f"background-color: rgba(255, 255, 255, 0);")

        """clock"""
        if self.tic:
            now = datetime.datetime.today().strftime("%H:%M:%S")
            self.tic = False
        else:
            now = datetime.datetime.today().strftime("%H %M %S")
            self.tic = True
        self.w_root.l_time.setText(now)

        self.setDataMore()

    def setWidth(self):
        if self.w_root.width() > 300:
            self.show_more = False

        if self.show_more:
            for i in W_hide:
                if self.w_root.width() > i:
                    continue
                self.w_root.resize(i, 490)
                self.w_root.f_background.resize(i, 490)
                self.w_root.f_panel.resize(i, 25)
                self.w_root.btn_more.move(i-30, 185)
                self.w_root.btn_close.move(i-30, 5)
                self.w_root.l_time.move(i - 100, 2)
                self.w_root.btn_more.setText('<<')
                self.app.processEvents()
                time.sleep(.02)
            self.show_more = False
        else:
            for i in reversed(W_show):
                self.w_root.resize(i, 490)
                self.w_root.f_background.resize(i, 490)
                self.w_root.f_panel.resize(i, 25)
                self.w_root.resize(i, 490)
                self.w_root.btn_more.move(i-30, 185)
                self.w_root.btn_close.move(i-30, 5)
                self.w_root.l_time.move(i - 100, 2)
                self.w_root.btn_more.setText('>>')
                self.app.processEvents()
                time.sleep(.02)
            self.show_more = True
        App.show_more = self.show_more

    def setMore(self):
        """weather for week days"""
        for i in self.weather.week:
            w_day = uic.loadUi('day.ui')
            w_day.setAttribute(Qt.WA_TranslucentBackground, True)
            w_day.setObjectName('w_day_' + str(i['num']))
            w_day.l_title.setText(i['title'])
            w_day.l_temp.setText(str(round(i['temp'])) + '°C')
            w_day.l_type.setText(i['type'])
            w_day.l_ico.setPixmap(QPixmap(f"img/week_ico/{i['icon']}.png"))
            w_day.l_title.setStyleSheet("color: " + i['color'] + "; background-color: none; border: none")
            if i['active']:
                w_day.frame.setStyleSheet("QFrame {\n"
                                          "background-color: rgba(255, 255, 255, 80);\n"
                                          "border: 1px solid;\n"
                                          "border-radius: 15px;\n"
                                          "}")
                w_day.l_temp.setStyleSheet("border: none;\n"
                                           "color: rgba(255, 255, 255, 180);")
                w_day.l_type.setStyleSheet("border: none;\n"
                                           "color: rgba(255, 255, 255, 180);")
            self.w_root.box.addWidget(w_day)
        self.w_root.box.addStretch()

    def setDataMore(self):
        """updating weather for a week"""
        for i in self.weather.week:
            for w in self.w_root.f_more.children():
                try:
                    w.l_title.setText(i['title'])
                    w.l_temp.setText(str(round(i['temp'])) + '°C')
                    w.l_type.setText(i['type'])
                except AttributeError:
                    pass
                break

    def set_background(self):
        alfas = {
            15: 10,   14: 20,   13: 30,  12: 40,  11: 50,
            10: 60,   9: 70,    8: 80,   7: 90,   6: 100,
            5: 110,   4: 120,   3: 130,  2: 140,  1: 150,
            0: 160,  -1: 170,  -2: 180, -3: 190, -4: 200,
            -5: 210, -6: 220,  -7: 230, -8: 240, -9: 250,
        }
        if self.weather.temp > 15:
            self.alfa = 0
        elif self.weather.temp <= -10:
            self.alfa = 255
        else:
            self.alfa = alfas[self.weather.temp]
        self.w_root.f_cold.setStyleSheet(f"background-color: rgba(51, 153, 255,{self.alfa});")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App(app)
    app.exec_()


