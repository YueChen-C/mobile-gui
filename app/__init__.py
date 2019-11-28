"""
@ Author：YueC
@ Description ：
"""
import os
import sys


def find_executable(executable, ENVIRON_PATH):
    path = os.environ['PATH']
    paths = path.split(os.pathsep)
    if ENVIRON_PATH:
        paths.append(ENVIRON_PATH)
    base, ext = os.path.splitext(executable)
    if sys.platform == 'win32' and not ext:
        batcutable = executable + '.bat'
        cmdcutable = executable + '.cmd'
        executable = executable + '.exe'
        for cutabl in [batcutable, cmdcutable, executable]:
            if os.path.isfile(cutabl):
                return cutabl
            for p in paths:
                full_path = os.path.join(p, cutabl)
                if os.path.isfile(full_path):
                    return full_path

    if os.path.isfile(executable):
        return executable

    for p in paths:
        full_path = os.path.join(p, executable)
        if os.path.isfile(full_path):
            return full_path

    return None


def app_path():
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)


SYSSTR = os.name
if SYSSTR == "nt":
    SPLIT_STR = '\\'
    ENVIRON_PATH = os.path.join(app_path(), 'imobiledevice{}'.format(SPLIT_STR))
    SCRCPY = os.path.join(app_path(), 'scrcpy{}'.format(SPLIT_STR))

else:
    ENVIRON_PATH = ''
    SCRCPY = ''
    SPLIT_STR = '/'

PROCESS_LIST = []
BACKGROUND_LIST = []
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


def check_environ():
    environ = ['adb', 'idevice_id', 'scrcpy', 'ideviceinfo', 'idevicesyslog', 'idevicescreenshot', 'ideviceinstaller', 'idevicecrashreport']

    for i in environ:
        if find_executable(i, ENVIRON_PATH) is None:
            raise Exception('缺少环境变量：{}'.format(i))


class Environ:
    adb = find_executable('adb', ENVIRON_PATH) or 'adb'
    scrcpy = find_executable('scrcpy', SCRCPY) or 'scrcpy'
    idevice_id = find_executable('idevice_id', ENVIRON_PATH) or 'idevice_id'
    ideviceinfo = find_executable('ideviceinfo', ENVIRON_PATH) or 'ideviceinfo'
    idevicesyslog = find_executable('idevicesyslog', ENVIRON_PATH) or 'idevicesyslog'
    idevicescreenshot = find_executable('idevicescreenshot', ENVIRON_PATH) or 'idevicescreenshot'
    ideviceinstaller = find_executable('ideviceinstaller', ENVIRON_PATH) or 'ideviceinstaller'
    idevicecrashreport = find_executable('idevicecrashreport', ENVIRON_PATH) or 'idevicecrashreport'
