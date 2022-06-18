import os
import sys

from sqlite3 import DatabaseError
from pykeepass import PyKeePass
from merger import merge_databases

"""
Merges .kdbx files in a dir using a single password provided as a command line argument.
writes the result to a provided destination encrypted with the provided password
example: python merge_files_in_dir.py ~/my_dir/ my_password ~/my_dir/RESULT.kdbx
"""

dir_name = sys.argv[1]
password = sys.argv[2]
destination_file_name = sys.argv[3]

files = os.listdir(dir_name)
databases = [PyKeePass(f"{dir_name}{file_name}", password=password) for file_name in files]

result_database = merge_databases(destination_file_name, password, databases)
result_database.save()
