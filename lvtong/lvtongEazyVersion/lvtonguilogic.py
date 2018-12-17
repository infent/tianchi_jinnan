from PyQt5.QtCore import QThread, QDateTime, pyqtSignal
from ui import lvtongui, calculateui, online_rules,login,sqlmode
from startingimage import *
from Sunshinemodel import *


import sys, re


# 登录界面
class userlogin(QtWidgets.QWidget, login.Ui_Form):
    def __init__(self):
        super(userlogin, self).__init__()
        self.setupUi(self)

        # 进行登录校验
        self.login.clicked.connect(self.checkUserInMysql)

    def checkUserInMysql(self):
        employid = self.employid.text()
        password = self.password.text()
        if (employid == '' or password == ''):
            QtWidgets.QMessageBox.warning(self, '警告', '员工号或密码不可为空', QtWidgets.QMessageBox.Yes)
            return
        df = userloginQuery(employid)
        # print(employid)
        # print(df['password'].values[0])
        if (len(df) == 0):
            QtWidgets.QMessageBox.information(self, '提示', '账号不存在')
        else:
            if (df['password'].values[0] == password):
                # print('tiaozhuan')
                self.user = employid
                self.usergroup = df['usergroup'].values[0]
                lvtong.show()
                self.close()
            else:
                QtWidgets.QMessageBox.information(self, '提示', '密码错误')
        return
#sqlmode界面
#需求：需要使用多线程和进度条来解决sql查询卡顿的情况
#当数据读取比较少的时候可以直接在init里执行executesql但是数据多了，可以把这部分逻辑
#放在QThread线程中，实现数据显示和数据读取的分离
class sqlThread(QThread):
    sinOut = pyqtSignal(int)
    sinOutFinish = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self,parent=None):
        super(sqlThread,self).__init__(parent)
        self.tabel = QtWidgets.QTableWidget()
        self.count = 0
    def run(self):
        try:
            sqlmodewidget.execsql.setEnabled(False)
            sql = sqlmodewidget.lineEdit.displayText()
            connect = create_engine('mysql+pymysql://root:123456@localhost:3306/lvtong')
            self.result = pd.read_sql_query(sql, connect)
            #sqlmodewidget.executesql()
            # info = 'running'
            # self.sinOut.emit(info)
            print('query ending')
            #self.sinOut.connect(sqlmodewidget.executesql)

            #sql查询展示部分
            result = self.result
            #这个不是14万了而是乘以维度数了，展开了
            #print(len(result.values.reshape(1, -1)[0]))
            #count = 0
            #tabel = QtWidgets.QTableWidget()

            self.tabel.setRowCount(len(result))
            self.tabel.setColumnCount(len(result.columns))
            self.tabel.setHorizontalHeaderLabels(result.columns)
            #sqlmodewidget.displayresult.addWidget(tabel)
            self.count = self.count + 1
            #self.tabel.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            #循环也相当耗时，即使分出来界面也卡一下，怎么解决。

            for i, j in enumerate(result.values.reshape(1, -1)[0]):
                newItem = QtWidgets.QTableWidgetItem(str(j))
                self.tabel.setItem(int(i / len(result.columns)), i % len(result.columns), newItem)
                #print(i,len(result.values.reshape(1, -1)[0]))
                if i % 50000 == 0:
                    process = i / len(result.values.reshape(1, -1)[0])*100
                    self.sinOut.emit(process)

            #print(result.values,result.values[0])
            print('ending')
            # if count > 0:
            #     sqlmodewidget.displayresult.removeWidget(tabel)
            #info = 'running'
            self.sinOutFinish.emit()
        except Exception as e:
            self.error.emit(str(e))
            print(e)

        finally:
            sqlmodewidget.execsql.setEnabled(True)

    # def timerEvent(self, *args, **kwargs):
    #     if sqlmodewidget.step >= 100:
    #         sqlmodewidget.timer.stop()
    #         return
    #     sqlmodewidget.step = sqlmodewidget.step + 1
    #     sqlmodewidget.pbar.setValue(sqlmodewidget.step)
    # def work(self):
    #     sqlmodewidget.mysqlThread.start()
    #
    #     #运行完毕发射信号
    #     sqlmodewidget.mysqlThread.sinOut.connect(self.finishedTip)
    #
    # def finishedTip(self):
    #
    #
    #     print('finished Thread')



