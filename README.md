# Mobile-GUI

pyqt5 编写的 可运行在 win、mac ，包含 iOS 和 Android 设备 GUI 命令行操控工具

功能：
- 获取设备基本信息
- 获取基础日志信息，导出 crash 日志
- 获取截图，清理缓存
- 以安装软件导出成 APK
- 批量安装卸载 
- [MobileGUI 下载](https://github.com/YueChen-C/mobile-gui/releases)  

### 运行项目
app.ini  按需配置自己常用 App 包名

win 运行需要安装 iTunes

mac 运行需要安装 


```
> brew install libimobiledevice
> brew install ideviceinstaller
> brew install scrcpy
```
启动程序
```
python ./app/Main.py
```



### 打包项目
打包成 EXE,mac执行文件

```
# 在 win 下打包成 .EXE
pyinstaller Main_win.spec 
# 在 mac 下打包成 .app
pyinstaller Main_mac.spec 
```



### Mac GUI 程序无法引用环境变量问题：
- 方案一：修改 spce 文件打包参数 LSEnvironment 增加 GUI 参数与环境变量字符串,直接打包
- 方案二：如果是打包完成的程序，可使用右键打开 ***.app 显示包内容修改 info.plist 增加 LSEnvironment 参数中添加 参数 GUI 与环境变量字符串
- 方案三：修改 mac 环境变量使之支持 GUI 程序可引用
- 最简单方案：打包后使用命令行方式 open ***.app 直接启动可避免无法找到环境变量问题

![](temp.png)