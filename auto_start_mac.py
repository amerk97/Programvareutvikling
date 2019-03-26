from pexpect import pxssh
import pexpect
import getpass
import time
import os


try:
    s = pxssh.pxssh()



    hostname = '74.207.252.20'
    username = 'dmedakovic'
    password = 'medakovic'
    
    s.login(hostname, username, password)
    print("[+] Successful SSH login.")
    print("[+] Starting up the Django development server. Please wait.")
   

    name = "share_shopping"

    s.sendline(f'cd {name}/handleliste')
    s.prompt()
    #print(s.before)
    

    s.sendline('python3 manage.py runserver 0.0.0.0:8000')
    s.prompt()
    print("[+] Django server up and running.")
    print("[+] Opening your browser at http://74.207.252.20:8000.")


    os.system("open http://74.207.252.20:8000")

    s.logout()


except pxssh.ExceptionPxssh as e:
    print("pxssh failed on login.")
    print(e)
