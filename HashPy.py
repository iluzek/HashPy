# =============================================================================
# Section: Library Imports 
# =============================================================================
import os, sys, argparse, hashlib, collections, csv, configparser
from time import localtime, strftime
# =============================================================================
# Section: Basic directory configuration
# =============================================================================
# Creation Date and Time directory name - Need to be overwritten when loading
# =============================================================================
session_datetime			=	str(strftime("%Y-%m-%d@%H-%M-%S", localtime()))
session_local_path			=	os.path.dirname(os.path.realpath(__file__))
session_main_dir			=	"Sessions"					# Sessions directory name
session_config_dir			=	"config"					# Session config directory
session_results_dir			=	"results"					# Session results directory
session_config_file			=	"hashpy.config"				# Session config file
session_discovered_list			=	"discovered_files.csv"		# List of discovered files
session_hashed_list			=	"hashed_files.csv"			# List with hashed files
# =============================================================================
config_dir_path = os.path.join(session_local_path,session_main_dir,session_datetime,session_config_dir)
# Path for config file
config_file_path = os.path.join(config_dir_path,session_config_file)
# Path for discovered_files file
discovered_list_path = os.path.join(config_dir_path,session_discovered_list)
# Path for hashed files status file  ('hashed_files_status.txt')
hashed_list_path = os.path.join(config_dir_path,session_hashed_list)
# =============================================================================
session_loaded = False 					# Loading session file
session_loaded_file = None              # Path to the session file
# =============================================================================
# Section: Script Output Options
# =============================================================================
session_target_path = None
session_recursive_search = False
session_hash_type = "MD5"
session_verbose_mode = False
# =============================================================================
# Section: Display Adjustment options
# =============================================================================
_last_output_length = 0
# =============================================================================
# Section: Output Tracking
# =============================================================================
_discovered_files_count = 0
_hashed_files_count = 0
# =============================================================================
# Section: Parser Initialisation
# =============================================================================
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
# =============================================================================
# Section: Argparse Validation Functions
# =============================================================================
# =============================================================================
# Name:       validate_target(path_string)
# Arguments:  path_string = string input from the user to hash
# Purpose:    Returns a valid path value or raises error
# =============================================================================
def validate_target(system_path):
	global session_loaded, session_loaded_file

	# Check if system_path is a file or a directory
	if os.path.isfile(system_path):
		#Check if file is HashPy.config session file
		if (os.path.basename(system_path) == session_config_file):
			# system path is a session config file to be loaded
			session_loaded = True
			return system_path
		else:
			return system_path
	elif (os.path.isdir(system_path)):
		# system path is a directory
		return system_path
	else:
		if(session_loaded == True):
			print('\n>>>>> Loaded target is not a valid file or directory!\n')
			sys.exit(1)
		else:
			raise argparse.ArgumentTypeError('\n>>>>> Provided target is not a valid file or directory!\n')
# =============================================================================
# =============================================================================
# Name:       validate_hash_type(hash_type)
# Arguments:  hash_type = a string representing type of hash to be used
# Purpose:    Returns a hash type or raises error
# =============================================================================
def validate_hash_type(hash_type):
	possible_hashes = ["MD5", "SHA1", "SHA224", "SHA256", "SHA384", "SHA512"]
	hash_type = hash_type.upper() # converts characters to upper case to match list

	if hash_type in possible_hashes:
		return hash_type
	else:
		if(session_loaded == True):
			print('\n>>>>> Loaded hash is not a valid or supported hash type!\n')
			sys.exit(1)
		else:
			raise argparse.ArgumentTypeError('\n\n>>>>> Provided hash is not a valid or supported hash type!\n')
# =============================================================================
# Argument Name:    target
# Argument Type:    argument value
# Functionality:    Receives target file or directory or recursive directory.
# =============================================================================
#region ArgParse Arguments
parser.add_argument("target", metavar='system_path', type=validate_target,
help="""
===============================================================================
'HashPy.py file_path'           - Hashes only the single file specified
'HashPy.py directory_path'      - Hashes files in specified directory
'HashPy.py directory_path -r    - Hashes files in directory recursively
'HashPy.py HashPy.config'       - Continues previous hashing session
===============================================================================           
""")
# =============================================================================
# Argument Name:    -r
# Argument Type:    flag
# Functionality:    Toggles ON recursive mode for file discovery.
# =============================================================================
parser.add_argument("-r", "--recursive", action='store_true',
help="""
===============================================================================
'HashPy.py directory -r'        - Hashes files in directory recursively
===============================================================================

""")
# =============================================================================
# =============================================================================
# Argument Name:    -v
# Argument Type:    flag
# Functionality:    Toggles ON verbose mode for output to console.
# =============================================================================
parser.add_argument("-v", "--verbose", action='store_true',
help="""
===============================================================================
Displays progress of the hashing process in console.
'HashPy.py file_path -v'
===============================================================================

""")
# =========================================================================
# Argument Name:    -hash_type 
# Argument Type:    argument value
# Functionality:    Receives hash_type
# =========================================================================
parser.add_argument("-hash","--hash_type", metavar='hash_type', type=validate_hash_type,
help="""
===============================================================================
Hashing type used: MD5, SHA1, SHA224, SHA256, SHA384 or SHA512.
'HashPy.py file_path -hash hash_type'
===============================================================================

""")
#endregion

