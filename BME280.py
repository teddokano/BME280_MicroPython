"""
BME280 (combined humidity and pressure sensor) operation sample
This code demonstrates basic feature of BME280. 
The BME280 supports I2C and SPI interfaces. Both interfaces are supported in this code. 
On addition to that, bbI2C and bbSPI classes are supported to perform the operation with those "bit-bang" interface classes. 
For bbI2C and bbSPI, see following repositories
	bbI2C: https://github.com/teddokano/bitbang_I2C_controller_MicroPython
	bbSPI: https://github.com/teddokano/bitbang_SPI_controller_MicroPython
	
This project is licensed under the MIT License, see LICENSE.txt file for details in 
https://github.com/teddokano/BME280_MicroPython
"""

from	machine	import	Pin, I2C, SPI
from	utime	import	sleep, sleep_ms
from	struct	import	unpack

try:
	from	bbI2C	import	bbI2C
except ImportError:
	pass
	
try:
	from	bbSPI	import	bbSPI
except ImportError:
	pass

DEFAILT_ADDRESS		= 0xEC >>1

class BME280_base:
	"""
	A class to operate a combined humidity and pressure sensor: BME280
	
	https://www.bosch-sensortec.com/products/environmental-sensors/humidity-sensors-bme280/
	"""
	def __init__( self ):
		"""
		BME280 initializer
	
		Parameters
		----------
		i2c : obj
			machine.I2C instance
		address : int
			I2C target (device) address
		"""
		
		(self.dig_T1, self.dig_T2, self.dig_T3)		= unpack( "<Hhh", self.read_reg( 0x88, 6 ) )

		(self.dig_P1, self.dig_P2, self.dig_P3, self.dig_P4, self.dig_P5, self.dig_P6, 
			self.dig_P7, self.dig_P8, self.dig_P9)	= unpack( "<Hhhhhhhhh", self.read_reg( 0x8E, 18 ) )
			
		self.dig_H1	= self.read_reg( 0xA1 )
		
		(self.dig_H2, self.dig_H3, E4, E5, E6, self.dig_H6)	= unpack( "<hBbbbb", self.read_reg( 0xE1, 7 ) )
		self.dig_H4	= (E4 << 4) | (E5 & 0x0F)
		self.dig_H5 = (E6 << 4) | (E5 >> 4)
		
		self.t_fine	= 0

		s	= 0x01
		self.write_reg( 0xF2, s )
		self.write_reg( 0xF4, (s << 5) | (s << 2) | 0x3 )
		
		sleep_ms( 14 )	# t_maesure(max) : waiting for first measurement complete (datasheet 9.1)
	
	def read( self ):
		data 	= self.read_reg( 0xF7, 8 )		
		pH, pL, tH, tL, h	= unpack( ">HBHBH", data )

		return self.compensate_T( tH << 4 | tL >> 4 ), self.compensate_P( pH << 4 | pL >> 4 ), self.compensate_H( h )
	
	def temperature( self ):
		"""
		get temperature value in degree-C
		
		Returns
		-------
		float : temperature value in degree-C
		"""
		data 	= self.read_reg( 0xFA, 3 )
		adc_T_High, adc_T_Low	= unpack( ">HB", data )
		return self.compensate_T( adc_T_High << 4 | adc_T_Low >> 4 )
	
	def pressure( self ):
		"""
		get pressure value in hPa
		
		Returns
		-------
		float : pressure value in hPa
		"""
		data 	= self.read_reg( 0xF7, 3 )
		adc_P_High, adc_P_Low	= unpack( ">HB", data )
		return self.compensate_P( adc_P_High << 4 | adc_P_Low >> 4 )

	def humidity( self ):
		"""
		get humidity value in %RH
		
		Returns
		-------
		float : humidity value in %RH
		"""
		data 	= self.read_reg( 0xFD, 2 )
		adc_H	= unpack( ">H", data )[ 0 ]
		return self.compensate_H( adc_H )
		
	def compensate_T( self, adc_T ):
		"""
		Calculate temperature from sensor read value
		
		Parameters
		----------
		adc_T : int
			read value form register 0xFA-0xFC as big-endian 20 bit integer
			
		Returns
		-------
		float : temperature value in degree-C

		"""
		var1	= ((((adc_T >> 3) - (self.dig_T1 << 1))) * (self.dig_T2)) >> 11
		var2	= (((((adc_T >> 4) - (self.dig_T1)) * ((adc_T >> 4) - (self.dig_T1))) >> 12) * (self.dig_T3)) >> 14
		self.t_fine	= var1 + var2
		T		= (self.t_fine * 5 + 128) >> 8
		return T / 100

	def compensate_P( self, adc_P ):
		"""
		Calculate pressure from sensor read value
		
		Parameters
		----------
		adc_P : int
			read value form register 0xF7-0xF9 as big-endian 20 bit integer
			
		Returns
		-------
		float : temperature value in hPa

		"""
		var1 = self.t_fine - 128000
		var2 = var1 * var1 * self.dig_P6
		var2 = var2 + ((var1 * self.dig_P5) << 17)
		var2 = var2 + (self.dig_P4 << 35)
		var1 = ((var1 * var1 * self.dig_P3) >> 8) + (var1 * self.dig_P2 << 12)
		var1 = (((1 << 47) + var1)) * self.dig_P1 >> 33
		
		if (var1 == 0):
			return 0
		
		p = 1048576 - adc_P
		p = (((p << 31) - var2) * 3125) // var1
		var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
		var2 = (self.dig_P8 * p) >> 19
		p = ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)
		return p / 25600

	def compensate_H( self, adc_H ):
		"""
		Calculate humidity from sensor read value
		
		Parameters
		----------
		adc_H : int
			read value form register 0xFD and 0xFE as big-endian 16 bit integer
			
		Returns
		-------
		float : temperature value in %RH
		
		"""
		v_x1_u32r = self.t_fine - 76800
		v_x1_u32r = (((((adc_H << 14) - (self.dig_H4 << 20) - (self.dig_H5 * v_x1_u32r)) + 16384) >> 15) * (((((((v_x1_u32r * self.dig_H6) >> 10) * (((v_x1_u32r * self.dig_H3) >> 11) + 32768)) >> 10) + 2097152) * self.dig_H2 + 8192) >> 14))
		v_x1_u32r = (v_x1_u32r - (((((v_x1_u32r >> 15) * (v_x1_u32r >> 15)) >> 7) * self.dig_H1) >> 4))
		v_x1_u32r = 0 if (v_x1_u32r < 0) else v_x1_u32r
		v_x1_u32r = 419430400 if (v_x1_u32r > 419430400) else v_x1_u32r
		return (v_x1_u32r >> 12) / 1024

	def show_reg( self, r ):
		"""
		Print register value
		
		Parameters
		----------
		r : int
			Register address			
		"""
		print( "reg:0x{:02X} = 0x{:02X}".format( r, self.read_reg( r ) ) )
		
	def show_dump( self ):
		reg_list	= [ 0xF2, 0xF3, 0xF4, 0xF5 ]
		
		for r in reg_list:
			self.show_reg( r )

