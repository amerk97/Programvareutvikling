from pexpect import pxssh
import getpass
import time


try:
    s = pxssh.pxssh()



    hostname = '74.207.252.20'
    username = 'dmedakovic'
    password = 'medakovic'
    
    s.login(hostname, username, password)
   

    name = "share_shopping"

    s.sendline(f'cd {name}/handleliste')
    s.prompt()
    print(s.before)
    

    s.sendline('python3 manage.py runserver 0.0.0.0:8000')
    s.prompt()
    print(s.before)

    s.logout()


except pxssh.ExceptionPxssh as e:
    print("pxssh failed on login.")
    print(e)
