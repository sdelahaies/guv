import os
import subprocess

INSTALL_PATH=os.getcwd()

print("create config.py file")
with open("./config.py","w") as f:
    f.write(f"INSTALL_PATH='{os.getcwd()}'")
    
print("create env_list")    
script_path = str(f"{INSTALL_PATH}/get_venv.sh")    
subprocess.run(["bash", script_path], check=True)

print("create ~/.bashrc_uv")
HOME=os.getenv("HOME")
with open(f"{HOME}/.bashrc","r") as f:
    bashrc=f.read()

with open(f"{HOME}/.bashrc_uv","w") as f:
    f.write(bashrc+"\n\n"+"source .venv/bin/activate"+"\n")

launcher="""#!/usr/bin/env xdg-open
[Desktop Entry]
Version=1.0
Type=Application
Terminal=true
Exec={INSTALL_PATH}/guv.py
Name=guv
Comment=guv
Icon={INSTALL_PATH}/uv.png
""".format(INSTALL_PATH=INSTALL_PATH)

print("create launcher")
with open("guv.desktop","w") as f:
    f.write(launcher)