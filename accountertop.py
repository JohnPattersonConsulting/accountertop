# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 20:28:09 2023

@author: John
"""

# Accountertop V1.0: A Fernet-based password manager by John Patterson.

# Warning: After decryption, passwords may persist in system memory until
# the memory is overwritten. Use at your own risk!

# --------------- Imports: ---------------

import os
import base64
import hashlib
import getpass
from cryptography.fernet import Fernet
import pickle 
import pyperclip 
import pyautogui
import time
import secrets

# --------------- Constants: ---------------

# Delay (seconds) until auto-typing is performed:
autotype_delay = 5;
# Default password length:
default_password_length = 16;
# Valid "lowercase" characters for creating passwords:
lowercase_chars = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'];
# Valid "uppercase" characters for creating passwords:
uppercase_chars = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'];
# Valid "digit' characters for creating passwords:
digit_chars = ['0','1','2','3','4','5','6','7','8','9'];
# Valid "special" characters for creating passwords:
special_chars = ['~','!','@','$','%','^','&','*','(',')','_','-','+','=','{','[','}',']','|',':',';','<','>','.','?'];
# Location for the save name/number config file:
save_number_location = "./accountertop_data/save_num.log";
# Locationto placce saved data:
save_location = "./accountertop_data/";


# --------------- User Prompt and Account Action Functions: ---------------

def get_save_number():
    # Check if a save name/number config file is avaialble:
    try:
        save_number_file = open(save_number_location);
        save_number = save_number_file.read();
        save_number_file.close();
    except:
        print("Save number file not found. Starting over at save 0.")
        print(" ")
        save_number_file = open(save_number_location, "w");
        save_number_file.write("0");
        save_number_file.close();
        save_number = 0;
        
    # Return save number:
    try:
        return int(save_number);
    except:
        print("Save number file error. Starting over at save 0.")
        print(" ")
        save_number_file = open(save_number_location, "w");
        save_number_file.write("0");
        save_number_file.close();
        save_number = 0;
        return save_number;

def read_from_disk():
    # Get the name of the latest save file:
    save_file_name = save_location + str(get_save_number()) + ".pkl";
    
    # Try to load the stored data from the latest file:
    try:
        loaded_data = pickle.load(open(save_file_name, "rb"));
    except:
        # Prompt the user to create a new save file:
        print("Saved data not found. We need to make a new empty save file.")
        print(" ")
        new_pass = getpass.getpass("Please provide a master password for the new save file: ");
        
        # Clear the display after the new password has been entered:
        os.system('cls')
        
        # Encrypt an empty dataset using the provided password:
        temp_data = [];
        temp_data_pickle = pickle.dumps(temp_data);
        temp_pass_hash = hashlib.sha256(bytes(new_pass, encoding="utf-8")).digest();
        temp_pass_hash = base64.urlsafe_b64encode(bytes(temp_pass_hash));
        temp_f = Fernet(temp_pass_hash);
        loaded_data = temp_f.encrypt(temp_data_pickle);
        
        # Write the new encrypted data to file:
        pickle.dump(loaded_data, open(save_file_name, "wb"));
        
    # Return the loaded encrypted file data:
    return loaded_data;
        
def write_to_disk(fernet_object,account_dictionaries):
    # Re-pickle the data:
    account_dictionaries_pickle = pickle.dumps(account_dictionaries);
    
    # Re-encrypt the data:
    temp_encrypted = fernet_object.encrypt(account_dictionaries_pickle);
    
    # Load and increment file name/number:
    save_number = get_save_number() + 1;
    
    # Create next file neam:
    save_file_name = save_location + str(save_number) + ".pkl";
    
    # Write the data to the next file in the list:
    pickle.dump(temp_encrypted, open(save_file_name, "wb"));
    
    # Write out the new file name/number to the config file:
    save_number_file = open(save_number_location, "w");
    save_number_file.write(str(save_number));
    save_number_file.close();


def account_select_prompt(account_dictionaries):
    # Display the stored accounts:
    print("--------------- Stored Accounts: --------------- ")
    print(" ")
    for index in range(len(account_dictionaries)):
        # Print accounts:
        print(str(index) + "   " + account_dictionaries[index]["account"])
    print(" ")
        
    # Prompt the user to select an account:
    print("Please enter the number of a stored account.")
    print("Otherwise, enter one of the following:")
    print(" 'n' to create a new account.")
    print(" 'p' to change the master password.")
    print(" 'q' to clear variables and quit.")
    print(" ")
    returned_string = input(">>");
    print(" ")
    
    # Return the string typed by the user:
    return returned_string;

def account_action_prompt(account_dictionary):
    # Display the selected account name:
    print("--------------- Selected Account: " + account_dictionary["account"] + " ---------------")
    print(" ")

    # Prompt the user to take action with the selected account:
    while 1:
        print("Please enter the number of the action to perform on the account: ")
        print(" ")
        print("0. Select a different account or exit.")
        print("1. Expose username and password to screen.")
        print("2. Copy username to clipboard.")
        print("3. Copy password to clipboard.")
        print("4. Auto-type username after " + str(autotype_delay) + " seconds.")
        print("5. Auto-type password after " + str(autotype_delay) + " seconds.")
        print("6. Update account username.")
        print("7. Update account password.")
        print("8. Remove account.")
        print(" ")
        returned_string = input(">>");
        print(" ")
        
        # Check if the selection matches one of the above list:
        try:
            returned_number = int(returned_string);
            action_string_convert_success = 1;
        except:
            # Clear display:
            os.system('cls')  
            # Alert the user that the selection was invalid:
            print("Invalid selection. Please try again.")
            print(" ")
            action_string_convert_success = 0;
        if (action_string_convert_success == 1) and (returned_number >= 0) and (returned_number <= 8):
            break;
            
    # Return the number typed by the user:
    return returned_number;

def update_master_password(fernet_object):    
    # Ask for new password:
    new_master = getpass.getpass("New master password (or press enter to abort): ");
    if new_master == '':
        # Clear display:
        os.system('cls') 
        # Indicate to the user that the update was skipped:
        print("Master password update skipped.")
        print(" ")
        return fernet_object;
    
    # Hash new password and create new Ferent object:
    new_pass_hash = hashlib.sha256(bytes(new_master, encoding="utf-8")).digest();
    new_pass_hash = base64.urlsafe_b64encode(bytes(new_pass_hash));
    new_f = Fernet(new_pass_hash);
    
    # Clear display:
    os.system('cls') 
    
    # Inidcate successful uodate to the user:
    print("Master password updated.")
    
    # Delete hashes and cleartext master password:
    del new_master;
    del new_pass_hash;
    
    # Return new Fernet object:
    return new_f;

def generate_password(password_length,minimum_lowercase,minimum_uppercase,minimum_digits,minimum_specials,use_specials):
    # If special characters are allowed, choose passwords from all available characters:
    available_characters = lowercase_chars + uppercase_chars + digit_chars;
    if use_specials == 1:
        available_characters = available_characters + special_chars;
    
    # Try out new passwords until all requirements are met:
    password_OK = 0;
    while password_OK == 0:
        password_to_try = '';
        # Use "secrets" library to get cryptographically secure selection:
        for character in range(password_length):
            password_to_try = password_to_try + secrets.choice(available_characters);
        
        # Determine the number of each character type in the random password:
        number_lowercase = 0;
        number_uppercase = 0;
        number_digits = 0;
        number_specials = 0;
        for character in password_to_try:
            # Search for matches in the lowercase characters:
            for search_char in lowercase_chars:
                if search_char == character:
                    number_lowercase = number_lowercase + 1;
            # Search for matches in the uppercase characters:
            for search_char in uppercase_chars:
                if search_char == character:
                    number_uppercase = number_uppercase + 1;
            # Search for matches in the digit characters:
            for search_char in digit_chars:
                if search_char == character:
                    number_digits = number_digits + 1;
            # Search for matches in the special characters:
            for search_char in special_chars:
                if search_char == character:
                    number_specials = number_specials + 1;
                    
        # Test to determine if the password meets minimum character criteria:
        if (number_lowercase >= minimum_lowercase) and (number_uppercase >= minimum_uppercase) and (number_digits >= minimum_digits) and (number_specials >= minimum_specials):
            # Mark that a suitable password was found:
            password_OK = 1;
            
    # Return the selected password:
    return password_to_try;
        
                
def update_password(account_dictionary):    
    # Ask the user what type of password update to perform:
    while 1:
        print("Please enter the number of the password generation method: ")
        print(" ")
        print("0. Skip updating password.")
        print("1. Type in a new password (show typed characters).")
        print("2. Type in a new password (obscure typed characters).")
        print("3. Generate a random alphanumeric password.")
        print("4. Generate a random alphanumeric password with special characters.")
        print(" ")
        returned_string = input(">>");
        print(" ")
        
        # Check if the selection matches one of the above list:
        try:
            returned_number = int(returned_string);
            password_string_convert_success = 1;
        except:
            # Clear display:
            os.system('cls')
            # Alert the user that the selection was invalid:
            print("Invalid selection. Please try again.")
            print(" ")
            password_string_convert_success = 0;
        if (password_string_convert_success == 1) and (returned_number >= 0) and (returned_number <= 4):
            break;
            
    if returned_number == 0:
        # Clear display:
        os.system('cls') 
        # Return the original account dictionary:
        print("Password update skipped.")
        print(" ")
        return account_dictionary;
    
    if returned_number == 1:
        # Prompt user to type password:
        new_password = input("New password (or press enter to abort): ")
        # Skip updating if password is left blank:
        if new_password == '':
            # Clear display:
            os.system('cls') 
            print("Password update skipped.")
            print(" ")
            return account_dictionary;
        
    if returned_number == 2:
        # Prompt user to type password:
        new_password = getpass.getpass("New password (or press enter to abort): ")
        # Skip updating if password is left blank:
        if new_password == '':
            # Clear display:
            os.system('cls') 
            print("Password update skipped.")
            print(" ")
            return account_dictionary;
        
    if returned_number == 3:
        # Ask how many characters the password should have:
        while 1:
            print("How many characters should the new password have?")
            number_chars_string = input("(Leave blank for default " + str(default_password_length) + " characters): ");
            if number_chars_string == "":
                number_chars = default_password_length;
                break;
            else:
                try:
                    number_chars = int(number_chars_string);
                    number_chars_conversion_success = 1;
                except:
                    print("Invalid length. Please try again.")
                    print(" ")
                    print(number_chars_string)
                    number_chars_conversion_success = 0;
                if number_chars_conversion_success == 1:
                    if number_chars >= 3:
                        break;
                    else:
                        print("Length must be at least 3. Please try again.")
                        print(" ")
        # Generate a random alphanumeric string of the desired size:
        new_password = generate_password(number_chars,1,1,1,0,0);
        
    if returned_number == 4:
        # Ask how many characters the password should have:
        while 1:
            print("How many characters should the new password have?")
            number_chars_string = input("(Leave blank for default " + str(default_password_length) + " characters): ");
            if number_chars_string == "":
                number_chars = default_password_length;
                break;
            else:
                try:
                    number_chars = int(number_chars_string);
                    number_chars_conversion_success = 1;
                except:
                    print("Invalid length. Please try again.")
                    print(" ")
                    number_chars_conversion_success = 0;
                if number_chars_conversion_success == 1:
                    if number_chars >= 4:
                        break;
                    else:
                        print("Length must be at least 4. Please try again.")
                        print(" ")
        # Generate a random alphanumeric string of the desired size:
        new_password = generate_password(number_chars,1,1,1,1,1);
        
    # Clear display:
    os.system('cls') 
        
    # Return updated dictionary:
    account_dictionary["password"] = new_password;
    print("Password updated.")
    print(" ")
    return account_dictionary;
    

def new_account_prompt(account_dictionaries):    
    # Ask for new account name:
    account_account = input("New account name (or press enter to abort): ");
    if account_account == '':
        # Clear display:
        os.system('cls') 
        # Indicate to the user that the new account was skipped:
        print("New account skipped.")
        print(" ")
        return account_dictionaries;
    
    # Ask for new account username:
    account_username = input("New account username: ");
    print(" ")
    
    # Create a mostly-complete dictionary without password:
    new_dictionary = dict(account = account_account, username = account_username, password = '');
    
    # Prompt the user to update the password:
    new_dictionary = update_password(new_dictionary);
    
    # Append the new account to the entire dictionary list:
    account_dictionaries.append(new_dictionary);
        
    # Return the updated dictionaries:
    return account_dictionaries;
    
def display_username_password(account_dictionary):
    # Directly display account information:
    print("Account Details: ")
    print(" ")
    print("Account: " + str(account_dictionary["account"]))
    print("Username: " + str(account_dictionary["username"]))
    print("Password: " + str(account_dictionary["password"]))
    print(" ")
    
def username_to_clipboard(account_dictionary):
    # Copy username to clipboard:
    pyperclip.copy(account_dictionary["username"]);
    print(str(account_dictionary["account"]) + " username copied to clipboard.")
    print(" ")

def password_to_clipboard(account_dictionary):
    # Copy username to clipboard:
    pyperclip.copy(account_dictionary["password"]);
    print(str(account_dictionary["account"]) + " password copied to clipboard.")
    print(" ")
    
def username_to_autotype(account_dictionary):
    # Display a countdown until autotyping occurs:
    countdown_whole_seconds = autotype_delay//1;
    countdown_partial_seconds = autotype_delay%1;
    for counter in range(int(countdown_whole_seconds)):
        print("Autotyping username in " + str(int(countdown_whole_seconds-counter)) + " seconds...");
        time.sleep(1);
    time.sleep(countdown_partial_seconds);
    # Perform autotyping:
    for letter in account_dictionary["username"]:
        pyautogui.press(letter);
    print(" ")
    print("Autotyping complete.")
    print(" ")
    
def password_to_autotype(account_dictionary):
    # Display a countdown until autotyping occurs:
    countdown_whole_seconds = autotype_delay//1;
    countdown_partial_seconds = autotype_delay%1;
    for counter in range(int(countdown_whole_seconds)):
        print("Autotyping password in " + str(int(countdown_whole_seconds-counter)) + " seconds...");
        time.sleep(1);
    time.sleep(countdown_partial_seconds);
    # Perform autotyping:
    for letter in account_dictionary["password"]:
        pyautogui.press(letter);
    print(" ")
    print("Autotyping complete.")
    print(" ")
    
def update_username(account_dictionary):
    # Prompt to update username:
    new_username = input("New username (or press enter to abort): ");
    # Skip updating if username is left blank:
    if new_username == '':
        # Clear display:
        os.system('cls') 
        print("Username update skipped.")
        print(" ")
        return account_dictionary;
    # Clear display:
    os.system('cls') 
    # Return updated dictionary:
    account_dictionary["username"] = new_username;
    print("Username updated.")
    print(" ")
    return account_dictionary;    
    
def confirm_remove_account(account_dictionary):
    choice = input("Are you sure you want to remove " + str(account_dictionary["account"]) + "? (y/n):");
    if (choice == 'y') or (choice == 'Y'):
        return 1;
    else:
        # Clear display:
        os.system('cls') 
        print("Account removal skipped.")
        print(" ")
    

# --------------- Main Program: ---------------

# Clear display:
os.system('cls')  

# Display information about the program:
print("--------------- Welcome to Accountertop V1.0 ---------------")
print(" ")

# Create data storage directory if it does not already exist:
if not os.path.exists(save_location):
    os.makedirs(save_location);

# Load in latest data set:
data_encrypted = read_from_disk();

# Enter a loop with "try-except" until correct password is entered:
password_OK = 0;
while password_OK == 0:
    # Prompt the user to enter the master password without showing characters:
    master = getpass.getpass("Please enter master password: ")
    print(" ")
    
    # Compute the base-64 URL-safe SHA-256 hash of the master password:
    master_hash = hashlib.sha256(bytes(master, encoding="utf-8")).digest();
    master_hash = base64.urlsafe_b64encode(bytes(master_hash));
    
    # Generate Fernet object using master hash:
    f = Fernet(master_hash);
    
    # Delete master password and hashes from *accessible* RAM:
    del master;
    del master_hash;
    
    # Assume password is OK until proven otherwise:
    password_OK = 1;
    
    # Check if password is OK:
    try:
        # Decrypt the contents of the encrypted data file:
        decrypted_pickle = f.decrypt(data_encrypted);
    except:
        # Indicate that password was not OK:
        print("Invalid master password!")
        print(" ")
        # Flag that password was not OK:
        password_OK = 0;

# Clear display:
os.system('cls') 

# Indicate that password was accepted:
print("Master password accepted. ")
print(" ")

# Extract the passwords dictionary from the pickled data.
decrypted_data = pickle.loads(decrypted_pickle);
del decrypted_pickle;

# Prompt user to select an account until the "quit" option is selected:
while 1:    
    # Prompt the user to select an account or perform other operations:
    prompt_string = account_select_prompt(decrypted_data);
    
    # Determine if the user has requested to quit the program:
    if (prompt_string == 'q') or (prompt_string == 'Q'):
        # Break the loop to exit the program:
        break;
    
    # Determine if the user has requested to create a new account:
    elif (prompt_string == 'n') or (prompt_string == 'N'):
        # Invoke the "create_new_account" prompt function:
        decrypted_data = new_account_prompt(decrypted_data);
        # Write updated dictionaries to disk:
        write_to_disk(f,decrypted_data);
        string_convert_success = 0;     
        
    # Determine if the user has requested to change the master password:
    elif (prompt_string == 'p') or (prompt_string == 'P'):
        # Invoke the "update_master_password" prompt function:
        f = update_master_password(f);
        # Write updated dictionaries to disk:
        write_to_disk(f,decrypted_data);
        string_convert_success = 0;   
    
    # Otherwise, check to see if the entered text is a valid account number:
    else:
       try:
           # Attempt to convert the entered string to an integer:
           prompt_number = int(prompt_string);
           string_convert_success = 1;
       except:
           # Clear display:
           os.system('cls')  
           # Alert the user that the selection was invalid:
           print("Invalid selection. Please try again.")
           print(" ")
           string_convert_success = 0;
    
    # If the account number is valid, provide the account action menu:
    if string_convert_success == 1:
        if (prompt_number >= 0) and (prompt_number < len(decrypted_data)):
            # Clear display:
            os.system('cls') 
            while 1:
                # Prompt the user to perform actions on the selected account:
                action_number = account_action_prompt(decrypted_data[prompt_number]);
                
                # Perform requested action:
                if action_number == 0:
                    # Clear display:
                    os.system('cls') 
                    # Select a different account (exit loop):
                    break;
                if action_number == 1:
                    # Clear display:
                    os.system('cls') 
                    # Display username and password to screen:
                    display_username_password(decrypted_data[prompt_number]);
                if action_number == 2:
                    # Clear display:
                    os.system('cls') 
                    # Copy username to clipboard:
                    username_to_clipboard(decrypted_data[prompt_number]);
                if action_number == 3:
                    # Clear display:
                    os.system('cls') 
                    # Copy password to clipboard:
                    password_to_clipboard(decrypted_data[prompt_number]);
                if action_number == 4:
                    # Clear display:
                    os.system('cls') 
                    # Auto-type username:
                    username_to_autotype(decrypted_data[prompt_number]);
                if action_number == 5:
                    # Clear display:
                    os.system('cls') 
                    # Auto-type password:
                    password_to_autotype(decrypted_data[prompt_number]);
                if action_number == 6:
                    # Clear display:
                    os.system('cls') 
                    # Update username:
                    decrypted_data[prompt_number] = update_username(decrypted_data[prompt_number]);
                    # Write updated dictionaries to disk:
                    write_to_disk(f,decrypted_data);
                if action_number == 7:
                    # Clear display:
                    os.system('cls') 
                    # Update password:
                    decrypted_data[prompt_number] = update_password(decrypted_data[prompt_number]);
                    # Write updated dictionaries to disk:
                    write_to_disk(f,decrypted_data);
                if action_number == 8:
                    # Clear display:
                    os.system('cls') 
                    # Confirm account deletion:
                    if confirm_remove_account(decrypted_data[prompt_number]):
                        # Delete account:
                        del decrypted_data[prompt_number];
                        # Write updated dictionaries to disk:
                        write_to_disk(f,decrypted_data); 
                        print("Account removed.")
                        print(" ");
                        # Return to account selection menu:
                        break;
                    # Otherwise, resume menu.
                    
        else:
            # Clear display:
            os.system('cls')  
            # Alert the user that the selection was invalid:
            print("Invalid selection. Please try again.")
            print(" ")

# Clear sensitive information from variables from *accessible* RAM:
del f;
del decrypted_data;
