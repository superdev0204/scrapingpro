import json,os,re,requests,sys,random,csv,time,pickle,datetime,zipfile
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import date

class Helper():

	def __init__(self):
		pass

	def read_txt_file(self,filename):
		with open(filename) as infile:
			ids = [row.replace('\n', '').replace('\r', '') for row in infile]
		return ids

	def reading_csv(self,csv_filename):
		f = open(csv_filename,'r',encoding='utf-8',errors='replace')
		csv_data = []
		reader = csv.reader(f)
		for row in reader:
			csv_data.append(row)

		f.close()
		return csv_data 

	def writing_csv(self,data,csv_filename):

		myFile = open(csv_filename, 'w', newline='',encoding='utf-8',errors='replace')
		with myFile:
			writer = csv.writer(myFile,quoting=csv.QUOTE_ALL)
			writer.writerows(data)

		return csv_filename

	def checking_folder_existence(self,dest_dir):
		if not os.path.exists(dest_dir):
			os.mkdir(dest_dir)
			print("Directory " , dest_dir ,  " Created ")
		else:
			pass
			#print("Directory " , dest_dir ,  " Exists ")

		return dest_dir
		
	def write_json_file(self,data,filename):

		while 1:
			try:
				with open(filename, 'w',encoding='utf-8') as outfile:
					json.dump(data, outfile,indent=4)
				break
			except Exception as error:
				print("Error in writing Json file: ",error)
				time.sleep(1)

	def read_json_file(self,filename):
		data = {}
		with open(filename,encoding='utf-8') as json_data:
			data = json.load(json_data)
		return data

	def is_file_exist(self,filename):
		if os.path.exists(filename):
			return True
		else:
			return False

	def list_all_files(self,directory,extension):
	    all_files = []
	    for file in os.listdir(directory):
	        if file.endswith(extension):
	            all_files.append(os.path.join(directory, file))
	    return all_files

	def write_random_file(self,text,file_name):
		file= open(file_name,"w",encoding='utf-8')
		file.write(str(text))
		file.close()

	def read_random_file(self,file_name):
		f = open(file_name, "r",encoding='utf-8')
		return f.read()

	def get_time_stamp(self):
		return time.strftime('%Y-%m-%d %H:%M:%S')

	def json_exist_data(self,fileName):
		json_data = []
		if self.is_file_exist(fileName):
			json_data = self.read_json_file(fileName)
		return json_data