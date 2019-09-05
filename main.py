import re
import subprocess
import datetime
import os
import time
from httplib2 import Http
from json import dumps

list_prod = "/tmp/serverlist.prod"

# url for channel google hangouts
url_primary = "https://chat.googleapis.com/v1/spaces/ABAAVSQn8t4/messages?key=X%3D"
url_loging = "https://chat.googleapis.com/v1/spaces/ABAA1EgMQ9U/messages?key=%3D"
url_test = "https://chat.googleapis.com/v1/spaces/ABAAz9uEl28/messages?key=%3D"

# dictionary 
ip_host = {}
with open(list_prod) as file:
	for line in file:
		if ("BLOCKPASS") in line or ("GINAR_DEV_1GB" in line):
			continue
		else:
			line = line.split("\t")
			ip_host[line[0]] = line[2]

# define number ip run once time so that calculated block number server
num_1_run = 10
num_block = len(ip_host.keys()) % num_1_run

if num_block > 0:
    num_block = (len(ip_host.keys()) / num_1_run) + 1
else:
    num_block = (len(ip_host.keys()) / num_1_run)

# function define exception ip and port
def modifierList():
	keyword_exception = ["_FN_BTC_","_FN_BTH_"]
	ip_port = {}
	with open("ip-port-exc.txt") as file:
		for line in file:
			line = line.split("\t")
			line[1] = line[1].replace("\n","")
			if ',' in line[1]:
				tmp = line[1].split(",")
				ip_port[line[0]] = tmp
			else:
				ip_port[line[0]] = [line[1]]
	#print ip_port
	# add ip and port
	ip_kw = {}
	for key, val in ip_host.items():
		for x in keyword_exception:
			if x in key:
				ip_kw[val] = ["8333"]
			else:
				continue
				ip_kw[val] = []

	ip_re = {}
	ip_re = ip_port
	for key in ip_kw:
		if key in ip_re:
			print key
			for x in ip_kw[key]:
				ip_re[key].append(x)
		else:
			print key
			ip_re[key] = ip_kw[key]

	return ip_re

# using it if you use Hangout chat
def sendGG(text, url_input):
	url = url_input
	bot_message = {'text' : text}
	message_headers = { 'Content-Type': 'application/json; charset=UTF-8'}
	
	http_obj = Http()
	
	response = http_obj.request(
		uri=url,
		method='POST',
		headers=message_headers,
		body=dumps(bot_message),
	)

# function send SQL because using Grafana or more
def sendSQL(a, b, c):
	import mysql.connector
	mydb = mysql.connector.connect(
			host="localhost",
			user="admin",         # your type
			passwd="password",    # your type
			database="nmapscan"   # your type
	)

	mycursor = mydb.cursor()

	sql = "INSERT INTO internal (ip, port, domain) VALUES (%s, %s, %s)"
	val = (a, b, c)
	mycursor.execute(sql, val)

	mydb.commit()

# function compare list server because list server real-time changing
def compare():
	if os.path.isfile('/log/serverlist.prod.bak'):
		cmd = "diff -w /tmp/serverlist.prod /log/serverlist.prod.bak"		# change location for file
		result = os.popen(cmd).read()
		components = result.split("\n")
		tmp_add = ""
		tmp_sub = ""
		for component in components:
			if "<" in component:
				a = component.split("\t")
				a[0] = a[0].replace("< ","")
				tmp_add = tmp_add + a[0] + "  -  " + a[2] + "\n"
			elif ">" in component:
				a = component.split("\t")
				a[0] = a[0].replace("> ","")
				tmp_sub = tmp_sub + a[0] + "  -  " + a[2] + "\n"
			else:
				continue
		if tmp_add:
			tmp_add = "[ADD] IP in serverlist: \n" + tmp_add
			sendGG(tmp_add, url_test)
		if tmp_sub:
			tmp_sub = "[SUB] IP in serverlist: \n" + tmp_sub
			sendGG(tmp_sub, url_test)
		os.system("cp /tmp/serverlist.prod /log/serverlist.prod.bak")
	else:
		os.system("cp /tmp/serverlist.prod /log/serverlist.prod.bak")		# change location for file
		print "coppy"

