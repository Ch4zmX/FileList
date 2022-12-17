from apscheduler.schedulers.blocking import BlockingScheduler
import os
import time
def run_pipeline():
	f = open("output_"+time.strftime("%Y-%m-%d-%H.%M.%S"), "a")
	f.close()
	os.system(r'python "file_list_pipeline.py" FileStats --local-scheduler --path C:\Users\Chasm\Documents')

scheduler = BlockingScheduler()
scheduler.add_job(run_pipeline, 'cron', hour='0-23')
scheduler.add_job(run_pipeline, 'cron', hour='0')
scheduler.start()

