# HowCompanyWorks
eine (lustig gemeinte) Umsetzung eines Unternehmens in Python (Queue.PriorityQueue)

Dieser Aufbau ist, so lustig auch gemeint, Grundlage f�r das kommende DoorPi3, das ich nun im dritten Ansatz versuche...

* corridor = zentraler Sammelpunkt aller Object
* employer = Chef, der �ber alles wacht
* employee = Schnittstelle mit Input und Output
* trainee = L�ufer der Nachrichten hin und her transportiert
* crip sheet = Spickzettel auf dem steht, welche Aktion bei welchem Event ausgel�st werden soll

* corridor war schon immer da
* corridor hatte schon immer eine message box
* corridor hatte schon immer ein crep sheet (aber leer)
* corridor hatte schon immer einen employer

* employer stellt trainee an
* employer zeigt trainee corridor
* employer stellt trainee auf den corridor

* employer f�llt event aus und legt diese in den corridor
* trainee sieht event im corridor
* trainee schaut auf crep sheet was bei diesem event zu tun ist -> bekommt list of task und steckt diese tasks in die message box
* trainee befolgt jeden Task und sagt jedem employee das was tun ist und was genau zu tun ist
* employee arbeitet und gibt Ergebnis als Result aus und legt diese in den corridor (bzw. message box)

* neue employee melden sich beim employer
* employee sagt dem employer was sie k�nnen (EmployeeOutput)
* employee sagt dem employer was was sie brauchen (EmployeeInput)
* employer vermerkt das auf zentralem crep sheet
* employee wartet im office / corridor bis er vom trainee angesprochen wird
