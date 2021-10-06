#	2021.02.01	→	10 seconds to 60 to VIP out status.

import time
from bluepy.btle import Scanner, DefaultDelegate


class BLE_proximity:
	def __init__(self):
		self.start_life_time = int( time.time() )
		self.last_time = 0
		self.t = 0
		#	Set Two 2:
		#		fc:58:fa:35:61:01	YellowF
		#		fc:58:fa:35:67:b4	Green
		#		74:0c:72:e6:ed:c9	Black
		#		fc:58:fa:35:36:d1	Purple
		#		fc:58:fa:35:33:6c	White
		self.VIP_dictionary =	{
								'dd:33:0a:11:16:c5': 'Rich',
								'D0:46:F5:64:62:BB': 'Approach X40',
								'd0:46:f5:64:62:bb': 'Approach X40',
								'fc:58:fa:41:cb:b5': 'White',
								'fc:58:fa:41:b5:e2': 'Yellow',
								'fc:58:fa:53:cb:32': 'Green',
								'fc:58:fa:18:8f:1b': 'Purple',
								'fc:58:fa:54:29:5f': 'Black',

								'fc:58:fa:35:33:6c': 'White2',
								'fc:58:fa:35:61:01': 'Yellow2',
								'fc:58:fa:35:67:b4': 'Green2',
								'fc:58:fa:35:36:d1': 'Purple2',
								'74:0c:72:e6:ed:c9': 'Black2',
								'fc:58:fa:35:55:c2': 'Blue'
							}
		self.VIP_IN_dictionary = {}
		self.BLE_notification = False


	class ScanDelegate(DefaultDelegate):
		def __init__(self):
	 		DefaultDelegate.__init__(self)

		def handleDiscovery(self, dev, isNewDev, isNewData):
			pass


	def get_seconds( self, epoch ):
		epoch =  int( epoch )
		return epoch - self.start_life_time


	def VIP_pop(self):
		for name in self.VIP_IN_dictionary.keys():
			# if self.VIP_IN_dictionary[name] + 300 < self.t:		#	Approach X40
			if self.VIP_IN_dictionary[name] + 10 < self.t:
				del self.VIP_IN_dictionary[name]
				# print(f'Removed {name} from {self.VIP_IN_dictionary}')
				return name

		return ''


	def background_bluetooth_broadcasts( self, address ):
		name = ''

		if address in self.VIP_dictionary:
			# print ( f"{self.t} [{address}] ", end='' )
			name = self.VIP_dictionary[address]
			# print( f'69 name={name} {self.t}')

			if name in self.VIP_IN_dictionary.keys():
				# print( f'name={name} = {self.VIP_IN_dictionary[name]} {self.t}')
				self.VIP_IN_dictionary[name] = self.t
				# print( self.VIP_IN_dictionary )
				name = ''
				return name

			self.VIP_IN_dictionary[name] = self.t
			# print( self.VIP_IN_dictionary )

		return name


	def scan(self):
		scanner = Scanner().withDelegate( self.ScanDelegate() )
		# devices = scanner.scan(1.0)
		devices = scanner.scan(1.0)		#	06/14/2021		# put in try ***************************
		return devices


	def VIP_BLE_added(self):
		self.t = self.get_seconds(time.time())
		devices = self.scan()

		name = []
		for dev in devices:
			# print( dev.addr )
			if dev.rssi > -900:
				new_name = self.background_bluetooth_broadcasts( dev.addr )
				if new_name:
					# print(f'log_event({new_name} is IN. {dev.rssi})')
					name.append( new_name )

		return name


	#	This can be check once a minute
	def VIP_BLE_removed(self):
		name = ''
		if self.t > self.last_time + 10:
			self.last_time += 10
			name = self.VIP_pop()
			# if name:
			# 	print(f'log_event({name} is OUT)')

		return name
