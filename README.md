# Centralized RDP Profile Management for Thin Clients

Syncs RDP profiles from local storage to remote clients (HP ThinPro, Linux with Remmina) using inventory.

## Requirements
- Python3
- `sshpass` (sudo apt install sshpass)

## Installation
```bash
apt install sshpass
git clone https://github.com/dampados/thin-clients-automation.git
cd thin-clients-automation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage 
```bash
source venv/bin/activate
python3 app.py
```
<img width="481" height="110" alt="image" src="https://github.com/user-attachments/assets/35c0b1a6-7a04-4783-9d0f-7ab89a66d15f" />


## Credits
icmplib used, thanks