class BME280_I2C( BME280_base ):
	def __init__( self, i2c, address = DEFAILT_ADDRESS ):
		"""
		BME280 initializer
	
		Parameters
		----------
		i2c : obj
			machine.I2C instance
		address : int
			I2C target (device) address
		"""
		self.__i2c	= i2c
		self.__addr	= address
		
		super().__init__()

	def write_reg( self, r, v ):
		"""
		Write register
		
		Parameters
		----------
		r : int
			Register address			
		v : int
			Value to write into the register	
		"""
		self.__i2c.writeto( self.__addr, bytearray( [ r, v ] ) )

	def read_reg( self, r, len = None ):
		"""
		Read register
		
		Parameters
		----------
		r : int
			Register address			
		len : int (option)
			Read length	

		Returns
		-------
		int : 		If len was not given or 1
		bytearray : If len was >1
		
		"""
		if len is None:
			len	= 1

		self.__i2c.writeto( self.__addr, bytearray( [ r ] ), False )
		
		data	= self.__i2c.readfrom( self.__addr, len )
		
		if len is 1:
			return list( data )[ 0 ]
		else:
			return data
		
class BME280_SPI( BME280_base ):
	def __init__( self, spi, cs = None ):
		"""
		BME280 initializer
	
		Parameters
		----------
		spi : obj
			machine.SPI instance
		cs : obj
			machine.Pin instance for chip_select
		"""
		
		self.__spi	= spi
		self.__cs	= cs if cs else Pin( 13 )
		
		self.__cs.init( Pin.OUT )
		
		self.__cs.value( 1 )
		sleep_ms( 2 )	# Wait until SPI read become ready

		super().__init__()


	def write_reg( self, r, v ):
		"""
		Write register
		
		Parameters
		----------
		r : int
			Register address			
		v : int
			Value to write into the register	
		"""
		
		data	= bytearray( [ r & 0x7F, v ] )
		
		self.__cs.value( 0 )
		self.__spi.write_readinto( data, data )
		self.__cs.value( 1 )

	def read_reg( self, r, len = None ):
		"""
		Read register
		
		Parameters
		----------
		r : int
			Register address			
		len : int (option)
			Read length	

		Returns
		-------
		int : 		If len was not given or 1
		bytearray : If len was >1
		
		"""
		if len is None:
			len	= 1
			
		data	= bytearray( [ r | 0x80 ] + [ 0xFF for _ in range( len ) ] )

		self.__cs.value( 0 )
		self.__spi.write_readinto( data, data )
		self.__cs.value( 1 )

		if len is 1:
			return list( data )[ 1 ]
		else:
			return data[ 1: ]

