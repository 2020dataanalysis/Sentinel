import threading
import time
import logging

def non_daemon():
    print ('start sleep')
    time.sleep(5)
    print ( 'Test non-daemon' )
    print ('.')
    print( 'aaaaaaaaaaaaaaaaaa')

t = threading.Thread(name='non-daemon', target=non_daemon)

# t.daemon = True
t.start()
# t.join()

print('1')
