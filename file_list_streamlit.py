import os
import argparse
import logging
import csv
import threading
import time
import win32api
import win32con
import streamlit as st
from datetime import datetime
from tkinter import Tk, filedialog
from threading import  Thread
from mttkinter import mtTkinter as tk


def streamlit_log(line):
	logging.info(line)
	st.text(line)

def folder_picker():
	root = tk.Tk()
	root.withdraw()
	root.attributes("-topmost", True)
	path = tk.filedialog.askdirectory()

	return path


def combine_file_paths(path,file_input):
	file_paths = []
	if file_input != None:

		if path != None and len(path) > 0:
			file_paths.append(path)
		try:
			with open(file_input, "r", encoding="utf-8") as f:
				for line in f.readlines():
					file_paths.append(str(line).strip().replace('"', ""))
		except Exception as e:
			(streamlit_log(str(datetime.now())+": " + "Error opening file: "+str(e)))
	else:
		if path != None and len(path) > 0:
			file_paths.append(path)
		else:
			(streamlit_log(str(datetime.now())+": " + "Path or file input not passed! Please try again"))
	return file_paths

def main(path, folderonly, filter, max_depth, file_input):

	try:
		logging.basicConfig(filename='file_list.log', encoding='utf-8', level=logging.DEBUG)
	except:
		logging.basicConfig(filename='file_list.log', level=logging.DEBUG)

	parser = argparse.ArgumentParser(description="Path of file to list directories in")
	start_time = time.time()

	if(filter != None):
		filter_exists = True

	if path == None and file_input == None:
		(streamlit_log(str(datetime.now())+": " + "Path argument or file input not passed. Please try again."))
		quit()
	if len(file_paths) == 0:
		(streamlit_log(str(datetime.now())+": " + "No folders to parse were passed. Check if arguments were passed or if file input is empty."))
	else:
		(streamlit_log(str(datetime.now())+": " + "Folder(s) to parse: "))
		for path in file_paths:
			(streamlit_log(str(datetime.now())+": " + path))
	print("\n")
	def get_files_in_directory(path, count=0):

		files=[]

		items = os.listdir(path)
		folder_files = []
		for item in items: #item = either folder or file name, no path included

			full_path = os.path.join(path, item)

			try:
				if(max_depth != None):

					if(count >= int(max_depth)+1):
						continue

				if os.path.isdir(full_path):
					if folderonly == True:
						files.append(full_path)
						for file in get_files_in_directory(full_path, count + 1):
							if(os.path.isdir(file)):
								files.append(file)
					else:
						files += get_files_in_directory(full_path, count+1)

				elif os.path.isfile(path + "\\" + item):
					if(folderonly == True):
						pass
					else:
						files.append(full_path)  # [item, time.strftime('%m/%d/%Y :: %H:%M:%S', time.gmtime(os.path.getmtime(path+"\\"+item))), os.stat(path+"\\"+item).st_size]

			except Exception as e:

				(streamlit_log(str(datetime.now())+": " + "Error checking item "+item+": "+str(e)))

		return files

	#
	#attribute = win32api.GetFileAttributes(full_path)
	#print("\n" + full_path)
	#print(attribute & win32con.FILE_ATTRIBUTE_HIDDEN)
	# '''if filter == "hidden":
	#
	# 	if attribute & win32con.FILE_ATTRIBUTE_HIDDEN == 0:
	# 		continue
	# 	elif attribute & win32con.FILE_ATTRIBUTE_HIDDEN == 0:
	# 		print("Hi")
	# 	print(full_path+" " +str(attribute & win32con.FILE_ATTRIBUTE_HIDDEN))'''

	files = []
	for fpath in file_paths:
		(streamlit_log(str(datetime.now())+": " + "Parsing all files in path "+fpath+"..."))
		try:

			files += get_files_in_directory(fpath)
		except Exception as e:
			(streamlit_log(str(datetime.now())+": " + "Error checking path "+fpath+": "+str(e)))

	half_time = time.time()
	(streamlit_log(str(datetime.now())+": Finished parsing files in "+str(half_time-start_time)+" seconds"))
	(streamlit_log(str(datetime.now())+": Writing filenames to csv file..."))

	if not os.path.exists("file_list.csv"):
		stats = open("file_list.csv", "w", encoding="utf-8", newline="")
		stats.close()
	stats = open("file_list.csv", "w", encoding="utf-8", newline="")
	writer = csv.DictWriter(stats, fieldnames=["file_name", "file_date", "file_size_bytes", "file_extension"])
	writer.writeheader()

	if folderonly:
		for file in files:

			try:
				attribute = win32api.GetFileAttributes(file)
				if filter == "hidden":

					#print(attribute & win32con.FILE_ATTRIBUTE_HIDDEN)
					if attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM) == 2:
						writer.writerow({"file_name": file, "file_date": time.strftime('%m/%d/%Y :: %H:%M:%S', time.gmtime(os.path.getmtime(file))), "file_size_bytes": os.stat(file).st_size, "file_extension": str(os.path.splitext(file)[1].lower())})
					else:
						continue
				elif filter == "readonly":
					if attribute & win32con.FILE_ATTRIBUTE_READONLY == 1:
						writer.writerow({"file_name": file, "file_date": time.strftime('%m/%d/%Y :: %H:%M:%S', time.gmtime(os.path.getmtime(file))), "file_size_bytes": os.stat(file).st_size, "file_extension": str(os.path.splitext(file)[1].lower())})
				elif filter == None:

					writer.writerow({"file_name": file, "file_date": time.strftime('%m/%d/%Y :: %H:%M:%S', time.gmtime(os.path.getmtime(file))), "file_size_bytes": os.stat(file).st_size, "file_extension": str(os.path.splitext(file)[1].lower())})
			except Exception as e:
				(streamlit_log(str(datetime.now())+": " + "Error writing file "+str(file)+" to csv: "+str(e)))
	else:
		stats = open("file_list.csv", "w", encoding="utf-8", newline="")
		writer = csv.DictWriter(stats, fieldnames=["file_path"])
		writer.writeheader()
		for file in files:
			try:
				writer.writerow({"file_path": file})
			except Exception as e:
				(streamlit_log(str(datetime.now())+": " + "Error writing file "+str(file)+" to csv: "+str(e)))
	end_time = time.time()
	(streamlit_log(str(datetime.now())+": " + str(len(files))+" files written to file_list.csv in "+str(round(end_time-half_time, 3))+" seconds. \n"))
	(streamlit_log(str(datetime.now()) + ": Total time taken: " + str(round(end_time - start_time, 3)) + " seconds. \n"))

	with open("file_list.csv", encoding="utf-8") as f:
		csv_text = f.read() + '\n'
	dl = st.download_button('Download CSV', data=csv_text, file_name="file_list.csv", mime='text/csv')

	stats.close()

	if stop:
		return

