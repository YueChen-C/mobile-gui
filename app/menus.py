# -*- coding: utf-8 -*-

import multiprocessing
import os
import subprocess
import sys
import time
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QTextCursor, QFontMetrics
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog
# from gevent.libev.corecffi import SIGNAL

from app.Threadcontrol import MiniThread, waitThread


def app_path():
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)


SYSSTR = os.name
if SYSSTR == "nt":
    SPLIT_STR = '\\'
    POPEN_STR = 'findstr'
    IMOBILE_PATH = os.path.join(app_path(), 'imobiledevice{}'.format(SPLIT_STR))

else:
    IMOBILE_PATH = ''
    POPEN_STR = 'grep'
    SPLIT_STR = '/'

SCREENSHOTS_PATH = os.path.join(app_path(), 'screenshots{}'.format(SPLIT_STR))
CRASHLOG_PATH = os.path.join(app_path(), 'crashlog{}'.format(SPLIT_STR))
APPLICATION_PATH = os.path.join(app_path(), 'application{}'.format(SPLIT_STR))
INI_PATH = os.path.join(app_path(), 'app.ini')
if not os.path.exists(SCREENSHOTS_PATH):
    os.makedirs(SCREENSHOTS_PATH)
if not os.path.exists(CRASHLOG_PATH):
    os.makedirs(CRASHLOG_PATH)
if not os.path.exists(APPLICATION_PATH):
    os.makedirs(APPLICATION_PATH)
multiprocessing.freeze_support()
process_list = []


def getevices():
    androidevices_list = []
    output, errors = subprocess.Popen('adb devices', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE).communicate()

    devices = output.decode("utf-8")
    for device in devices.splitlines():
        if 'device' in device and 'devices' not in device:
            device = device.split('\t')[0]
            androidevices_list.append(device)
    return androidevices_list


def get_iosevices():
    output, errors = subprocess.Popen('{}idevice_id -l'.format(IMOBILE_PATH), shell=True, stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE).communicate()

    devices = output.decode("utf-8")
    return devices.splitlines()


