from	machine	import	Pin, I2C
from	utime	import	sleep
from	struct	import	unpack

DEFAILT_ADDRESS		= 0xEC >>1

class BME280:
	def __init__( self, i2c, address = DEFAILT_ADDRESS ):
		self.__i2c	= i2c
		self.__addr	= address
		
		(self.dig_T1, self.dig_T2, self.dig_T3)		= unpack( "<Hhh", self.read( 0x88, 6 ) )
		
		(self.dig_P1, self.dig_P2, self.dig_P3, self.dig_P4, self.dig_P5, self.dig_P6, 
			self.dig_P7, self.dig_P8, self.dig_P9)	= unpack( "<Hhhhhhhhh", self.read( 0x8E, 18 ) )
			
		self.dig_H1	= self.read( 0xA1 )
		
		(self.dig_H2, self.dig_H3, E4, E5, E6, self.dig_H6)	= unpack( "<hBbbbb", self.read( 0xE1, 7 ) )
		self.dig_H4	= (E4 << 4) | (E5 & 0x0F)
		self.dig_H5 = (E6 << 4) | (E5 >> 4)
		
		self.t_fine	= 0

		s	= 0x01
		self.write( 0xF2, s )
		self.write( 0xF4, (s << 5) | (s << 2) | 0x3 )
	
	def temperature( self ):
		data 	= self.read( 0xFA, 3 )
		adc_T_High, adc_T_Low	= unpack( ">HB", data )
		adc_T	= adc_T_High << 4 | adc_T_Low >> 4
	
		var1	= ((((adc_T >> 3) - (self.dig_T1 << 1))) * (self.dig_T2)) >> 11
		var2	= (((((adc_T >> 4) - (self.dig_T1)) * ((adc_T >> 4) - (self.dig_T1))) >> 12) * (self.dig_T3)) >> 14
		
		self.t_fine	= var1 + var2
		
		T		= (self.t_fine * 5 + 128) >> 8
		return T / 100

	def pressure( self ):
		data 	= self.read( 0xF7, 3 )
		adc_P_High, adc_P_Low	= unpack( ">HB", data )
		adc_P	= adc_P_High << 4 | adc_P_Low >> 4

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

	def humidity( self ):
		data 	= self.read( 0xFD, 2 )
		adc_H	= unpack( ">H", data )[ 0 ]

		v_x1_u32r = self.t_fine - 76800
		v_x1_u32r = (((((adc_H << 14) - (self.dig_H4 << 20) - (self.dig_H5 * v_x1_u32r)) + 16384) >> 15) * (((((((v_x1_u32r * self.dig_H6) >> 10) * (((v_x1_u32r * self.dig_H3) >> 11) + 32768)) >> 10) + 2097152) * self.dig_H2 + 8192) >> 14))
		v_x1_u32r = (v_x1_u32r - (((((v_x1_u32r >> 15) * (v_x1_u32r >> 15)) >> 7) * self.dig_H1) >> 4))
		v_x1_u32r = 0 if (v_x1_u32r < 0) else v_x1_u32r
		v_x1_u32r = 419430400 if (v_x1_u32r > 419430400) else v_x1_u32r
		return (v_x1_u32r >> 12) / 1024

	def write( self, r, v ):
		self.__i2c.writeto( self.__addr, bytearray( [ r, v ] ) )
		
	def read( self, r, len = None ):
		if len is None:
			len	= 1

		self.__i2c.writeto( self.__addr, bytearray( [ r ] ) )
		data	= self.__i2c.readfrom( self.__addr, len )
		
		if len is 1:
			return list( data )[ 0 ]
		else:
			return data
		
	def show_reg( self, r ):
		print( "reg:0x{:02X} = 0x{:02X}".format( r, self.read( r ) ) )
		
	def show_dump( self ):
		reg_list	= [ 0xF2, 0xF3, 0xF4, 0xF5 ]
		
		for r in reg_list:
			self.show_reg( r )
					
def main():
	i2c	= I2C( 0, sda = Pin( 0 ), scl = Pin( 1 ), freq = 400_000 )
	bme	= BME280( i2c )
	
	bme.write( 0xF4, 0x03 )
	bme.show_dump()

	while True:
		print( f"bme.temperature() = {bme.temperature()}" )
		print( f"bme.pressure()    = {bme.pressure()}" )
		print( f"bme.humidity()    = {bme.humidity()}" )
		print( "" )
		
		sleep( 1 )
		
if __name__ == "__main__":
	main()

