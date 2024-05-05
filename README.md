# getOSMAttendance: getAttendence.py
Python script to pull attendance records of members from Online Scout Manager

Online Scout Manager provides a place to keep membership data.

This script was designed to authenticate to the Online Scout Manager site and download attendance data using the undocumented API.

To use this script you will need an API key via the service https://www.onlinescoutmanager.co.uk/main.php
As the service uses XMLHTTPRequests to load most pages via JSON I cannot give you a permalink (AFAIK). 
1. Expand "Settings" (bottom of left pane)
2. Select "My Account Details"
3. From the new menu on the left in the main pane select "Develpoer Tools"
4. Click Create Application button (top right)
  - This will give you a client_id and client_secret: keep these secret; keep these safe
5. Register a *Redirect URL* for your application by clicking on the application name in the "My Applications" tab
6. Put this URL and the application key and secret in a separate *.env* file alongside getAttendence.py
```
OSM_API_KEY=<put key here>
OSM_API_SECRET=<put secret here>
OSM_API_RETURL=<put OAuth2 Callback URI here>
```
# Using the code
Once setup for OAuth2 authentication, to run this
First make sure it's executable
```
chmod u+x getAttendence.py
```
Then just run ```./getAttendence.py``` and follow the instructions. A browser should pop up and ask you to log into OSM. Do this, and pop the redirect url into the terminal window when promped.

# NB
* I use GNU/linux. This code was written and tested on such a device (Ubuntu 22.04 and KDE if you must know). It may (/should) work on Windows and Mac though I haven't tested on those OSes. 
* The code requires a browser for the OAuth2 handshake. 

# Licence
Copyright 2024 Mike Jones, <dr.mike.jones@gmail.com>
AKA Grey Wolf <mike.jones@mansouthscouts.org>
AKA Akela <mike.jones@mansouthscouts.org>
[23rd Manchester (Birch with Fallowfield)]
Scout Membership number: 12114313

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

# Kudos
If you find this useful you can show your gratitude thusly:
* Buy me a coffee: https://buymeacoffee.com/emceearsey
* Donate to 23rd Manchester Scout Group: https://checkout.justgiving.com/c/3118763