# function with format log notify in chat channel
def sendLog(name, cate, status):
        dt = datetime.datetime.now()
        d = str(dt).split(" ")
        message = "```" + d[0] + " | " + d[1] + " | " + name + "\t| " + cate + " | [PROD] Scanning port is " + status + "!```"
	sendGG(message, url_test)

# function with command and logic for tool
def run(file_name):
	arr_file = []
	num_lines = sum(1 for line in open(list_prod))
	print "vao ham run roi"
	with open(file_name) as myfile:
		count = 0
		for line in myfile:
			print line
			line = line.split("\t")
			ip = line[0]
			print "print ip " + ip
			domain = str(line[1]).replace("\n","")
			arr_file.append(ip + "_" + domain +".txt")

			cmd = "nohup sh -c 'sudo nmap -p- " + ip.strip() + "| grep open > /tmp/"+ ip + "_" + domain +".txt' &"
        		try:
				print "chay processes"
                		ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
				ps = subprocess.Popen("sleep 1",shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	       		except:
	               		sendLog("nmap","ERROR","Error. Check log in /var/log/.log ")
	       		output = ps.communicate()[0]
			count += 1
			
			if (count == num_lines):
				while True:
					print "dieu kien bang"
					time.sleep(1)
					cmd_check = 'ps -ef | grep -E -o "/tmp/([0-9]{1,3}[\.]){3}[0-9]{1,3}" |wc -l'
					count_proccess = os.popen(cmd_check).read()
					print "proccess: " + count_proccess
					if ("0" in count_proccess):
						break
			else:
				while True:
					time.sleep(1)
                                        cmd_check = 'ps -ef | grep -E -o "/tmp/([0-9]{1,3}[\.]){3}[0-9]{1,3}" |wc -l'
 					count_proccess = os.popen(cmd_check).read()
					print "proccess: " + count_proccess
                                        if num_1_run > int(count_proccess):
                                                break

	print arr_file
	for file in arr_file:
		parse(file)


# function parse to ouput from nmap file
def parse(file_name):
	ip_kw = modifierList()
	
	ip = re.findall("\d+\.\d+\.\d+\.\d+",file_name)[0] 
	domain = re.findall("_\w+",file_name)[0]
	a = "[Internal IP]: " + ip + "  -   " + domain + "\n"

	if os.stat("/tmp/" + file_name).st_size != 0:
		flag_port = False
		list_port_sql = ""
		with open("/tmp/" + file_name) as file:
			for port in file:
				port_number = port.split("/")[0]
				if ip in ip_kw.keys():
					if port_number in ip_kw[ip]:
						continue
					else:
						flag_port = True
						a = a + str(port)
				else:
					flag_port = True
					a = a + str(port)
					list_port_sql = list_port_sql + port_number + ", "

			if (flag_port == True):
                        	#sendSQL(ip, list_port_sql, domain)
                        	sendGG(a, url_test)	
	print ip

# function main control flow for tool
def main():
	sendLog("main.py","INFO","Starting ")
	print datetime.date.today()
	print ip_host
	compare()
	count = 0
	count_file = 0
	for key, value in ip_host.items():
		if count % num_1_run == 0:
			print "Block " + str(count / num_1_run)
			count_file += 1
		with open("test/" + str(count_file) + ".txt", "a") as urlfile:
                	urlfile.write(value + "\t" + key + "\n")
    		count+=1
	print "Writed to file with number IP"
	for i in range(0,num_block):
		run("test/"+str(i+1)+".txt")
	sendLog("test.py","INFO","Completed ")
	os.system("rm /test/*.txt")       # Warning: select accuracy path
	
main()
