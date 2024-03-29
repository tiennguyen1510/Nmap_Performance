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
num_1_run = 20
time_limit = "1800"
num_block = len(ip_host.keys()) % num_1_run

if num_block > 0:
    num_block = (len(ip_host.keys()) / num_1_run) + 1
else:
    num_block = (len(ip_host.keys()) / num_1_run)

# function define exception ip and port
def modifierList():
	keyword_exception = ["_FN_BTC_","_FN_BTH_"]
	ip_port = {}
	with open("/home/snmap/scripts/infinito/ip-port-exc.txt") as file:
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

def sendSQL(a, b, c):
	import mysql.connector
	mydb = mysql.connector.connect(
			host="localhost",
			user="snmap",
			passwd="P4ssw0rd123!",
			database="nmapscan"
	)

	mycursor = mydb.cursor()

	sql = "INSERT INTO internal (ip, port, domain) VALUES (%s, %s, %s)"
	val = (a, b, c)
	mycursor.execute(sql, val)

	mydb.commit()

def compare():
	if os.path.isfile('/home/snmap/scripts/infinito/log/serverlist.prod.bak'):
		cmd = "diff -w /tmp/serverlist.prod /home/snmap/scripts/infinito/log/serverlist.prod.bak"		# change location for file
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
		os.system("cp /tmp/serverlist.prod /home/snmap/scripts/infinito/log/serverlist.prod.bak")
	else:
		os.system("cp /tmp/serverlist.prod /home/snmap/scripts/infinito/log/serverlist.prod.bak")		# change location for file
		print "coppy"


def sendLog(name, cate, status):
        dt = datetime.datetime.now()
        d = str(dt).split(" ")
        message = "```" + d[0] + " | " + d[1] + " | " + name + "\t| " + cate + " | [PROD] Scanning port is " + status + "!```"
	sendGG(message, url_test)

def run(file_name):
	arr_file = []
	num_lines = sum(1 for line in open(file_name))
	open("/tmp/late_file.txt","w").close()
	with open(file_name) as myfile:
		count = 0
		for line in myfile:
			print line
			line = line.split("\t")
			ip = line[0]
			print "print ip " + ip
			domain = str(line[1]).replace("\n","")
			arr_file.append(ip + "_" + domain +".txt")

			cmd = "nohup sh -c 'sudo nmap -p- " + ip.strip() + " | grep open > /tmp/"+ ip + "_" + domain +".txt' &"
        		try:
				print "chay processes"
                		ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
				ps = subprocess.Popen("sleep 1",shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	       		except:
	               		sendLog("nmap","ERROR","Error. Check log in /var/log/.log ")
	       		output = ps.communicate()[0]
			count += 1
			print "so luong: " + str(count)	
			if (count == (num_lines - 1)):
				while True:
					print "Waiting proccess 0"
					time.sleep(1)
					cmd_check_time_write = "ps -eo comm,pid,etimes,user,cmd | awk '/^sh/ {if ($3 > " + time_limit +" && $4==\"snmap\") { print $10}}' >> /tmp/late_file.txt"
					os.system(cmd_check_time_write)
					cmd_kill_late = "kill -9 $(ps -eo comm,pid,etimes,user,cmd | awk '/^sh/ {if ($3 > " + time_limit +" && $4==\"snmap\") { print $2}}')"
					os.system(cmd_kill_late)
					cmd_check_pro = 'ps -ef | grep -E -o "/tmp/([0-9]{1,3}[\.]){3}[0-9]{1,3}" |wc -l'
					count_proccess = os.popen(cmd_check_pro).read()
					print "proccess: " + count_proccess
					if (int(count_proccess) == 0):
						break
			else:
				while True:
					print "[*] Add proccess!"
					time.sleep(1)
                                        time.sleep(1)
                                        cmd_check_time_write = "ps -eo comm,pid,etimes,user,cmd | awk '/^sh/ {if ($3 > " + time_limit +" && $4==\"snmap\") { print $10}}' >> /tmp/late_file.txt"
                                        os.system(cmd_check_time_write)
                                        cmd_kill_late = "kill -9 $(ps -eo comm,pid,etimes,user,cmd | awk '/^sh/ {if ($3 > " + time_limit +" && $4==\"snmap\") { print $2}}')"
                                        os.system(cmd_kill_late)
                                        cmd_check = 'ps -ef | grep -E -o "/tmp/([0-9]{1,3}[\.]){3}[0-9]{1,3}" |wc -l'
 					count_proccess = os.popen(cmd_check).read()
					print "proccess: " + count_proccess
                                        if num_1_run > int(count_proccess):
                                                break
						
	cmd_sort_log = "sort /tmp/late_file.txt | uniq > /tmp/last_late_file.txt"
	for file in arr_file:
		parse(file)

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
                        	sendSQL(ip, list_port_sql, domain)
                        	sendGG(a, url_test)	

def main():
	sendLog("main.py","INFO","Starting ")
	print datetime.date.today()
	compare()
	open("/tmp/ip_domain.txt","w").close()	#delete data older
	start = time.time()
	for key, value in ip_host.items():
		with open("/tmp/ip_domain.txt", "a") as urlfile:
	               	urlfile.write(value + "\t" + key + "\n")
	run("/tmp/ip_domain.txt")
	end = time.time()
	print "Time for script: " + str(end - start)
	sendLog("test.py","INFO","Completed ")
		
main()
