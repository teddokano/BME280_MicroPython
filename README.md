# BME280

## What is this?
Sample code to operate a combined humidity and pressure sensor: [BME280](https://www.bosch-sensortec.com/products/environmental-sensors/humidity-sensors-bme280/).   
The BME280 operation can be done with simple API through its class library.  

This code operation is confirmed with MicroPython v1.22.0 on Raspberry Pi Pico  

![bme280.jpg](https://github.com/teddokano/BME280_MicroPython/blob/main/reference/pic/bme280.jpg)


## Purpose of this code
### A sample of BME280 operation using both I²C and SPI interfaces
This code had been written to show samples of basic I²C and SPI operation using BME280.  
The BME280 supports I²C and SPI interfaces. The interface can be switched by CSB pin setting. When the CSB pin is tied to VDDIO, it is configured for I²C. 
For SPI, the CSB is used as a ChipSelect signal input.  
For more details, please refer section 6.1 of [BME280 datacheet](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf) 

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

## Hardware

![sch_I2C.png](https://github.com/teddokano/BME280_MicroPython/blob/main/reference/sch/sch_I2C.png)  
![sch_SPI.png](https://github.com/teddokano/BME280_MicroPython/blob/main/reference/sch/sch_SPI.png)  



