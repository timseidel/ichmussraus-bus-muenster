# Ich Muss Hier Raus!
# Analyse des Münsteraner Busnetzwerks.

## How to start:
1. passende tglib binary auswählen, in pytglib.xyz umbenennen und auf die Ordnerebene von app.py kopieren.
3. app.py ausführen mit Python 3.13 ausführen
4. local IP aus Konsole im Browser aufrufen

## Was kann die Flask-App:
Diese Flask-App ermöglicht eine umfassende Analyse des ÖPNV-Netzes in Münster. 
Nutzer können eine Startuhrzeit und eine Ausgangshaltestelle wählen, um die Verbindungen im Stadtgebiet zu betrachten. 
Die Ergebnisse werden auf einer interaktiven Karte visualisiert, die mithilfe eines Farbsystems die Erreichbarkeit der 
einzelnen Haltestellen anzeigt: Grüntöne stehen für schnelle, dunkle Farbtöne für langsamere Verbindungen. 
Durch Anklicken der farbigen Punkte können Nutzer weitere Informationen wie den Namen der Haltestelle 
und die benötigte Fahrzeit abrufen. 
Dies hilft, Schwachstellen im Verkehrsnetz zu identifizieren und bietet wertvolle Einblicke in die aktuellen Planungsstrategien des ÖPNV.


## tglib Compiled Info

- Einfach die richtige für euch aus compiled Ordner in Projektordner kopieren!

### Kompilierte tglib Pakete
pytglib.cpython-313-darwin.so
  -> kompiliert mit gcc14 auf Apple; arm; MacOS 15; Python 3.13

pytglib.cpython-313-darwin_x86.so
  -> kompiliert mit gcc14 auf Intel; MacOS 12.7; Python 3.13

pytglib.cp313-win_amd64.pyd
  -> kompiliert mit MSVCin VS22 auf Intel; Windows 10 Enterprise 22H2; Python 3.13