#-------------------------------,
#   Start Streamlit code here  /
#-----------------------------'

st.set_page_config(layout="wide", page_title="File List")

st.header("Parsing the requested folder:")


btn1, btn2, btn3 = st.columns(3)

with btn1:
	path_btn = st.button("Choose path", key="path")

with btn2:
	start = st.button("Start", key="start"
					  )
with btn3:
	stop = st.button("Stop", key="stop")






folderonly = st.checkbox(label="Folder Only", key="folder_only", value=False, help="Only parse the names of the folders in the given directory, not the file names")

filter = st.radio("Filters", options=["None", "Readonly", "Hidden"], index=0, horizontal=True, help='Readonly: Only parses files that have the "readonly" attribute. Hidden: Only parses files that have the "hidden" attribute').lower()
if filter == "none":
	filter = None


range = [i for i in range(100, -1, -1)]
range.insert(0, "Infinite")

max_depth = st.select_slider("Max Depth", options=range, help="The maximum number of folders deep the program should parse. Set to None for no limit.")
if max_depth == "Infinite":
	max_depth = None

file_input = st.file_uploader(label="Upload List of Paths", help="Upload a file with a list of paths to parse, seperated by newlines")

if path_btn:
	t = threading.Thread(target=folder_picker())
	t.setDaemon(True)
	t.start()
	t.root.quit()

if(start):
	file_paths = combine_file_paths(path, file_input)
	if len(file_paths) > 0:
		main(path, folderonly, filter, max_depth, file_input)