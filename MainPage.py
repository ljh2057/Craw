# from PyQt5.QtWidgets import QMainWindow, QTextEdit,QDesktopWidget, QFileDialog, QApplication,QPushButton,QTableWidget,QAbstractItemView,QComboBox,QHBoxLayout,QWidget,QGroupBox,QVBoxLayout
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QMutex
from plugins.Craw_cnki import Getxml
from ImportFile import SaveData
import pymysql
from PyQt5.QtCore import QThread,pyqtSignal,Qt
from plugins.Craw_cnki.Craw_cnki import Craw_cnki
from plugins.Craw_baidu.Craw_baidu import Craw_baidu
from plugins.Craw_souhu.Craw_souhu import Craw_souhu
import os
import LoadPlugins as lp
qumt1 = QMutex()
qumt2 = QMutex()
qumt3 = QMutex()
class CrawCnkiThread(QThread):
    '''信号槽获取爬虫对象的爬取进度信息'''
    crawSignal=pyqtSignal(str)
    '''该信号作为插件运行结束标志'''
    crawSignal_f=pyqtSignal()
    def __init__(self,filepath=None,propath=None):
        super().__init__()
        '''实例化爬虫对象'''
        self.craw_cnki = Craw_cnki(filepath=filepath,propath=propath)
    '''启动线程'''
    def run(self):
        qumt1.lock()
        qumt2.lock()
        qumt3.lock()
        self.craw_cnki.CrawProcess.connect(self.update)
        self.craw_cnki.run()
        self.craw_cnki.saveData()
        self.crawSignal_f.emit()
        qumt3.unlock()
        qumt2.unlock()
        qumt1.unlock()
    '''传递爬虫对象中的进度信息'''
    def update(self, data):
        self.crawSignal.emit(data)

    '''停止线程'''
    def stop(self):
        self.craw_cnki.stop()
    '''加载爬虫对象属性信息'''
    def loadFromConfig(self):
        return self.craw_cnki.getParameters()
class CrawBaiduThread(QThread):
    '''信号槽获取爬虫对象的爬取进度信息'''
    crawSignal=pyqtSignal(str)
    '''该信号作为插件运行结束标志'''
    crawSignal_f=pyqtSignal()

    def __init__(self,filepath=None,propath=None):
        super().__init__()
        '''实例化爬虫对象'''
        self.craw_baidu = Craw_baidu(filepath=filepath,propath=propath)
    '''启动线程'''
    def run(self):
        qumt1.lock()
        qumt2.lock()
        qumt3.lock()
        self.craw_baidu.CrawProcess.connect(self.update)
        self.craw_baidu.run()
        self.crawSignal_f.emit()
        qumt3.unlock()
        qumt2.unlock()
        qumt1.unlock()
    '''传递爬虫对象中的进度信息'''
    def update(self,data):
        self.crawSignal.emit(data)
    '''停止线程'''
    def stop(self):
        self.craw_baidu.stop()
    '''加载爬虫对象属性信息'''
    def loadFromConfig(self):
        return self.craw_baidu.getParameters()
class CrawSouhuThread(QThread):
    '''信号槽获取爬虫对象的爬取进度信息'''
    crawSignal=pyqtSignal(str)
    '''该信号作为插件运行结束标志'''
    crawSignal_f=pyqtSignal()

    def __init__(self,filepath=None,propath=None):
        super().__init__()
        '''实例化爬虫对象'''
        self.craw_souhu = Craw_souhu(filepath=filepath,propath=propath)
    '''启动线程'''
    def run(self):
        qumt1.lock()
        qumt2.lock()
        qumt3.lock()
        self.craw_souhu.CrawProcess.connect(self.update)
        self.craw_souhu.run()
        self.crawSignal_f.emit()
        qumt3.unlock()
        qumt2.unlock()
        qumt1.unlock()
    '''传递爬虫对象中的进度信息'''
    def update(self,data):
        self.crawSignal.emit(data)
    '''停止线程'''
    def stop(self):
        self.craw_souhu.stop()
    '''加载爬虫对象属性信息'''
    def loadFromConfig(self):
        return self.craw_souhu.getParameters()
