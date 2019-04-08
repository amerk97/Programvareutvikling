# ShareShopping README


[![build status](https://gitlab.com/fdroid/fdroidclient/badges/master/build.svg)](https://gitlab.stud.idi.ntnu.no/programvareutvikling-v19/gruppe-3/-/jobs)


## For å komme i gang:
- Last ned Python 3.7.2 fra https://www.python.org/downloads/
- Sjekk at den fungerer ved å skrive "python" i kommandolinjen.
- Last ned package-manageren til python, pip, ved å skrive `curl https://bootst$`
og deretter `python get-pip.py`
- Last ned den nyeste ofisielle versjonen av Django ved å skrive `pip install Django==2.1.5` i kommandolinjen.

## Git:
- Åpne kommandolinjen og naviger til hvor du vil ha filene.
- "git clone https://gitlab.stud.idi.ntnu.no/programvareutvikling-v19/gruppe-3.$
- "git init" inne i mappen hvor filene fra prosjektet ligger.
- Du bør nå ha alle filene og kunne adde, committe, pulle og pushe kode.


## Administrativt:
- For å logge inn på admin siden bruk:
username: superuser
password: superuser

- Sjekk at den fungerer ved å skrive "python" i kommandolinjen.  
- Last ned package-manageren til python, pip, ved å skrive `curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`
    og deretter `python get-pip.py` 
- Last ned den nyeste ofisielle versjonen av Django ved å skrive 
    `pip install Django==2.1.5` i kommandolinjen. 


## Tilgang til serveren: 
- Åpne et nytt terminalvindu.
- Tast inn "ssh dmedakovic@74.207.252.20" (i windows må du laste ned PuTTy som lar deg koble deg til servere over internettet på tilsvarende
- måte. I PuTTy skriver du inn du inn dmedakovic@74.207.252.20 under "hostname" og trykker "open". Resten av prosessen bør være lik).
- Du vil bli spørt om passord (passord: medakovic). 
- Du er nå i "home" mappen til serveren. Gå til "gruppe-3" mappen og deretter til "handleliste" mappen ved å bruke cd og dir/ls kommandoene. 
- Kjør kommandoen "python3 manage.py runserver 0.0.0.0:8000"
- Django serveren kjører nå på IP-adressen til serveren, som er 74.207.252.20:8000.
"

## Kjøre serveren: 
- Kjør filen auto_start.py og vent noen sekunder mens programmet logger inn gjennom ssh og starter serveren. 
- Åpne nettleseren og gå til 74.207.252.20:8000.