class Ui_MainWindow(object):
    MainWindowSignal = pyqtSignal()

    def __init__(self):
        self.device_id = ""
        self.device_cmd = ""
        self.device_list = []
        self.mobile = 'Android'
        self.search_text = ''
        # self.connect(self.searchEdit, SIGNAL("returnPressed()"), self.set_search)  # 信号绑定到槽

    @staticmethod
    def stop_refresh():
        """ 清理所有进程 
        """
        if process_list:
            for process in process_list:
                process.kill()

    def invoke(self, cmd, background=False):
        self.comboBoxAdd()
        self.TextEdit_cmd.clear()
        if not self.device_list:
            self.TextEdit_cmd.append('命令执行失败，当前没有连接设备，请点击右侧"获取设备"按钮，尝试获取设备。')
            return False
        self.groupCenter.setTitle("执行命令：{}".format(cmd.split('\\')[-1]))
        try:
            if process_list:
                for process in process_list:
                    process.kill()
            if background:
                Thread = MiniThread(cmd)
                process_list.append(Thread)
                Thread.start()
                Thread.sinOut.connect(self.slotAdd)
            else:
                output, errors = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE, stdin=subprocess.PIPE).communicate()
                if errors:
                    self.TextEdit_cmd.append('命令执行执行失败：{0}'.format(errors.decode("utf-8")))
                    return False
                o = output.decode("utf-8")
                if o:
                    self.TextEdit_cmd.append(o)
                    return o
                return True
        except Exception as E:
            self.TextEdit_cmd.append('命令执行出错：{0}'.format(E))
            return False

    def adb(self, args, background=False):
        if self.device_id:
            self.device_cmd = "-s %s" % self.device_id
        cmd = "%s %s %s" % ('adb', self.device_cmd, str(args))
        return self.invoke(cmd, background=background)

    def iOSshell(self, execute, args='', background=False):
        if self.device_id:
            self.device_cmd = "-u {}".format(self.device_id)

        cmd = '{0}{1} {2} {3}'.format(IMOBILE_PATH, execute, self.device_cmd, args)
        return self.invoke(cmd, background=background)

    def shell(self, args, background=False):
        if self.device_id:
            self.device_cmd = "-s %s" % self.device_id
        cmd = "%s %s shell %s" % ('adb', self.device_cmd, str(args),)
        return self.invoke(cmd, background=background)

    def getevice_state(self):
        """
        获取设备状态： offline | bootloader | device
        """
        self.adb("get-state")

    def connect_tcp(self, ip):
        """
        绑定设备信息 用于无线测试
        """
        self.adb('tcpip 5555')
        self.adb('connect {0}:5555'.format(ip))

    def disconnect_tcp(self, ip):
        """
        解除设备信息 用于无线测试
        """
        self.adb('tcpip 5555')
        self.adb('disconnect {0}:5555'.format(ip))

    def getevice_id(self):
        """
        获取设备id号，serialNo
        """
        self.adb("get-serialno")

    def get_version(self):
        """
        获取设备中的Android版本号，如4.2.2
        """
        if self.mobile == 'iOS':
            return self.iOSshell('ideviceinfo', '-k ProductVersion')
        self.shell(
            "getprop ro.build.version.release")

    def get_model(self):
        """
        获取设备型号
        """
        if self.mobile == 'iOS':
            return self.iOSshell('ideviceinfo', '-k ProductType')

        self.shell('getprop ro.product.model')

    def get_brand(self):
        """
        设备名称
        """
        if self.mobile == 'iOS':
            return self.iOSshell('ideviceinfo', '-k ProductName')

        self.shell('getprop ro.product.brand')

    def get_ip(self):
        """
          获取设备 IP 地址
        """
        if self.mobile == 'iOS':
            return self.TextEdit_cmd.setText('iOS 暂时不支持此方法')

        self.shell('ifconfig')

    def get_id(self):
        """
           获取设备 ID 
        """
        if self.mobile == 'iOS':
            return self.iOSshell('ideviceinfo', '-k UniqueDeviceID')
        self.shell('settings get secure android_id')

    def getisplays(self):
        """
        获取设备 displays
        """
        if self.mobile == 'iOS':
            return self.TextEdit_cmd.setText('iOS 暂时不支持此方法')
        self.shell('"dumpsys window displays | grep init"')

    def get_mac(self):
        """
        获取设备 mac 地址
        """
        if self.mobile == 'iOS':
            return self.iOSshell('ideviceinfo', '-k EthernetAddress')

        self.shell('cat /sys/class/net/wlan0/address')

    def get_log(self):
        """
         获取设备 LOG 数据
        """
        if self.mobile == 'iOS':
            return self.iOSshell('idevicesyslog', background=True)
        self.adb('logcat', True)

    def get_log_crash(self):
        """
         获取设备 Crash LOG 数据
        """
        self.TextEdit_cmd.append('正在导出崩溃日志请稍后....')

        if self.mobile == 'iOS':
            reply = QMessageBox.warning(self.centralWidget,
                                        "获取崩溃日志",
                                        "是否确认是否导出 iOS 崩溃日志，导出后手机内日志将清除。",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                cmd = '{0}idevicecrashreport  -u {1}  {2}'.format(IMOBILE_PATH, self.device_id, CRASHLOG_PATH)
                Thread = waitThread(cmd)
                process_list.append(Thread)
                Thread.waitSinOut.connect(self.slotAdd)
                Thread.start()
                return
        self.adb('logcat -b crash', True)

    def clear_log(self):
        reply = QMessageBox.warning(self.centralWidget,
                                    "清除日志",
                                    "是否确认清理缓存日志，清理缓存日志后之前所有日志将不可恢复",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.adb('logcat -c', True)

    def get_top(self):
        if self.mobile == 'iOS':
            return self.TextEdit_cmd.setText('iOS 暂时不支持此方法')
        self.shell('top -m 10', True)

    def get_screencap(self):
        """
        获取截图
        """
        path = '{0}{1}.png'.format(SCREENSHOTS_PATH, int(time.time()))

        if self.mobile == 'iOS':
            self.iOSshell('idevicescreenshot', path)
        else:
            self.adb('exec-out screencap -p > {}'.format(path))
        if os.path.exists(path):
            self.TextEdit_cmd.append('截图成功,截图已保存在：{}'.format(path))
            if os.name == 'nt':
                os.system('explorer.exe "{}"'.format(path))
            else:
                os.system('open "{}"'.format(path))

    def get_list_packages(self):
        if self.mobile == 'iOS':
            return self.iOSshell('ideviceinstaller ', '-l')
        self.shell('pm list packages -3')

    def get_app_pid(self):
        """
        获取 APP PID
        """
        if self.mobile == 'iOS':
            return self.TextEdit_cmd.setText('iOS 暂时不支持此方法')
        app = self.app_list()
        if app:
            pid = self.shell('"ps | grep -m1 {} "'.format(app))
            if isinstance(pid, bool):
                self.TextEdit_cmd.append('{0} 应用未启动'.format(app))
            else:
                self.TextEdit_cmd.append('{0} 应用 PID 为：{1}'.format(app, pid.split()[1]))

    def clear_app_cache(self):
        app = self.app_list()
        if app:
            if self.shell('pm clear {}'.format(app)):
                self.TextEdit_cmd.append('{} 应用缓存已重置'.format(app))

    def uninstall_app(self):
        app = self.app_list()
        if app:
            self.TextEdit_cmd.append('设备：{0} 正在删除应用 {1}'.format(self.device_id, app))
            if self.mobile == 'iOS':
                if self.iOSshell('ideviceinstaller', '-U {}'.format(app)):
                    self.TextEdit_cmd.append('{} 应用已卸载'.format(app))
            else:
                if self.adb('uninstall {}'.format(app)):
                    self.TextEdit_cmd.append('{} 应用已卸载'.format(app))

    def install_app(self):
        self.comboBoxAdd()
        if self.mobile == 'iOS':
            openfile_name = QFileDialog.getOpenFileName(self.centralWidget, '选择文件', '', 'Excel files(*.ipa)')
            cmd = '{0}ideviceinstaller -u {1} -i \"{2}\"'.format(IMOBILE_PATH, self.device_id, openfile_name[0])
        else:
            openfile_name = QFileDialog.getOpenFileName(self.centralWidget, '选择文件', '', 'Excel files(*.apk)')
            cmd = 'adb -s {0} install -r -g \"{1}\"'.format(self.device_id, openfile_name[0])
        if openfile_name[0]:
            self.TextEdit_cmd.clear()
            Thread = waitThread(cmd)
            process_list.append(Thread)
            Thread.waitSinOut.connect(self.slotAdd)
            Thread.start()

    def export_app(self):
        """
        导出已安装 APP 安装包
        """
        app = self.app_list()
        if app:
            self.TextEdit_cmd.append('App 正在导出请稍后...')

            package = self.shell('pm path {}'.format(app))
            if isinstance(package, str):
                package = package.split(':')[1].strip()
                if self.adb('''exec-out "cat {0} ">{1}{2}.apk '''.format(package, APPLICATION_PATH, app)):
                    self.TextEdit_cmd.append('App 已经导出至：{}'.format(APPLICATION_PATH))

    def slotAdd(self, file_inf):
        if 'total' in file_inf and 'running' in file_inf:
            self.TextEdit_cmd.append('\n')
        if self.search_text:
            if self.search_text in file_inf:
                self.TextEdit_cmd.append(file_inf)
                self.TextEdit_cmd.moveCursor(QTextCursor.End)
            return
        self.TextEdit_cmd.append(file_inf)

    def selection_change(self, i):
        self.device_id = self.comboBoxId.currentText()

    def mobile_change(self):
        """ 更换设备类型时，使部分按钮不可点击
        :return:
        """
        self.mobile = self.comboBoxMobile.currentText()
        if self.mobile == 'iOS':
            self.comboBoxAdd()
            self.mActionSubTop.setDisabled(True)
            self.mActionClearLog.setDisabled(True)
            self.mActionSubClearCache.setDisabled(True)
            self.mActionSubPID.setDisabled(True)
        else:
            self.comboBoxAdd()
            self.mActionSubTop.setEnabled(True)
            self.mActionClearLog.setEnabled(True)
            self.mActionSubClearCache.setEnabled(True)
            self.mActionSubPID.setEnabled(True)

    def comboBoxAdd(self):
        """ 获取设备ID，添加至设备列表
        :return:
        """
        i = get_iosevices() if self.mobile == 'iOS' else getevices()
        if not i:
            self.device_id = ''
            self.comboBoxId.clear()
            self.TextEdit_cmd.setText('当前没有连接设备，请检查设备设备是否连接')
            return
        list_index = 0

        try:
            list_index = i.index(self.comboBoxId.currentText())
        except Exception as E:
            self.TextEdit_cmd.setText('获取设备信息报错：{}'.format(E))

        txt = (max(i, key=len))
        metrics = QFontMetrics(self.comboBoxId.font())
        w = metrics.width(txt)
        self.comboBoxId.setMinimumWidth(w)
        self.comboBoxId.clear()
        self.comboBoxId.addItems(i)
        self.comboBoxId.setCurrentIndex(list_index)
        self.device_list = i

    def batch_install_app(self):
        """
        选择安装包弹窗
        """
        self.comboBoxAdd()
        if not self.device_list:
            self.TextEdit_cmd.setText('命令执行失败，当前没有连接设备，请点击右侧"获取设备"按钮，尝试获取设备。')
            return
        if self.mobile == 'iOS':
            openfile_name = QFileDialog.getOpenFileName(self.centralWidget, '选择文件', '', 'Excel files(*.ipa)')
        else:
            openfile_name = QFileDialog.getOpenFileName(self.centralWidget, '选择文件', '', 'Excel files(*.apk)')
        if openfile_name[0]:
            self.TextEdit_cmd.clear()
            self.TextEdit_cmd.append('开始安装：{}'.format(openfile_name[0]))
            self.TextEdit_cmd.append('请勿操作等待软件安装')
            for device in self.device_list:
                self.TextEdit_cmd.append('开始安装设备：{}'.format(device))
                if self.mobile == 'iOS':
                    cmd = '{0}ideviceinstaller -u {1} -i \"{2}\"'.format(IMOBILE_PATH, device, openfile_name[0])
                else:
                    cmd = 'adb -s {0} install -r -g \"{1}\"'.format(device, openfile_name[0])
                Thread = waitThread(cmd)
                process_list.append(Thread)
                Thread.waitSinOut.connect(self.slotAdd)
                Thread.start()

    def batch_uninstall_app(self):
        app = self.app_list()
        self.TextEdit_cmd.clear()
        if app:

            for device in self.device_list:
                self.TextEdit_cmd.append('设备：{0} 正在删除应用 {1}'.format(device, app))
                if self.mobile == 'iOS':
                    cmd = '{0}ideviceinstaller -u {1} -U {2}'.format(IMOBILE_PATH, device, app)
                else:
                    cmd = 'adb -s {0} uninstall {1}'.format(device, app)

                Thread2 = waitThread(cmd)
                process_list.append(Thread2)
                Thread2.waitSinOut.connect(self.slotAdd)
                Thread2.start()

    def app_list(self):
        # 1为默认选中选项目，True/False  列表框是否可编辑。
        try:
            with open(INI_PATH, 'r') as applist:
                items = list(map(lambda x: x.strip('\n'), applist))
        except Exception as E:
            self.TextEdit_cmd.setText('{}'.format(E))
            return
        value, ok = QInputDialog.getItem(self.centralWidget, "选择应用", "请选择应用的包名", items, 1, True)  # 选择确认框
        if ok:
            return value

    def clear_cache(self):
        self.device_cmd = ''
        self.device_id = ''
        self.device_list = []

    def set_search(self):
        self.search_text = self.searchEdit.text()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(596, 717)
        self.centralWidget = QtWidgets.QWidget(MainWindow)  # 主窗口
        self.centralWidget.setObjectName("centralWidget")
        self.gridCentral = QtWidgets.QGridLayout(self.centralWidget)  # 主窗口全局 grid
        self.gridCentral.setObjectName("gridCentral")

        # 页面右侧布局批量安装等
        self.groupBoxRight = QtWidgets.QGroupBox(self.centralWidget) # 右侧控制台 GroupBox
        self.groupBoxRight.setObjectName("groupBoxRight")
        self.groupGridRight = QtWidgets.QGridLayout(self.groupBoxRight)  # 右侧控制台 grid
        self.groupGridRight.setObjectName("groupConsole")


        self.label_mobile = QtWidgets.QLabel()
        self.label_mobile.setObjectName("label_mobile")
        self.label_mobile.setAlignment(Qt.AlignLeft)
        self.comboBoxId = QtWidgets.QComboBox()
        self.comboBoxId.setObjectName("comboBoxId")
        self.comboBoxMobile = QtWidgets.QComboBox()
        self.comboBoxMobile.setObjectName("comboBoxMobile")
        self.comboBoxMobile.addItems(['Android', 'iOS'])
        self.pushButton = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton.setMinimumSize(QtCore.QSize(0, 0))
        self.pushButton.setObjectName("pushButton")
        self.unintallButton = QtWidgets.QPushButton(self.centralWidget)
        self.unintallButton.setMinimumSize(QtCore.QSize(0, 0))
        self.unintallButton.setObjectName("unintallButton")
        self.installButton = QtWidgets.QPushButton(self.centralWidget)
        self.installButton.setMinimumSize(QtCore.QSize(0, 0))
        self.installButton.setObjectName("installButton")
        self.stopButton = QtWidgets.QPushButton(self.centralWidget)
        self.stopButton.setMinimumSize(QtCore.QSize(0, 0))
        self.stopButton.setObjectName("stopButton")
        self.label_right = QtWidgets.QLabel()
        self.label_right.setObjectName("label_right")
        self.label_right.setAlignment(Qt.AlignHCenter)

        self.groupGridRight.addWidget(self.label_mobile, 0, 0, 1, 5, Qt.AlignTop)
        self.groupGridRight.addWidget(self.comboBoxMobile, 0, 1, 1, 5, Qt.AlignTop)
        self.groupGridRight.addWidget(self.comboBoxId, 1, 1, 1, 5, Qt.AlignTop)
        self.groupGridRight.addWidget(self.pushButton, 1, 0, 1, 1, Qt.AlignTop)
        self.groupGridRight.addWidget(self.installButton, 2, 0, 1, 1, Qt.AlignTop)
        self.groupGridRight.addWidget(self.unintallButton, 2, 1, 1, 1, Qt.AlignTop)
        self.groupGridRight.addWidget(self.stopButton, 3, 0, 1, 1, Qt.AlignTop)
        self.groupGridRight.addWidget(self.label_right, 5, 0, 10, 10, Qt.AlignTop)

        # 中间命令行窗口布局

        self.groupCenter = QtWidgets.QGroupBox(self.centralWidget)  # 中间命令行 GroupBox
        self.groupCenter.setObjectName("groupCenter")
        self.groupConsole = QtWidgets.QGridLayout(self.groupCenter)  # 中间命令行 grid
        self.groupConsole.setObjectName("groupConsole")

        self.searchLabel = QtWidgets.QLabel()
        self.searchLabel.setObjectName("searchLabel")
        self.searchEdit = QtWidgets.QLineEdit()
        self.searchEdit.setObjectName("searchEdit")
        self.searchButton = QtWidgets.QPushButton(self.centralWidget)
        self.searchButton.setMinimumSize(QtCore.QSize(0, 0))
        self.searchButton.setObjectName("searchButton")
        self.TextEdit_cmd = QtWidgets.QTextEdit()
        self.TextEdit_cmd.setObjectName("TextEdit_cmd")
        self.TextEdit_cmd.setAlignment(Qt.AlignLeft)
        self.groupConsole.addWidget(self.searchLabel, 0, 0, 1, 1)
        self.groupConsole.addWidget(self.searchEdit, 0, 1, 1, 1)
        self.groupConsole.addWidget(self.searchButton, 0, 2, 1, 1)
        self.groupConsole.addWidget(self.TextEdit_cmd, 1, 0, 1, 3)

        self.gridCentral.addWidget(self.groupCenter, 0, 0, 1, 1)  # 全局布局合成
        self.gridCentral.addWidget(self.groupBoxRight, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)

        # 左侧系统按钮相关布局
        # 注册菜单栏
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 596, 25))
        self.menubar.setObjectName("menubar")
        self.menuMenu = QtWidgets.QMenu(self.menubar)
        self.menuMenu.setObjectName("menuMenu")
        self.menuMenuSub = QtWidgets.QMenu(self.menuMenu)
        self.menuMenuSub.setObjectName("menuMenuSub")
        self.menuMobileSub = QtWidgets.QMenu(self.menuMenu)
        self.menuMobileSub.setObjectName("menuMobileSub")
        MainWindow.setMenuBar(self.menubar)

        # 注册工具栏
        self.sysToolBar = QtWidgets.QToolBar(MainWindow)
        self.sysToolBar.setObjectName("toolBar")
        self.mobileToolBar = QtWidgets.QToolBar(MainWindow)
        self.mobileToolBar.setObjectName("mobileToolBar")
        MainWindow.addToolBar(QtCore.Qt.LeftToolBarArea, self.sysToolBar)
        MainWindow.addToolBar(QtCore.Qt.LeftToolBarArea, self.mobileToolBar)

        self.sysActionA = QtWidgets.QAction(MainWindow)
        self.sysActionA.setObjectName("sysActionA")
        self.sysActionSubSdk = QtWidgets.QAction(MainWindow)
        self.sysActionSubSdk.setObjectName("sysActionSubSdk")
        self.sysActionSubBrand = QtWidgets.QAction(MainWindow)
        self.sysActionSubBrand.setObjectName("sysActionSubBrand")
        self.sysActionSubModel = QtWidgets.QAction(MainWindow)
        self.sysActionSubModel.setObjectName("sysActionSubModel")
        self.sysActionSubIP = QtWidgets.QAction(MainWindow)
        self.sysActionSubIP.setObjectName("sysActionSubIP")
        self.sysActionSubID = QtWidgets.QAction(MainWindow)
        self.sysActionSubID.setObjectName("sysActionSubID")
        self.sysActionSubDisplays = QtWidgets.QAction(MainWindow)
        self.sysActionSubDisplays.setObjectName("sysActionSubDisplays")
        self.sysActionSubMac = QtWidgets.QAction(MainWindow)
        self.sysActionSubMac.setObjectName("sysActionSubMac")
        self.sysActionSubPackages = QtWidgets.QAction(MainWindow)
        self.sysActionSubPackages.setObjectName("sysActionSubPackages")
        self.sysActionSubI = QtWidgets.QAction(MainWindow)
        self.sysActionSubI.setObjectName("sysActionSubI")

        self.mActionA = QtWidgets.QAction(MainWindow)
        self.mActionA.setObjectName("mActionA")
        self.mActionSubTop = QtWidgets.QAction(MainWindow)
        self.mActionSubTop.setObjectName("mActionSubTop")
        self.mActionLog = QtWidgets.QAction(MainWindow)
        self.mActionLog.setObjectName("mActionLog")
        self.mActionClearLog = QtWidgets.QAction(MainWindow)
        self.mActionClearLog.setObjectName("mActionClearLog")
        self.mActionSubCrashLog = QtWidgets.QAction(MainWindow)
        self.mActionSubCrashLog.setObjectName("mActionSubCrashLog")
        self.mActionSubScreencap = QtWidgets.QAction(MainWindow)
        self.mActionSubScreencap.setObjectName("mActionSubScreencap")
        self.mActionSubClearCache = QtWidgets.QAction(MainWindow)
        self.mActionSubClearCache.setObjectName("mActionSubClearCache")
        self.mActionSubUninstall = QtWidgets.QAction(MainWindow)
        self.mActionSubUninstall.setObjectName("mActionSubUninstall")
        self.mActionSubInstall = QtWidgets.QAction(MainWindow)
        self.mActionSubInstall.setObjectName("mActionSubInstall")
        self.mActionSubPID = QtWidgets.QAction(MainWindow)
        self.mActionSubPID.setObjectName("mActionSubPID")
        self.mActionSubExport = QtWidgets.QAction(MainWindow)
        self.mActionSubExport.setObjectName("mActionSubExport")

        # 将按钮添加至菜单栏
        self.menuMobileSub.addAction(self.mActionSubTop)
        self.menuMobileSub.addAction(self.mActionLog)
        self.menuMobileSub.addAction(self.mActionClearLog)
        self.menuMobileSub.addAction(self.mActionSubCrashLog)
        self.menuMobileSub.addAction(self.mActionSubScreencap)
        self.menuMobileSub.addAction(self.mActionSubClearCache)
        self.menuMobileSub.addAction(self.mActionSubUninstall)
        self.menuMobileSub.addAction(self.mActionSubInstall)
        self.menuMobileSub.addAction(self.mActionSubPID)
        self.menuMobileSub.addAction(self.mActionSubExport)

        self.menuMenuSub.addAction(self.sysActionSubSdk)
        self.menuMenuSub.addAction(self.sysActionSubBrand)
        self.menuMenuSub.addAction(self.sysActionSubModel)
        self.menuMenuSub.addAction(self.sysActionSubIP)
        self.menuMenuSub.addAction(self.sysActionSubID)
        self.menuMenuSub.addAction(self.sysActionSubDisplays)
        self.menuMenuSub.addAction(self.sysActionSubMac)
        self.menuMenuSub.addAction(self.sysActionSubPackages)
        self.menuMenuSub.addAction(self.sysActionSubI)

        self.menuMenu.addAction(self.menuMobileSub.menuAction())
        self.menubar.addAction(self.menuMenu.menuAction())
        self.menuMenu.addAction(self.menuMenuSub.menuAction())
        self.menubar.addAction(self.menuMenu.menuAction())

        self.sysToolBar.addAction(self.sysActionA)
        self.sysToolBar.addSeparator()
        self.sysToolBar.addAction(self.sysActionSubSdk)
        self.sysToolBar.addAction(self.sysActionSubBrand)
        self.sysToolBar.addAction(self.sysActionSubModel)
        self.sysToolBar.addAction(self.sysActionSubIP)
        self.sysToolBar.addAction(self.sysActionSubID)
        self.sysToolBar.addAction(self.sysActionSubDisplays)
        self.sysToolBar.addAction(self.sysActionSubMac)
        self.sysToolBar.addAction(self.sysActionSubPackages)

        self.mobileToolBar.addAction(self.mActionA)
        self.mobileToolBar.addSeparator()
        self.mobileToolBar.addAction(self.mActionSubTop)
        self.mobileToolBar.addAction(self.mActionLog)
        self.mobileToolBar.addAction(self.mActionClearLog)
        self.mobileToolBar.addAction(self.mActionSubCrashLog)
        self.mobileToolBar.addAction(self.mActionSubScreencap)
        self.mobileToolBar.addAction(self.mActionSubClearCache)
        self.mobileToolBar.addAction(self.mActionSubUninstall)
        self.mobileToolBar.addAction(self.mActionSubInstall)
        self.mobileToolBar.addAction(self.mActionSubPID)
        self.mobileToolBar.addAction(self.mActionSubExport)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # 按钮绑定触发事件
        self.sysActionSubSdk.triggered.connect(lambda: self.get_version())
        self.sysActionSubBrand.triggered.connect(lambda: self.get_brand())
        self.sysActionSubModel.triggered.connect(lambda: self.get_model())
        self.sysActionSubIP.triggered.connect(lambda: self.get_ip())
        self.sysActionSubID.triggered.connect(lambda: self.get_id())
        self.sysActionSubDisplays.triggered.connect(lambda: self.getisplays())
        self.sysActionSubMac.triggered.connect(lambda: self.get_mac())
        self.sysActionSubPackages.triggered.connect(lambda: self.get_list_packages())

        self.mActionSubTop.triggered.connect(lambda: self.get_top())
        self.mActionLog.triggered.connect(lambda: self.get_log())
        self.mActionClearLog.triggered.connect(lambda: self.clear_log())
        self.mActionSubCrashLog.triggered.connect(lambda: self.get_log_crash())
        self.mActionSubScreencap.triggered.connect(lambda: self.get_screencap())
        self.mActionSubClearCache.triggered.connect(lambda: self.clear_app_cache())
        self.mActionSubUninstall.triggered.connect(lambda: self.uninstall_app())
        self.mActionSubInstall.triggered.connect(lambda: self.install_app())
        self.mActionSubPID.triggered.connect(lambda: self.get_app_pid())
        self.mActionSubExport.triggered.connect(lambda: self.export_app())

        self.pushButton.clicked.connect(lambda: self.comboBoxAdd())
        self.comboBoxId.currentIndexChanged.connect(self.selection_change)
        self.comboBoxMobile.currentIndexChanged.connect(self.mobile_change)

        self.installButton.clicked.connect(self.batch_install_app)
        self.unintallButton.clicked.connect(self.batch_uninstall_app)
        self.stopButton.clicked.connect(self.stop_refresh)

        self.searchEdit.returnPressed.connect(self.set_search)
        self.searchButton.clicked.connect(self.set_search)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupCenter.setTitle(_translate("MainWindow", "执行命令: "))
        self.searchLabel.setText(_translate("MainWindow", "输入筛选内容："))
        self.TextEdit_cmd.setText(_translate("MainWindow", "TextLabel"))
        self.searchButton.setText(_translate("MainWindow", "确认"))
        self.label_right.setText(_translate("MainWindow", "批量安装：给所有连接设备批量安装APK安装包\n"
                                                          "批量卸载：卸载所有连接设备安装包"))

        self.label_mobile.setText(_translate("MainWindow", '设备类型'))
        self.menuMenu.setTitle(_translate("MainWindow", "Menu"))
        self.menuMenuSub.setTitle(_translate("MainWindow", "获取系统信息"))
        self.menuMobileSub.setTitle(_translate("MainWindow", "手机控制"))

        self.sysToolBar.setWindowTitle(_translate("MainWindow", "Tool bar actions"))

        self.sysActionA.setText(_translate("MainWindow", "系统信息"))
        self.sysActionSubSdk.setText(_translate("MainWindow", "获取SDK版本号"))
        self.sysActionSubBrand.setText(_translate("MainWindow", "获取手机名称"))
        self.sysActionSubModel.setText(_translate("MainWindow", "获取手机型号"))
        self.sysActionSubIP.setText(_translate("MainWindow", "获取手机IP"))
        self.sysActionSubID.setText(_translate("MainWindow", "获取手机设备ID"))
        self.sysActionSubDisplays.setText(_translate("MainWindow", "获取手机分辨率"))
        self.sysActionSubMac.setText(_translate("MainWindow", "获取手机Mac地址"))
        self.sysActionSubPackages.setText(_translate("MainWindow", "获取手机应用列表"))

        self.mActionA.setText(_translate("MainWindow", "手机控制"))
        self.mActionSubTop.setText(_translate("MainWindow", "查看资源&进程信息"))
        self.mActionLog.setText(_translate("MainWindow", "获取logcat日志"))
        self.mActionClearLog.setText(_translate("MainWindow", "清空logcat缓存日志"))
        self.mActionSubCrashLog.setText(_translate("MainWindow", "获取近期崩溃日志"))
        self.mActionSubScreencap.setText(_translate("MainWindow", "获取手机截图"))
        self.mActionSubClearCache.setText(_translate("MainWindow", "清理应用缓存"))
        self.mActionSubUninstall.setText(_translate("MainWindow", "删除应用程序"))
        self.mActionSubInstall.setText(_translate("MainWindow", "安装应用程序"))
        self.mActionSubPID.setText(_translate("MainWindow", "获取应用PID"))
        self.mActionSubExport.setText(_translate("MainWindow", "导出已安装的应用"))

        self.comboBoxId.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.comboBoxId.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.comboBoxId.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.pushButton.setText(_translate("DockWidget", "获取设备"))
        self.installButton.setText(_translate("DockWidget", "批量安装软件"))
        self.unintallButton.setText(_translate("DockWidget", "批量卸载软件"))
        self.stopButton.setText(_translate("DockWidget", "停止刷新"))
