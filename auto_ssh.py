from pexpect import pxssh
import getpass
import time

#dmedakovic@74.207.252.20
try:
    s = pxssh.pxssh()

    hostname = '74.207.252.20'
    username = 'dmedakovic'
    password = 'medakovic'
    
    s.login(hostname, username, password)
   

    name = time.time()
    name = str(name)
    ACTOKEN = 'UTfyZCCs4f3H6TZQGjux'

    s.sendline('find -delete')
    s.prompt()
    print(s.before)

    s.sendline(f'git clone https://oauth2:{ACTOKEN}@gitlab.stud.idi.ntnu.no/programvareutvikling-v19/gruppe-3.git {name}')
    s.prompt()
    print(s.before)

    s.sendline(f'cd {name}/handleliste')
    s.prompt()
    print(s.before)
    
    s.sendline('python3 -m pip install django')
    s.prompt()
    print(s.before)

    # s.sendline('python3 manage.py runserver 0.0.0.0:8000')
    # s.prompt()
    # print(s.before)
    aesdojgioj
    
    ogoskafd
    asdjok


    s.logout()
except pxssh.ExceptionPxssh as e:
    print("pxssh failed on login.")
    print(e)

   

    'https://oauth2:UTfyZCCs4f3H6TZQGjux@gitlab.stud.idi.ntnu.no/programvareutvikling-v19/gruppe-3.git'