class sqlmode(QtWidgets.QWidget,sqlmode.Ui_Form):
    def __init__(self):
        super(sqlmode,self).__init__()
        self.setupUi(self)
        self.execsql.clicked.connect(self.work)



        #self.connect = create_engine('mysql+pymysql://root:123456@localhost:3306/lvtong')
        #self.mysqlThread = sqlThread()
        #使用多线程
        #self.execsql.clicked.connect(self.go)
        #self.mysqlThread.sinOut.connect(self.executesql)
        #self.mysqlThread.sinOut.connect(self.mysqlThread.work)
        #使用单线程
        #self.execsql.clicked.connect(self.executesql)



    def work(self):
        mysqlThread.start()
        mysqlThread.sinOut.connect(self.pbarShow)
        mysqlThread.error.connect(self.errorTip)
        mysqlThread.sinOutFinish.connect(self.showresult)

    def errorTip(self,e):
        QtWidgets.QMessageBox.about(self, '提示', e)

    def pbarShow(self,value):
        self.progressBar.setValue(value)

    # 把页面逻辑拿回来
    def showresult(self):
        result = QtWidgets.QTableWidget()
        result.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        result = mysqlThread.tabel
        self.displayresult.addWidget(result)
        if mysqlThread.count > 0:
            sqlmodewidget.displayresult.removeWidget(mysqlThread.tabel)
        self.execsql.setEnabled(True)

    #可以到多线程
    def go(self):
        self.execsql.setEnabled(False)
        self.mysqlThread.start()

    def executesql(self):
        #sql = self.lineEdit.displayText()
        #result = pd.read_sql_query(sql,self.connect)

        result = self.mysqlThread.result
        self.execsql.setEnabled(True)
        count = 0
        tabel = QtWidgets.QTableWidget()

        tabel.setRowCount(len(result))
        tabel.setColumnCount(len(result.columns))
        tabel.setHorizontalHeaderLabels(result.columns)
        self.displayresult.addWidget(tabel)
        count = count + 1
        tabel.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        for i, j in enumerate(result.values.reshape(1,-1)[0]):
            newItem = QtWidgets.QTableWidgetItem(str(j))
            tabel.setItem(int(i / len(result.columns)), i % len(result.columns), newItem)
        #print(result.values,result.values[0])
        print('ending')
        if count>0:
            self.displayresult.removeWidget(tabel)



            #sip.delete(tabel)

# 计算违规因子界面
class ChildrenForm_calculateillegal(QtWidgets.QWidget, calculateui.Ui_Form):
    def __init__(self):
        super(ChildrenForm_calculateillegal, self).__init__()
        self.setupUi(self)


# 关联规则离线展示界面
class offline_rulesmenu(QtWidgets.QWidget):
    def __init__(self, row, column, content):
        super().__init__()

        self.addTable(row, column, content)

    def addTable(self, row, column, content):
        self.setWindowTitle('关联规则离线查看器')
        self.resize(400, 600)
        layout = QtWidgets.QHBoxLayout()
        tabel = QtWidgets.QTableWidget()
        tabel.setRowCount(row)
        tabel.setColumnCount(column)
        layout.addWidget(tabel)
        tabel.setHorizontalHeaderLabels(['条件项集', '结果项集', '支持度', '置信度'])
        tabel.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        for i, j in enumerate(content):
            newItem = QtWidgets.QTableWidgetItem(str(j))
            tabel.setItem(int(i / 4), i % 4, newItem)
        self.setLayout(layout)


# 关联规则在线挖取界面
class online_rulesmenu(QtWidgets.QWidget, online_rules.Ui_Form):
    def __init__(self):
        super(online_rulesmenu, self).__init__()
        self.setupUi(self)
        # 子界面的按钮触发放在子界面的init下即可
        self.startmining.clicked.connect(lvtong.startMining)


