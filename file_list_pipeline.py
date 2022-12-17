import win32api

import csv
import os
import time
import modin.pandas as pd
from distributed import Client
import luigi
import os
import argparse
import logging
import csv
import sys
import time
import win32api
import win32con
import vaex
from datetime import datetime

class FileList(luigi.Task):
    path = luigi.Parameter()
    attribute_filter = luigi.Parameter()
    recursion_depth = luigi.IntParameter()
    folder_only = luigi.Parameter()
    file_input = luigi.Parameter()
    def requires(self):
        return []

    def output(self):
        if self.folder_only == "False" or self.folder_only == "false" or self.folder_only == "None":
            return luigi.LocalTarget("file_list.csv")
        if self.folder_only == "True" or self.folder_only == "true":
            return luigi.LocalTarget("file_list_folders.csv")

    def run(self):

        path = self.path
        filter = self.attribute_filter
        max_depth = self.recursion_depth
        folder_only = self.folder_only
        file_input = self.file_input

        if folder_only == "True" or "true":
            max_depth -= 1

        try:
            logging.basicConfig(filename='file_list.log', encoding='utf-8', level=logging.DEBUG)
        except:
            logging.basicConfig(filename='file_list.log', level=logging.DEBUG)
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

        file_paths = []
        start_time = time.time()
        logging.info(str(datetime.now()) + ": " + "Start time: " + str(start_time))
        if file_input != "None":

            if path != None:
                file_paths.append(path)
            try:
                with open(file_input, "r") as f:
                    for line in f.readlines():
                        file_paths.append(str(line).strip().replace('"', ""))
            except Exception as e:
                logging.error(str(datetime.now()) + ": " + "Error opening file: " + str(e))
        else:
            if (path != None):
                file_paths.append(path)
            else:
                logging.error(str(datetime.now()) + ": " + "Path or file input not passed! Please try again")


        if path == None and file_input == None:
            logging.error(str(datetime.now()) + ": " + "Path argument or file input not passed. Please try again.")
            quit()
        if len(file_paths) == 0:
            logging.error(str(
                datetime.now()) + ": " + "No folders to parse were passed. Check if arguments were passed or if file input is empty.")
        else:
            logging.info(str(datetime.now()) + ": " + "Folder(s) to parse: ")
            for path in file_paths:
                logging.info(str(datetime.now()) + ": " + path)
        print("\n")

        def get_files_in_directory(path, count=0):

            files = []

            items = os.listdir(path)
            folder_files = []
            for item in items:  # item = either folder or file name, no path included

                full_path = os.path.join(path, item)

                try:
                    if (max_depth != None):
                        #print("EWRERERER\n\n\n\n\n\n")
                        if (count >= int(max_depth) + 1):
                            continue

                    if os.path.isdir(full_path):
                        if folder_only == "True" or folder_only == "true":
                            files.append(full_path)
                            for file in get_files_in_directory(full_path, count + 1):
                                if (os.path.isdir(file)):
                                    files.append(file)
                        else:
                            #print(full_path)
                            files += get_files_in_directory(full_path, count + 1)

                    elif os.path.isfile(path + "\\" + item):
                        if (folder_only == "True" or folder_only == "true"):
                            pass
                        else:
                            files.append(
                                full_path)  # [item, time.strftime('%m/%d/%Y :: %H:%M:%S', time.gmtime(os.path.getmtime(path+"\\"+item))), os.stat(path+"\\"+item).st_size]

                except Exception as e:

                    logging.error(str(datetime.now()) + ": " + "Error checking item " + item + ": " + str(e))

            return files

        files = []
        for fpath in file_paths:
            logging.info(str(datetime.now()) + ": " + "Checking target path " + fpath + "...")
            try:

                files += get_files_in_directory(fpath)
            except Exception as e:
                logging.error(str(datetime.now()) + ": " + "Error checking target path " + fpath + ": " + str(e))

        logging.info(str(datetime.now()) + ": " + "Writing filenames to csv file...")


        if folder_only == "None" or folder_only == "False" or folder_only == "false" or folder_only == None:
            if not os.path.exists("file_list.csv"):
                stats = open("file_list.csv", "w", newline="")
                stats.close()

            stats = open("file_list.csv", "w", encoding="utf-8", newline="")
            writer = csv.DictWriter(stats, fieldnames=["file_name", "file_date", "file_size_bytes", "file_extension"])
            writer.writeheader()

            for file in files:

                try:
                    attribute = win32api.GetFileAttributes(file)
                    if filter == "hidden":

                        # print(attribute & win32con.FILE_ATTRIBUTE_HIDDEN)
                        if attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM) == 2:
                            writer.writerow({"file_name": file, "file_date": time.strftime('%m/%d/%Y :: %H:%M:%S',
                                                                                           time.gmtime(
                                                                                               os.path.getmtime(
                                                                                                   file))),
                                             "file_size_bytes": os.stat(file).st_size,
                                             "file_extension": str(os.path.splitext(file)[1].lower())})
                        else:
                            continue
                    elif filter == "readonly":
                        if attribute & win32con.FILE_ATTRIBUTE_READONLY == 1:
                            writer.writerow({"file_name": file, "file_date": time.strftime('%m/%d/%Y :: %H:%M:%S',
                                                                                           time.gmtime(
                                                                                               os.path.getmtime(
                                                                                                   file))),
                                             "file_size_bytes": os.stat(file).st_size,
                                             "file_extension": str(os.path.splitext(file)[1].lower())})
                    elif filter == "None":

                        writer.writerow({"file_name": file, "file_date": time.strftime('%m/%d/%Y :: %H:%M:%S',
                                                                                       time.gmtime(
                                                                                           os.path.getmtime(
                                                                                               file))),
                                         "file_size_bytes": os.stat(file).st_size,
                                         "file_extension": str(os.path.splitext(file)[1].lower())})
                except Exception as e:
                    logging.error(str(datetime.now()) + ": " + "Error writing file " + str(file) + " to csv: " + str(e))
        elif folder_only == "True" or folder_only == "true":
            if not os.path.exists("file_list_folders.csv"):
                stats = open("file_list_folders.csv", "w", newline="")
                stats.close()

            stats = open("file_list_folders.csv", "w", newline="")
            writer = csv.DictWriter(stats, fieldnames=["file_path"])
            writer.writeheader()
            for file in files:
                try:
                    writer.writerow({"file_path": file})
                except Exception as e:
                    logging.error(str(datetime.now()) + ": " + "Error writing file " + str(file) + " to csv: " + str(e))
        else:
            logging.error(str(datetime.now()) + ": " + "Folder_only parameter invalid! Please try again!")
            quit()
        logging.info(str(datetime.now()) + ": " + "Files written to csv.")
        stats.close
        end_time = time.time()

        logging.info(str(datetime.now()) + ": " + "End time: " + str(end_time))
        logging.info(str(datetime.now()) + ": " + str(len(files)) + " files written to file_list.csv in " + str(
            end_time - start_time) + " seconds. \n")


