import os
import sys

from sqlite3 import DatabaseError
from pykeepass import PyKeePass
from merger import merge_databases
"""
Merges .kdbx files in a dir using a single password provided as a command line argument.
writes the result to ./RESULT.kdbx encrypted with the provided password
example: python merge_files_in_dir.py ~/my_dir/ my_password
"""


dir_name = sys.argv[1]
password = sys.argv[2]

files = os.listdir(dir_name)
databases = [PyKeePass(f"{dir_name}{file_name}", password=password) for file_name in files]

result_database = merge_databases("RESULT.kdbx", password, databases)
result_database.save()
