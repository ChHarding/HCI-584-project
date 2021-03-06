"""This is the class that Handles all the GUI events(button pressed). It handles users actions on GUI. """

# -----------------------------------------------------------------------------------------------------------------------
# Name:       EventHandler.py
# Purpose:    This class handles the GUI events, it handles user actions on GUI.
# Author:     Yiding Han
# Created:    6/12/2020
# TODO:       Add function body
# Note:       Handles GUI events and interacts with google calendar API directly
# -----------------------------------------------------------------------------------------------------------------------
from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dateutil import tz
from PySide2.QtWidgets import QApplication, QWidget, QDialog, QPushButton, QCalendarWidget,QListWidget, QPlainTextEdit

from apiclient import errors
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes



class EventHandler(object):

    def __init__(self, calUI):
        self.calUI = calUI
        self.user_info = ''
        self.user_name = ''
        self.user_email = ''
        self.user_selection = ''

        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('tokenCal.pickle'):
            with open('tokenCal.pickle', 'rb') as token:
                creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
            with open('tokenCal.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    #when book button is clicked
    def bookPushButton_cliked(self):
        self.calUI.showInfoDialog()


    #when book button is clicked
    #need to fill in the body
    def refreshPushButton_clicked(self):
        print("Page is refreshed")

    def sendPushButton_clicked(self):
        #enable main window
        self.calUI.setEnabled(True)
        #hide popup window
        self.calUI.infoDialog.hide()
        self.getUserInfo()
        message = self.CreateMessage(self.user_email, 'yidingh@iastate.edu', self.user_name, self.user_info)
        #self.SendMessage(self.gmail_service_ID(),self.user_email,message)


    def cancelPushButton_clicked(self):
        #hide popup window
        self.calUI.infoDialog.hide()
        #enable main window
        self.calUI.setEnabled(True)

    #This function is called when any date on the GUI calendar is clicked
    #it will record the date that is selected,
    #and pull calendar data from Google calendar account using Dr's calendarID and credentials,
    #then print out and return the events list(availablity)
    def clickOnDate(self):
        self.calUI.QListWidget.clear()
        events_list = []
        selected_date = self.calUI.calWidget.selectedDate()

        now_time = datetime.datetime.now()
        # if selected_date is today, show events from now to 11:59pm today
        if (now_time.year == selected_date.year() and now_time.month == selected_date.month()
                and now_time.day == selected_date.day()):
            start_time = now_time
        # else, show events from 0:00am to 11:59pm today
        elif (selected_date.year() >= now_time.year and selected_date.month() >= now_time.month
              and selected_date.day() > now_time.day):
            start_time = datetime.datetime(selected_date.year() , selected_date.month(), selected_date.day(), 0, 0, 1)
        else:
            # Selected a previous date, print error message, reset list
            self.calUI.QListWidget.addItem("Invalid date, please try again!")
            print("Invalid date, please try again!")
            return events_list
        #no matter what, end_time is 23:59:59 of selected_date
        end_time = datetime.datetime(selected_date.year(), selected_date.month(), selected_date.day(), 23, 59, 59)

        #print out title for the results
        title = "Availabilities for "+ str(selected_date.month())+ "/"+ str(selected_date.day())+ "/"+ str(selected_date.year())
        print(title)

        tzinfo = tz.gettz('America/Los_Angeles')
        start_time = start_time.astimezone(tzinfo)
        end_time = end_time.astimezone(tzinfo)

        #call service.events().list to set up calendar ID and start and end time
        events_result = self.service.events().list(
            calendarId='iastate.edu_0s2c32mjtkthhlefe3le63lgms@group.calendar.google.com',
            timeMin=start_time.isoformat(), timeMax=end_time.isoformat(),
            maxResults=10, singleEvents=True, orderBy='startTime').execute()

        #store all valid events in a list
        events = events_result.get('items', [])

        #check if events list is empty, print No availability found if is empty.
        if not events:
            self.calUI.QListWidget.addItem('No availability found.')
            print('No availability found.')
            return
        #if events list is not empty, for every event in the list, get its'dateTime' and 'summary' in the dictionary list
        self.calUI.QListWidget.addItem(title)
        for event in events:
            start = event['start'].get('dateTime')
            s = start +' '+ event['summary']
            #append all results to events_list and print it
            events_list.append(s)
            #print(s)
            self.calUI.QListWidget.addItem(s)
        return events_list


    def getUserInfo(self):
        select_widget = self.calUI.QListWidget
        array1= select_widget.selectedItems()
        self.user_info += array1[0].text()
        self.user_name = self.calUI.infoDialog.findChild(QPlainTextEdit, 'nameTextEdit').toPlainText()
        self.user_info = self.user_info + '\n' + self.user_name
        self.user_email = self.calUI.infoDialog.findChild(QPlainTextEdit, 'emailTextEdit').toPlainText()
        self.user_info = self.user_info + '\n' + self.user_email
        self.user_reason = self.calUI.infoDialog.findChild(QPlainTextEdit, 'reasonTextEdit').toPlainText()
        self.user_info = self.user_info + '\n' + self.user_reason
        print(self.user_info)


    def CreateMessage(self, sender, to, subject, message_text):
        """Create a message for an email.

        Args:
          sender: Email address of the sender.
          to: Email address of the receiver.
          subject: The subject of the email message.
          message_text: The text of the email message.

        Returns:
          An object containing a base64url encoded email object.
        """
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    def SendMessage(self, service, user_id, message):
        try:
            message = service.users().messages().send(userId=user_id, body=message).execute()

            print('Message Id: %s' % message['id'])
            return message
        except ValueError:
            print("An error occurred")

    def gmail_service_ID(self):
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('tokenGmail.pickle'):
            with open('tokenGmail.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'gmailCredential.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('tokenGmail.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials=creds)
        return service