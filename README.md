# spongebot
Spongebot for Discord

Takes messages from anyone in the "Mocked" role and responds with the same text in a mocking spongebob-style.


## Requirements/Packages:

Python3

Packages:
- discord
- python-dotenv

Use the following commands to install:

*installs pipx*
```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

*installs virtualenv via pipx*
```bash
sudo -u <username> pipx install virtualenv
sudo apt install python3.8-venv
pipx install virtualenv
```

*initiates the virtualenv*
source venv/bin/activate

*installs python packages to the virtualenv*
```bash
sudo apt install python3 python3-pip
python3 -m pip install -U discord.py python-dotenv
```
