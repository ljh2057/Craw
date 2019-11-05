# from PyQt5.QtWidgets import QMainWindow, QTextEdit,QDesktopWidget, QFileDialog, QApplication,QPushButton,QTableWidget,QAbstractItemView,QComboBox,QHBoxLayout,QWidget,QGroupBox,QVBoxLayout
import sys
from PyQt5.QtWidgets import *

from PyQt5.QtCore import QThread,pyqtSignal,Qt
from plugins.Craw_cnki.Craw_cnki import Craw_cnki
import LoadPlugins as lp
class CrawCnkiThread(QThread):
    cnkiSignal=pyqtSignal(str)
    craw_cnki = Craw_cnki()
    def run(self):
        # self.craw_cnki = Craw_cnki()
        self.craw_cnki.CrawProcess.connect(self.update)
        # self.craw_cnki.loadFromConfig()
        self.craw_cnki.run()
        self.craw_cnki.saveData()

    def update(self,data):
        self.cnkiSignal.emit(data)
    def stop(self):
        self.craw_cnki.stop()
    def loadFromConfig(self):
        # self.craw_cnki.loadFromConfig()
        return self.craw_cnki.getParameters()

class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        # self.initUI()
        self.names=self.__dict__

        self.setup_main_window()
        self.set_window_layout()
        self.craw_cnki_thread = CrawCnkiThread()
        self.filePath=None
        self.proPath=None

    def setup_main_window(self):
        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)
        self.resize(800, 600)
        self.setWindowTitle("Test")

    def set_window_layout(self):
        self.textEdit = QTextEdit()

        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        # self.horizontalLayout.addWidget(self.textEdit)

        # 设置表格
        self.TableWidget = QTableWidget(5, 5)
        self.TableWidget.setHorizontalHeaderLabels(['序号','选中', '状态', '名称', '描述'])
        self.TableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.TableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.TableWidget.setTextAlignment()


        self.horizontalGroupBox = QGroupBox("My Group")
        self.horizontalLayout.addWidget(self.horizontalGroupBox)

        btn = QPushButton('选择目录', self)
        btn.clicked.connect(self.showDialog)

        self.btn2 = QPushButton('开始爬取', self)
        self.btn2.clicked.connect(self.work)

        self.btn3 = QPushButton('结束爬取', self)
        self.btn3.clicked.connect(self.stop)
        self.btn3.setEnabled(False)

        self.main_horizontal_layout = QHBoxLayout()
        self.main_vertical_layout = QVBoxLayout()
        self.horizontalGroupBox.setLayout(self.main_vertical_layout)
        self.main_vertical_layout.addStretch(1)

        self.main_horizontal_1_layout = QHBoxLayout()
        self.textEdit_configPath = QLineEdit(self)
        self.main_horizontal_1_layout.addWidget(btn)
        self.main_horizontal_1_layout.addWidget(self.textEdit_configPath)

        self.main_horizontal_layout.addWidget(self.btn2)
        self.main_horizontal_layout.addWidget(self.btn3)

        self.lb_filepath=QLabel('文件位置',self)
        self.le_filepath=QLineEdit()
        self.btn_filepath = QPushButton('选择', self)
        self.btn_filepath.clicked.connect(self.modifFilepath)

        self.lb_propath=QLabel('属性位置',self)
        self.le_propath=QLineEdit(self)
        self.btn_propath = QPushButton('选择', self)
        self.btn_propath.clicked.connect(self.modifPropath)

        self.main_horizontal_2_layout = QHBoxLayout()
        self.main_horizontal_2_layout.addWidget(self.lb_filepath)
        self.main_horizontal_2_layout.addWidget(self.le_filepath)
        self.main_horizontal_2_layout.addWidget(self.btn_filepath)

        self.main_horizontal_3_layout = QHBoxLayout()
        self.main_horizontal_3_layout.addWidget(self.lb_propath)
        self.main_horizontal_3_layout.addWidget(self.le_propath)
        self.main_horizontal_3_layout.addWidget(self.btn_propath)

        self.main_vertical_layout.addLayout(self.main_horizontal_1_layout)
        self.main_vertical_layout.addLayout(self.main_horizontal_layout)
        self.main_vertical_layout.addWidget(self.TableWidget)
        self.main_vertical_layout.addLayout(self.main_horizontal_2_layout)
        self.main_vertical_layout.addLayout(self.main_horizontal_3_layout)
        self.main_vertical_layout.addWidget(self.textEdit)

    def work(self):
        self.btn3.setEnabled(True)
        self.btn2.setEnabled(False)
        print(self.jobList)
        self.craw_cnki_thread.cnkiSignal.connect(self.updateTextEdit)
        self.craw_cnki_thread.start()
        QApplication.processEvents()


    def updateTextEdit(self,info):
        self.textEdit.setText(info)

    def stop(self):
        self.btn3.setEnabled(False)
        self.btn2.setEnabled(True)
        QApplication.processEvents()
        self.craw_cnki_thread.stop()
        QApplication.processEvents()




    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    def modifFilepath(self):
        path = QFileDialog.getExistingDirectory(self, 'choose file')
        self.le_filepath.setText(path)
        self.filePath=path
        self.craw_cnki=Craw_cnki(filepath=self.filePath,propath=self.proPath)

    def modifPropath(self):
        path = QFileDialog.getExistingDirectory(self, 'choose file')
        self.le_propath.setText(path)
        self.proPath=path
        self.craw_cnki=Craw_cnki(filepath=self.filePath,propath=self.proPath)

    def showDialog(self):
        self.filename=QFileDialog.getExistingDirectory(self,'choose file')
        self.textEdit_configPath.setText(self.filename)

        self.jobList = []
        if self.filename != " " and self.filename !="":

            plgs = lp.getAllPlugin(self.filename)
            if len(plgs):
                print(plgs)

                self.cb_list=[]

                for index, plg in enumerate(plgs):
                    plg_info=lp.call_plugin(plg,'getParameters',filepath=self.filePath,propath=self.proPath)
                    if plg_info['name']:
                        id=QTableWidgetItem(str(index+1))
                        id.setTextAlignment(Qt.AlignCenter)
                        state = QTableWidgetItem('等待爬取')
                        state.setTextAlignment(Qt.AlignCenter)
                        name = QTableWidgetItem(plg_info['name'])
                        name.setTextAlignment(Qt.AlignCenter)

                        describe = QTableWidgetItem(plg_info['describe'])
                        describe.setTextAlignment(Qt.AlignCenter)

                        h = QHBoxLayout()
                        self.names['cb_'+str(index)]=QCheckBox('', self)

                        h.addWidget(self.names['cb_'+str(index)])

                        h.setAlignment(Qt.AlignCenter)
                        w = QWidget()
                        w.setLayout(h)
                        self.cb_list.append(self.names['cb_'+str(index)])
                        # self.TableWidget.setCellWidget(index, 0, self.names['cb_'+str(index)])
                        self.TableWidget.setItem(index, 0, id)
                        self.TableWidget.setCellWidget(index, 1, w)
                        self.TableWidget.setItem(index, 2, state)
                        self.TableWidget.setItem(index, 3, name)
                        self.TableWidget.setItem(index, 4, describe)
                        self.le_filepath.setText(plg_info['filepath'])
                        self.le_propath.setText(plg_info['propath'])

                for cb in self.cb_list:
                    cb.stateChanged.connect(lambda :self.changecb())

    #动态改变多选框选择内容，通过循环遍历实现动态加载
    def changecb(self):
        cb_checked=[]
        for cb in self.cb_list:
            if cb.isChecked():
                cb_checked.append(cb)
        self.jobList=cb_checked
        print(self.jobList)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    programWindow = Window()
    programWindow.show()
    sys.exit(app.exec_())