# =============================================================================
# Name:       update_settings(args)
# Arguments:  args = argparse arguments after user input or loaded from config
# Purpose:    Changes values to global variables based on user input
# =============================================================================
def update_settings(args):

	global  session_target_path 
	global  session_recursive_search
	global  session_hash_type
	global  session_verbose_mode
	global  session_datetime
	global  session_loaded_file
	global  config_dir_path
	global  config_file_path
	global  discovered_list_path
	global  hashed_list_path
	# Handle checking session_loaded_file first
	if (session_loaded == True):
		# Handle checking session_loaded_file first
		session_loaded_file = args.target
		if (session_loaded_file is not None):
			# Load settings from file
			config = configparser.ConfigParser()
			config.read(session_loaded_file)
			settings = config['settings']
			session_target_path = validate_target(settings['session_target_path'])
			session_recursive_search = settings['session_recursive_search']
			session_hash_type = validate_hash_type(settings['session_hash_type'])
			session_verbose_mode = settings['session_verbose_mode']
			session_datetime = settings['session_datetime']
	else:
		session_target_path = args.target
		session_recursive_search = args.recursive
		session_hash_type = args.hash_type if args.hash_type is not None else "MD5"
		session_verbose_mode = args.verbose
		session_loaded_file = config_file_path

	config_dir_path = os.path.join(session_local_path,session_main_dir,session_datetime,session_config_dir)
	# Path for config file
	config_file_path = os.path.join(config_dir_path,session_config_file)
	# Path for discovered_files fil
	discovered_list_path = os.path.join(config_dir_path,session_discovered_list)
	# Path for hashed files status file  ('hashed_files_status.txt')
	hashed_list_path = os.path.join(config_dir_path,session_hashed_list)
# =============================================================================
# Name:       save_settings()
# Purpose:    Saves current settings to session folder, ignores if loaded.
# =============================================================================
def save_settings():
	if(session_loaded == False):
		config = configparser.ConfigParser()
		config['settings'] = {
		'session_target_path': session_target_path,
		'session_recursive_search': session_recursive_search,
		'session_hash_type': session_hash_type,
		'session_verbose_mode': session_verbose_mode,
		'session_datetime': session_datetime
		}
		# Create folder for current session
		os.makedirs(config_dir_path, exist_ok=True)
		# Create/Open File in directory for new session
		with open(config_file_path, 'w', encoding='utf8') as f:
			config.write(f)
# =============================================================================
# Name:       print_settings
# Purpose:    Prints current settings
# =============================================================================
def print_settings():
	print ("{:<2}{:<25}".format('','======================================================================='))
	print ("{:<2}{:<25}{:<10}".format('','Setting', 'Value'))
	print ("{:<2}{:<25}".format('','======================================================================='))
	print ("{:<2}{:<25}{:<10}".format('',"Session File", str(session_loaded_file)))
	print ("{:<2}{:<25}{:<10}".format('',"Session Date&Time", str(session_datetime)))
	print ("{:<2}{:<25}{:<10}".format('',"Session Loaded", str(session_loaded)))
	print ("{:<2}{:<25}{:<10}".format('',"Target Path", str(session_target_path)))
	print ("{:<2}{:<25}{:<10}".format('',"Recursive", str(session_recursive_search)))
	print ("{:<2}{:<25}{:<10}".format('',"Hash Type", str(session_hash_type)))
	print ("{:<2}{:<25}{:<10}".format('',"Verbose Progress", str(session_verbose_mode)))
	print ("{:<2}{:<25}".format('','======================================================================='))
# =============================================================================
# =============================================================================
# Name:       file_discovery_saving())
# Purpose:    Saves list of discovered files to a file 'discovered_files.txt'
# =============================================================================
# TODO Might make a switch to determine if it's file discovery or hashed data
def file_discovery_saving(discovered_file_data):
	global _discovered_files_count
	# Create folder for current session
	os.makedirs(config_dir_path, exist_ok=True)
	f = open(discovered_list_path, 'a', newline='', encoding='utf8') # newline='' removes blank lines between outputs that csv data tries to input?
	with f:
		writer = csv.writer(f)
		writer.writerow(discovered_file_data)
	_discovered_files_count += 1
