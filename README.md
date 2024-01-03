# BME280

## What is this?
Sample code to operate a combined humidity and pressure sensor: BME280. 
The BME280 operation can be done with simple API through its class library. 
![bme280.jpg](https://github.com/teddokano/BME280_MicroPython/blob/main/reference/pic/bme280.jpg)


## I²C and SPI interface buses
The class library supports both I²C and SPI buses. 
User don't need to tweak the code for interface changing but just giving an instance of the interface to constructor function. 

```python
if USE_I2C:
	intf	= I2C( 0, sda = Pin( 0 ), scl = Pin( 1 ), freq = 400_000 )
else:
	intf	= SPI( 1, 1000000, sck = Pin( 10 ), mosi = Pin( 11 ), miso = Pin( 12 ) )
	
bme		= BME280( intf )

while True:
	t, p, h	= bme.read()
	print( f"{t:5.2f} ℃, {p:7.2f} hPa, {h:5.2f} %RH" )
	sleep( 1 )
```
