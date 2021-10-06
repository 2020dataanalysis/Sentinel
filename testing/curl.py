# https://support.reolink.com/hc/en-us/articles/360007011233-How-to-Capture-Live-JPEG-Image-of-Reolink-Cameras-via-Web-Browsers

# # curl -X POST -H 'Content-type: application/json' --data '{"text":"Hello, World!"}' https://hooks.slack.com/services/asdfasdfasdf
#
# import requests
#
# headers = {
#     'Content-type': 'application/json',
# }
#
# data = '{"text":"Hello, World!"}'
#
# # response = requests.post('https://hooks.slack.com/services/asdfasdfasdf', headers=headers, data=data)
# response = requests.post('http://admin:@10.0.0.190/image.jpg', headers=headers, data=data)


import subprocess
# process = subprocess.Popen(['curl', 'http://admin:@10.0.0.190/image.jpg', '-o', 'cool.jpg'],
process = subprocess.Popen(['curl', 'http://10.0.0.64/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=wuuPhkmUCeI9WG7C&user=admin&password=', '-o', 'cool.jpg'],
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
print( stdout, stderr )
