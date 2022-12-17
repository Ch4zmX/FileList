import csv
import os
import time
#import pandas as pd
import pandas as pd
import luigi
from distributed import Client

def main():
	start_time = time.time()

	def size_of(num, suffix='B'):
		for unit in ['','K','M','G','T','P','E','Z']:
			if abs(num) < 1024.0:
				return "%3.5f%s%s" % (num, unit, suffix)
			num /= 1024.0
		return "%.5f%s%s" % (num, 'Yi', suffix)

	df = pd.read_csv("file_list.csv")

	extensions = list(pd.unique(list(df['file_extension'])))
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

	for extension in extension_data: #Print all filetypes and their corresponding size and count
		print("Extension "+str(extension[0])+":\t\t"+str(extension[2])+" file(s), taking up "+str(size_of(extension[1]))+" of space. Mean filesize: "+str(size_of(extension[3])))

	print("Process completed in "+str(end_time-start_time)+" seconds. "+str(len(extensions))+" different extensions found. Extension statistics written to file_stats.csv.")

if __name__ == "__main__":
    main()