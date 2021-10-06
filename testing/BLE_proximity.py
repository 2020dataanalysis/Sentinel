import time
from bluepy.btle import Scanner, DefaultDelegate

class BLE_proximity:
	def __init__(self):
		self.start_life_time = int( time.time() )
		self.last_time = 0
		self.t = 0
		self.VIP_dictionary =	{
								'dd:33:0a:11:16:c5': 'Sammy',
								'D0:46:F5:64:62:BB': 'Approach X40',
								'd0:46:f5:64:62:bb': 'Approach X40',
								'fc:58:fa:41:cb:b5': 'White',
								'fc:58:fa:41:b5:e2': 'Yellow',
								'fc:58:fa:53:cb:32': 'Green',
								'fc:58:fa:18:8f:1b': 'Purple',
								'fc:58:fa:54:29:5f': 'Black'
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
			if self.VIP_IN_dictionary[name] + 10 < self.t:
				del self.VIP_IN_dictionary[name]
				print(f'Removed {name} from {self.VIP_IN_dictionary}')
				return name

		return ''


	def background_bluetooth_broadcasts( self, address ):
		name = ''

		if address in self.VIP_dictionary:
			print ( f"{self.t} [{address}] ", end='' )
			name = self.VIP_dictionary[address]

			if name in self.VIP_IN_dictionary.keys():
				self.VIP_IN_dictionary[name] = self.t
				# print( self.VIP_IN_dictionary )
				name = ''
				return name

			self.VIP_IN_dictionary[name] = self.t
			# print( self.VIP_IN_dictionary )

		return name


	def scan(self):
		scanner = Scanner().withDelegate(self.ScanDelegate())
		devices = scanner.scan(1.0)
		return devices


	def VIP_BLE_added(self):
		self.t = self.get_seconds(time.time())
		devices = self.scan()

		name = []
		for dev in devices:
			if dev.addr == '53:2e:6b:0a:57:37':
				continue
			if dev.addr == '4c:71:c1:bf:06:ac':
				continue
			if dev.addr == 'd0:03:df:63:aa:2c':
				continue
			if dev.addr == '64:ea:ab:32:4e:33':
				continue
			if dev.addr == '5e:fc:43:26:26:64':
				continue
			if dev.addr == 'd0:46:f5:64:62:bb':
				continue
			if dev.addr == '34:1a:b8:9c:8f:e7':
				continue
			if dev.addr == '58:27:da:29:42:ec':
				continue
			if dev.addr == '5c:5a:aa:80:4c:dd':
				continue


			if dev.rssi > -48:
				print( dev.addr, dev.rssi )
				new_name = self.background_bluetooth_broadcasts( dev.addr )
				if new_name:
					print(f'log_event({new_name} is IN. {dev.rssi})')
					name.append( new_name )

		return name


	def VIP_BLE_removed(self):
		name = ''
		if self.t > self.last_time + 10:
			self.last_time += 10
			name = self.VIP_pop()
			if name:
				print(f'log_event({name} is OUT)')

		return name
