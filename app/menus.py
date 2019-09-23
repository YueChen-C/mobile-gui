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


def get_android_devices():
    android_devices_list = []
    output, errors = subprocess.Popen('adb devices', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE).communicate()

    devices = output.decode("utf-8")
    for device in devices.splitlines():
        if 'device' in device and 'devices' not in device:
            device = device.split('\t')[0]
            android_devices_list.append(device)
    return android_devices_list


def get_ios_devices():
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

    @staticmethod
    def stop_refresh():
        if process_list:
            for process in process_list:
                process.kill()

    def invoke(self, cmd, background=False):
        self.comboBoxAdd()
        self.label_cmd.clear()
        if not self.device_list:
            self.label_cmd.append('命令执行失败，当前没有连接设备，请点击右侧"获取设备"按钮，尝试获取设备。')
            return False
        self.groupBox_center.setTitle("执行命令：{}".format(cmd.split('\\')[-1]))
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
                    self.label_cmd.append('命令执行执行失败：{0}'.format(errors.decode("utf-8")))
                    return False
                o = output.decode("utf-8")
                if o:
                    self.label_cmd.append(o)
                    return o
                return True
        except Exception as E:
            self.label_cmd.append('命令执行出错：{0}'.format(E))
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

    def get_device_state(self):
        """
        获取设备状态： offline | bootloader | device
        """
        self.adb("get-state")

    def connect_android_tcp(self, ip):
        """
        绑定设备信息 用于无线测试
        """
        self.adb('tcpip 5555')
        self.adb('connect {0}:5555'.format(ip))

    def disconnect_android_tcp(self, ip):
        """
        解除设备信息 用于无线测试
        """
        self.adb('tcpip 5555')
        self.adb('disconnect {0}:5555'.format(ip))

    def get_device_id(self):
        """
        获取设备id号，serialNo
        """
        self.adb("get-serialno")

    def get_android_version(self):
        """
        获取设备中的Android版本号，如4.2.2
        """
        if self.mobile == 'iOS':
            return self.iOSshell('ideviceinfo', '-k ProductVersion')
        self.shell(
            "getprop ro.build.version.release")

    def get_android_model(self):
        """
        获取设备型号
        """
        if self.mobile == 'iOS':
            return self.iOSshell('ideviceinfo', '-k ProductType')

        self.shell('getprop ro.product.model')

    def get_android_brand(self):
        """
        设备名称
        """
        if self.mobile == 'iOS':
            return self.iOSshell('ideviceinfo', '-k ProductName')

        self.shell('getprop ro.product.brand')

    def get_android_ip(self):
        if self.mobile == 'iOS':
            return self.label_cmd.setText('iOS 暂时不支持此方法')

        self.shell('ifconfig')

    def get_android_id(self):
        if self.mobile == 'iOS':
            return self.iOSshell('ideviceinfo', '-k UniqueDeviceID')
        self.shell('settings get secure android_id')

    def get_android_displays(self):
        if self.mobile == 'iOS':
            return self.label_cmd.setText('iOS 暂时不支持此方法')
        self.shell('"dumpsys window displays | grep init"')

    def get_android_mac(self):
        if self.mobile == 'iOS':
            return self.iOSshell('ideviceinfo', '-k EthernetAddress')

        self.shell('cat /sys/class/net/wlan0/address')

    def get_logcat(self):
        if self.mobile == 'iOS':
            return self.iOSshell('idevicesyslog', background=True)
        self.adb('logcat', True)

    def get_logcat_crash(self):
        self.label_cmd.append('正在导出崩溃日志请稍后....')

        if self.mobile == 'iOS':
            reply = QMessageBox.warning(self.centralwidget,
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

    def clear_logcat(self):
        reply = QMessageBox.warning(self.centralwidget,
                                    "清除日志",
                                    "是否确认清理缓存日志，清理缓存日志后之前所有日志将不可恢复",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.adb('logcat -c', True)

    def get_top(self):
        if self.mobile == 'iOS':
            return self.label_cmd.setText('iOS 暂时不支持此方法')
        self.shell('top -m 10', True)

    def get_screencap(self):
        path = '{0}{1}.png'.format(SCREENSHOTS_PATH, int(time.time()))

        if self.mobile == 'iOS':
            self.iOSshell('idevicescreenshot', path)
        else:
            self.adb('exec-out screencap -p > {}'.format(path))
        if os.path.exists(path):
            self.label_cmd.append('截图成功,截图已保存在：{}'.format(path))
            if os.name == 'nt':
                os.system('explorer.exe "{}"'.format(path))
            else:
                os.system('open "{}"'.format(path))

    def get_list_packages(self):
        if self.mobile == 'iOS':
            return self.iOSshell('ideviceinstaller ', '-l')
        self.shell('pm list packages -3')

    def get_app_pid(self):
        if self.mobile == 'iOS':
            return self.label_cmd.setText('iOS 暂时不支持此方法')
        app = self.app_list()
        if app:
            pid = self.shell('"ps | grep -m1 {} "'.format(app))
            if isinstance(pid, bool):
                self.label_cmd.append('{0} 应用未启动'.format(app))
            else:
                self.label_cmd.append('{0} 应用 PID 为：{1}'.format(app, pid.split()[1]))

    def clear_app_cache(self):
        app = self.app_list()
        if app:
            if self.shell('pm clear {}'.format(app)):
                self.label_cmd.append('{} 应用缓存已重置'.format(app))

    def uninstall_app(self):
        app = self.app_list()
        if app:
            self.label_cmd.append('设备：{0} 正在删除应用 {1}'.format(self.device_id, app))
            if self.mobile == 'iOS':
                if self.iOSshell('ideviceinstaller', '-U {}'.format(app)):
                    self.label_cmd.append('{} 应用已卸载'.format(app))
            else:
                if self.adb('uninstall {}'.format(app)):
                    self.label_cmd.append('{} 应用已卸载'.format(app))

    def install_app(self):
        self.comboBoxAdd()
        if self.mobile == 'iOS':
            openfile_name = QFileDialog.getOpenFileName(self.centralwidget, '选择文件', '', 'Excel files(*.ipa)')
            cmd = '{0}ideviceinstaller -u {1} -i \"{2}\"'.format(IMOBILE_PATH, self.device_id, openfile_name[0])
        else:
            openfile_name = QFileDialog.getOpenFileName(self.centralwidget, '选择文件', '', 'Excel files(*.apk)')
            cmd = 'adb -s {0} install -r -g \"{1}\"'.format(self.device_id, openfile_name[0])
        if openfile_name[0]:
            self.label_cmd.clear()
            Thread = waitThread(cmd)
            process_list.append(Thread)
            Thread.waitSinOut.connect(self.slotAdd)
            Thread.start()

    def export_app(self):
        app = self.app_list()
        if app:
            self.label_cmd.append('App 正在导出请稍后...')

            package = self.shell('pm path {}'.format(app))
            if isinstance(package, str):
                package = package.split(':')[1].strip()
                if self.adb('''exec-out "cat {0} ">{1}{2}.apk '''.format(package, APPLICATION_PATH, app)):
                    self.label_cmd.append('App 已经导出至：{}'.format(APPLICATION_PATH))

    def slotAdd(self, file_inf):
        if 'total' in file_inf and 'running' in file_inf:
            self.label_cmd.append('\n')
        self.label_cmd.moveCursor(QTextCursor.End)
        self.label_cmd.append(file_inf)

    def selection_change(self, i):
        self.device_id = self.comboBoxId.currentText()

    def mobile_change(self):
        """ 更换设备类型时，使部分按钮不可点击
        :return:
        """
        self.mobile = self.comboBoxMobile.currentText()
        if self.mobile == 'iOS':
            self.comboBoxAdd()
            self.mobileActionSubA.setDisabled(True)
            self.mobileActionSubC.setDisabled(True)
            self.mobileActionSubF.setDisabled(True)
            self.mobileActionSubI.setDisabled(True)
        else:
            self.comboBoxAdd()
            self.mobileActionSubA.setEnabled(True)
            self.mobileActionSubC.setEnabled(True)
            self.mobileActionSubF.setEnabled(True)
            self.mobileActionSubI.setEnabled(True)

    def comboBoxAdd(self):
        """ 获取设备ID，添加至设备列表
        :return:
        """
        i = get_ios_devices() if self.mobile == 'iOS' else get_android_devices()
        if not i:
            self.device_id = ''
            self.comboBoxId.clear()
            self.label_cmd.setText('当前没有连接设备，请检查设备设备是否连接')
            return
        list_index = 0

        try:
            list_index = i.index(self.comboBoxId.currentText())
        except Exception as E:
            self.label_cmd.setText('获取设备信息报错：{}'.format(E))

        txt = (max(i, key=len))
        metrics = QFontMetrics(self.comboBoxId.font())
        w = metrics.width(txt)
        self.comboBoxId.setMinimumWidth(w)
        self.comboBoxId.clear()
        self.comboBoxId.addItems(i)
        self.comboBoxId.setCurrentIndex(list_index)
        self.device_list = i

    def batch_install_app(self):
        self.comboBoxAdd()
        if not self.device_list:
            self.label_cmd.setText('命令执行失败，当前没有连接设备，请点击右侧"获取设备"按钮，尝试获取设备。')
            return
        if self.mobile == 'iOS':
            openfile_name = QFileDialog.getOpenFileName(self.centralwidget, '选择文件', '', 'Excel files(*.ipa)')
        else:
            openfile_name = QFileDialog.getOpenFileName(self.centralwidget, '选择文件', '', 'Excel files(*.apk)')
        if openfile_name[0]:
            self.label_cmd.clear()
            self.label_cmd.append('开始安装：{}'.format(openfile_name[0]))
            self.label_cmd.append('请勿操作等待软件安装')
            for device in self.device_list:
                self.label_cmd.append('开始安装设备：{}'.format(device))
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
        self.label_cmd.clear()
        if app:

            for device in self.device_list:
                self.label_cmd.append('设备：{0} 正在删除应用 {1}'.format(device, app))
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
            self.label_cmd.setText('{}'.format(E))
            return
        value, ok = QInputDialog.getItem(self.centralwidget, "选择应用", "请选择应用的包名", items, 1, True) # 选择确认框
        if ok:
            return value

    def clear_cache(self):
        self.device_cmd = ''
        self.device_id = ''
        self.device_list = []

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(596, 717)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.groupBox_center = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_center.setObjectName("groupBox_center")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_center)
        self.gridLayout.setObjectName("gridLayout")

        # 页面右侧布局批量安装等
        self.comboBoxId = QtWidgets.QComboBox()
        self.comboBoxId.setObjectName("comboBoxId")
        self.comboBoxMobile = QtWidgets.QComboBox()
        self.comboBoxMobile.setObjectName("comboBoxMobile")
        self.comboBoxMobile.addItems(['Android', 'iOS'])

        self.pushButton_D = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_D.setMinimumSize(QtCore.QSize(0, 0))
        self.pushButton_D.setObjectName("pushButton")
        self.unintallButton_D = QtWidgets.QPushButton(self.centralwidget)
        self.unintallButton_D.setMinimumSize(QtCore.QSize(0, 0))
        self.unintallButton_D.setObjectName("unintallButton_D")
        self.installButton_D = QtWidgets.QPushButton(self.centralwidget)
        self.installButton_D.setMinimumSize(QtCore.QSize(0, 0))
        self.installButton_D.setObjectName("installButton")
        self.stopButton_D = QtWidgets.QPushButton(self.centralwidget)
        self.stopButton_D.setMinimumSize(QtCore.QSize(0, 0))
        self.stopButton_D.setObjectName("stopButton_D")

        self.label_right = QtWidgets.QLabel()
        self.label_right.setObjectName("label_right")
        self.label_right.setAlignment(Qt.AlignHCenter)

        self.groupBox_right = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_right.setObjectName("groupBox_right")

        self.label_mobile = QtWidgets.QLabel()
        self.label_mobile.setObjectName("label_mobile")
        self.label_mobile.setAlignment(Qt.AlignLeft)

        self.gridLayout_right = QtWidgets.QGridLayout(self.groupBox_right)
        self.gridLayout_right.setObjectName("gridLayout")
        self.gridLayout_right.addWidget(self.label_mobile, 0, 0, 1, 5, Qt.AlignTop)
        self.gridLayout_right.addWidget(self.comboBoxMobile, 0, 1, 1, 5, Qt.AlignTop)
        self.gridLayout_right.addWidget(self.comboBoxId, 1, 1, 1, 5, Qt.AlignTop)
        self.gridLayout_right.addWidget(self.pushButton_D, 1, 0, 1, 1, Qt.AlignTop)
        self.gridLayout_right.addWidget(self.installButton_D, 2, 0, 1, 1, Qt.AlignTop)
        self.gridLayout_right.addWidget(self.unintallButton_D, 2, 1, 1, 1, Qt.AlignTop)
        self.gridLayout_right.addWidget(self.stopButton_D, 3, 0, 1, 1, Qt.AlignTop)
        self.gridLayout_right.addWidget(self.label_right, 5, 0, 10, 10, Qt.AlignTop)

        # 中间命令行窗口布局
        self.label_cmd = QtWidgets.QTextEdit()
        self.label_cmd.setObjectName("label_cmd")
        self.label_cmd.setAlignment(Qt.AlignLeft)

        self.gridLayout.addWidget(self.label_cmd, 0, 0, 1, 1)
        self.gridLayout_7.addWidget(self.groupBox_center, 0, 0, 1, 1)
        self.gridLayout_7.addWidget(self.groupBox_right, 0, 1, 1, 1)

        self.label_71 = QtWidgets.QLabel(self.centralwidget)
        self.label_71.setAlignment(Qt.AlignVCenter)
        self.label_71.setObjectName("label_71")
        self.gridLayout_7.addWidget(self.label_71, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        # 左侧系统按钮相关布局
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 596, 25))
        self.menubar.setObjectName("menubar")
        self.menuMenu = QtWidgets.QMenu(self.menubar)
        self.menuMenu.setObjectName("menuMenu")
        self.menuMenuSub = QtWidgets.QMenu(self.menuMenu)
        self.menuMenuSub.setObjectName("menuMenuSub")
        self.menuMobileSub = QtWidgets.QMenu(self.menuMenu)
        self.menuMobileSub.setObjectName("menuMobileSub")

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        MainWindow.setMenuBar(self.menubar)

        self.sysToolBar = QtWidgets.QToolBar(MainWindow)
        self.sysToolBar.setObjectName("toolBar")
        self.mobileToolBar = QtWidgets.QToolBar(MainWindow)
        self.mobileToolBar.setObjectName("mobileToolBar")
        MainWindow.addToolBar(QtCore.Qt.LeftToolBarArea, self.sysToolBar)
        MainWindow.addToolBar(QtCore.Qt.LeftToolBarArea, self.mobileToolBar)

        self.sysActionA = QtWidgets.QAction(MainWindow)
        self.sysActionA.setObjectName("sysActionA")
        self.sysActionSubA = QtWidgets.QAction(MainWindow)
        self.sysActionSubA.setObjectName("sysActionSubA")
        self.sysActionSubB = QtWidgets.QAction(MainWindow)
        self.sysActionSubB.setObjectName("sysActionSubB")
        self.sysActionSubC = QtWidgets.QAction(MainWindow)
        self.sysActionSubC.setObjectName("sysActionSubC")
        self.sysActionSubD = QtWidgets.QAction(MainWindow)
        self.sysActionSubD.setObjectName("sysActionSubD")
        self.sysActionSubE = QtWidgets.QAction(MainWindow)
        self.sysActionSubE.setObjectName("sysActionSubE")
        self.sysActionSubF = QtWidgets.QAction(MainWindow)
        self.sysActionSubF.setObjectName("sysActionSubF")
        self.sysActionSubG = QtWidgets.QAction(MainWindow)
        self.sysActionSubG.setObjectName("sysActionSubG")
        self.sysActionSubH = QtWidgets.QAction(MainWindow)
        self.sysActionSubH.setObjectName("sysActionSubH")
        self.sysActionSubI = QtWidgets.QAction(MainWindow)
        self.sysActionSubI.setObjectName("sysActionSubI")

        self.mobileActionA = QtWidgets.QAction(MainWindow)
        self.mobileActionA.setObjectName("mobileActionA")
        self.mobileActionSubA = QtWidgets.QAction(MainWindow)
        self.mobileActionSubA.setObjectName("mobileActionSubA")
        self.mobileActionSubB = QtWidgets.QAction(MainWindow)
        self.mobileActionSubB.setObjectName("mobileActionSubB")
        self.mobileActionSubC = QtWidgets.QAction(MainWindow)
        self.mobileActionSubC.setObjectName("mobileActionSubC")
        self.mobileActionSubD = QtWidgets.QAction(MainWindow)
        self.mobileActionSubD.setObjectName("mobileActionSubD")
        self.mobileActionSubE = QtWidgets.QAction(MainWindow)
        self.mobileActionSubE.setObjectName("mobileActionSubE")
        self.mobileActionSubF = QtWidgets.QAction(MainWindow)
        self.mobileActionSubF.setObjectName("mobileActionSubF")
        self.mobileActionSubG = QtWidgets.QAction(MainWindow)
        self.mobileActionSubG.setObjectName("mobileActionSubG")
        self.mobileActionSubH = QtWidgets.QAction(MainWindow)
        self.mobileActionSubH.setObjectName("mobileActionSubH")
        self.mobileActionSubI = QtWidgets.QAction(MainWindow)
        self.mobileActionSubI.setObjectName("mobileActionSubI")
        self.mobileActionSubJ = QtWidgets.QAction(MainWindow)
        self.mobileActionSubJ.setObjectName("mobileActionSubJ")

        self.menuMobileSub.addAction(self.mobileActionSubA)
        self.menuMobileSub.addAction(self.mobileActionSubB)
        self.menuMobileSub.addAction(self.mobileActionSubC)
        self.menuMobileSub.addAction(self.mobileActionSubD)
        self.menuMobileSub.addAction(self.mobileActionSubE)
        self.menuMobileSub.addAction(self.mobileActionSubF)
        self.menuMobileSub.addAction(self.mobileActionSubG)
        self.menuMobileSub.addAction(self.mobileActionSubH)
        self.menuMobileSub.addAction(self.mobileActionSubI)
        self.menuMobileSub.addAction(self.mobileActionSubJ)

        self.menuMenuSub.addAction(self.sysActionSubA)
        self.menuMenuSub.addAction(self.sysActionSubB)
        self.menuMenuSub.addAction(self.sysActionSubC)
        self.menuMenuSub.addAction(self.sysActionSubD)
        self.menuMenuSub.addAction(self.sysActionSubE)
        self.menuMenuSub.addAction(self.sysActionSubF)
        self.menuMenuSub.addAction(self.sysActionSubG)
        self.menuMenuSub.addAction(self.sysActionSubH)
        self.menuMenuSub.addAction(self.sysActionSubI)

        self.menuMenu.addAction(self.menuMobileSub.menuAction())
        self.menubar.addAction(self.menuMenu.menuAction())

        self.menuMenu.addAction(self.menuMenuSub.menuAction())
        self.menubar.addAction(self.menuMenu.menuAction())

        self.sysToolBar.addAction(self.sysActionA)
        self.sysToolBar.addSeparator()
        self.sysToolBar.addAction(self.sysActionSubA)
        self.sysToolBar.addAction(self.sysActionSubB)
        self.sysToolBar.addAction(self.sysActionSubC)
        self.sysToolBar.addAction(self.sysActionSubD)
        self.sysToolBar.addAction(self.sysActionSubE)
        self.sysToolBar.addAction(self.sysActionSubF)
        self.sysToolBar.addAction(self.sysActionSubG)
        self.sysToolBar.addAction(self.sysActionSubH)

        self.mobileToolBar.addAction(self.mobileActionA)
        self.mobileToolBar.addSeparator()
        self.mobileToolBar.addAction(self.mobileActionSubA)
        self.mobileToolBar.addAction(self.mobileActionSubB)
        self.mobileToolBar.addAction(self.mobileActionSubC)
        self.mobileToolBar.addAction(self.mobileActionSubD)
        self.mobileToolBar.addAction(self.mobileActionSubE)
        self.mobileToolBar.addAction(self.mobileActionSubF)
        self.mobileToolBar.addAction(self.mobileActionSubG)
        self.mobileToolBar.addAction(self.mobileActionSubH)
        self.mobileToolBar.addAction(self.mobileActionSubI)
        self.mobileToolBar.addAction(self.mobileActionSubJ)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.sysActionSubA.triggered.connect(lambda: self.get_android_version())
        self.sysActionSubB.triggered.connect(lambda: self.get_android_brand())
        self.sysActionSubC.triggered.connect(lambda: self.get_android_model())
        self.sysActionSubD.triggered.connect(lambda: self.get_android_ip())
        self.sysActionSubE.triggered.connect(lambda: self.get_android_id())
        self.sysActionSubF.triggered.connect(lambda: self.get_android_displays())
        self.sysActionSubG.triggered.connect(lambda: self.get_android_mac())
        self.sysActionSubH.triggered.connect(lambda: self.get_list_packages())

        self.mobileActionSubA.triggered.connect(lambda: self.get_top())
        self.mobileActionSubB.triggered.connect(lambda: self.get_logcat())
        self.mobileActionSubC.triggered.connect(lambda: self.clear_logcat())
        self.mobileActionSubD.triggered.connect(lambda: self.get_logcat_crash())
        self.mobileActionSubE.triggered.connect(lambda: self.get_screencap())
        self.mobileActionSubF.triggered.connect(lambda: self.clear_app_cache())
        self.mobileActionSubG.triggered.connect(lambda: self.uninstall_app())
        self.mobileActionSubH.triggered.connect(lambda: self.install_app())
        self.mobileActionSubI.triggered.connect(lambda: self.get_app_pid())
        self.mobileActionSubJ.triggered.connect(lambda: self.export_app())

        self.pushButton_D.clicked.connect(lambda: self.comboBoxAdd())
        self.comboBoxId.currentIndexChanged.connect(self.selection_change)
        self.comboBoxMobile.currentIndexChanged.connect(self.mobile_change)

        self.installButton_D.clicked.connect(self.batch_install_app)
        self.unintallButton_D.clicked.connect(self.batch_uninstall_app)
        self.stopButton_D.clicked.connect(self.stop_refresh)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox_center.setTitle(_translate("MainWindow", "执行命令: "))

        self.label_cmd.setText(_translate("MainWindow", "TextLabel"))
        self.label_71.setText(_translate("MainWindow", "Inside Central Widget"))
        self.label_right.setText(_translate("MainWindow", "批量安装：给所有连接设备批量安装APK安装包\n"
                                                          "批量卸载：卸载所有连接设备安装包"))

        self.label_mobile.setText(_translate("MainWindow", '设备类型'))
        self.menuMenu.setTitle(_translate("MainWindow", "Menu"))
        self.menuMenuSub.setTitle(_translate("MainWindow", "获取系统信息"))
        self.menuMobileSub.setTitle(_translate("MainWindow", "手机控制"))

        self.sysToolBar.setWindowTitle(_translate("MainWindow", "Tool bar actions"))

        self.sysActionA.setText(_translate("MainWindow", "系统信息"))
        self.sysActionSubA.setText(_translate("MainWindow", "获取SDK版本号"))
        self.sysActionSubB.setText(_translate("MainWindow", "获取手机名称"))
        self.sysActionSubC.setText(_translate("MainWindow", "获取手机型号"))
        self.sysActionSubD.setText(_translate("MainWindow", "获取手机IP"))
        self.sysActionSubE.setText(_translate("MainWindow", "获取手机设备ID"))
        self.sysActionSubF.setText(_translate("MainWindow", "获取手机分辨率"))
        self.sysActionSubG.setText(_translate("MainWindow", "获取手机Mac地址"))
        self.sysActionSubH.setText(_translate("MainWindow", "获取手机应用列表"))

        self.mobileActionA.setText(_translate("MainWindow", "手机控制"))
        self.mobileActionSubA.setText(_translate("MainWindow", "查看资源&进程信息"))
        self.mobileActionSubB.setText(_translate("MainWindow", "获取logcat日志"))
        self.mobileActionSubC.setText(_translate("MainWindow", "清空logcat缓存日志"))
        self.mobileActionSubD.setText(_translate("MainWindow", "获取近期崩溃日志"))
        self.mobileActionSubE.setText(_translate("MainWindow", "获取手机截图"))
        self.mobileActionSubF.setText(_translate("MainWindow", "清理应用缓存"))
        self.mobileActionSubG.setText(_translate("MainWindow", "删除应用程序"))
        self.mobileActionSubH.setText(_translate("MainWindow", "安装应用程序"))
        self.mobileActionSubI.setText(_translate("MainWindow", "获取应用PID"))
        self.mobileActionSubJ.setText(_translate("MainWindow", "导出已安装的应用"))

        self.comboBoxId.setToolTip(_translate("DockWidget", "This is a tool tip"))
        self.comboBoxId.setStatusTip(_translate("DockWidget", "This is a status tip"))
        self.comboBoxId.setWhatsThis(_translate("DockWidget", "This is \"what is this\""))
        self.pushButton_D.setText(_translate("DockWidget", "获取设备"))
        self.installButton_D.setText(_translate("DockWidget", "批量安装软件"))
        self.unintallButton_D.setText(_translate("DockWidget", "批量卸载软件"))
        self.stopButton_D.setText(_translate("DockWidget", "停止刷新"))
