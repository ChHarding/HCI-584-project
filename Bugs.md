Bug sheet

6/17
1. To fix: EventHandler class, function clickOnDate: fix "now"(startMin) to be date clicked starting from 0:00?
6/20
Bug 1 fixed.

6/21
2. close The pop-up infoWindow will automatically exit the running program, which is not expected
3. close the main window will not close the infoWindow,and the program still runs
4. when the pop-up info window shows up, I can still use the main window to look up dates, when it shouldn’t, the pop-up window should have the priority, and the main window should be blocked at this time.

Bugs 2,3,4 fixed by adding features to the popup window(made it frameless and stay on top), hide when send button is clicked.git 

5. Gmail API won't work with credentials and tokens. May try another method to use GoogleCalendar API and use another email address to "insert events", thus creating an event and send an invite to admin for review.
Will call this method2 and work in another branch. 