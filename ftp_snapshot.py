#     References:
#          GPIO                         →     https://sourceforge.net/p/raspberry-gpio-python/wiki/PWM/
#          sudo apt-get install rpi.gpio          Does not workon
#          pip  install RPi.GPIO                    For python 2.7
#          pip3 install RPi.GPIO                    For python 3.5
#          dpkg --get-selections          List installed modules

#     Setup:
#          sudo service motion stop  →     If you have motion installed then you will need to stop the service
#                                             If the camera's blue light is on then the motion service is active.
#          lsusb
#          v4l2-ctl --list-devices                    Set cap = cv2.VideoCapture( x ) to /dev/videox
#          workon cv1                    to exit cv1 environment → deactivate
#          python c1.py

import os, sys, time, ftplib
import smtplib
import urllib.request               #   ip request
import ifaddr                       # pip3 install ifaddr

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ftplib import FTP, error_perm
from security.credentials_ftp import server_email_address, server_email_password, recipients, ftp_host, ftp_user, ftp_password

# # location	= 'blackhawk'
# location	= 'bear'
home 		= '/home/pi/motion'

if not os.path.exists(home):
    os.makedirs(home)
os.chdir(home)


# def ftp0():
    #   First check if there is anything to upload before establishing an FTP connection
	# global home
	# os.chdir(home)
	# start = time.time()
	# nof = len([name for name in os.listdir('.') if os.path.isfile(name)])
	#
	# if nof > 0:
	# 	return ftp()       # Recursive			12/11/2020
	# return ftp()


def ftp( location ):
	try:
		start = time.time()
		f = FTP(ftp_host)
		login_code = f.login(user=ftp_user, passwd=ftp_password)
		f.cwd( '/bayrvs/' + location + '/snapshots')
		# print( 'remote --> ', f.pwd() )
		# print( f.dir() )
		# print(login_code)
		login_code = login_code.split()
		# print(login_code)
		login_code = login_code[0]
		# print (login_code)
		# last_snap = upload(f, home)			#	12.11.2020
		upload(f, home)			#	12.11.2020
		f.quit()

	except Exception as e:
		print('Exception ', e)


	# f.quit()
	# print( 'ftp quit' )
	# return last_snap



def upload(f, path):
	os.chdir(path)

	# if len( os.listdir( path ) ) == 0:
	# 	print('ftp_snapshot.py → upload → No files in dir - going to sleep')
	# 	time.sleep( 1 )
	# 	print( len( os.listdir( path ) ) )

	# if len( os.listdir( path ) ) > 2:
	# 	print( 'ftp_snapshot.py → upload → More than 2 file to upload')


	for entry in os.scandir(path):
		if entry.name.startswith('.'):
			continue

		if entry.name.endswith('.mkv'):
			os.remove(entry.name)				#	Keep system optimized

		if entry.name == 'lastsnap.jpg':
			continue

		if entry.is_dir():
            # print('dir --> ', entry.name)
			if not entry.name in f.nlst():
                # print('in --> ', entry.name)
				f.mkd(entry.name)

			f.cwd(entry.name)
            # print('ftp ', f.pwd() )
			upload(f, path + '/' + entry.name)
			f.cwd('../')
			os.chdir('../')
		else:
            #            print('file --> ', entry.name)
			try:
			    #print ('entry.name ', entry.name)
				if entry.name in f.nlst():					#	If name already exists, delete.
				    # print('in --> ', entry.name)
					f.delete(entry.name)

				f.storbinary('STOR ' + entry.name, open(entry.name, 'rb'))
				# print( 'FTP upload --> ', entry.name )
				# print('removing: ' + entry.name)
				os.remove(entry.name)
				# print('removed: ' + entry.name)
				# return entry.name				#	12/11/2020

			except ftplib.error_perm as e:  # Handle only 550 (not found / no permission error)
				error_code = str(e).split(None, 1)
				print('error code = ', error_code)
				if error_code[0] == '550':
					print(error_code[1], 'File may not exist or you may not have permission.')
				print('Error not explicitly handled ', error_code[0])

			except Exception as e:
				error_code = str(e).split(None, 1)
				print('Exception Error ', error_code)
