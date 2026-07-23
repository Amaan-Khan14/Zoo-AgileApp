ZOO SPRINT SIMULATION
=====================

QUICK START
-----------
1. Keep all files in this folder together.
2. Open a terminal / command prompt in this folder.
3. Run:

       python server.py

   (Mac / Linux: use  python3 server.py )

4. Your browser opens automatically at http://localhost:8000

That's it. The board now saves to zoo-data.json in this folder,
automatically, every 2 seconds. Refresh the page as much as you
like - nothing is lost.


LETTING THE TEAM SEE IT
-----------------------
When the server starts it prints a second address, e.g.

       http://192.168.1.7:8000

Anyone on the SAME WIFI can open that on their laptop or phone
and see the same live board. Changes appear within ~4 seconds.
Type your name in the box on the top bar so saves are attributed.


FILES
-----
index.html        the app (all 50 stories are inside it)
server.py         run this
zoo-data.json     created on first run - THIS IS YOUR DATA
backups/          created automatically, last 20 saves


WHAT GETS SAVED
---------------
- Every card's column, owner, sprint and PO verdict
- The velocity worksheet numbers
- Retrospective start / stop / continue
- Both improvement commitments

The timer is deliberately NOT saved - it always starts fresh.


NO PYTHON?
----------
Just double-click index.html. Everything still works, it simply
won't auto-save. Use the "Download JSON" and "Load JSON" buttons
at the top of the page instead - download once at the end of
each sprint.


BETWEEN TWO TEAMS
-----------------
Click "Download JSON" to keep the first team's board,
then click "Reset board" on the Kanban tab before the next team.


TROUBLESHOOTING
---------------
"python is not recognized"
    Install Python from python.org, or try  py server.py

Port 8000 already in use
    Windows:  set PORT=8080 && python server.py
    Mac/Linux: PORT=8080 python3 server.py

Team can't open the wifi address
    Your firewall is blocking it. Allow Python through, or
    fall back to Download/Load JSON.

Harmless "favicon.ico not found" traceback
    Fixed in this version. If you see it, you are running an
    older server.py - replace it with this one.
