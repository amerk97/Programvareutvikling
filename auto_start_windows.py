
import paramiko
import os

ssh = paramiko.SSHClient()

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect("74.207.252.20", username="shareshop", password="djangoproject")


print("[+] Successful SSH login.")
print("[+] Starting up the Django development server. Please wait.")

name = "share_shopping"

ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("cd share_shopping/handleliste; python3 manage.py runserver 0.0.0.0:8000")

print("[+] Django server up and running.")

print("[+] Opening your browser at http://74.207.252.20:8000.")

os.system("start http://74.207.252.20:8000")

while True:

    inp = input("[+] Server is up and running. Press 'q' to shut down: ")

    if ord(inp) == 113:

        break

    else:
        print("[-] Invalid key. Press 'q' to shut down the server")
        continue

print("[+] Shutting down...")

ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("cd share_shopping/handleliste; pkill -f runserver")

