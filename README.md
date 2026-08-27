# Thin clients RDP configs flushing script with post checks
### Debian-like linux + remmina and old HP ThinPro
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

## Configuration
gotta configure your own inventory.json:
- credentials (multiple supported)
- different connecion options (for older ssh servers)
- custom new types of clients (u can make your own handlers)
- hosts

just follow the example

## Usage 
```bash
source venv/bin/activate
python3 app.py
```

## Credits
icmplib used, thanks