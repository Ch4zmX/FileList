import vaex
import csv
import os
import time

start_time = time.time()
try:
	os.remove("file_list.csv.hdf5")
except:
	pass
df = vaex.from_csv("file_list.csv", convert=True, chunk_size=5_000_000)

def size_of(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.5f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.5f%s%s" % (num, 'Yi', suffix)

extensions = (df.unique(df.file_extension))
extension_data =[]
for x, i in enumerate(extensions):

	if i == None or i != i :
		continue

	df_sum = float(df.sum(df.file_size_bytes, selection=df.file_extension == i))
	df_count = int(df.count(df.file_size_bytes, selection=df.file_extension == i))
	df_mean = float(df.mean(df.file_size_bytes, selection=df.file_extension == i))


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