MESSAGE = """
   _____ _                 _  _____                  
  / ____| |               | |/ ____|                 
 | |    | | ___  _   _  __| | (___  _   _ _ __   ___ 
 | |    | |/ _ \| | | |/ _` |\___ \| | | | '_ \ / __|
 | |____| | (_) | |_| | (_| |____) | |_| | | | | (__ 
  \_____|_|\___/ \__,_|\__,_|_____/ \__, |_| |_|\___|
                                     __/ |           
                                    |___/            
"""


def print_boot_message():
    print(MESSAGE)
    print("Starting cloud_sync...")
    print("")
    print("This script will sync the accounts from the Exchange Online")
    print("to the SCIM API of Zivver.")
    print("")
