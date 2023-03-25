# FileList

## file_list_pipeline:
A pipeline in programming is a automated program that basically runs one program after another, in the case of a program that needs the output of a previous program to run. If one of the programs in between fails, the entire thing will fail. 

My implementation uses the ```luigi``` module to implement the pipeline, which simply runs the file_list and file_stats programs in sequence, outputting file_stats.csv. This eliminates the need to run ```file_list.py``` and wait for the execution to complete before running ```file_stats.py```, so we can run the entire sequence of programs unattended.

To run it, simply install the python packages ```distributed```, ```modin```, and ```luigi```, and then run the ```file_list_pipeline.py```

### file_list_cron:
A cron script simply runs a program on a scheduled interval or at a specific time, useful for purposes such as hourly indexing of file locations for easy searching. 
In this case, ```file_list_cron.py``` simply runs ```file_list_pipeline.py``` hourly, using the ```apscheduler``` package.
