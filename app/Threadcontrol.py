"""
@ 项目：RCEflask
@ 模块：
"""
import subprocess
from time import sleep

from PyQt5.QtCore import QThread, pyqtSignal


class MiniThread(QThread):
    """
    常驻后台线程
    """
    sinOut = pyqtSignal(str)

    def __init__(self, cmd):
        super().__init__()
        self._kill = True
        self.cmd = cmd
        self.__running = True
        self.num = 0

    def run(self):
        pi = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        for i in iter(pi.stdout.readline, 'b'):
            sleep(0.001)
            if not self.__running:
                pi.terminate()
                return
            try:
                i = i.decode('utf-8').strip()
                if not i:  # 如果空行超过5行，则判断线程结束
                    self.num += 1
                    if self.num >= 5:
                        self.sinOut.emit('执行完成，进程结束')
                        return
                else:
                    if self.num > 0:
                        self.num -= 1
            except:
                pass
            self.sinOut.emit(str(i))

    def kill(self):
        self.__running = False


class waitThread(QThread):
    """
    可自动结束线程
    """
    waitSinOut = pyqtSignal(str)  # 自定义信号，执行run()函数时，从相关线程发射此信号

    def __init__(self, cmd):
        super().__init__()
        self._kill = True
        self.cmd = cmd
        self.__running = True

    def __del__(self):
        self.working = False
        self.wait()

    def run(self):
        self.waitSinOut.emit(str(self.cmd))
        output, errors = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE).communicate()
        try:
            errors = errors.decode('utf-8')
        except:
            self.waitSinOut.emit('errors 解析失败，输入内容:{}'.format(errors))
        try:
            output.decode('utf-8')
        except:
            self.waitSinOut.emit('output 解析失败，输出内容:{}'.format(output))
        if errors:
            self.waitSinOut.emit(str(errors))
        self.waitSinOut.emit(str(output))

    def kill(self):
        self.__running = False
