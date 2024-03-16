# 基于openKylin的hid input 设备共享协议

### 1. 赛题说明
基于openKylin操作系统Wayland环境，实现多主机共享一套hid input设备的技术方案（以一套键鼠为例），形成一套具备安全性、通用性的协议标准。

### 2. 赛题要求
1)支持一套键鼠控制多台主机（大于等于2）。鼠标可在多主机之间自由移动，键盘可跟随鼠标焦点所在的窗口做输入操作。多套主机在同一时刻仅有1套设备实际响应input操作。
2)提供配置主机之间相对位置的功能，鼠标移动范围及方向受相对位置限制；
3)支持主机间剪切板功能共享
4)额外功能：支持文本文档、图片、word文档等文件的主机间拖拽功能

### 3. 赛题导师
liujie01@kylinos.cn

### 4. 参考资料
1)https://www.kernel.org/doc/html/latest/usb/usbip_protocol.html
2)https://help.ubuntu.com/community/SynergyHowto