class FileStats(luigi.Task):
    recursion_depth = (luigi.IntParameter(default=1000))
    path = luigi.Parameter(default="None")
    attribute_filter = (luigi.Parameter(default="None"))
    folder_only = (luigi.Parameter(default="None"))
    file_input = (luigi.Parameter(default="None"))
    def requires(self):
        return [FileList(path=self.path, attribute_filter=self.attribute_filter, recursion_depth=self.recursion_depth, folder_only=self.folder_only, file_input=self.file_input)]
    def output(self):
        return luigi.LocalTarget("file_stats.csv")
    def run(self):
        #tkinter.messagebox.showinfo(title=None, message=path)
        client = Client()

        start_time = time.time()

        def size_of(num, suffix='B'):
            for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
                if abs(num) < 1024.0:
                    return "%3.5f%s%s" % (num, unit, suffix)
                num /= 1024.0
            return "%.5f%s%s" % (num, 'Yi', suffix)

        if self.folder_only == "False" or self.folder_only == "false" or self.folder_only == "None":
            df = pd.read_csv("file_list.csv")
        if self.folder_only == "True" or self.folder_only == "true":
            print("Since the --folder-only argument was passed, file_stats.csv will be empty. The program will now end.")
            return
        extensions = list(pd.unique((df['file_extension'])))
        extension_data = []
        for i in extensions:
            if i == None or i != i:
                continue

            df_sum = sum(df[df['file_extension'] == i]['file_size_bytes'])
            df_mean = df[df['file_extension'] == i]['file_size_bytes'].mean()
            df_count = len((df[df['file_extension'] == i]['file_size_bytes']))
            extension_data.append([i, df_sum, df_count, df_mean])

        extension_data.sort(key=lambda x: x[1], reverse=True)

        with open("file_stats.csv", "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["extension", "extension_size", "extension_count", "extension_mean"])
            writer.writerows(extension_data)
        end_time = time.time()

        for extension in extension_data:  # Print all filetypes and their corresponding size and count
            print("Extension " + str(extension[0]) + ":\t\t" + str(extension[2]) + " file(s), taking up " + str(
                size_of(extension[1])) + " of space. Mean filesize: " + str(size_of(extension[3])))

        print("Process completed in " + str(end_time - start_time) + " seconds. " + str(
            len(extensions)) + " different extensions found. Extension statistics written to file_stats.csv.")


if __name__ == '__main__':
    if os.path.exists("file_list_folders.csv"):
        os.remove("file_list_folders.csv")
    if os.path.exists("file_list.csv"):
        os.remove("file_list.csv")
    if os.path.exists("file_stats.csv"):
        os.remove("file_stats.csv")
    luigi.run()