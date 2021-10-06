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

USB_GPS  = '/dev/ttyUSB1'
USB_LoRa = '/dev/ttyUSB0'
home = '/home/pi/motion'

if not os.path.exists(home):
    os.makedirs(home)
os.chdir(home)

motion_detected = False
detecting_motion = False
alarm_set = False
alarm_triggered = False
RX = False
LoRa_RX = False
ftp_command = False


def ip():
    ipv6 = ''
    while len(ipv6) < 1:
        try:
            ipv6 = urllib.request.urlopen('http://ident.me').read().decode('utf8')
            print('IPv6: ', ipv6)

        except Exception as e:
            print('Exception ', e)

    from requests import get
    ipv4 = get('https://api.ipify.org').text
    print('IPv4: {}'.format(ipv4))
    home = '/home/pi/motion'

    if not os.path.exists(home):
        os.makedirs(home)
    os.chdir(home)
    filename = time.strftime("%Y%m%d-%H%M%S") + '.txt'
    file = open(filename, 'w')
    file.write('IPv6: ' + ipv6 + '\n' )
    file.write('IPv4: {}\n'.format(ipv4))

    adapters = ifaddr.get_adapters()
    for adapter in adapters:
        print ("IPs of network adapter " + adapter.nice_name)
        file.write("IPs of network adapter " + adapter.nice_name + '\n')
        for ip in adapter.ips:
            print ("   %s/%s" % (ip.ip, ip.network_prefix) )
            file.write("   %s/%s\n" % (ip.ip, ip.network_prefix) )

    file.close()



def ftp0():
    #   First check if there is anything to upload before establishing an FTP connection
	global home
	os.chdir(home)
	start = time.time()
	while True:
		nof = len([name for name in os.listdir('.') if os.path.isfile(name)])

		if nof > 0:
			ftp()       # Recursive

			if time.time() > start + 360:
				print ( nof )
				notify( 'BEAR Sentinel Alert: ' + str( nof ) + ' files uploaded', str( nof ) + ' '  )
				start = time.time()

        #print('.')
		time.sleep(1)




def ftp():
	try:
		start = time.time()
		f = FTP(ftp_host)
		login_code = f.login(user=ftp_user, passwd=ftp_password)
		f.cwd( '/bayrvservice')
		print( 'remote --> ', f.pwd() )
		print( f.dir() )
		print(login_code)
		login_code = login_code.split()
		print(login_code)
		login_code = login_code[0]
		print (login_code)
		upload(f, home)

	except Exception as e:
		print('Exception ', e)


	f.quit()
	print( 'ftp quit' )



def upload(f, path):
    os.chdir(path)

    for entry in os.scandir(path):
        if entry.name.startswith('.'):
            continue
        if entry.is_dir():
            print('dir --> ', entry.name)
            if not entry.name in f.nlst():
                print('in --> ', entry.name)
                f.mkd(entry.name)
            f.cwd(entry.name)
            print('ftp ', f.pwd() )
            upload(f, path + '/' + entry.name)
            f.cwd('../')
            os.chdir('../')
        else:
            #            print('file --> ', entry.name)
            try:
                #print ('entry.name ', entry.name)
                if entry.name in f.nlst():
                    print('in --> ', entry.name)
                    f.delete(entry.name)

                f.storbinary('STOR ' + entry.name, open(entry.name, 'rb'))
                print( 'FTP upload --> ', entry.name )
                os.remove(entry.name)

            except ftplib.error_perm as e:  # Handle only 550 (not found / no permission error)
                error_code = str(e).split(None, 1)
                print('error code = ', error_code)
                if error_code[0] == '550':
                    print(error_code[1], 'File may not exist or you may not have permission.')
                print('Error not explicitly handled ', error_code[0])

            except Exception as e:
                error_code = str(e).split(None, 1)
                print('Exception Error ', error_code)


def notify(subject, body):
	msg = MIMEMultipart()
	msg['From'] = server_email_address
	msg['To'] =  ", ".join( recipients )	# email_send

	print('body = {}'.format( body ))
	msg['Subject'] = subject
	msg.attach(MIMEText(body, 'plain'))
	text = msg.as_string()

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(server_email_address, server_email_password)
	server.sendmail(server_email_address, recipients, text)
	server.quit()


ip()
ftp0()
