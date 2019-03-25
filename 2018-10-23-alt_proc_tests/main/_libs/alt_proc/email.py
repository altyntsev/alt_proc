from __future__ import absolute_import
import smtplib
from email.mime.text import MIMEText

def send( email, subject, text ):
    
    print('Sending email to %s with subject: %s' % (email, subject))
    
    text = [s.strip() for s in text.split('\n')]
    text = '\n'.join(text)
    
    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = 'alt_proc@scanex.ru'
    msg['To'] = email
    
    s = smtplib.SMTP('192.168.5.167')
    s.sendmail('alt_proc@scanex.ru', [email], msg.as_string())
    s.quit()    