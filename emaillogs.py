#!/usr/bin/env python3
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

# Function to read the contents of a file
def get_file_contents(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to attach a file to the email
def attach_file(msg, file_path):
    with open(file_path, 'rb') as file:
        part = MIMEApplication(file.read(), Name=os.path.basename(file_path))
    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
    msg.attach(part)

# Define the command to run and the log file path
command = "btcli w list"
log_file = "/./.pm2/logs/MINER-out.log"
search_string = "| Stake: "

# Run the command and capture its output, save to a file
process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
btcli_output, btcli_error = process.communicate()
btcli_output_filename = '/workspace/btcli_output.txt'
with open(btcli_output_filename, 'w') as f:
    f.write(btcli_output.decode('utf-8'))

# Read the last matching line from the log file, save to a file
newest_entry = None
newest_entry_filename = '/workspace/newest_log_entry.txt'
with open(log_file, 'r') as file, open(newest_entry_filename, 'w') as outfile:
    for line in reversed(list(file.readlines())):
        if search_string in line:
            newest_entry = line.strip()
            outfile.write(newest_entry)
            break

# Prepare the email
username = '.'
password = '.'
sender_email = '.'
receiver_email = '.'
subject = "Log File Entry - ."

# Create the email message
msg = MIMEMultipart()
msg['Subject'] = subject
msg['From'] = sender_email
msg['To'] = receiver_email

# Include the contents in the body of the email
body = "Please find the command output and the newest log entry attached.\n\n"
body += "----- btcli output -----\n" + get_file_contents(btcli_output_filename) + "\n"
body += "----- Newest log entry -----\n" + (get_file_contents(newest_entry_filename) if newest_entry else "No matching log entry found.")
msg.attach(MIMEText(body, 'plain'))

# Attach the files to the email
attach_file(msg, btcli_output_filename)
attach_file(msg, newest_entry_filename)

# Send the email
with smtplib.SMTP('mail.smtp2go.com', 2525) as server:
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())

print("Email sent successfully!")
