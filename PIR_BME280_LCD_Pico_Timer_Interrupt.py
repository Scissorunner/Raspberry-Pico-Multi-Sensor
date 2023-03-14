from machine import Pin, I2C, ADC, PWM
from utime import sleep, time
from lib import BME280
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

# ----- setup I2C LCD
I2C_ADDR     = 0x27
I2C_NUM_ROWS = 4
I2C_NUM_COLS = 20

i2c1 = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000) # Pin assignment
lcd = I2cLcd(i2c1, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
# ----- end

# ----- setup I2C BME280
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=10000) # Pin assignment
bme = BME280.BME280(i2c=i2c)
# ----- end

# ----- setup PIR motion sensor and interrupt
motion = False
start_timer = False
last_motion_time = 0
delay_interval = 9

def handle_interrupt(pin):
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Warning!")    
    lcd.move_to(0, 1)
    lcd.putstr("Intruder!     ")    
    print("Warning!")
    global motion, last_motion_time, start_timer # global variable - usable both inside the function and throughout the code
    motion = True
    start_timer = True
    last_motion_time = time()
    
pir = Pin(15, Pin.IN)
red_led = Pin(14, Pin.OUT)

pir.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)
# ----- end

# ----- LDR
ldr = ADC(26)
blue_led = Pin(13, Pin.OUT)
# ----- end

# ----- Voltage Measure
#red_led = Pin(15, Pin.OUT)
#yellow_led = Pin(14, Pin.OUT)
#green_led = Pin(13, Pin.OUT)
adc_value = ADC(27)
ref_voltage = 3.07  # measure pico board with multimeter
R1 = 30000.0  # voltage divider board, divides voltage by 5
R2 = 7500.0
# ----- end

while True:
    if motion and start_timer:
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Warning!")
        lcd.move_to(0, 1)
        lcd.putstr("Motion Detected!!")
        red_led.value(1)
        start_timer = False
         
        for i in range(10, -1, -1):
            sleep(1)
            lcd.move_to(0, 2)
            lcd.putstr("Countdown: " + (str(i)) + " ")
            print(i)
        
    elif motion and (time() - last_motion_time) > delay_interval:
        print("Motion stopped!")
        red_led.value(0)
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Motion stopped")
        lcd.move_to(0, 1)
        lcd.putstr("Clear to resume")
        sleep(2)
        lcd.clear()
        motion = False
        
    lightlevel = ldr.read_u16()
    print("Light level:", lightlevel)
    if (lightlevel < 30000):
        blue_led(1)
    else:
        blue_led(0)
    sleep(0)
    
    value = adc_value.read_u16() # "value" is now a variable
    print("raw value", value)
    adc_voltage = value * ref_voltage / 65536
    print("adc voltage", adc_voltage)
    in_voltage = str(round(adc_voltage, 2) / (R2/(R1+R2)))
    print("voltage", in_voltage)
    
    tempC = bme.temperature
    hum = bme.humidity
    pres = bme.pressure
    tempF = (bme.read_temperature()/100) * (9/5) + 32 # temperature in Fahrenheit
    temp = str(round(tempF, 2)) + "F    "
    print("Temperature Celcius: ", tempC)
    print("Temperature Fahrenheit: ", tempF)
    print("Humidity: ", hum)
    print("Pressure: ", pres)
  
    #lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Voltage: ") # Text string
    lcd.putstr(in_voltage)
    lcd.move_to(0, 1)
    lcd.putstr("Temp F: ")
    lcd.putstr (temp)
    lcd.move_to(0, 2)
    lcd.putstr("Humidity: ")
    lcd.putstr(hum)
    lcd.move_to(0, 3)
    lcd.putstr("Pressure: ")
    lcd.putstr(pres)
    sleep(0)
