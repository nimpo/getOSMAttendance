#!/usr/bin/env perl
# This is a simple CGI script to help getOSMAttendance: getAttendance.py
# If you wish to use this, pop it in your website and give it +ExecCGI in your 
# Apache config or equivilent. It should be configured to execute when the 
# browser lands on the Redirect URL specified in your OSM app.

print "Content-type: text/html\r\n\r\n";

print <<EOF;
<!DOCTYPE html>
<html>
  <head>
    <title>You authorised the OSM app</title>
    <script>
function addURLToClipboard() {
  var txt = document.getElementById("url");
  txt.select();
  navigator.clipboard.writeText(txt.value);
}
    </script>
  </head>
  <body>
    <h1>You authorised the OSM app</h1>
    <p>The OAuth2 process now requires you to pass it back some data.</p>
    <p>This could be the whole URL, you can copy that from the address bar of your browser but here it is for your convenience:</p>
    <table width="100%">
      <tr><td><textarea rows="8" id="url" style="width:100%; word-break: break-all;">https://$ENV{'SERVER_NAME'}$ENV{'REQUEST_URI'}</textarea></td></tr>
      <tr><td align="right"><button onclick="addURLToClipboard()">Copy text</button></td></tr>
    </table>
  </body>
</html>
EOF

