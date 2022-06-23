import sensor, time, lcd, ujson
import  dataset, PinController
from machine import UART
import KPU as kpu

sensor.reset()                      # Reset and initialize the sensor. It will
                                    # run automatically, call sensor.run(0) to stop
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect
clock = time.clock()                # Create a clock object to track the FPS

# configure the UART for transferring images
uart = UART(UART.UART2, 5000000, timeout=1000, read_buf_len=64)

# load model
model = kpu.load("/sd/model.kmodel")
kpu.set_outputs(model, 0, 1, 1, 1)

recorder = dataset.Dataset()
pin = PinController.PinController()
print("[I] K210 initialized")

auto = False
record = False
angle = ""
speed = ""

while (True):
    pin.led_r()                     # blink, K210 is alive
    # clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot()         # Take a picture and return the image
    #lcd.display(img)                # Display on LCD
    #print(clock.fps())              # Note: MaixPy's Cam runs about half as fast when connected
                                    # to the IDE. The FPS should increase once disconnected
    '''
    - command为从ESP32接收到的数据，可以选择设置接收的字节数量或者接收一行
        - 串口文档：https://wiki.sipeed.com/soft/maixpy/zh/api_reference/machine/uart.html#read
    - command需要解析出命令与参数几个部分之后进行判断，执行记录或自动驾驶操作
      解析方式可以参考：
        - JSON数据格式：https://wiki.sipeed.com/soft/maixpy/zh/api_reference/standard/ujson.html
        - 字符串分割：https://www.runoob.com/python3/python3-list.html
    - 我这里以逗号（","）为分隔符解析ESP32发送过来的命令
        - 记录命令需持续发送带有起始标志的命令，发送一次尝试进行一次记录
          （为防止记录过多冗余数据，设置为大于50ms才会保存一次），
          若想要停止记录则需要发送结束命令，记录状态下绿灯常亮
        - 自动驾驶命令为开关量，即发送一次改变一次状态，无需持续发送，
          自动驾驶状态下蓝灯常亮
    '''

    command = uart.read()           # Receive control commands from ESP32
    command = command.split(",")
    if command[0] == "":            # Record mode on
        record = True
        angle = command[1]
        speed = command[2]
    elif command[0] == "":          # Record mode off
        record = False

    if command[0] == "":            # Autopilot mode
        auto = not auto

    if record:                      # Record mode
        pin.led_g(0)                # On
        angle = command[1]
        speed = command[2]
        recorder.save(img, angle, speed)
        uart.write("OK")            # Send ack to ESP32
        print("[I] angle:%s\tspeed:%s" % (angle, speed))
    else:
        pin.led_g(1)                # Off

    if auto:                        # Autopilot mode
        pin.led_b(0)                # On
        calcu_start = time.ticks_ms()# Start calculating
        img = img.resize(160, 160)
        img.pix_to_ai()             # Sync "RGB888" memory block
        fmap = kpu.forward(model, img)
        calcu_end = time.ticks_ms() # End calculation
        plist = fmap[:]
        uart.write(plist[0])        # Send calculation results to ESP32
        print("[I] pridict angle: %f\t(%.2f ms)" % (plist[0], calcu_end - calcu_start))
    else:
        pin.led_g(1)                # Off