# =============================================================================
# Name:       file_discovery_status(file_count)
# Purpose:    Displays formatted console output showing number of files discovered.
# =============================================================================
def file_discovery_status(list_end):
	if session_verbose_mode:
		real__discovered_files_count = _discovered_files_count - 1 # correction for the header row
		if (list_end):
			print ("{:<2}{:<25}{:<10}".format('',"Discovered files", str(real__discovered_files_count)))
			print ("{:<2}{:<25}".format('','======================================================================='))
		else:
			text = ("\r{:<2}{:<25}{:<10}".format('',"Discovered files", str(real__discovered_files_count)))
			print (text,end='\r')
# =============================================================================
# Name:       file_discovery()
# Purpose:    Discovers files and directories based on provided path.
# =============================================================================
def file_discovery():
	#global discovered_files_data
	# The general idea is to have a file discovery as before, but this time save all of the files and the information about them in csv format.
	# Data that we are interested in mainly:
	csv_format_header = ["Location", "Name", "Size","Created","Modified","Hash"]
	file_discovery_saving(csv_format_header) # Save first Row
	# File Discovery Functions Here:
	# If path is a single file
	if (os.path.isfile(session_target_path)):
		current_file_info = get_file_info(session_target_path)

		#discovered_files_data.append(current_file_info)
		file_discovery_saving(current_file_info) 
		file_discovery_status(False)
	# If path is a directory
	elif (os.path.isdir(session_target_path)):
		for dir_path, directories, files in os.walk(session_target_path):
			for file_name in files:
				full_path = (os.path.join(dir_path, file_name))

				current_file_info = get_file_info(full_path)
				#discovered_files_data.append(current_file_info)
				file_discovery_saving(current_file_info)
				file_discovery_status(False)

			# If it is not in recursive mode then it should stop now
			if (session_recursive_search == False):
				break
			# Else it is recursive
			else:
				pass

	file_discovery_status(True)
# =============================================================================
# Name:       get_file_info(file_path)
# Purpose:    Returns metadata about file
# =============================================================================
def get_file_info(file_path):

	# If path is a valid file
	if (os.path.isfile(file_path)):
		# 10 digit tuple with following data: (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
		st = os.stat(file_path)
		file_path, file_name = os.path.split(file_path)
		# Format:           ["Location", "Name", "Size","Created","Modified","Hash"]
		current_file_info = [file_path, file_name, st[6],st[9],st[8],None]
		return current_file_info
	else:
		#Perhaps some error code here with path for when it happened.
		pass
# =============================================================================
# Name:       correct_file_size(num)
# Purpose:    Return corrected value for file size.
# =============================================================================
def correct_file_size(num):
    # this function will return the file size with apropriate size notation
    for x in ['B', 'KB', 'MB', 'GB', 'TB']:
    	if num < 1024.0:
    		return "%3.1f %s" % (num, x)
    	num /= 1024.0
# =============================================================================
# Name:       get_hashing_status(file_path, list_end)
# Purpose:    Displays formatted console output showing number of files discovered.
# =============================================================================
def display_hashing_status(hashing_file_data, list_end):
	global _last_output_length

	file_name = hashing_file_data[1]
	file_size = correct_file_size(int(hashing_file_data[2]))
	# Shortens the name to 40 characters
	file_name = file_name[:40]

	if(list_end):
		print("{:<2}{:<8}{:<5}{:<1}{:<8}{:<6}{:<10}{:<6}{:<10}".format('',"Hashing",_hashed_files_count,"/",_discovered_files_count-1, "Size:", file_size,"Name: ",str(file_name)))
		print("{:<2}{:<25}".format('','======================================================================='))
	else:
		# Add +1 if this doesn't work correctly
		text = ("\r{:<2}{:<8}{:<5}{:<1}{:<8}{:<6}{:<10}{:<6}{:<10}".format('',"Hashing",_hashed_files_count,"/",_discovered_files_count-1, "Size:", file_size,"Name: ",str(file_name)))
		# If previous entry was longer, clear the entry
		if (_last_output_length > len(text)):
			print(" "*_last_output_length,end='\r')
		# Display current entry
		print (text,end='\r')
		# Update last entry length
		_last_output_length = len(text)
# =============================================================================
# Name:       file_hashed_saving()
# Purpose:    Saves list of hashed files to a file 'hashed_files.csv'
# =============================================================================
def file_hashed_saving(hashed_file_data):
	global _hashed_files_count
	# Create folder for current session
	os.makedirs(config_dir_path, exist_ok=True)
	f = open(hashed_list_path, 'a', newline='', encoding='utf8') # newline='' removes blank lines between outputs that csv data tries to input?
	with f:
		writer = csv.writer(f)
		#writer.writerows(discovered_file_data)
		writer.writerow(hashed_file_data)
	_hashed_files_count += 1
