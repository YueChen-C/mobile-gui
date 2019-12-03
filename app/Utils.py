"""
@ Author：YueC
@ Description ：
"""

from app import Environ
from app.Static import Variables

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor

from app import PROCESS_LIST


class Command:
    def __init__(self, mobile=None, device_id=None):
        self.mobile = mobile
        self.device_id = device_id

    def shell(self, args: list):
        return [Environ.adb, '-s', self.device_id, 'shell', ] + args

    def iOSshell(self, execute, args=None):
        if args is None:
            args = []
        return [execute, '-u', self.device_id] + args

    def devices(self):
        return [Environ.adb, 'devices'] if self.mobile == Variables.Android else [Environ.idevice_id, '-l']

    def model(self):
        return self.shell(['getprop', 'ro.product.model']) if self.mobile == Variables.Android else self.iOSshell(Environ.ideviceinfo, ['-k', 'ProductType'])

    def version(self):
        return self.shell(['getprop', 'ro.build.version.release']) if self.mobile == Variables.Android else self.iOSshell(Environ.ideviceinfo, ['-k', 'ProductVersion'])

    def brand(self):
        return self.shell(['getprop', 'ro.product.brand']) if self.mobile == Variables.Android else self.iOSshell(Environ.ideviceinfo, ['-k', 'ProductName'])

    def mac(self):
        return self.shell(['cat' '/sys/class/net/wlan0/address']) if self.mobile == Variables.Android else self.iOSshell(Environ.ideviceinfo, ['-k', 'EthernetAddress'])

    def log(self):
        return [Environ.adb, '-s', self.device_id, 'logcat'] if self.mobile == Variables.Android else self.iOSshell(Environ.idevicesyslog)

    def id(self):
        return self.shell(['settings', 'get', 'secure android_id']) if self.mobile == Variables.Android else self.iOSshell(Environ.ideviceinfo, ['-k', 'UniqueDeviceID'])

    def crash_log(self, path):
        return self.shell(['logcat', '-b', 'crash']) if self.mobile == Variables.Android else self.iOSshell(Environ.idevicecrashreport, [path])

    def screencap(self, path):
        return [Environ.adb, '-s', self.device_id, 'exec-out', 'screencap', '-p'] \
            if self.mobile == Variables.Android else self.iOSshell(Environ.idevicescreenshot, [path])

    def packages(self):
        return self.shell(['pm', 'list', 'packages', '-3']) if self.mobile == Variables.Android else self.iOSshell(Environ.ideviceinstaller, ['-l'])

    def install(self, file_name, device_id=None):
        return [Environ.adb, '-s', device_id or self.device_id, 'install', '-r', '-g', file_name] \
            if self.mobile == Variables.Android else self.iOSshell(Environ.ideviceinstaller, ['-i', file_name])

    def uninstall(self, app, device_id=None):
        return [Environ.adb, '-s', device_id or self.device_id, 'uninstall', app] \
            if self.mobile == Variables.Android else self.iOSshell(Environ.ideviceinstaller, ['-U', app])

    def app_path(self, app):
        return self.shell(['pm', 'path', app])

    def pid(self, app):
        return self.shell(['ps | grep -m1 {} '.format(app)])

    def export(self, package):
        return [Environ.adb, '-s', self.device_id, 'exec-out', 'cat {}'.format(package)]

    def clear_cache(self, app):
        return self.shell(['pm', 'clear', app])

    def clear_logcat(self):
        return [Environ.adb, '-s', self.device_id, 'logcat', '-c']

    def ip(self):
        return self.shell(['ifconfig'])

    def displays(self):
        return self.shell(['dumpsys', 'window', 'displays'])

    def top(self):
        return self.shell(['top', '-m', '20'])

    def scrcpy(self):
        return [Environ.scrcpy, '-s', self.device_id]


class WaitThread(QThread):
    """
    多任务后台进程
    """
    waitSinOut = pyqtSignal(str)  # 自定义 str 类型信号
    waitSinOutBytes = pyqtSignal(bytes)  # 自定义 bytes 类型信号

    def __init__(self, cmd, Terminal, massage, decode=True):
        super().__init__()
        self._kill = True
        self.cmd = cmd
        self.Terminal = Terminal
        self.massage = massage
        self.decode = decode

    def run(self):
        process = None
        try:
            self.Terminal.append('任务：{}'.format(self.massage))
            self.Terminal.moveCursor(QTextCursor.End)
            cmd_str = ' '.join(self.cmd) if isinstance(self.cmd, list) else self.cmd
            self.Terminal.append('正在执行命令: {}'.format(cmd_str))
            process = QtCore.QProcess()
            process.start(self.cmd[0], self.cmd[1:])
            process.waitForFinished()
            errors = process.readAllStandardError()
            output = process.readAllStandardOutput()
            if errors:
                errors = str(errors, encoding='utf-8')
                self.waitSinOut.emit(errors)
            if output:
                if self.decode:
                    output = str(output, encoding='utf-8')
                    self.waitSinOut.emit(str(output))
                else:
                    self.waitSinOutBytes.emit(bytes(output))
            self.waitSinOut.emit(str('finish'))

            self.Terminal.append('任务：{} 已完成'.format(self.massage))
            self.Terminal.moveCursor(QTextCursor.End)
            process.close()
            if self in PROCESS_LIST:
                PROCESS_LIST.remove(self)
        except Exception as e:
            self.Terminal.append('任务报错 {}'.format(e))
        finally:
            if process:
                process.close()
