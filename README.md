# site-blocker
A simple Python script to block distracting social media sites on macOS and Linux by modifying your /etc/hosts file. 
Includes 3 CLI options:

1. Block social media
2. Unblock social media
3. Unblock sites for 20 minutes
Choose an option (1, 2, or 3):

# Features

Blocks social media sites by redirecting them to your local machine (127.0.0.1 for IPv4 and ::1 for IPv6).

Temporary unblock for 20 minutes with automatic re-blocking and browser closer to reinstantiate block

Unblock logging: Tracks unblock requests in a journal file with timestamps. (Adds friction so unblocks are no immediate) 

Backup: Creates a one-time backup of the original /etc/hosts file.

# Usage

Download the site-blocker.py file. From the directory where you saved the script, 

Run `sudo python3 site-blocker.py` to start the script
