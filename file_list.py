import os
import argparse
import logging
import csv
import sys
import time
import win32api
import win32con

from datetime import datetime
try:
	logging.basicConfig(filename='file_list.log', encoding='utf-8', level=logging.DEBUG)
except:
	logging.basicConfig(filename='file_list.log', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
parser = argparse.ArgumentParser(description="Path of file to list directories in")
parser.add_argument("--path")
parser.add_argument("--attribute_filter")
parser.add_argument("--recursion_depth")
parser.add_argument("--folder_only")
parser.add_argument("--file_input")
folderonly = str(vars(parser.parse_args())['folder_only'])
path = vars(parser.parse_args())['path']
filter = vars(parser.parse_args())['attribute_filter']
max_depth = vars(parser.parse_args())['recursion_depth']
file_input = vars(parser.parse_args())['file_input']
file_paths = []
start_time = time.time()
logging.info(str(datetime.now())+": " + "Start time: "+str(start_time))
logging.info(str(datetime.now()) + ": Passed arguments: ")
for arg in vars(parser.parse_args()):
	logging.info(str(datetime.now())+": " + arg+": "+str(vars(parser.parse_args())[arg]))
if file_input != None:

	if path != None:
		file_paths.append(path)
	try:
		with open(file_input, "r") as f:
			for line in f.readlines():
				file_paths.append(str(line).strip().replace('"', ""))
	except Exception as e:
		logging.error(str(datetime.now())+": " + "Error opening file: "+str(e))
else:
	if(path != None):
		file_paths.append(path)
	else:
		logging.error(str(datetime.now())+": " + "Path or file input not passed! Please try again")

if(filter != None):
	filter_exists = True

if path == None and file_input == None:
	logging.error(str(datetime.now())+": " + "Path argument or file input not passed. Please try again.")
	quit()
if len(file_paths) == 0:
	logging.error(str(datetime.now())+": " + "No folders to parse were passed. Check if arguments were passed or if file input is empty.")
else:
	logging.info(str(datetime.now())+": " + "Folder(s) to parse: ")
	for path in file_paths:
		logging.info(str(datetime.now())+": " + path)
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
				if folderonly == "True" or folderonly == "true":
					files.append(full_path)
					for file in get_files_in_directory(full_path, count + 1):
						if(os.path.isdir(file)):
							files.append(file)
				else:
					files += get_files_in_directory(full_path, count+1)

			elif os.path.isfile(path + "\\" + item):
				if(folderonly == "True" or folderonly == "true"):
					pass
				else:
					files.append(full_path)  # [item, time.strftime('%m/%d/%Y :: %H:%M:%S', time.gmtime(os.path.getmtime(path+"\\"+item))), os.stat(path+"\\"+item).st_size]

		except Exception as e:

			logging.error(str(datetime.now())+": " + "Error checking item "+item+": "+str(e))

	return files

#
#attribute = win32api.GetFileAttributes(full_path)
#print("\n" + full_path)
#print(attribute & win32con.FILE_ATTRIBUTE_HIDDEN)
'''if filter == "hidden":

	if attribute & win32con.FILE_ATTRIBUTE_HIDDEN == 0:
		continue
	elif attribute & win32con.FILE_ATTRIBUTE_HIDDEN == 0:
		print("Hi")
	print(full_path+" " +str(attribute & win32con.FILE_ATTRIBUTE_HIDDEN))'''








files = []
for fpath in file_paths:
	logging.info(str(datetime.now())+": " + "Checking path "+fpath+"...")
	try:

		files += get_files_in_directory(fpath)
	except Exception as e:
		logging.error(str(datetime.now())+": " + "Error checking path "+fpath+": "+str(e))

logging.info(str(datetime.now())+": " + "Writing filenames to csv file...")

if not os.path.exists("file_list.csv"):
	stats = open("file_list.csv", "w", newline="")
	stats.close()
stats = open("file_list.csv", "w", encoding="utf-8", newline="")
writer = csv.DictWriter(stats, fieldnames=["file_name", "file_date", "file_size_bytes", "file_extension"])
writer.writeheader()

if folderonly == "None":
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
			logging.error(str(datetime.now())+": " + "Error writing file "+str(file)+" to csv: "+str(e))
elif folderonly == "True" or folderonly == "true":
	stats = open("file_list_folders.csv", "w", newline="")
	writer = csv.DictWriter(stats, fieldnames=["file_path"])
	writer.writeheader()
	for file in files:
		try:
			writer.writerow({"file_path": file})
		except Exception as e:
			logging.error(str(datetime.now())+": " + "Error writing file "+str(file)+" to csv: "+str(e))
else:
	logging.error(str(datetime.now())+": " + "Folder_only parameter invalid! Please try again!")
	quit()
logging.info(str(datetime.now())+": " + "Files written to csv.")
stats.close
end_time = time.time()

logging.info(str(datetime.now())+": " + "End time: "+str(end_time))
logging.info(str(datetime.now())+": " + str(len(files))+" files written to file_list.csv in "+str(end_time-start_time)+" seconds. \n")
