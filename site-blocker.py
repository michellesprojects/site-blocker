import os
import sys
import time
import threading
from datetime import datetime

HOST_PATH = "/etc/hosts" #mac/linux host file
REDIRECT_IP4 = "127.0.0.1" #redirect IP (dead end local IP to point sites to) works for IP4
REDIRECT_IP6 = "::1" #redirect IP for IP6
BLOCK_COMMENT_BEGIN = "# BEGIN BLOCKED SITES"
BLOCK_COMMENT_END = "# END BLOCKED SITES"
TEMP_UNBLOCK_DURATION = 20 * 60  # 20 minutes (in seconds)

#All the sites you want blocked!
BLOCKED_SITES = [
    "www.youtube.com", "youtube.com",
    "www.instagram.com", "instagram.com",
    "www.substack.com", "substack.com",
    "www.x.com", "x.com",
    "www.facebook.com", "facebook.com",
    "www.reddit.com", "reddit.com",
    "www.tiktok.com", "tiktok.com"
]


DOCS_DIR = os.path.expanduser("~/Documents/social-blocker") #Documents folder to keep our stuff backup & journal 
os.makedirs(DOCS_DIR, exist_ok=True) #check if directory already exists
BACKUP_FILE = os.path.join(DOCS_DIR, "hosts.backup") #backup of original /etc/hosts
JOURNAL_FILE = os.path.join(DOCS_DIR, "unblock-request-journal.txt") #file for unblock requests



#--- HOSTS FILE BACKUP ---
def backup_hosts():
    '''
    one time backup of the /etc/hosts file when the script is first run
    saved in Documents/social-blocker/hosts.backup
    '''
    if not os.path.exists(BACKUP_FILE):
        with open(HOST_PATH, "r") as original, open(BACKUP_FILE, "w") as backup:
            backup.write(original.read())
        print(f"Hosts file backup created at {BACKUP_FILE}")



# --- BLOCKING LOGIC ---- 
def build_block():
    '''
    creates lines in the format of:
    127.0.0.1 www.youtube.com
    ::1 www.youtube.com
    127.0.0.1 youtube.com
    ::1 youtube.com
    '''
    lines = [f"{BLOCK_COMMENT_BEGIN}\n"]
    for site in BLOCKED_SITES:
        lines.append(f"{REDIRECT_IP4} {site}\n")
        lines.append(f"{REDIRECT_IP6} {site}\n")
    lines.append(f"{BLOCK_COMMENT_END}\n")
    return lines

# --- SHARED BLOCK/UNBLOCK FUNCTION ---
def manage_block_entries(action='block'):
    """
    Add or remove blocked sites in the hosts file.
    action: 'block' to add blocked sites, 'unblock' to remove them
    """
    if action == 'block':
        backup_hosts()  # Only backup before addiing block

    # Read current state of /etc/hosts
    with open(HOST_PATH, 'r') as file:
        lines = file.readlines()

    # Clean lines: remove any existing blocked sites section (make /etc/hosts look like its original state)
    '''
    remove any existing blocked sites section (make /etc/hosts look like its original state).
    we check the /etc/hosts line by line and only save the lines that are not part of a blocked sites section to cleaned[]
    '''
    cleaned = []
    inside_block = False
    for line in lines:
        if line.strip() == BLOCK_COMMENT_BEGIN:
            inside_block = True
            continue
        if line.strip() == BLOCK_COMMENT_END:
            inside_block = False
            continue
        if not inside_block:
            cleaned.append(line)

    # Add new block if action is 'block'. If 'unblock' we are good because above cleaned it to original
    if action == 'block':
        cleaned.extend(build_block())

    # Write the new state to /etc/hosts file
    with open(HOST_PATH, 'w') as file:
        file.writelines(cleaned)
    
    print(action+"ed social media sites.")

def journal_entry():
    log_entry = input("Why do you want to unblock socials? (100 char minimum) ").strip()
    if len(log_entry) < 100:
        print(f"\nExplanation too short ({len(log_entry)}). Unblock request denied.")
        sys.exit(0)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(JOURNAL_FILE, 'a') as log:
        log.write(f"[{timestamp}] {log_entry}\n\n")

def unblock_sites():
    journal_entry()
    manage_block_entries('unblock')

# --- TIMED UNBLOCK ---
def unblock_sites_timed():
    journal_entry()
    manage_block_entries('unblock')
    print("Unblocked socials for 20 minutes. Timer started.")
    timer_thread = threading.Thread(target=reblock_after_timeout, daemon=False)
    timer_thread.start()


def reblock_after_timeout():
    elapsed = 0
    while elapsed < TEMP_UNBLOCK_DURATION:
        remaining_minutes = (TEMP_UNBLOCK_DURATION - elapsed) // 60
        print(f"{remaining_minutes} minute warning")
        time.sleep(60)
        elapsed += 60
    manage_block_entries('block')
    close_browsers()
    print("Sites re-blocked and browsers closed.")

# --- CLOSE BROWSERS ---
#only used for timed block
def close_browsers():
    system = sys.platform
    if system == "darwin":
        os.system("pkill -f 'Google Chrome'")
        os.system("pkill -f 'Firefox'")
        os.system("pkill -f 'Safari'")
    elif system.startswith("linux"):
        os.system("pkill -f chrome")
        os.system("pkill -f firefox")

# --- MAIN MENU ---
def main():
    print("1. Block social media\n2. Unblock social media\n3. Unblock sites for 20 minutes")
    choice = input("Choose an option (1, 2, or 3): ")
    if choice == "1":
        manage_block_entries('block')
    elif choice == "2":
        unblock_sites()
    elif choice == "3":
        unblock_sites_timed()
    else:
        print("Invalid choice.")
        sys.exit(0)

if __name__ == "__main__":
    main()
