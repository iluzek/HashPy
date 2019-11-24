# HashPy
HashPy - Generating Hash Values into .csv file

## About the Project
**[HashPy V1]** Project started as simple tool for hashing files and while other tools are available that they did not handle well:
- hashing large number of files
- displaying status of the hashing
Hashes could be displayed on the screen or saved to a .txt file

**[HashPy V2]** Second itteration of the project allowed for:
- Handling interruptions to the hashing process
- Resuming the hashing process

**[HashPy V3]** Third itteration of the project worked on saving data into more accessible format.

**[HashPy V4]** Fourth itteration of the project changed directions in the way that data was saved and entire list of files and hashed files was now stored in .csv format.

Features:
- Discovers and saves location for all valid files in target location before attempting to hash them.
- Saves metadata like ["Location", "Name", "Size","Created","Modified","Hash"] which will be used for sorting and finding duplicates.
- Hashed files are saved one by one to the list with already hashed files.
- Able to resume progress if target location is pointed to the configuration file.

## Usage and Command Options
```
python .\HashPy.py -h
usage: HashPy.py [-h] [-r] [-v] [-hash hash_type] system_path

positional arguments:
  system_path
                        ===============================================================================
                        'HashPy.py file_path'           - Hashes only the single file specified
                        'HashPy.py directory_path'      - Hashes files in specified directory
                        'HashPy.py directory_path -r    - Hashes files in directory recursively
                        'HashPy.py HashPy.config'       - Continues previous hashing session
                        ===============================================================================

optional arguments:
  -h, --help            show this help message and exit
  -r, --recursive
                        ===============================================================================
                        'HashPy.py directory -r'        - Hashes files in directory recursively
                        ===============================================================================

  -v, --verbose
                        ===============================================================================
                        Displays progress of the hashing process in console.
                        'HashPy.py file_path -v'
                        ===============================================================================

  -hash hash_type, --hash_type hash_type

                        ===============================================================================
                        Hashing type used: MD5, SHA1, SHA224, SHA256, SHA384 or SHA512.
                        'HashPy.py file_path -hash hash_type'
                        ===============================================================================
```
## Example
<br />![alt text](https://i.imgur.com/ygM8MXl.png)<br />