# 主界面
class lvtonglogic(QtWidgets.QMainWindow, lvtongui.Ui_MainWindow):
    # mySignal = QtCore.pyqtSignal(str)

    def __init__(self):
        super(lvtonglogic, self).__init__()
        self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint)

        self.setupUi(self)
        # 自动设置时间为当前系统时间
        time = QDateTime.currentDateTime()
        timeDisplay = time.toString('yyyy-MM-dd hh:mm:ss')
        self.time.setText(timeDisplay)

        # self.child = ChildrenForm_calculateillegal()
        # self.pushButton.clicked.connect(self.showresult)

    # def calculateShow(self):
    #     self.calculatelayout.addWidget(self.child)
    #     self.child.show()

    def getinfo(self):
        carid = self.carid.displayText()
        cartype = self.cartype.currentText()
        weight = self.weight.displayText()
        inport = self.driveinplace.displayText()
        outport = self.driveoutplace.displayText()
        goods = self.goods.displayText()
        axle = self.axle.text()
        # 因为暂时只有1-6月份数据，所以此处默认使用5.18日
        # time = (self.time.text().split('-')[1]+'/'+self.time.text().split('-')[2]).split(' ')[0]
        time = '5/18'
        calculateParam = [cartype, outport, inport, time, goods, weight]
        allParam = [carid, cartype, weight, inport, outport, goods, axle, time]
        return calculateParam, allParam

    # def sendin
    # fo2cal(self):
    #     content = 'lallal'
    #     print(content)
    #     self.mySignal.emit(content)

    def sendinfo2cal(self):
        try:
            self.cal = ChildrenForm_calculateillegal()
            content = queryByCarid(self.carid.displayText())
            calculateParam = self.getinfo()[0]
            # 接入用户数据，调用模型预测函数
            content2 = rf_predict(calculateParam)

            self.cal.textEdit.setText(content + content2)
            self.cal.show()
        except Exception as e:
            self.cal.textEdit.setText('您输入的出入口站或是货物类型不在模型中，请更新模型后重试')
            print(e)
            self.cal.show()


    def saveData2MySql(self):
        allParam = self.getinfo()[1]
        # ['', '计货1', '', '', '', '', '0', '5/18']原格式插入被认为是八行一列，只有reshape才能按行插入
        # ValueError: Shape of passed values is (1, X), indices imply (X, X)
        # print(allParam)
        if allParam.count('') > 0:
            QtWidgets.QMessageBox.about(self, '警告', '有信息值为空，请填充')
        else:
            dfuser = pd.DataFrame(np.array(allParam).reshape(1, 8),
                                  columns=['carid', 'cartype', 'weight', 'inport', 'outport', 'goods', 'axle', 'time'])
            userInputData2mysql(dfuser)
            QtWidgets.QMessageBox.about(self, '存储中~~~', '存储成功')

    # menu read help document
    def help(self):
        #with open('E:\lvtongEazyVersion\data\help.txt', 'r', encoding='utf-8') as file:
        with open('data\help.txt', 'r', encoding='utf-8') as file:
            helpContent = file.read()
            QtWidgets.QMessageBox.about(self, '帮助文档', helpContent)

    # menu read version document
    def version(self):
        #with open('E:\lvtongEazyVersion\data\lvtongversion.txt', 'r', encoding='utf-8') as file:
        with open('data\lvtongversion.txt', 'r', encoding='utf-8') as file:
            versionContent = file.read()
            QtWidgets.QMessageBox.about(self, '版本信息', versionContent)

    def offline_associate(self):
        #with open('E:\lvtongEazyVersion\data\interval_goods_rule2.txt', 'r', encoding='gbk') as file:
        with open('data\interval_goods_rule2.txt', 'r', encoding='gbk') as file:
            content = []
            count = 0
            # file已经是读取好了，不用在file.readline 了
            for line in file:
                pattern = re.compile(r'[{|}]')
                items = re.split(pattern, line)
                # print(items)
                item1 = items[1]
                item2 = items[3]
                support = line.split(' ')[2]
                prob = line.split(' ')[3]
                count = count + 1
                content.extend([item1, item2, support, prob])
        # 如果子窗口不作为成员变量出现，直接rules=offline_rulesmenu()创建，创建一瞬间就销毁了，表现出来就是窗口一闪而过
        self.rulesoffline = offline_rulesmenu(count, 4, content)
        self.rulesoffline.show()

    def online_associate(self):
        self.online_associate = online_rulesmenu()
        self.online_associate.show()

    # 注意重量除了一百，单位为百千克，金额除了一百单位为，百元
    def startMining(self):
        itemset = [self.online_associate.miningitem1.currentText(),
                   self.online_associate.miningitem2.currentText(),
                   self.online_associate.miningitem3.currentText(),
                   self.online_associate.miningitem4.currentText()]
        rules = rule_mining(itemset)
        content = []
        count = 0
        for line in rules:
            temp = ' '.join(list(map(str, line)))
            # print(line)
            pattern = re.compile(r'[{|}]')
            items = re.split(pattern, temp)
            # print(items)
            # print(items)
            item1 = items[1]
            item2 = items[3]
            support = str(line[2])
            prob = str(line[3])
            count = count + 1
            content.extend([item1, item2, support, prob])
        self.rulesoffline = offline_rulesmenu(count, 4, content)
        self.rulesoffline.show()

    # menu updateModel
    def updateModelParams(self):
        update_records_num = queryUpdateRecords('user_input_data').values[0]
        QtWidgets.QMessageBox.about(self,'提示','共新增了'+str(update_records_num)+'条数据，确认更新')

    # enter mysqlmode
    def mysqlQueryMode(self):
        if (loginwidget.usergroup!='admin'):
            QtWidgets.QMessageBox.about(self, '警告', '只有超级管理员才具有进入可视数据库模块权限')
        else:
            QtWidgets.QMessageBox.about(self,'警告','进入数据库编辑模式，请确认后操作！')
            sqlmodewidget.show()



    # userinfo Of current user
    def userInfo(self):
        user = loginwidget.user
        usergroup = loginwidget.usergroup
        QtWidgets.QMessageBox.about(self, '用户信息',
                                    '尊敬的:' + user + '\t用户组：' + usergroup + '\n    欢迎使用Sunshinelvtong大数据辅助系统\n上次登录时间:2018/12/7 15:22:12')