def BME280( interface, *, address = DEFAILT_ADDRESS, cs = None ):
	"""
	A constructor interface for BME280

	Parameters
	----------
	interface	: obj
		machine.I2C or machine.SPI object
	address		: int (option)
		If need to specify (for I2C interface)
	cs			: machine.Pin object (option)
		If need to specify (for SPI interface)

	Returns
	-------
	BME280_I2C or BME280_SPI object
		returns BME280_I2C when interface is I2C or bbI2C
		returns BME280_SPI when interface is SPI or bbSPI

	Examples
	--------
	For using I2C
		>>> intf = I2C( 0, freq = (400 * 1000) )
		>>> rtc  = BME280( intf )
	For using SPI
		>>> intf = SPI( 0, 500 * 1000, cs = 0 )
		>>> rtc  = BME280( intf )
	
	"""
	if isinstance( interface, I2C ) or isinstance( interface, bbI2C ):
		return BME280_I2C( interface, address )

	if isinstance( interface, SPI ) or isinstance( interface, bbSPI ):
		return BME280_SPI( interface, cs )



def main():
	intf	= I2C( 0, sda = Pin( 0 ), scl = Pin( 1 ) )
	#intf	= bbI2C( sda = Pin( 0 ), scl = Pin( 1 ) )
	#intf	= SPI( 1, 1000000, sck = Pin( 10 ), mosi = Pin( 11 ), miso = Pin( 12 ) )
	#intf	= bbSPI( sck = Pin( 10 ), mosi = Pin( 11 ), miso = Pin( 12 ) )
	
	bme		= BME280( intf )	
	bme.show_dump()

	while True:
		t, p, h	= bme.read()
		print( f"{t:5.2f} ℃, {p:7.2f} hPa, {h:5.2f} %RH" )
		sleep( 1 )
		
if __name__ == "__main__":
	main()

　
