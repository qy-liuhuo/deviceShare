# DeviceShare —— 跨平台多主机输入设备共享

## 项目介绍
![](https://img.qylh.xyz/blog/1723181688963.png)
DeviceShare 是一款跨平台的多主机输入设备共享工具，支持 Windows、Linux、MacOS 等操作系统,支持在Wayland环境下运行。
通过 DeviceShare，您可以在多台主机之间共享鼠标、键盘、剪贴板等输入设备，实现多台主机之间的输入设备共享。


## 功能特性

1. **跨平台支持**：支持 Windows、Linux、MacOS 等操作系统。
2. **多主机支持**：支持多台主机之间的输入设备共享。
3. **鼠标共享**：支持鼠标在多台主机之间的共享。
4. **键盘共享**：支持键盘在多台主机之间的共享。
5. **剪贴板共享**：支持剪贴板在多台主机之间的共享。
6. **屏幕位置配置**：支持配置屏幕位置，方便多台主机之间的切换。
7. **主机发现机制**：支持自动发现局域网内的主机。
8. **安全性**：支持公私钥加密机制，支持对剪贴板内容加密传输。
9. **易用性**：支持一键启动，无需复杂配置。
10. **开源免费**：支持开源免费使用。

**演示环境**
![1719817611466.png](https://img.qylh.xyz/blog/1719817611466.png)

**双机演示**

https://github.com/qy-liuhuo/deviceShare/assets/60374114/6e126292-22e0-4d91-bab9-272470689ecd


**三机演示**

https://github.com/qy-liuhuo/deviceShare/assets/60374114/1b911b8a-976f-4128-9518-9c64c73a7a39



## 使用说明
针对x86架构的Windows、OpenKylin操作系统，我们打包构建了可执行程序，可在Release界面下载合适的版本。 

若构建的版本无法支持目标机器，可选择源码运行或自行打包。该方案需具备Python3 环境，具体步骤如下：
1. 获取项目代码
2. 使用`pip install -r requirements.txt`命令安装依赖
3. 执行`python deviceShare.py`启动程序
<<<<<<< HEAD
4. 安装`pyinstaller`
5. 使用`pyinstaller`打包目标程序
=======
4. 安装`pyinstaller`: `pip install pyinstaller`
5. 使用`pyinstaller`打包目标程序: `pyinstaller deviceShare.spec`
6. 运行`dist`目录下生成的可执行文件
7. 将`resources`目录复制到dist目录下
8. 若在Linux下运行，采用脚本`run.sh`启动程序，将`run.sh`复制到dist目录下，执行`sudo chmod 777 run.sh`赋予执行权限，执行`bash run.sh`启动程序,windows下无需执行此步骤,直接运行exe文件即可
>>>>>>> dev

6. 注意Kylin操作系统在安装python的evdev依赖时可能出现错误，请选择安装预编译版本evdev-binary，参考 https://python-evdev.readthedocs.io/en/latest/install.html

## 控制原理

1. 主要基于`pynput`进行鼠标和键盘的控制，基于`pyperclip`进行剪切板的控制。
2. 在`wayland`环境下，基于`evdev`和`uinput`进行鼠标和键盘的控制，基于`wl-clipboard`进行剪切板的控制。

## 系统架构

![1723181787105.png](https://img.qylh.xyz/blog/1723181787105.png)

项目的整体设计框架如上图所示，整体由四个部分构成：
- 服务端为Hid Input设备的拥有者，可向其他客户端主机共享其拥有的输入设备。
- 客户端可使用主机共享的输入设备。
- 网络通信模块用于服务端和客户端的数据传输。
- 设备控制模块用于读取Hid Input设备信息及控制Hid Input设备。

项目目录结构
```
DeviceShare
├── resources # 资源文件
├── src # 源码
│   ├── communication # 网络通信模块
│   │   ├── client_state.py # 客户端状态
│   │   ├── message.py # 消息定义
│   │   └── my_socket.py # socket封装
│   ├── controller # 设备控制模块
│   │   ├── clipboard_controller.py # 剪切板控制
│   │   ├── keyboard_controller.py # 键盘控制
│   │   └── mouse_controller.py # 鼠标控制
│   ├── gui # GUI界面
│   │   ├── client_gui.py # 客户端GUI
│   │   ├── position.py # 屏幕位置
│   │   ├── screen.py # 屏幕管理
│   │   └── server_gui.py # 服务端GUI 
│   ├── utils # 工具模块
│   │   ├── device.py # 设备信息
│   │   ├── device_name.py #  设备名称
│   │   ├── device_storage.py # 设备存储 
│   │   ├── key_code.py # 键盘按键 
│   │   ├── key_storage.py # 键盘存储
│   │   ├── net.py # 网络工具 
│   │   ├── plantform.py # 平台信息
│   │   ├── rsautil.py # RSA加密工具 
│   │   └── service_listener.py # 服务监听
│   ├── client.py # 客户端,被控设备
│   └── server.py # 服务端,主控设备
├── deviceShare.py # 启动程序
├── run.sh # linux启动脚本
├── deviceShare.spec # pyinstaller打包配置
├── keys.db # RSA密钥存储，自动生成
├── readme.md # 说明文档
├── requirements.txt # 依赖
└── temp.db # 设备信息存储, 自动生成
```


软件的运行流程如下图所示，客户端与服务端作为两个独立模块单独启动，客户端启动后会向局域网中广播自身信息，
服务端收到广播信息后将其加入主机列表，并配置屏幕间的相对位置信息。当服务端主机的光标移出屏幕范围后，会自动判断接下来被控的主机，
并将本机输入设备产生的输入拦截，通过网络模块转发给客户端，客户端收到输入信息后响应相应的控制信号。当客户端的光标移出范围后向服务端主机发送事件标志，
服务端主机停止控制信号的转发，并恢复输入事件的响应。

![1723181806729.png](https://img.qylh.xyz/blog/1723181806729.png)

服务端为具备Hid Input设备的主机，由以下几个线程构成：
- 主线程：服务注册及启动其他线程
- TCP监听线程：用于监听处理TCP连接，并为每一个连接创建子线程。
- TCP 处理线程，用于处理与客户端的TCP连接
- 消息监听线程：监听客户端消息，主要为心跳信息和剪切板信息
- 设备监听线程：监听Hid Input设备的输入信息和剪切板信息。
- GUI线程： GUI界面的显示和处理。

![1723181908743.png](https://img.qylh.xyz/blog/1723181908743.png)

客户端为需要使用服务主机的Hid Input设备的主机，由以下几个线程构成：
- 主线程：处理服务发现，发起连接请求，启动其他线程。
- 心跳包线程：定期发送心跳包。
- 消息监听线程：用于接收并响应主机传递的控制信息。
- GUI线程： GUI界面的显示和处理。
- 设备监听线程：用于监听鼠标移出事件及剪切板更新事件。

![1723181937936.png](https://img.qylh.xyz/blog/1723181937936.png)

## TODO
- [x] 主机发现机制
- [x] 屏幕位置配置
- [x] 鼠标共享功能
- [x] 键盘共享功能
- [x] 剪切板共享功能
- [x] 剪切板内容加密传输
- [x] 优化屏幕管理功能
- [x] 优化代码质量，提升代码可读性，提升软件性能和稳定性
- [x] 测试更多类型操作系统
- [x] 优化文档
<<<<<<< HEAD
- [ ] 解耦各设备共享模块，支持用户自定义开关相关功能
- [ ] 文件拖拽共享功能
=======
- [ ] 文件拖拽共享功能(实现中)
>>>>>>> dev
