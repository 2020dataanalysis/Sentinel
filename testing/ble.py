#	 Order Details
#		Ordered on October 30, 2020 Order# 114-9224000-8869050
#		Set Two 2:
#		fc:58:fa:35:61:01	Yellow
#		fc:58:fa:35:67:b4	Green
#		74:0c:72:e6:ed:c9	Black
#		fc:58:fa:35:36:d1	Purple
#		fc:58:fa:35:33:6c	White


from BLE_proximity import BLE_proximity
ble = BLE_proximity()

while True:
	if ble.VIP_BLE_added():
		print('.', end='')
