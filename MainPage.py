# from PyQt5.QtWidgets import QMainWindow, QTextEdit,QDesktopWidget, QFileDialog, QApplication,QPushButton,QTableWidget,QAbstractItemView,QComboBox,QHBoxLayout,QWidget,QGroupBox,QVBoxLayout
import sys
from PyQt5.QtWidgets import *

from PyQt5.QtCore import QThread,pyqtSignal,Qt
from plugins.Craw_cnki.Craw_cnki import Craw_cnki
import LoadPlugins as lp
class CrawCnkiThread(QThread):
    '''信号槽获取爬虫对象的爬取进度信息'''
    crawSignal=pyqtSignal(str)
    def __init__(self,filepath=None,propath=None):
        super().__init__()
        '''实例化爬虫对象'''
        self.craw_cnki = Craw_cnki(filepath=filepath,propath=propath)
    '''启动线程'''
    def run(self):
        self.craw_cnki.CrawProcess.connect(self.update)
        self.craw_cnki.run()
        self.craw_cnki.saveData()
    '''传递爬虫对象中的进度信息'''
    def update(self,data):
        self.crawSignal.emit(data)
    '''停止线程'''
    def stop(self):
        self.craw_cnki.stop()
    '''加载爬虫对象属性信息'''
    def loadFromConfig(self):
        # self.craw_cnki.loadFromConfig()
        return self.craw_cnki.getParameters()

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.initUI()
        self.names=self.__dict__
        self.filePath=None
        self.proPath=None
        '''plugin_job用来存储插件线程,jobList用来存储插件名'''
        self.plugin_job=[]
        self.jobList = []

        self.setup_main_window()
        self.set_window_layout()
        self.craw_cnki_thread = CrawCnkiThread(filepath=self.filePath,propath=self.proPath)

    def setup_main_window(self):
        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)
        self.resize(800, 600)
        self.setWindowTitle("基于科技文献资料的数据抓取、识别及分析技术开发及应用")

    def set_window_layout(self):
        self.textEdit = QTextEdit()
        self.horizontalLayout = QHBoxLayout(self.centralwidget)

        '''设置表格'''
        self.TableWidget = QTableWidget(6, 6)
        self.TableWidget.setHorizontalHeaderLabels(['序号','选中', '状态', '名称', '描述','配置文件修改'])
        self.TableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.TableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        '''第一列随内容改变列宽'''
        self.TableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        self.horizontalGroupBox = QGroupBox("数据自动采集、移植及更新")
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

        self.main_horizontal_2_layout = QVBoxLayout()

        self.filepath_horizontal_layout = QHBoxLayout()
        self.filepath_horizontal_layout.addWidget(self.lb_filepath)
        self.filepath_horizontal_layout.addWidget(self.le_filepath)
        self.filepath_horizontal_layout.addWidget(self.btn_filepath)

        self.propath_horizontal_layout = QHBoxLayout()
        self.propath_horizontal_layout.addWidget(self.lb_propath)
        self.propath_horizontal_layout.addWidget(self.le_propath)
        self.propath_horizontal_layout.addWidget(self.btn_propath)

        self.main_horizontal_2_layout.addLayout(self.filepath_horizontal_layout)
        self.main_horizontal_2_layout.addLayout(self.propath_horizontal_layout)
        self.main_horizontal_2_layout.setSpacing(6)

        self.main_vertical_layout.addLayout(self.main_horizontal_1_layout)
        self.main_vertical_layout.addLayout(self.main_horizontal_layout)

        self.label_1=QLabel(self)
        self.label_1.setText('爬虫列表')
        self.label_1.setAlignment(Qt.AlignLeft)
        self.main_vertical_layout.addWidget(self.label_1)

        self.main_vertical_layout.addWidget(self.TableWidget)

        self.label_2 = QLabel(self)
        self.label_2.setText('路径')
        self.label_2.setAlignment(Qt.AlignLeft)
        self.main_vertical_layout.addWidget(self.label_2)

        self.main_vertical_layout.addLayout(self.main_horizontal_2_layout)

        self.label_3 = QLabel(self)
        self.label_3.setText('爬取进度')
        self.label_3.setAlignment(Qt.AlignLeft)
        self.main_vertical_layout.addWidget(self.label_3)

        self.main_vertical_layout.addWidget(self.textEdit)


    '''根据插件名，加载对应的插件线程'''
    def Plugin_Switch(self,plugin_name):
        plugins={
            'Craw_cnki':[self.cnki_plugin_init(),plugin_name[1]],
            'Craw_baidu':None
        }
        return plugins.get(plugin_name[0],None)
    '''启动插件'''
    def work(self):
        '''修改对应按钮状态'''
        self.btn3.setEnabled(True)
        self.btn2.setEnabled(False)
        '''强制页面刷新'''
        QApplication.processEvents()
        # print(self.jobList)
        '''更新当前选中插件列表'''
        temp=[]
        for job_name in self.jobList:
            temp.append(self.Plugin_Switch(job_name))
        self.plugin_job=temp
        # print(self.plugin_job)
        QApplication.processEvents()
        '''job[0]为线程对象,job[1]为对应的行号,通过行号修改爬取状态'''
        for job in self.plugin_job:
            try:
                state = QTableWidgetItem('正在爬取')
                state.setTextAlignment(Qt.AlignCenter)
                job[0].start()
                self.TableWidget.setItem(job[1], 2,state)
            except:
                pass
        QApplication.processEvents()

    '''cnki插件线程初始化'''
    def cnki_plugin_init(self):
        self.craw_cnki_thread = CrawCnkiThread(filepath=self.filePath,propath=self.proPath)
        '''通过信号槽传递,实现实时更新爬取进度'''
        self.craw_cnki_thread.crawSignal.connect(self.updateTextEdit)
        return self.craw_cnki_thread

    '''更新页面显示进度'''
    def updateTextEdit(self,info):
        self.textEdit.setText(info)

    '''停止插件运行'''
    def stop(self):
        self.btn3.setEnabled(False)
        self.btn2.setEnabled(True)
        QApplication.processEvents()
        # print(self.plugin_job)
        '''依次执行插件任务'''
        for job in self.plugin_job:
            try:
                '''修改爬取状态'''
                state = QTableWidgetItem('结束爬取')
                state.setTextAlignment(Qt.AlignCenter)
                self.TableWidget.setItem(job[1], 2, state)
                job[0].stop()
            except:
                pass
        QApplication.processEvents()
        self.textEdit.setText('爬取结束')

    '''显示配置文件内容'''
    def showConfigFile(self,ConfigFilePath):
        dialog=QDialog()
        dialog.resize(600, 400)
        config_layout = QHBoxLayout(dialog)
        '''用于显示配置文件内容'''
        configEdit=QTextEdit()
        btn_save=QPushButton('保存')
        try:
            str_xml = open(ConfigFilePath, 'r').read()
            configEdit.setText(str_xml)
        except:
            pass
        btn_save.clicked.connect(lambda: self.saveConfigFile(ConfigFilePath,configEdit.toPlainText()))
        config_layout.addWidget(configEdit)
        config_layout.addWidget(btn_save)
        dialog.setWindowTitle('修改配置文件')
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()

    '''保存修改的配置文件,ConfigFilePath为文件路径,content为修改后的内容'''
    def saveConfigFile(self,ConfigFilePath,content):
        try:
            '''将修改后的配置文件内容保存'''
            with open(ConfigFilePath,'w') as f:
                f.write(content)
                QMessageBox.about(self,'提示','修改成功')
        except:
            pass
        self.initTable()

    '''修改默认文件存储路径'''
    def modifFilepath(self):
        path = QFileDialog.getExistingDirectory(self, 'choose file')
        self.le_filepath.setText(path)
        self.filePath=path
        self.craw_cnki_thread = CrawCnkiThread(filepath=self.filePath,propath=self.proPath)

    '''修改默认属性文件存储路径'''
    def modifPropath(self):
        path = QFileDialog.getExistingDirectory(self, 'choose file')
        self.le_propath.setText(path)
        self.proPath=path
        self.craw_cnki_thread = CrawCnkiThread(filepath=self.filePath,propath=self.proPath)

    '''选择插件目录'''
    def showDialog(self):
        self.filename=QFileDialog.getExistingDirectory(self,'choose file')
        self.textEdit_configPath.setText(self.filename)
        self.initTable()

    '''表格内容刷新'''
    def initTable(self):
        if self.filename != " " and self.filename !="":
            plgs = lp.getAllPlugin(self.filename)
            if len(plgs):
                # print(plgs)
                '''CheckBox键值对，键为CheckBox对象，值为对应的插件库名称'''
                self.cb_dict={}
                btn_modify_config=[i for i in range(len(plgs))]
                for index, plg in enumerate(plgs):
                    plg_info=lp.call_plugin(plg,'getParameters',filepath=self.filePath,propath=self.proPath)
                    if plg_info['name']:
                        '''对应表格中序号、状态、名称、描述，并设置居中'''
                        id=QTableWidgetItem(str(index+1))
                        id.setTextAlignment(Qt.AlignCenter)
                        state = QTableWidgetItem('等待爬取')
                        state.setTextAlignment(Qt.AlignCenter)
                        name = QTableWidgetItem(plg_info['name'])
                        name.setTextAlignment(Qt.AlignCenter)
                        describe = QTableWidgetItem(plg_info['describe'])
                        describe.setTextAlignment(Qt.AlignCenter)

                        '''在CheckBox外添加一层layout，使其居中'''
                        h = QHBoxLayout()
                        self.names['cb_'+str(index)]=QCheckBox('', self)
                        h.addWidget(self.names['cb_'+str(index)])
                        '''设置居中'''
                        h.setAlignment(Qt.AlignCenter)
                        w = QWidget()
                        w.setLayout(h)

                        '''将行号一并传递'''
                        self.cb_dict[self.names['cb_'+str(index)]]=[plg,index]
                        self.TableWidget.setItem(index, 0, id)
                        self.TableWidget.setCellWidget(index, 1, w)
                        self.TableWidget.setItem(index, 2, state)
                        self.TableWidget.setItem(index, 3, name)
                        self.TableWidget.setItem(index, 4, describe)
                        '''动态添加修改配置文件按钮'''
                        self.setRowData(index,btn_modify_config,plg_info['configPath'])
                        self.le_filepath.setText(plg_info['filepath'])
                        self.le_propath.setText(plg_info['propath'])
                '''绑定CheckBox改变事件'''
                for cb in self.cb_dict.keys():
                    cb.stateChanged.connect(lambda :self.changecb())

    '''动态在TableWidget中添加组件'''
    def setRowData(self, row, btn_modify_config,ConfigFilePath):
        btn_modify_config[row] = QPushButton('修改')
        btn_modify_config[row].clicked.connect(lambda: self.showConfigFile(ConfigFilePath))
        self.TableWidget.setCellWidget(row, 5, btn_modify_config[row])

    '''动态改变多选框选择内容，通过循环遍历实现动态加载'''
    def changecb(self):
        cb_checked=[]
        for cb in self.cb_dict.keys():
            if cb.isChecked():
                cb_checked.append(self.cb_dict[cb])
        self.jobList=cb_checked
        print(self.jobList)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
