from pexpect import pxssh
import pexpect
import getpass
import time
import os


try:
    s = pxssh.pxssh()



    hostname = '74.207.252.20'
    username = 'shareshop'
    password = 'djangoproject'
    
    s.login(hostname, username, password)
    print("[+] Successful SSH login.")
    print("[+] Starting up the Django development server. Please wait.")
   

    name = "share_shopping"

    s.sendline(f'cd {name}/share_shopping')
    s.prompt()
    #print(s.before)
    

    s.sendline('python3 manage.py runserver 0.0.0.0:8000')
    s.prompt()
    print("[+] Django server up and running.")
    print("[+] Opening your browser at http://74.207.252.20:8000.")


    os.system("open http://74.207.252.20:8000")

    while True: 

        inp = input("[+] Server is up and running. Press 'q' to shut down: ")


        if ord(inp) == 113:

            break

        else:
            print("[-] Invalid key. Press 'q' to shut down the server")
            continue

    print("[+] Shutting down...")
    s.sendcontrol('c')
    s.sendline('exit')

    s.logout()


except pxssh.ExceptionPxssh as e:
    print("pxssh failed on login.")
    print(e)
