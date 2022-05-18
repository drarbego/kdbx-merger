import os
from sqlite3 import DatabaseError
from pykeepass import PyKeePass
from merger import merge_databases

base_dir = "./KDBX merge/"
files = os.listdir(base_dir)


databases = [PyKeePass(f"{base_dir}{file_name}", password=password) for file_name in files]

result_database = merge_databases("RESULT.kdbx", password, databases)
result_database.save()
