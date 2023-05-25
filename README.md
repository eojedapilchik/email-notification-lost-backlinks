# email-notification-lost-backlinks

To make the google API work you need to create a project in the google developer console and enable the google drive API.   
Then you need to create a service account and download the credentials file.  
You can find more information here: https://developers.google.com/drive/api/v3/quickstart/python   

You need to create a file called `credentials.json` in the root directory of this project and paste the content of the downloaded file into it.  
You need to open the app in a desktop to authenticate the app for the first time, once you have done that you can run the app on a server.  
Remember to copy the `token.json` and `credentials.json` file to the server as well.  