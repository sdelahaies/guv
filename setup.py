import os
import subprocess

INSTALL_PATH=os.getcwd()

print("create config.py file")
with open("./config.py","w") as f:
    f.write(f"INSTALL_PATH='{os.getcwd()}'")
    
print("create env_list")    
script_path = str(f"{INSTALL_PATH}/get_venv.sh")    
subprocess.run(["bash", script_path], check=True)

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