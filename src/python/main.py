from pyutils import Logger
from datetime import date, datetime, timedelta
import smtplib
import base64
import ssl
import json
import os

# Check for log file
if os.path.exists("config.json"):
    with open("config.json", "r") as c:
        config = json.load(c)
else:
    print("Failed to find config file. Using defaults.")

def send_email(mailfrom, mailto, server, message, subject=None, mailfrompwd = None, tlsRequired = False): 
    # Create out subject for email
    if subject != None:
        message = "Subject: %s\n\n%s\n\n" % (subject, message)
    server = smtplib.SMTP(server, 587)
    server.ehlo()
    server.starttls(context=ssl.create_default_context())
    if mailfrompwd != None:
        server.login(mailfrom, mailfrompwd)
    server.sendmail(mailfrom, mailto, message)
    server.quit()
  
logfile = "logs\\" + str(date.today()) + ".log"

logger = Logger.Logger(logfile)
slowcount = 0
totaltime = 0
totalcount = 0
slowentries = {}
for file in config["logfiles"]: 
    file = file.replace("%y", str(date.today().strftime("%y"))).replace("%m", str(date.today().strftime("%m"))).replace("%d", str(date.today().strftime("%d")))
    with open(file, "r") as f:
        eof = False
        while not eof:
            currline = f.readline()
            if not currline:
                eof = True
                break
        
            # If the start of the line starts with a '#' should be ignored, it's a comment and won't have right amount of fields
            if currline[0] == "#":
                continue

            entry = currline.split()

            # If the log time is older than the last hour
            if config["maxMinAgo"]:
                if datetime.strptime(entry[1], "%H:%M:%S").time() < (datetime.now() + timedelta(minutes=-config["maxMinAgo"])).time():
                    continue

            restime = float(entry[14]) / 1000
            # Response times over 10 get an email sent straight away
            if restime > config["alertResponseTimeGT"]:
                slowcount += 1
                message = "Date: %s %s\nMethod: %s\nURI: %s\nSiteID: %s\nSource IP: %s\nUsername: %s\nStatus: %d\nTime Taken: %.2f\n" % (
                    entry[0], # Date
                    entry[1], # Time
                    entry[3], # Method
                    entry[4], # URI
                    entry[5], # Params
                    entry[8], # Source IP
                    entry[7], # Username
                    int(entry[11]), # Status
                    float(entry[14]) / 1000, # Time Taken
                )
                if config["email"]["send"]:
                    subject = "Response Longer Than 20 Seconds! (Took %.2fs)" % (float(entry[14]) / 1000)
                    smtp.send_email(config["email"]["from"],
                        config["email"]["from"],
                        config["email"]["smtpAddr"],
                        message,
                        subject=subject, 
                        tlsRequired=config["email"]["tlsRequired"],
                        mailfrompwd=config["email"]["password"]
                    )

            # If response time is greater than 5 increase total count found and log result to file
            message = "Date: %s %s\nMethod: %s\nURI: %s\Params: %s\nSource IP: %s\nUsername: %s\nStatus: %d\nTime Taken: %.2f\n" % (
                entry[0], # Date
                entry[1], # Time
                entry[3], # Method
                entry[4], # URI
                entry[5], # SiteID 
                entry[8], # Source IP
                entry[7], # Username
                int(entry[11]), # Status
                float(entry[14]) / 1000, # Time Taken
            )
            totaltime += restime
            totalcount += 1
            if restime > 5:
                slowcount += 1
                if entry[4] not in slowentires:
                    slowentires[entry[4]] = 0
                slowentires[entry[4]] += 1
                slowentries.append(message)
                logger.info(message)


if totaltime > 1 and totalcount > 0: # Prevent div by zero 
    avg = totaltime / totalcount
else: 
    avg = 0

if slowcount > 5:
    message = "The average response time is %ss\n\n" % avg 
    for entry in slowentries:
        message += entry + "\n-----------------------------------------------------------------\n"
    if config["email"]["send"]:
        subject = "More than 5 requests took longer than 5 seconds to resolve"
        smtp.send_email(config["email"]["from"],
            config["email"]["from"],
            config["email"]["smtpAddr"],
            message,
            subject=subject, 
            tlsRequired=config["email"]["tlsRequired"],
            mailfrompwd=config["email"]["password"]
        )

