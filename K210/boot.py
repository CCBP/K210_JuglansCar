from fpioa_manager import fm

print("K210 initializing")

# LED G R B
fm.register(12, fm.fpioa.GPIO0)
fm.register(13, fm.fpioa.GPIO1)
fm.register(14, fm.fpioa.GPIO2)
# ESP32 state
fm.register(35, fm.fpioa.GPIOHS0)
# KEY 2 3 4 5
fm.register(34, fm.fpioa.GPIOHS2)
fm.register(33, fm.fpioa.GPIOHS3)
fm.register(32, fm.fpioa.GPIOHS4)
fm.register(31, fm.fpioa.GPIOHS5)
# UART2
fm.register(8, fm.fpioa.UART2_TX)
fm.register(9, fm.fpioa.UART2_RX)