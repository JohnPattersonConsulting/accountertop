# accountertop

## A local Python-based account and password manager based on Fernet cryptography.

## Warning:
Accountertop is currently experimental and should not be considered as a fully secure password management tool. Although accountertop encrypts all data before it is written to disk, account information is temporarily stored as clear text in RAM once extracted. Furthermore, although all variables are deleted on exit of the program, their values may remain persistent in RAM until they are overwritten. Use at own risk.

## Files/folders avaialble for download:
 -"accountertop.py": Human-readable python script that can be run in a suitably configured Python environment (see "Python script dependencies").
 -"accountertop_standalone.exe": Windows executable file that should run standalone, but may be slow to start.
 -"accountertop_exe_distribution": Folder containing a windows executable version of accountertop (accountertop.exe) with DLLs and other compiled files.
   (This distribution is less portable, but is slightly faster than the standalone exe).

## Python script dependencies:
 -os
 -base64
 -hashlib
 -getpass
 -cryptography.fernet
 -pickle 
 -pyperclip 
 -pyautogui
 -time
 -secrets

## Overview:
Accountertop is designed to provide a local file-based password management and storage solution that requires no sign-up or account creation. Accountertop can be launched from a standalone .py script or from a standalone .exe file, and thus is designed for portability. All accountertop source code is visible within accountertop.py, so its security and application suitability can be directly inspected by the user, if desired.

Accountertop offers the following password access methods (as of V1.0):
 -Direct display of usernames and passwords to the console (less secure)
 -Copying of usernames and passwords into the clipboard (somewhat secure)
 -Direct auto-typing of passwords into selected browser of program fields using pyautogui (more secure)

Accountertop also offers the following password creation methods:
 -Direct typing/pasting of passwords with entries visible on the screen (less secure)
 -Direct typing/pasting of passwords with entries obscured (somewhat secure)
 -Automatic password generation with custom length and optional use of special characters using the “secrets” cryptographically secure randomizer (more secure)

## Basic Functionality:
Accountertop works by storing account information in Python dictionary format, with the keys “account”, “username”, and “password” stored within each dictionary. A list of these dictionaries is maintained in RAM, and whenever a field within one of these is updated, the entire list of dictionaries is “pickled” into a binary data blob, is encrypted using a master password using Fernet, and is subsequently written to a unique new file on the disk. 

In order to minimize the risk of password loss, a new storage file is created every time a field in any of the dictionaries is changed. If password loss of data file corruption occurs, any of the previous files can still be accessed to recover the data. In light of this, it is recommended that all prior password files be deleted if you change your master password, as these may still be accessible using older master passwords.
When the program is first started, the master password is provided by the user in order to decrypt the most recent storage file. The name/number of the most recent saved file is logged in “save_num.log”. Saved files are stored as binary “pickle” files containing the encrypted binary data, and are sequentially numbered starting from 0 in the form “X.pkl”.

Failure to read the save number log file or the latest saved file will result in the creation of a new empty storage file at file name/number 0. This typically only occurs when a new accountertop installation is used before any files have been created. 
