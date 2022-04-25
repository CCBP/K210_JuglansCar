<div align="center">
<img src= "assets/LOGO/juglans_banner.png" alt="LOGO" />
</div>

# JuglansCar

![Python](https://img.shields.io/badge/Python-3.8.3-red)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.7.0-yellowgreen)
![CUDA](https://img.shields.io/badge/CUDA-v11.5-brightgreen)
![NNCase](https://img.shields.io/badge/NNCase-0.2.0%20Beta4-yellow)
![Author](https://img.shields.io/badge/Author-CCBP-blue)
![license](https://img.shields.io/badge/license-MIT-lightgrey)

基于勘智K210实现的深度学习智能循迹车，使用ESP32搭建HTTP服务器提供Web页面用于小车的遥控控制。在Google Colab环境下使用Keras并基于MobileNet进行模型训练实现小车的自动横向驾驶。

# 运行环境

- K210: MaixBit
  - MaixPy v0.6.2_73 minimum with kmodel v4 support
- ESP32: NodeMCU-32S
  - IDE: VSCode+PlatfromIO
  - Framework:Arduino
- Windows
  - Python 3.8.3
  - TensorFlow/Keras 2.7.0
  - CUDA v11.5
  - cuDNN 8.3.1
- Google Colab
  - Python 3.7.13
  - TensorFlow/Keras 2.8.0
- [NNCase v0.2.0 Beta4](https://github.com/kendryte/nncase/releases/tag/v0.2.0-beta4)
- 车模: [PiRacer Pro AI Kit](https://www.waveshare.net/wiki/PiRacer_Pro_AI_Kit)

# 项目结构

```
JuglansCar
|
|---Dataset
|      |---datax
|      |      |---output
|      |      |      |---xxxx.jpg 处理过后的训练用图片
|      |      |      |---output.csv 处理后的训练数据
|      |      |---xxxx.jpg 采集的原始图片
|      |      |---dataset.csv 采集的原始数据
|      |---dataset.py 数据处理程序
|
|---ESP32
|      |---data 存放SPIFFS中的静态资源
|      |---include 存放头文件
|      |---src 存放源文件
|
|---K210
|      |---data 驾驶数据存放目录
|      |---actuator.py 舵机以及电调驱动
|      |---boot.py 配置K210 FPIOA
|      |---dataset.py 采集数据，可以自动从上一次编号继续
|      |---main.py 主要逻辑控制程序
|      |---model.kmodel 模型文件
|      |---pca9685.py PCA9685驱动程序
|      |---PINController.py 引脚相关驱动控制程序，包括按键、LED等
|      |---receiver.py 接收并执行来自ESP32的控制命令
|
|--- PCB
|      |---3D drawing 3D模型文件
|      |---JuglansPCB 用于将K210与ESP32连接到小车驱动扩展板的PCB工程目录
|      |---datasheet 绘制PCB所用到的数据手册
|
|---Train
       |---calibrate 用于kmodel的量化与预测图片
       |---data
       |      |---xxxx.jpg 训练图片
       |      |---output.csv 训练数据
       |---keras_applications 修改过的MobileNet
       |---kmodel_infer 储存使用kmodel预测出的二进制文件
       |---model.h5 keras模型
       |---model.tflite TensorFlowLite模型
       |---model.kmodel kmodel模型
       |---model_train.ipynb 模型训练程序
       |---nnc Linux NNCase v0.2.0 Beta4
       |---ncc.exe Windows NNCase v0.2.0 Beta4
```

下面对一些重要部分分别进行详细说明。

## ESP32

ESP32工程目录，使用Arduino框架在VSCode下使用PlatformIO插件的方式进行开发。ESP32以Station模式运行，故需在`src/main.c`中设置路由器的SSID及密码以接入本地网络，在成功接入网络后会通过**串口**打印本机IP地址，全部初始化完成后便会保持板载蓝色LED常亮（**若LED熄灭则说明ESP32重启**），之后便可通过此IP地址连接至服务器，可在提供的页面中操控摇杆实现对小车的控制。

控制信息通过WebSock进行传输，ESP32在接收到控制信息后会立即通过I2C转发至K210中；在WebSocket客户端成功连接后ESP32会将`CONNECT_STATE`引脚拉高（断开时拉低），以通知K210开始通过串口传输图像数据，ESP32会使用`multipart/x-mixed-replace`类型实现HTTP的实时视频流（由于速度过慢**已禁用**）。

### data

此目录用于存放将会被烧录进ESP32的SPIFFS中的资源文件，包括HTML、JavaScript、CSS等文件（修改自DonkeyCar），用于当用户访问时提供相应的页面，为了加快传输速度通过删去换行的方式进行了压缩，并且由于ESP32文件系统对路径长度的限制对文件名进行了缩减。由于本身精力有限，此目录下包含很多冗余文件，并且页面的功能也并不完善。

## K210

K210工程目录，可直接将此目录下的文件拷贝至SD卡中使用。此工程项目主要功能为接收ESP32传来的控制信息、与驱动扩展板通信与进行模型的运算，实现了小车的遥控驾驶、自动横向驾驶以及对驾驶数据的采集以用于模型训练。

MaixBit板载RGB三色LED，其中当K210初始化完成后**红色LED闪烁**，表示K210正常运行；K2用于切换是否进行数据采集，当允许数据采集时**绿色LED常亮**，并且仅当按键按下且小车速度大于零时才储存行驶数据（倒车时不储存）；K3用于切换是否进行自动横向驾驶，当允许自动横向驾驶时**蓝色LED**常亮。

### data

驾驶数据存放目录，运行时会自动将道路图像储存在此并生成储存相应转角、速度信息的`dataset.csv`文件，`dataset.scv`文件中每一行对应一张道路图像，第一列为图像编号，与储存的图像名相同；第二列为转角信息；第三列为速度信息。采集功能由`dataset.py`完成，为防止采集速度过快使数据相差不大，设置为默认**50ms进行一次采集**。

### actuator.py

此程序用于提供接口驱动PCA9685控制舵机以及电调，在程序开头给出了一些常量，可以通过修改这些值改变舵机的最大角度与电机的最大转速，以进行小车的校准。

```
# STEERING FOR PWM_STEERING_THROTTLE (and deprecated I2C_SERVO)
STEERING_CHANNEL = 1            # (deprecated) channel on the 9685 pwm board 0-15
STEERING_LEFT_PWM = 450         # pwm value for full left steering
STEERING_RIGHT_PWM = 250        # pwm value for full right steering

# THROTTLE FOR PWM_STEERING_THROTTLE (and deprecated I2C_SERVO)
THROTTLE_CHANNEL = 0            # (deprecated) channel on the 9685 pwm board 0-15
THROTTLE_FORWARD_PWM = 400      # pwm value for max forward throttle
THROTTLE_STOPPED_PWM = 370      # pwm value for no movement
THROTTLE_REVERSE_PWM = 320      # pwm value for max reverse throttle
```

## Dataset
### dataset.py

此程序用于将K210采集到的包含道路图像的`xxxx.jpg`文件以及储存图片编号、转角与速度的`dataset.csv`文件进行处理。具体为依次读取**认为处理**过后的图像，同时读取`dataset.csv`中与图像编号对应的转角及速度信息，跳过速度为负的**倒车**数据，之后对所有图像与对应的速度、转角信息以新的编号依序储存在`output`目录下，其中通过使用OpenCV读取并重新保存的方式消除`Corrupt JPEG data: premature end of data segment`错误，处理过程如下：

1. **人为**对采集到的道路图像进行筛选，删除掉因操作不当而导致无法使用的图像；
2. 运行`dataset.py`，并依照提示依次输入：
   - 数据存放路径，即原始`xxxx.jpg`与`dataset.csv`文件的所在路径；
   - 图片起始编号，即原始`xxxx.jpg`的最小编号（**可小于等于**）；
   - 图片结束编号，即原始`xxxx.jpg`的最大编号（**可大于等于**）；
   - 储存起始编号，即**处理过后**图像储存的起始编号。
3. 读取图像与转角、速度数据->跳过倒车数据->在`output`目录下重新储存

关于**储存起始编号**是为了当分几次收集并处理数据后，方便接续上一次的数据编号。

## Train
### model_train.ipynb

此程序用于在Google Colab的**托管环境**及**本地环境**下完成数据处理、模型构建、模型训练、模型转换与模型验证的全过程。在Google Colab托管环境下需在**Google Drive**根目录下新建`Juglans/data`目录，并将训练数据即道路图像`xxxx.jpg`与储存转角、速度信息的`output.csv`文件存放在该目录下，而在程序运行过程中生成的所有文件将会储存在`Juglans`目录下；在本地环境下需将此程序与包含训练数据的`data`文件夹放在同一目录下，程序运行过程中生成的所有文件也会存放在当前目录中。

注：
- 也可参照[这些说明](https://research.google.com/colaboratory/local-runtimes.html)在Google Colab中创建本地连接运行此程序；
- 虽然存在数据增强部分，但并未使用。

### keras_applications

由于使用MobileNet作为模型架构，为了使其满足KPU的[加速条件](https://wiki.sipeed.com/soft/maixpy/zh/course/ai/basic/maixpy_hardware_ai_basic.html#%E5%85%B3%E4%BA%8E-KPU)，故需对其做做一些修改。[这里](https://en.bbs.sipeed.com/t/topic/682)给出了详细说明并给出了[修改后的程序](https://github.com/sipeed/Maix-Keras-workspace)，但由于TensorFlow/Keras的版本更新其中一些语法已经发生变化，故我又在其基础上进行了一些修改以使其可以在我的环境中正常运行，并存放在此目录下以便`model_train.ipynb`可以直接调用。

### calibrate

此目录用于存放使用OpenCV的`cv2.resize(img, (160, 160))`函数将训练图像缩放为**160X160像素**后的图像数据，用于在NNCase模型转换时进行量化，以及用于对转换过后的kmodel文件进行验证。

# 已知问题
- 模型准确率以及在K210中的运行速度有待提升；
- 使用**手机**连接ESP32时页面发送过慢会使看门狗超时，导致需多次尝试才可成功连接，而使用电脑连接时则不会出现该问题，推测为需要发送的页面过大导致；
- 图传速度过慢，故目前已禁用；
- 控制页面还需优化。

# 相关链接
- [MaixPy 文档简介](https://wiki.sipeed.com/soft/maixpy/zh/)
- [Keras 中文文档](https://keras.io/zh/)
- 我的博客：
  - [Juglans](https://www.ccbp.me/2022/01/03/juglans/)
  - [kmodel 避坑指南](https://www.ccbp.me/2022/04/25/kmodel/)
- [漂移驴车-1-硬件组装教程](https://www.bilibili.com/video/BV1qQ4y1S7kw?spm_id_from=444.41.header_right.fav_list.click)

# 致谢
- [DonkeyCar](https://www.donkeycar.com/)
- [sipeed_k210_dokeycar](https://github.com/apinuntong/sipeed_k210_dokeycar)
- [深圳嘉立创](https://www.jlc.com/)
- [Behavioral Cloning](https://github.com/Gan-Tu/CarND-Behavioral-Cloning)
- [Chenghsi Hsieh: Deep Learning with Python video tutorial](https://www.youtube.com/playlist?list=PL8xPPUJdubH7CDmUqRioMdM3nnxJv2PGX)
- [Deep Learning with Python](https://www.manning.com/books/deep-learning-with-python)
- [flaticon walnut](https://www.flaticon.com/free-icon/walnut_811674)