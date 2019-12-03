# -*- coding: utf-8 -*-
"""
@ Author：YueC
@ Description ：逻辑处理相关内容
"""
import multiprocessing
import time

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QUrl
from PyQt5.QtGui import QTextCursor, QDesktopServices
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog

from app import *
from app.Interface import UIMainWindow
from app.Static import VirtualKey, Variables
from app.Utils import Command
from app.Utils import WaitThread

multiprocessing.freeze_support()


class MainWindow(Command, UIMainWindow):
    MainWindowSignal = pyqtSignal()

    def __init__(self):
        super().__init__(mobile=None, device_id=None)
        self.device_id = ""
        self.device_cmd = ""
        self.device_list = []
        self.mobile = Variables.Android
        self.search_text = ''
        self.process = None

    def msg(self, text):
        QMessageBox.about(self.centralWidget, "标题", "{}".format(text))

    def check_device(self):
        self.comboBoxAdd()
        if not self.device_list:
            self.Terminal.setText('命令执行失败，当前没有连接设备，请点击右侧"获取设备"按钮，尝试获取设备。')
            return False
        return True

    def get_devices(self):
        cmd = self.devices()
        my_process = QtCore.QProcess()
        my_process.start(cmd[0], cmd[1:])
        my_process.waitForFinished()
        devices = my_process.readAllStandardOutput()
        if not devices:
            self.Terminal.append('获取设备列表失败')
            return
        else:
            devices = str(devices, encoding='utf-8')

        androidevices_list = []
        if self.mobile == Variables.Android:
            for device in devices.splitlines():
                if 'device' in device and 'devices' not in device:
                    device = device.split('\t')[0]
                    androidevices_list.append(device)
            return androidevices_list

        return devices.splitlines()

    def stop_refresh(self):
        """ 清理所有进程
        """
        if self.process:
            reply = QMessageBox.warning(self.centralWidget,
                                        "提示",
                                        "当前有任务正在执行，是否停止操作",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.process.close()
                self.process = None
            elif reply == QMessageBox.No:
                return False
        return True

    def data_ready_process(self):
        try:
            data = str(self.process.readAll(), encoding='utf-8')
        except:
            data = str(self.process.readAll())
        if 'total' in data and 'running' in data:
            self.Terminal.append('\n')
        if self.search_text:
            if self.search_text in data:
                self.Terminal.append(data)
            return
        self.Terminal.append(data)

    def data_ready(self, data):
        """ 将消息流数据打印到窗口
        :param data: 消息流
        :return:
        """
        if self.search_text:
            if self.search_text in data:
                self.Terminal.append(data)
            return
        self.Terminal.append(data)

    def process_finished(self):
        self.Terminal.append('获取数据失败,请检查相关设备连接情况')
        if self.process:
            self.process.close()
            self.process = None

    def invoke(self, cmd, background=False, decode=True):
        """
        :param cmd: 命令行
        :param background: 如果是常驻进程则为 True
        :return:
        """
        # if not self.stop_refresh(): return
        # self.comboBoxAdd()
        if not self.device_list:
            self.Terminal.append('命令执行失败，当前没有连接设备，请点击右侧"获取设备"按钮，尝试获取设备。')
            return False
        try:
            if not self.stop_refresh(): return
            cmd_str = ' '.join(cmd) if isinstance(cmd, list) else cmd
            self.groupCenter.setTitle("执行命令：{}".format(cmd_str))
            self.Terminal.append('正在执行命令: {}'.format(cmd_str))
            if background:
                self.process = QtCore.QProcess()
                self.process.start(cmd[0], cmd[1:])
                self.process.readyRead.connect(self.data_ready_process)
                self.process.finished.connect(self.process_finished)
            else:
                my_process = QtCore.QProcess()
                my_process.start(cmd[0], cmd[1:])
                my_process.waitForFinished()
                errors = my_process.readAllStandardError()
                output = my_process.readAllStandardOutput()
                if errors:
                    errors = str(errors, encoding='utf-8')
                    self.Terminal.append('命令执行执行失败：{0}'.format(errors))
                    return False
                if output:
                    if decode:
                        output = str(output, encoding='utf-8')
                        self.Terminal.append('执行结果：')
                        self.Terminal.append(output)
                        self.Terminal.moveCursor(QTextCursor.End)
                    else:
                        output = bytes(output)

                    return output
                my_process.close()
                return True
        except Exception as E:
            self.Terminal.append('命令执行出错：{0}'.format(E))
            return False

    def android_control(self):
        """ 开启画面投屏
        """
        if not self.check_device(): return

        if int(self.get_version().split('.')[0]) <= 5:
            self.Terminal.append('Android 版本小于 5.0 设备无法开启画面同步功能')
            return
        self.Terminal.append(VirtualKey)
        Thread = WaitThread(self.scrcpy(), self.Terminal, '开启手机控制')
        PROCESS_LIST.append(Thread)
        Thread.waitSinOut.connect(self.data_ready)
        Thread.start()

    def get_version(self):
        """
        获取设备中的Android版本号，如4.2.2
        """
        return self.invoke(self.version())

    def get_model(self):
        """
        获取设备型号
        """
        return self.invoke(self.model())

    def get_brand(self):
        """
        设备名称
        """
        return self.invoke(self.brand())

    def get_ip(self):
        """
          获取设备 IP 地址
        """
        if self.mobile == 'iOS':
            return self.Terminal.setText('iOS 暂时不支持此方法')

        return self.invoke(self.ip())

    def get_id(self):
        """
           获取设备 ID
        """
        return self.invoke(self.id())

    def get_displays(self):
        """
        获取设备 displays
        """
        if self.mobile == 'iOS':
            return self.Terminal.setText('iOS 暂时不支持此方法')
        return self.invoke(self.displays())

    def get_mac(self):
        """
        获取设备 mac 地址
        """
        return self.invoke(self.mac())

    def get_log(self):
        """
         获取设备 LOG 数据
        """
        try:
            return self.invoke(self.log(), background=True)
        except Exception as E:
            self.Terminal.append('命令执行出错：{0}'.format(E))

    def get_log_crash(self):
        """
         获取设备 Crash LOG 数据
        """
        if not self.check_device(): return
        self.stop_refresh()
        cmd = self.crash_log(CRASHLOG_PATH)

        if self.mobile == Variables.iOS:
            reply = QMessageBox.warning(self.centralWidget,
                                        "获取崩溃日志",
                                        "是否确认是否导出 iOS 崩溃日志，导出后手机内日志将清除。",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                Thread = WaitThread(cmd, self.Terminal, '正在导出崩溃日志')
                PROCESS_LIST.append(Thread)
                Thread.waitSinOut.connect(self.data_ready)
                Thread.start()
                return
        return self.invoke(cmd, background=True)

    def clear_log(self):
        reply = QMessageBox.warning(self.centralWidget,
                                    "清除日志",
                                    "是否确认清理缓存日志，清理缓存日志后之前所有日志将不可恢复",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            return self.invoke(self.clear_logcat())

    def get_top(self):
        if self.mobile == Variables.iOS:
            return self.Terminal.setText('iOS 暂时不支持此方法')
        return self.invoke(self.top(), background=True)

    def get_screencap(self):
        """
        获取截图
        """
        if not self.check_device(): return

        path = '{0}{1}.png'.format(SCREENSHOTS_PATH, int(time.time()))

        def save_png(png_bytes):
            if self.mobile == Variables.Android:
                with open(path, 'wb') as png:
                    png.write(png_bytes)

        def is_save(end_str):
            if end_str == 'finish':
                if os.path.exists(path):
                    self.Terminal.append('截图成功,截图已保存在：{}'.format(path))
                    QDesktopServices.openUrl(QUrl.fromLocalFile(path))
            else:
                self.Terminal.append('{}'.format(end_str))

        Thread = WaitThread(self.screencap(path), self.Terminal, '正在获取 {} 设备截图'.format(self.device_id), decode=False)
        PROCESS_LIST.append(Thread)
        Thread.waitSinOutBytes.connect(save_png)
        Thread.waitSinOut.connect(is_save)
        Thread.start()

    def get_list_packages(self):
        """ 获取 APP 中的应用
        """
        return self.invoke(self.packages())

    def get_app_pid(self):
        """
        获取 APP PID
        """
        if self.mobile == Variables.iOS:
            return self.Terminal.setText('iOS 暂时不支持此方法')
        app = self.app_list()
        if app:
            pid = self.invoke(self.pid(app))
            if isinstance(pid, bool):
                self.Terminal.append('{0} 应用未启动'.format(app))
            else:
                self.Terminal.append('{0} 应用 PID 为：{1}'.format(app, pid.split()[1]))

    def clear_app_cache(self):
        """ 清理 APP 缓存 （Android）
        """
        app = self.app_list()
        if app:
            if self.invoke(self.clear_cache(app)):
                self.Terminal.append('{} 应用缓存已重置'.format(app))

    def uninstall_app(self):
        """
        卸载 APP
        """
        if not self.check_device(): return

        app = self.app_list()
        if app:
            self.Terminal.append('设备：{0} 正在删除应用 {1}'.format(self.device_id, app))
            if self.invoke(self.uninstall(app)):
                self.Terminal.append('{} 应用已卸载'.format(app))

    def install_app(self):
        """
        安装 APP
        """
        if not self.check_device(): return

        if self.mobile == Variables.iOS:
            openfile_name = QFileDialog.getOpenFileName(self.centralWidget, '选择文件', '', 'Excel files(*.ipa)')
        else:
            openfile_name = QFileDialog.getOpenFileName(self.centralWidget, '选择文件', '', 'Excel files(*.apk)')
        if openfile_name[0]:
            cmd = self.install(openfile_name[0])
            Thread = WaitThread(cmd, self.Terminal, '{0} 设备正在安装应用 {1},请稍后...'.format(self.device_id, openfile_name[0]))
            PROCESS_LIST.append(Thread)
            Thread.waitSinOut.connect(self.data_ready)
            Thread.start()

    def export_app(self):
        """
        导出已安装 APP 安装包
        """
        if not self.check_device(): return

        app = self.app_list()
        path = '{0}{1}.apk'.format(APPLICATION_PATH, app)

        def seve_apk(file_inf):
            with open(path, 'wb+') as f:
                f.write(file_inf)

        if app:
            package = self.invoke(self.app_path(app))
            if isinstance(package, str):
                package = package.split(':')[1].strip()
                Thread = WaitThread(self.export(package), self.Terminal, '{0} 设备正在导出应用 {1} 安装包'.format(self.device_id, app), decode=False)
                PROCESS_LIST.append(Thread)
                Thread.waitSinOutBytes.connect(seve_apk)
                Thread.start()

    def device_change(self, i):
        if self.device_id == self.comboBoxId.currentText():
            return
        if not self.stop_refresh():
            self.comboBoxId.setCurrentText(self.device_id)
            return
        self.device_id = self.comboBoxId.currentText()

    def comboBoxAdd(self):
        """ 获取设备ID，添加至设备列表
        :return:
        """
        devices = self.get_devices()
        list_index = 0
        if not devices:
            self.device_id = ''
            self.device_list = []
            self.comboBoxId.clear()
            self.Terminal.setText('当前没有连接设备，请检查设备设备是否连接')
            return
        if self.comboBoxId.currentText() and self.comboBoxId.currentText() in devices:
            try:
                list_index = devices.index(self.comboBoxId.currentText())
            except Exception as E:
                self.Terminal.setText('获取设备信息报错：{}'.format(E))
        self.comboBoxId.clear()
        self.comboBoxId.addItems(devices)
        self.comboBoxId.setCurrentIndex(list_index)
        self.device_list = devices

    def batch_install_app(self):
        """
        选择安装包弹窗
        """
        if not self.check_device(): return

        if self.mobile == Variables.iOS:
            openfile_name = QFileDialog.getOpenFileName(self.centralWidget, '选择文件', '', 'Excel files(*.ipa)')
        else:
            openfile_name = QFileDialog.getOpenFileName(self.centralWidget, '选择文件', '', 'Excel files(*.apk)')
        if openfile_name[0]:
            self.Terminal.append('开始安装：{}'.format(openfile_name[0]))
            self.Terminal.append('请勿操作等待软件安装')
            for device in self.device_list:
                cmd = self.install(openfile_name[0], device)
                Thread = WaitThread(cmd, self.Terminal, '开始安装设备 {}'.format(device))
                PROCESS_LIST.append(Thread)
                Thread.waitSinOut.connect(self.data_ready)
                Thread.start()

    def batch_uninstall_app(self):
        """ 批量删除应用
        :return:
        """
        if not self.check_device(): return

        app = self.app_list()
        if app:
            for device in self.device_list:
                cmd = self.uninstall(app, device)
                Thread2 = WaitThread(cmd, self.Terminal, '{0} 设备正在删除应用 {1}'.format(device, app))
                PROCESS_LIST.append(Thread2)
                Thread2.waitSinOut.connect(self.data_ready)
                Thread2.start()

    def app_list(self):
        # 1为默认选中选项目，True/False  列表框是否可编辑。
        try:
            with open(INI_PATH, 'r') as applist:
                items = list(map(lambda x: x.strip('\n'), applist))
        except Exception as E:
            self.Terminal.setText('{}'.format(E))
            return
        value, ok = QInputDialog.getItem(self.centralWidget, "选择应用", "请选择应用的包名", items, 1, True)  # 选择确认框
        if ok:
            return value

    def set_search(self):
        """ 数据筛选
        """
        self.search_text = self.searchEdit.text()

    def cmd_end(self):
        """将光标移动至末尾
        """
        self.Terminal.moveCursor(QTextCursor.End)

    def cleer_TextEdit(self):
        self.Terminal.clear()

    def mobile_type_change(self):
        """ 更换设备类型时，使部分按钮不可点击
            添加删除元素时要注意改方法的使用
        :return:
        """

        if self.mobile == self.comboBoxMobile.currentText():
            return
        if not self.stop_refresh():
            self.comboBoxMobile.setCurrentText(self.mobile)
            return
        self.mobile = self.comboBoxMobile.currentText()
        if self.mobile == Variables.iOS:
            self.comboBoxAdd()
            self.sysToolBar.clear()
            self.sysToolBar.addAction(self.sysActionA)
            self.sysToolBar.addSeparator()
            self.sysToolBar.addAction(self.sysActionSubSdk)
            self.sysToolBar.addAction(self.sysActionSubBrand)
            self.sysToolBar.addAction(self.sysActionSubModel)
            self.sysToolBar.addAction(self.sysActionSubID)
            self.sysToolBar.addAction(self.sysActionSubMac)
            self.sysToolBar.addAction(self.sysActionSubPackages)

            self.mobileToolBar.clear()
            self.mobileToolBar.addAction(self.mActionA)
            self.mobileToolBar.addSeparator()
            self.mobileToolBar.addAction(self.mActionLog)
            self.mobileToolBar.addAction(self.mActionSubCrashLog)
            self.mobileToolBar.addAction(self.mActionSubScreencap)
            self.mobileToolBar.addAction(self.mActionSubUninstall)
            self.mobileToolBar.addAction(self.mActionSubInstall)
        else:
            self.comboBoxAdd()
            self.sysToolBar.clear()
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

            self.mobileToolBar.clear()

            self.mobileToolBar.addAction(self.mActionA)
            self.mobileToolBar.addSeparator()
            self.mobileToolBar.addAction(self.mActionControl)
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