# =============================================================================
# Name:       convert_bytes(num)
# Purpose:    Returns placeholder length for hash
# =============================================================================	
def convert_bytes(num):
	# Converts number to correct size string
	for x in ['B', 'KB', 'MB', 'GB', 'TB']:
		if num < 1024.0:
			return "%3.1f %s" % (num, x)
		num /= 1024.0
# =============================================================================
# Name:       get_hash_object(hash_type)
# Arguments:  hash_type = a string that corresponds to the type of hash being used
# Purpose:    Returns a hash object or none
# Source:     https://docs.python.org/2/library/hashlib.html
# =============================================================================
def get_hash_object(hash_type):

	if hash_type == "MD5":
		return hashlib.md5()
	elif hash_type == "SHA1":
		return hashlib.sha1()
	elif hash_type == "SHA224":
		return hashlib.sha224()
	elif hash_type == "SHA256":
		return hashlib.sha256()
	elif hash_type == "SHA384":
		return hashlib.sha384()
	elif hash_type == "SHA512":
		return hashlib.sha512()
	else:
		return hashlib.md5()
		# default md5
# =============================================================================
# Name:       get_dummy_hash_value()
# Purpose:    Returns placeholder length for hash
# =============================================================================	
def get_dummy_hash_value():
	if session_hash_type == "MD5":
		return "-" * 32
	elif session_hash_type == "SHA1":
		return "-" * 40
	elif session_hash_type == "SHA224":
		return "-" * 56
	elif session_hash_type == "SHA256":
		return "-" * 64
	elif session_hash_type == "SHA384":
		return "-" * 96
	elif session_hash_type == "SHA512":
		return "-" * 128
# =============================================================================
# Name:       hash_file(filename)
# Arguments:  filename = a string that corresponds to the file that is being hashed
# Source:     http://www.programiz.com/python-programming/examples/hash-file
# Purpose:    Returns a hash digest from the file
# Notes:      Removed Try catch from it as per recommendation on
# Source:     https://stackoverflow.com/questions/35953283/how-do-i-have-a-python-function-return-an-exception-traceback-or-the-result
# =============================================================================
def hash_file(filename):
	# make a hash object
	h = get_hash_object(session_hash_type)
	# open file for reading in binary mode
	f = open(filename, 'rb')
	# TODO do some benchmarking for chunk size based on file size?
	try:
		# loop till the end of the file
		chunk = 0
		while chunk != b'':
			# read only 1024 bytes at a time
			chunk = f.read(1024)
			h.update(chunk)
	finally:
		f.close()
	# return the hex representation of digest
	return h.hexdigest()

# =============================================================================
# Name:       file_hasher()
# Purpose:    Hashes all discovered files
# =============================================================================
def file_hasher():

	#Here Save first row with headers
	csv_format_header = ["Location", "Name", "Size","Created","Modified","Hash"]
	file_hashed_saving(csv_format_header)

	with open(discovered_list_path, newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		#current_csv_position = 0

		for row in reader:
			_Location = row['Location']
			_Name = row['Name']
			_Size = row['Size']
			_Created = row['Created']
			_Modified = row['Modified']
			_Hash = row['Hash']
			file_hash = ""

			if _Hash == "":
				# Print  Hashing Status - important to display hashing before file is actually hashed
				end_of_file = (_hashed_files_count + 1 == _discovered_files_count)
				display_hashing_status([_Location,_Name,_Size,_Created,_Modified,file_hash], end_of_file)

				#If hash value is empty then proceed with hashing
				file_path = os.path.join(_Location,_Name)
				#file_hash = hash_file(file_path)
				try:
					file_hash = hash_file(file_path)
				except Exception:
					file_hash = get_dummy_hash_value() # Returns Dummy Hash Value '-------' to keep structure
				# Update current_file_info
				hashed_file_data = [_Location,_Name,_Size,_Created,_Modified,file_hash]
				file_hashed_saving(hashed_file_data)
			else:
				pass
			#current_csv_position += 1

# =============================================================================
# Name:       run_app
# Purpose:    starts off all required funcitions.
# =============================================================================
def run_app():
	args = parser.parse_args()
	update_settings(args)
	print_settings()
	file_discovery()
	save_settings()
	file_hasher()
# =============================================================================
# Name:       main
# Purpose:    Starts runApp() and listens for keyboard interrupt to end script
# =============================================================================
if __name__ == '__main__':
	try:
		run_app()
	except KeyboardInterrupt:
		import sys
		print("\n\n{*} User Requested An Interrupt!")
		print("{*} Application Shutting Down.")
		sys.exit(1)
# =============================================================================