if __name__ == '__main__':
    #freeze_support()
    app = QtWidgets.QApplication(sys.argv)
    #print(sys.argv)
    #['E:/neunn/lvtongprogram/lvtonguilogic.py']
    # login = userlogin()

    calculateWidget = ChildrenForm_calculateillegal()
    startingimage()

    loginwidget = userlogin()
    loginwidget.show()
    lvtong = lvtonglogic()
    mysqlThread = sqlThread()
    sqlmodewidget = sqlmode()

    # lvtong.show()
    lvtong.calculateillegal.clicked.connect(lvtong.sendinfo2cal)
    lvtong.store2mysql.clicked.connect(lvtong.saveData2MySql)
    # menubar 查看
    lvtong.read_help.triggered.connect(lvtong.help)
    lvtong.read_soft_info.triggered.connect(lvtong.version)
    lvtong.read_associate.triggered.connect(lvtong.offline_associate)
    # menubar 功能
    lvtong.mine_rules.triggered.connect(lvtong.online_associate)
    lvtong.update_modelparams.triggered.connect(lvtong.updateModelParams)
    lvtong.mysql_pattern.triggered.connect(lvtong.mysqlQueryMode)

    # menubar 我的
    lvtong.user_info.triggered.connect(lvtong.userInfo)

    # 如果我们在ui里写了信号和槽我们只需要在界面类里实现对应的槽函数就行了，而无需手动调用。
    # lvtong.calculateillegal.click.connect(lvtong.showresult)
    # 这个循环一直在监听事件，但是没有信号传送貌似状态不刷新，所以getInput没接受到改变之后的文字
    # getInput(lvtong)

    sys.exit(app.exec_())
