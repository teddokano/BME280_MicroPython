# BME280 class library

## What is this?
Sample code to operate a combined humidity and pressure sensor: [BME280](https://www.bosch-sensortec.com/products/environmental-sensors/humidity-sensors-bme280/).   
The BME280 operation can be done with simple API through its class library.  

This code operation is confirmed with MicroPython v1.22.0 on Raspberry Pi Pico  

![bme280.jpg](https://github.com/teddokano/BME280_MicroPython/blob/main/reference/pic/bme280.jpg)
_AE-BME280: A sensor module using BME280_

## Purpose of this code (Why this code had been written?)
### A sample of BME280 operation using both I²C and SPI interfaces
This code had been written to show samples of basic I²C and SPI operation using BME280.  
The BME280 supports I²C and SPI interfaces. The interface can be switched by CSB pin setting. When the CSB pin is tied to VDDIO, it is configured for I²C. 
For SPI, the CSB is used as a ChipSelect signal input.  
For more details, please refer section 6.1 of [BME280 datasheet](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf) 

### Bitbang sample code operation
On addition to the BME280 operation sample, this can perform **bit-banging** I²C and SPI libralies ([bbI2C](https://github.com/teddokano/bitbang_I2C_controller_MicroPython) and [bbSPI](https://github.com/teddokano/bitbang_SPI_controller_MicroPython)) demo.  
Since the MicroPython has build-in libraris of SoftI2C and SoftSPI, those handmade bit-banging interfaces may not be needed.  

However, the libraries were dared by a magazine project.  
The magazine article was tried to explain the I²C and SPI protocols from bit-banging Python code.  
This BME280.py was made as a test application of the **bbI2C** and **bbSPI**. 

## I²C and SPI interface buses
### When the `BME280.py` is used as a class library
This BME280.py can be used as a class library which supports both I²C and SPI buses. 
User don't need to tweak the code for interface changing but just giving an instance of the interface to constructor function. 

```python
# An application sample using class library in BME280.py
from machine import Pin, I2C, SPI

if USE_I2C:
    intf    = I2C( 0, sda = Pin( 0 ), scl = Pin( 1 ), freq = 400_000 )
else:
    intf    = SPI( 1, 1000000, sck = Pin( 10 ), mosi = Pin( 11 ), miso = Pin( 12 ) )
	
bme = BME280( intf )

while True:
    t, p, h	= bme.read()
    print( f"{t:5.2f} ℃, {p:7.2f} hPa, {h:5.2f} %RH" )
    sleep( 1 )
```


### When the `BME280.py` is executed alone
A main function is executed.  
In the main function, there are 4 lines to declare the `intf` instance. One of them should be enabled and others needed to be comment-out.  
The I2C and SPI can be enabled and used in default MicroPython environment.  


```python
# The main() function in BME280.py
...
..
def main():
    intf	= I2C( 0, sda = Pin( 0 ), scl = Pin( 1 ) )
    #intf	= bbI2C( sda = Pin( 0 ), scl = Pin( 1 ) )
    #intf	= SPI( 1, 1000000, sck = Pin( 10 ), mosi = Pin( 11 ), miso = Pin( 12 ) )
    #intf	= bbSPI( sck = Pin( 10 ), mosi = Pin( 11 ), miso = Pin( 12 ) )
    
    bme		= BME280( intf )
    ...
    ..
```


### If you want to try `bbI2C` and/or `bbSPI` ...

The `bbI2C` and `bbSPI` can be enabled if those libraies are installed in executable path. Those libraries are available on [bbI2C](https://github.com/teddokano/bitbang_I2C_controller_MicroPython) and [bbSPI](https://github.com/teddokano/bitbang_SPI_controller_MicroPython).  
The bbI2C.py and bbSPI.py are needed to be copied in to MicroPython device. 

![bb_libs_installed.png](https://github.com/teddokano/BME280_MicroPython/blob/main/reference/pic/bb_libs_installed.png)
_bbI2C and bbSPI libraries installed in in to MicroPython device (Operated in Thonny app)_

## Hardware and options
For I²C and SPI, diferent wirings are required.  
Followings are example of hardware connection between a Raspberry Pi Pico and a BME280.  
Power supply (3.3V) and GND are common in both cases.  

In both cases, the BME280's VDD and VDDIO are connected together. The 3.3V is supplied from pin 36 of Raspberry Pi Pico.  
Any one of a GND pin can be used on Raspberry Pi Pico (pin 3, 8, 13, 18, 23, 28, 33 or 38).  

### I²C
GP0 (pin1) and GP1 (pin2) are used for I²C SDA and SCL signals. Both of those signal lines needed to be pulled-up by resisters. 
The resister value 1kΩ~10kΩ can be used.  
The CSB pin of BME280 is tied to VDDIO pin to select I²C interface.  
The SDO is connected to GND to select I²C address: `0b1110110`. 
BME280 supports to use another I²C address: `0b1110111` by connecting SDO to VDDIO.  
![sch_I2C.png](https://github.com/teddokano/BME280_MicroPython/blob/main/reference/sch/sch_I2C.png)  
_Device connection for I2C_

BME280.py support to use both I²C addresses. The default is `0b1110110`. To specify the `0b1110111`, use option parameter of `BME280`.  
A keyword parameter `address` can be used to use the BME280 which SDO pin is tied to VDDIO.  

```python
# When BME280 SDO is connected to GND
from machine import Pin, I2C

intf = I2C( 0, sda = Pin( 0 ), scl = Pin( 1 ) )	
bme  = BME280( intf )   # to use default address of 0b1110110
```

```python
# When BME280 SDO is connected to VDDIO
from machine import Pin, I2C

intf = I2C( 0, sda = Pin( 0 ), scl = Pin( 1 ) )	
bme  = BME280( intf, address = 0b1110111 )   # to use address of 0b1110111
```


### SPI
4 wire SPI conection is supported. In next example diagram, GP10 ~ GP13 are used for SPI interface.  

![sch_SPI.png](https://github.com/teddokano/BME280_MicroPython/blob/main/reference/sch/sch_SPI.png)  
_Device connection for SPI_

If other ChipSelect(CS) pin needed to be specified on the microcontroller, it can be done by giving an option parameter for `BME280()`.  
Default setting is GP13 but other pin can be used with keyword parameter `cs`.  

```python
# When BME280 CSB is connected to GP13 (pin 17)
from machine import Pin, SPI

intf = SPI( 1, 1000000, sck = Pin( 10 ), mosi = Pin( 11 ), miso = Pin( 12 ) )
bme  = BME280( intf )   # to use GP13 as default ChipSelect pin	
```

```python
# When BME280 CSB is connected to GP15 (pin 20)
from machine import Pin, SPI

intf = SPI( 1, 1000000, sck = Pin( 10 ), mosi = Pin( 11 ), miso = Pin( 12 ) )
bme  = BME280( intf, cs = Pin( 15 ) )   # to use GP15 as ChipSelect pin instead of GP13	
```

### Handling option parameters

> **Note**  
> If `address` and `cs` are given for inapprppreate interface, the option will be just ignored.  
> If both options are given, an invalid option will be ignored.  

### Example of using AE-BME280
[AE-BME280 (Japanese site)](https://akizukidenshi.com/catalog/g/gK-09421/) is a module using BME280.   
![ae-bme280.JPG](https://github.com/teddokano/BME280_MicroPython/blob/main/reference/pic/ae-bme280.JPG)  
_AE-BME280 module_   

This module has single-inline 6 pins of VDD, GND, CSB, SDI SDO and SCK. This makes easy to wire on bread-board.  
Following wiring diagram is a sample for I²C and SPI. Both interface operations can be tried by replacing the module in slots.  
For **I²C**, ***F25~F30 slot*** can be used. For **SPI**, ***E25~E30 slot*** can be used. 


![BME280_connection.png](https://github.com/teddokano/BME280_MicroPython/blob/main/reference/sch/BME280_connection.png)
_Bread-board connections between AE-BME280 and Raspberry Pi Pico for both I²C and SPI_   

![ae-bme280-i2c-spi.png](https://github.com/teddokano/BME280_MicroPython/blob/main/reference/pic/ae-bme280-i2c-spi.png)  
_AE-BME280 slots for I²C and SPI_

## References
Reference|Link
---|---
BME280				|https://www.bosch-sensortec.com/products/environmental-sensors/humidity-sensors-bme280/
BME280 datasheet	|https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf
AE-BME280(Japanese)	|https://akizukidenshi.com/catalog/g/gK-09421/
Raspberry Pi Pico	|https://www.raspberrypi.com/products/raspberry-pi-pico/
MicroPython			|https://micropython.org
bbI2C				|https://github.com/teddokano/bitbang_I2C_controller_MicroPython
bbSPI				|https://github.com/teddokano/bitbang_SPI_controller_MicroPython