class UploadThread(QThread):
    '''信号槽获取爬虫对象的爬取进度信息'''
    uploadSignal = pyqtSignal(str)
    uploadSignal_f=pyqtSignal()

    def __init__(self, configs):
        super().__init__()
        self.configs=configs
        self.configs['flag']=True
        self.up_db = SaveData.BlobDataTestor(self.configs)
    def run(self):
        self.up_db.CrawProcess.connect(self.update)
        if self.configs['type']=='pfile':
            # self.up_db.upload_pfile(self.configs['path'])
            self.up_db.run()
            self.uploadSignal_f.emit()
        # if self.configs['type'] == 'simple':
        #     self.up_db.upload_simple(self.configs["path"])
        # elif self.configs['type'] == 'pfile':
        #     self.up_db.upload_pfile(self.configs["path"])
        # elif self.configs['type'] == 'txt':
        #     self.up_db.upload_txt(self.configs["path"])
        else:
            QMessageBox.about(self, '提示', '导入方式有误,请检查配置文件')
        self.stop()
    '''停止线程'''
    def stop(self):
        self.up_db.stop()
    '''传递进度信息'''
    def update(self,data):
        print(data)
        self.uploadSignal.emit(data)


class Window(QTabWidget):
    def __init__(self):
        super().__init__()
        # self.initUI()
        self.names=self.__dict__
        self.filePath=None
        self.proPath=None
        '''plugin_job用来存储插件线程,jobList用来存储插件名'''
        self.plugin_job=[]
        self.jobList = []
        self.craw_cnki_thread = CrawCnkiThread(filepath=self.filePath,propath=self.proPath)
        self.setWindowTitle("基于科技文献资料的数据抓取、识别及分析技术开发及应用")
        self.resize(800, 600)

        self.tab1=QWidget()
        self.tab2=QWidget()

        self.addTab(self.tab1,'数据自动采集')
        self.addTab(self.tab2,'数据移植、集成与更新')
        '''加载tab1'''
        self.set_tab1_layout()
        self.set_tab2_layout()

    '''数据采集页面start'''
    def set_tab1_layout(self):
        self.textEdit = QTextEdit()
        self.horizontalLayout = QHBoxLayout(self.tab1)

        '''设置表格'''
        self.TableWidget = QTableWidget(6, 6)
        '''隐藏序号'''
        self.TableWidget.verticalHeader().setVisible(False)
        '''设置表头样式,白色背景显示出边框'''
        stylesheet = "QHeaderView::section{Background-color:white}"
        self.setStyleSheet(stylesheet)
        '''设置行距'''
        for index in range(self.TableWidget.rowCount()):
            self.TableWidget.setRowHeight(index,32)
        self.TableWidget.setHorizontalHeaderLabels(['序号','选中', '状态', '名称', '描述','配置文件修改'])
        self.TableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.TableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        '''第一列随内容改变列宽'''
        self.TableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        self.horizontalGroupBox = QGroupBox("")
        self.horizontalLayout.addWidget(self.horizontalGroupBox)

        # btn = QPushButton('加载爬虫', self)
        # btn.clicked.connect(self.showDialog)
        # self.showDialog()

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
        # self.textEdit_configPath = QLineEdit(self)
        # self.main_horizontal_1_layout.addWidget(btn)
        # self.main_horizontal_1_layout.addWidget(self.textEdit_configPath)

        self.main_horizontal_layout.addWidget(self.btn2)
        self.main_horizontal_layout.addWidget(self.btn3)

        self.lb_filepath=QLabel('保存位置',self)
        self.le_filepath=QLineEdit()
        self.btn_filepath = QPushButton('选择', self)
        self.btn_filepath.clicked.connect(self.modifFilepath)

        # self.lb_propath=QLabel('属性位置',self)
        # self.le_propath=QLineEdit(self)
        # self.btn_propath = QPushButton('选择', self)
        # self.btn_propath.clicked.connect(self.modifPropath)

        self.main_horizontal_2_layout = QVBoxLayout()

        '''文件位置布局'''
        self.filepath_horizontal_layout = QHBoxLayout()
        self.filepath_horizontal_layout.addWidget(self.lb_filepath)
        self.filepath_horizontal_layout.addWidget(self.le_filepath)
        self.filepath_horizontal_layout.addWidget(self.btn_filepath)
        # '''属性文件位置布局'''
        # self.propath_horizontal_layout = QHBoxLayout()
        # self.propath_horizontal_layout.addWidget(self.lb_propath)
        # self.propath_horizontal_layout.addWidget(self.le_propath)
        # self.propath_horizontal_layout.addWidget(self.btn_propath)

        self.main_horizontal_2_layout.addLayout(self.filepath_horizontal_layout)
        # self.main_horizontal_2_layout.addLayout(self.propath_horizontal_layout)
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

        self.initTable()

    '''根据插件名，加载对应的插件线程'''
    def Plugin_Switch(self,plugin_name):
        plugins={
            'Craw_cnki':[self.cnki_plugin_init(),plugin_name[1]],
            'Craw_baidu':[self.baidu_plugin_init(),plugin_name[1]],
            'Craw_souhu':[self.souhu_plugin_init(),plugin_name[1]]
        }
        return plugins.get(plugin_name[0],None)
    '''启动插件'''
    def work(self):
        '''更新当前选中插件列表'''
        temp = []
        for job_name in self.jobList:
            temp.append(self.Plugin_Switch(job_name))
        self.plugin_job = temp
        if len(self.plugin_job):
            '''修改对应按钮状态'''
            self.btn3.setEnabled(True)
            self.btn2.setEnabled(False)
            '''强制页面刷新'''
            QApplication.processEvents()
            '''job[0]为线程对象,job[1]为对应的行号,通过行号修改爬取状态'''
            for job in self.plugin_job:
                try:
                    state = QTableWidgetItem('正在爬取')
                    state.setTextAlignment(Qt.AlignCenter)
                    job[0].crawSignal_f.connect(lambda :self.getState(job[1]))
                    job[0].start()
                    self.TableWidget.setItem(job[1], 2,state)
                except:
                    pass
            QApplication.processEvents()
        else:
            QMessageBox.about(self, '提示', '未选择任务')

    '''cnki插件线程初始化'''
    def cnki_plugin_init(self):
        self.craw_cnki_thread = CrawCnkiThread(filepath=self.filePath,propath=self.proPath)
        '''通过信号槽传递,实现实时更新爬取进度'''
        self.craw_cnki_thread.crawSignal.connect(self.updateTextEdit)
        return self.craw_cnki_thread

    '''baidu插件线程初始化'''
    def baidu_plugin_init(self):
        self.craw_baidu_thread = CrawBaiduThread(filepath=self.filePath, propath=self.proPath)
        '''通过信号槽传递,实现实时更新爬取进度'''
        self.craw_baidu_thread.crawSignal.connect(self.updateTextEdit)
        return self.craw_baidu_thread

    '''souhu插件线程初始化'''
    def souhu_plugin_init(self):
        self.craw_souhu_thread = CrawSouhuThread(filepath=self.filePath, propath=self.proPath)
        '''通过信号槽传递,实现实时更新爬取进度'''
        self.craw_souhu_thread.crawSignal.connect(self.updateTextEdit)
        return self.craw_souhu_thread

    '''更新页面显示进度'''
    def updateTextEdit(self,info):
        self.textEdit.setText(info)

    '''插件运行结束后更新页面爬取状态'''
    def getState(self,index):
        print(index)
        state = QTableWidgetItem('爬取完成')
        state.setTextAlignment(Qt.AlignCenter)
        self.TableWidget.setItem(index, 2, state)
        self.btn3.setEnabled(False)
        self.btn2.setEnabled(True)
        QApplication.processEvents()

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
        print(ConfigFilePath)
        dialog=QDialog()
        dialog.resize(600, 400)
        config_layout = QHBoxLayout(dialog)
        '''用于显示配置文件内容'''
        configEdit=QTextEdit()
        btn_save=QPushButton('保存')
        try:
            str_xml = open(ConfigFilePath, 'r',encoding='UTF-8').read()
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
            with open(ConfigFilePath,'w',encoding='UTF-8') as f:
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
        self.proPath=path
        # self.craw_cnki_thread = CrawCnkiThread(filepath=self.filePath,propath=self.proPath)

    # '''修改默认属性文件存储路径'''
    # def modifPropath(self):
    #     path = QFileDialog.getExistingDirectory(self, 'choose file')
    #     self.le_propath.setText(path)
    #     self.proPath=path
        # self.craw_cnki_thread = CrawCnkiThread(filepath=self.filePath,propath=self.proPath)

    '''选择插件目录'''
    def showDialog(self):
        self.filename = os.getcwd()+"/plugins"
        self.textEdit_configPath.setText(self.filename)
        self.initTable()

    '''表格内容刷新'''
    def initTable(self):
        self.filename = os.getcwd()+"/plugins"
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
                        # self.le_filepath.setText(plg_info['filepath'])
                        # self.le_propath.setText(plg_info['propath'])
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

    '''数据采集页面end'''




    '''数据移植页面start'''
    def set_tab2_layout(self):
        self.horizontalLayout_tab2 = QHBoxLayout(self.tab2)
        self.horizontalGroupBox_tab2 = QGroupBox("数据自动移植")
        self.horizontalLayout_tab2.addWidget(self.horizontalGroupBox_tab2)

        btn_tab2 = QPushButton('选择配置文件', self)
        btn_tab2.clicked.connect(self.SelectConfigFile)

        self.btn_start = QPushButton('开始导入', self)
        self.btn_start.clicked.connect(self.work_tab2)

        self.btn_stop = QPushButton('结束导入', self)
        self.btn_stop.clicked.connect(self.stop_tab2)
        self.btn_stop.setEnabled(False)
        '''导入类型布局'''
        # self.tab2_horizontal_RadioButton_layout = QHBoxLayout()
        # self.simple_rb=QRadioButton('简单导入')
        # self.pfile_rb=QRadioButton('从属性文件导入')
        # self.txt_rb=QRadioButton('导入txt文本')
        # self.tab2_horizontal_RadioButton_layout.addWidget(self.simple_rb)
        # self.tab2_horizontal_RadioButton_layout.addWidget(self.pfile_rb)
        # self.tab2_horizontal_RadioButton_layout.addWidget(self.txt_rb)


        '''开始、结束按钮布局'''
        self.tab2_horizontal_layout = QHBoxLayout()
        '''主页面布局，垂直布局'''
        self.tab2_vertical_layout = QVBoxLayout()
        self.horizontalGroupBox_tab2.setLayout(self.tab2_vertical_layout)
        # self.tab2_vertical_layout.addStretch(1)
        '''水平布局，选择、编辑配置文件组件'''
        self.main_horizontal_tab2_layout = QHBoxLayout()
        self.textEdit_configPath_tab2 = QLineEdit(self)

        btn_edit = QPushButton('修改', self)
        btn_edit.clicked.connect(lambda: self.showConfigFile_tab2(self.textEdit_configPath_tab2.text()))

        self.main_horizontal_tab2_layout.addWidget(btn_tab2)
        self.main_horizontal_tab2_layout.addWidget(self.textEdit_configPath_tab2)
        self.main_horizontal_tab2_layout.addWidget(btn_edit)

        self.tab2_horizontal_layout.addWidget(self.btn_start)
        self.tab2_horizontal_layout.addWidget(self.btn_stop)

        # self.lb_filepath_tab2=QLabel('文件位置',self)
        # self.le_filepath_tab2=QLineEdit()
        # self.btn_filepath_tab2 = QPushButton('选择', self)
        # self.btn_filepath_tab2.clicked.connect(self.modifFilepath_tab2)

        # self.lb_propath_tab2=QLabel('属性位置',self)
        # self.le_propath_tab2=QLineEdit(self)
        # self.btn_propath_tab2 = QPushButton('选择', self)
        # self.btn_propath_tab2.clicked.connect(self.modifPropath_tab2)
        #
        # self.main_horizontal_tab2_2_layout = QVBoxLayout()
        #
        # '''文件位置布局'''
        # self.filepath_horizontal_tab2_layout = QHBoxLayout()
        # self.filepath_horizontal_tab2_layout.addWidget(self.lb_filepath_tab2)
        # self.filepath_horizontal_tab2_layout.addWidget(self.le_filepath_tab2)
        # self.filepath_horizontal_tab2_layout.addWidget(self.btn_filepath_tab2)
        # '''属性文件位置布局'''
        # self.propath_horizontal_tab2_layout = QHBoxLayout()
        # self.propath_horizontal_tab2_layout.addWidget(self.lb_propath_tab2)
        # self.propath_horizontal_tab2_layout.addWidget(self.le_propath_tab2)
        # self.propath_horizontal_tab2_layout.addWidget(self.btn_propath_tab2)

        # self.main_horizontal_tab2_2_layout.addLayout(self.filepath_horizontal_tab2_layout)
        # self.main_horizontal_tab2_2_layout.addLayout(self.propath_horizontal_tab2_layout)
        # self.main_horizontal_tab2_2_layout.setSpacing(6)

        self.tab2_vertical_layout.addLayout(self.main_horizontal_tab2_layout)
        self.tab2_vertical_layout.addLayout(self.tab2_horizontal_layout)

        # self.label_1 = QLabel(self)
        # self.label_1.setText('导入方式')
        # self.label_1.setAlignment(Qt.AlignLeft)
        # self.tab2_vertical_layout.addWidget(self.label_1)

        # self.tab2_vertical_layout.addLayout(self.tab2_horizontal_RadioButton_layout)


        # self.label_2 = QLabel(self)
        # self.label_2.setText('路径')
        # self.label_2.setAlignment(Qt.AlignLeft)
        # self.tab2_vertical_layout.addWidget(self.label_2)
        # self.tab2_vertical_layout.addLayout(self.main_horizontal_tab2_2_layout)

        self.label_3 = QLabel(self)
        self.label_3.setText('导入进度')
        self.label_3.setAlignment(Qt.AlignLeft)
        self.tab2_vertical_layout.addWidget(self.label_3)
        self.textEdit_tab2 = QTextEdit()
        self.tab2_vertical_layout.addWidget(self.textEdit_tab2)



    '''启动插件'''
    def work_tab2(self):
        '''修改对应按钮状态'''
        self.btn_stop.setEnabled(True)
        self.btn_start.setEnabled(False)
        QApplication.processEvents()
        up_thread=self.upload_init()
        if up_thread is not None:
            up_thread.uploadSignal_f.connect(self.updateState)
            up_thread.start()
        else:
            QMessageBox.about(self, '提示', '文件位置不存在**')
        self.textEdit_tab2.setText('导入完毕')

    '''停止插件运行'''
    def stop_tab2(self):
        self.btn_stop.setEnabled(False)
        self.btn_start.setEnabled(True)
        QApplication.processEvents()
        self.textEdit_tab2.setText('结束导入')

    '''显示配置文件内容'''
    def showConfigFile_tab2(self,ConfigFilePath):
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
        btn_save.clicked.connect(lambda: self.saveConfigFile_tab2(ConfigFilePath,configEdit.toPlainText()))
        config_layout.addWidget(configEdit)
        config_layout.addWidget(btn_save)
        dialog.setWindowTitle('修改配置文件')
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()

    '''导入结束后更新页面按钮'''
    def updateState(self):
        self.btn_stop.setEnabled(False)
        self.btn_start.setEnabled(True)
        QApplication.processEvents()

    '''保存修改的配置文件,ConfigFilePath为文件路径,content为修改后的内容'''
    def saveConfigFile_tab2(self,ConfigFilePath,content):
        try:
            '''将修改后的配置文件内容保存'''
            with open(ConfigFilePath,'w') as f:
                f.write(content)
                QMessageBox.about(self,'提示','修改成功')
        except:
            pass
        self.verifyConfigFile(ConfigFilePath)

    '''初始化上传线程'''
    def upload_init(self):
        filename = self.textEdit_configPath_tab2.text()
        if filename != "" and filename != " ":
            getxml = Getxml.getXml(filename)
            configs = getxml.getDestination()
            if os.path.exists(configs['path']):
                self.upload_thread = UploadThread(configs=configs)
                '''通过信号槽传递,实现实时更新爬取进度'''
                self.upload_thread.uploadSignal.connect(self.updateTextEdit_tab2)
                return self.upload_thread
            else:
                return None
        else:
            QMessageBox.about(self, '提示', '请先选择配置文件')
        return None
    # '''选择文件存储路径'''
    # def modifFilepath_tab2(self):
    #     path = QFileDialog.getExistingDirectory(self, 'choose file')
    #     self.le_filepath_tab2.setText(path)
    #     self.filePath=path
    #
    # '''选择属性文件存储路径'''
    # def modifPropath_tab2(self):
    #     path = QFileDialog.getExistingDirectory(self, 'choose file')
    #     self.le_propath_tab2.setText(path)
    #     self.proPath=path

    '''更新页面显示进度'''
    def updateTextEdit_tab2(self,info):
        self.textEdit_tab2.setText(info)

    '''选择插件目录'''
    def SelectConfigFile(self):
        filename,filetype=QFileDialog.getOpenFileName(self,'choose file','','Text Files(importer.xml)')
        self.textEdit_configPath_tab2.setText(filename)
        self.verifyConfigFile(filename)

    '''验证配置文件，检查配置文件中数据库的连接'''
    def verifyConfigFile(self,filename):
        if filename!= "" and filename!=" ":
            getxml = Getxml.getXml(filename)
            configs = getxml.getDestination()
            try:
                self.conn = pymysql.connect(host=configs['ip'], port=int(configs['port']), user=configs['username'],passwd=configs['password'], db=configs['servicename'])
            except Exception as e:
                QMessageBox.about(self,'提示','数据库连接错误')
                print(e)
            try:
                if self.conn.open:
                    if configs['type']=='pfile':
                        pass
                    # if configs['type'] == 'simple':
                    #     self.simple_rb.click()
                    # elif configs['type'] == 'pfile':
                    #     self.pfile_rb.click()
                    # elif configs['type'] == 'uptxt':
                    #     self.txt_rb.click()
                    else:
                        QMessageBox.about(self, '提示', '导入方式有误,请检查配置文件')
                QApplication.processEvents()

            except Exception as e:
                print(e)
        else:
            QMessageBox.about(self, '提示', '请先选择配置文件')
    '''数据移植页面end'''

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
    os.system("pause")
