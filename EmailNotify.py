#!/usr/bin/python
 
# Import smtplib for the actual sending function
import smtplib
 
# For guessing MIME type
import mimetypes
 
# Import the email modules we'll need
import email
import email.mime.application
 
#Import sys to deal with command line arguments
import sys

def send_mail(source, password, destination, subject, message):
 
	# Create a text/plain message
	msg = email.mime.Multipart.MIMEMultipart()
	msg['Subject'] = subject
	msg['From'] = source
	msg['To'] = destination
 
	# The main body is just another attachment
	body = email.mime.Text.MIMEText(message)
	msg.attach(body)
 
	# send via Gmail server
	# NOTE: my ISP, Centurylink, seems to be automatically rewriting
	# port 25 packets to be port 587 and it is trashing port 587 packets.
	# So, I use the default port 25, but I authenticate.
	s = smtplib.SMTP('smtp.gmail.com:587')
	s.starttls()
	s.login(source,password)
	s.sendmail(source,[destination], msg.as_string())
	s.quit()
