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

## I²C and SPI interface buses
The class library supports both I²C and SPI buses. 
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


## Hardware
![sch_I2C.png](https://github.com/teddokano/BME280_MicroPython/blob/main/reference/sch/sch_I2C.png)  
![sch_SPI.png](https://github.com/teddokano/BME280_MicroPython/blob/main/reference/sch/sch_SPI.png)  



