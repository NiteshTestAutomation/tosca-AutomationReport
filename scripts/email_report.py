import smtplib
from email.message import EmailMessage

from scripts.generate_report import OUTPUT_HTML

msg = EmailMessage()
msg['Subject'] = 'Tosca Automation Report'
msg['From'] = 'niteshbadge1505@gmail.com'
msg['To'] = 'niteshtestautomation@gmail.com'


msg.set_content("Attached Tosca execution report.")

with open(OUTPUT_HTML, 'rb') as f:
    msg.add_attachment(f.read(),
                       maintype='text',
                       subtype='html',
                       filename='Tosca_Report.html')

with smtplib.SMTP('smtp.server.com', 587) as s:
    s.starttls()
    s.login('user','password')
    s.send_message(msg)