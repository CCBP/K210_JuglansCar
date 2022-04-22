![LOGO](assets/LOGO/juglans_banner.png)
# JuglansCar
基于勘智K210实现的深度学习智能循迹车，使用ESP32搭建HTTP服务器提供Web页面用于小车的遥控控制。在Google Colab环境下使用Keras并基于MobileNet进行模型训练实现小车的自动横向驾驶。
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
|---ESP32 ESP32工程目录
|
|---K210 K210工程目录
|
|--- PCB
|      |---3D drawing 3D模型文件
|      |---JuglansPCB 用于将K210与ESP32连接到小车驱动扩展板的PCB工程目录
|      |---datasheet 绘制PCB所用到的数据手册
|
|---Train
|      |---data
|      |      |---xxxx.jpg 训练图片
|      |      |---output.csv 训练数据
|      |---kmodel_infer 使用kmodel的预测结果
|      |---calibrate 用于kmodel的量化与预测图片
|      |---model.h5 keras模型
|      |---model.tflite TensorFlowLite模型
|      |---model.kmodel kmodel模型
|      |---ncc.exe Windows NNCase v0.2.0 Beta4
|      |---nnc Linux NNCase v0.2.0 Beta4
|
|---assets/LOGO
```