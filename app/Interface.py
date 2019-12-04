"""
@ Author：YueC
@ Description ：界面布局相关
"""
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt


class UIMainWindow():

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(596, 717)
        self.centralWidget = QtWidgets.QWidget(MainWindow)  # 主窗口
        self.centralWidget.setObjectName("centralWidget")
        self.gridCentral = QtWidgets.QGridLayout(self.centralWidget)  # 主窗口全局 grid
        self.gridCentral.setObjectName("gridCentral")

        # 页面右侧布局批量安装等
        self.groupBoxRight = QtWidgets.QGroupBox(self.centralWidget)  # 右侧控制台 GroupBox
        self.groupBoxRight.setObjectName("groupBoxRight")
        self.groupGridRight = QtWidgets.QGridLayout(self.groupBoxRight)  # 右侧控制台 grid
        self.groupGridRight.setObjectName("groupConsole")

        self.label_mobile = QtWidgets.QLabel()
        self.label_mobile.setObjectName("label_mobile")
        self.label_mobile.setAlignment(Qt.AlignLeft)
        self.comboBoxId = QtWidgets.QComboBox()  # 设备 ID 选择框
        self.comboBoxId.setObjectName("comboBoxId")
        self.comboBoxId.setMinimumWidth(150)
        self.comboBoxId.setEditable(True)
        self.comboBoxMobile = QtWidgets.QComboBox()  # 设备类型选择框 iOS,Android
        self.comboBoxMobile.setObjectName("comboBoxMobile")
        self.comboBoxMobile.addItems(['Android', 'iOS'])
        self.comboBoxMobile.setEditable(True)
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
        self.clearText = QtWidgets.QPushButton(self.centralWidget)
        self.clearText.setMinimumSize(QtCore.QSize(0, 0))
        self.clearText.setObjectName("clearText")

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
        self.groupGridRight.addWidget(self.clearText, 3, 1, 1, 1, Qt.AlignTop)
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
        self.endButton = QtWidgets.QPushButton(self.centralWidget)
        self.endButton.setMinimumSize(QtCore.QSize(0, 0))
        self.endButton.setObjectName("endButton")

        self.Terminal = QtWidgets.QPlainTextEdit()
        self.Terminal.setObjectName("Terminal")
        self.Terminal.setMaximumBlockCount(50000)
        self.groupConsole.addWidget(self.searchLabel, 0, 0, 1, 1)
        self.groupConsole.addWidget(self.searchEdit, 0, 1, 1, 1)
        self.groupConsole.addWidget(self.searchButton, 0, 2, 1, 1)
        self.groupConsole.addWidget(self.endButton, 0, 3, 1, 1)

        self.groupConsole.addWidget(self.Terminal, 1, 0, 1, 4)

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
        self.sysToolBar.setMovable(False)
        self.mobileToolBar = QtWidgets.QToolBar(MainWindow)
        self.mobileToolBar.setObjectName("mobileToolBar")
        self.mobileToolBar.setMovable(False)

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

        self.mActionControl = QtWidgets.QAction(MainWindow)
        self.mActionControl.setObjectName("mActionControl")

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
        self.menuMobileSub.addAction(self.mActionControl)
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

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # 按钮绑定触发事件
        self.sysActionSubSdk.triggered.connect(lambda: self.get_version())
        self.sysActionSubBrand.triggered.connect(lambda: self.get_brand())
        self.sysActionSubModel.triggered.connect(lambda: self.get_model())
        self.sysActionSubIP.triggered.connect(lambda: self.get_ip())
        self.sysActionSubID.triggered.connect(lambda: self.get_id())
        self.sysActionSubDisplays.triggered.connect(lambda: self.get_displays())
        self.sysActionSubMac.triggered.connect(lambda: self.get_mac())
        self.sysActionSubPackages.triggered.connect(lambda: self.get_list_packages())

        self.mActionSubTop.triggered.connect(lambda: self.get_top())
        self.mActionControl.triggered.connect(lambda: self.android_control())
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
        self.comboBoxId.currentIndexChanged.connect(self.device_change)
        self.comboBoxMobile.currentIndexChanged.connect(self.mobile_type_change)

        self.installButton.clicked.connect(self.batch_install_app)
        self.unintallButton.clicked.connect(self.batch_uninstall_app)
        self.stopButton.clicked.connect(self.stop_refresh)
        self.clearText.clicked.connect(self.cleer_TextEdit)

        self.searchEdit.returnPressed.connect(self.set_search)
        self.searchButton.clicked.connect(self.set_search)
        self.endButton.clicked.connect(self.cmd_end)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupCenter.setTitle(_translate("MainWindow", "执行命令: "))
        self.searchLabel.setText(_translate("MainWindow", "输入过滤内容："))
        self.searchButton.setText(_translate("MainWindow", "确认"))
        self.endButton.setText(_translate("MainWindow", "滚动到底部"))
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
        self.mActionControl.setText(_translate("MainWindow", "开启屏幕投屏"))
        self.mActionSubTop.setText(_translate("MainWindow", "查看资源&进程信息"))
        self.mActionLog.setText(_translate("MainWindow", "获取手机日志"))
        self.mActionClearLog.setText(_translate("MainWindow", "清空日志缓存"))
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
        self.stopButton.setText(_translate("DockWidget", "停止当前任务"))
        self.clearText.setText(_translate("DockWidget", "清空数据"))
