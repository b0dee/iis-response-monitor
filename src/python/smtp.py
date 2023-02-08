import smtplib
import base64
import ssl

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
  
if __name__ == "__main__":
    pass
