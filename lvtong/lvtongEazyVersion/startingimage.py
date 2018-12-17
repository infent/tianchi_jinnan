from PyQt5 import QtCore,QtGui,QtWidgets
import time


class StartingWindow(QtWidgets.QWidget):
    def __init__(self):
        super(StartingWindow,self).__init__()

    #模拟主程序加载过程
    def load_data(self,sp):
        for i in range(1,11):
            time.sleep(0.1)
            sp.showMessage("加载。。{0}%".format(i * 10), QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, QtCore.Qt.black)
        #允许主进程处理事件
        QtWidgets.qApp.processEvents()

def startingimage():
    print('starting program')
    #splash = QtWidgets.QSplashScreen(QtGui.QPixmap('E:\lvtongEazyVersion\image\lvtongdraft.PNG'))
    splash = QtWidgets.QSplashScreen(QtGui.QPixmap('image\lvtongdraft.PNG'))
    splash.showMessage('加载。。0%', QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, QtCore.Qt.black)
    # 显示启动界面
    splash.show()
    # 处理主进程事件
    QtWidgets.qApp.processEvents()
    window1 = StartingWindow()
    # window.setWindowTitle('starting image')
    # window.resize(300, 30)
    window1.load_data(splash)
    window1.show()
    splash.finish(window1)

# if __name__ == '__main__':
#     app = QtWidgets.QApplication(sys.argv)
#     splash = QtWidgets.QSplashScreen(QtGui.QPixmap('image/lvtongdraft.png'))
#     splash.showMessage('加载。。0%',QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom,QtCore.Qt.black)
#     #显示启动界面
#     splash.show()
#     #处理主进程事件
#     QtWidgets.qApp.processEvents()
#     window = MyWindow()
#     window.setWindowTitle('starting image')
#     window.resize(300,30)
#     window.load_data(splash)
#     window.show()
#     splash.finish(window)
