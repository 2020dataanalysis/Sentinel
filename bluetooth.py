# https://janakiev.com/blog/python-shell-commands/
import subprocess, time, datetime

def process( mac, channel ):
	# print( f'process started: { datetime.datetime.now() }' )
	# sudo rfcomm connect hci0 84:0D:8E:3D:3E:16 1
	# process = subprocess.run(['sudo', 'rfcomm', 'connect', 'hci0', '84:0D:8E:3D:3E:16', '1'],
	#                            stdout=subprocess.PIPE,
	# 						   stderr=subprocess.PIPE,
	# 						   text=True)


	# process = subprocess.run(['sudo', 'rfcomm', 'connect', 'hci0', '84:0D:8E:21:06:7E', '1'],
	process = subprocess.run([ 'sudo', 'rfcomm', 'connect', 'hci0', mac, channel ],
	                           stdout=subprocess.PIPE,
							   stderr=subprocess.PIPE,
							   text=True)



	# Do something else
	return_code = process.returncode
	if return_code is not None:
		print('RETURN CODE', return_code)
		print( f'process terminated: { datetime.datetime.now() }' )

		# Process has finished, read rest of the output
		for output in process.stdout:
			print(output)

		output = process.stderr
		if output:
			print( f'[{output}]' )


if __name__ == '__main__':
	process()
