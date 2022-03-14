import os
import glob

list_of_files = glob.glob('./uploads/*') # * means all if need specific format then for example: *.csv
latest_file = max(list_of_files, key=os.path.getctime)

print(latest_file)