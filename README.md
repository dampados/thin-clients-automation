# Thin clients RDP configs flushing script with post checks (Debian-like linux + remmina and old HP ThinPro)

## Requirements
- Python 3
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
source venv/bin/activate
python3 app.py

## Credits
icmplib used, thanks