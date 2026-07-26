import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.header import Header
import datetime
from fnmatch import fnmatch, fnmatchcase

sender = 'Grafana_APPCHQ'
password = 'Grafana89'
sender_from = 'BudgetCIT_APPCHQ@app.com.cn'

time1 = datetime.datetime.now().strftime('%Y')
time2 = datetime.datetime.now().strftime('%m')
time3 = datetime.datetime.now().strftime('%d')
time4 = datetime.datetime.now().strftime('%H')

with open('/cit/budgetforreminder', 'r') as file:
    data = file.read()

p1 = 'LIUBIN_CHQ@APP.COM.CN'
p2 = 'MAOJINLONG@APP.COM.CN' 
p3 = 'XUXIHUI@APP.COM.CN'
p4 = 'CAIJIANXI@APP.COM.CN'
p5 = 'ZHUANGJIANFENG@APP.COM.CN'
p6 = 'LUZHENGWEI@APP.COM.CN'
p7 = 'XUYAN_CHQ@APP.COM.CN'
p8 = 'WANGLINGJIE@APP.COM.CN'
p9 = 'YANGYIJUN@APP.COM.CN'
p10 = 'CIT-LEADERS@APP.COM.CN'

receiver = { p1, p2, p3, p5, p8, p9 }
#receiver = { p8 }
receiver_to = p1+'; '+p2+'; '+p3+'; '+p8+'; '+p9
#receiver_to = p8
cc_to = p5
#cc_to = p8

#print(receiver)

#采用related定义内嵌资源的邮件体
message = MIMEMultipart('related')

message['From'] = Header(sender_from, 'utf-8')
message['To'] = Header(receiver_to, 'utf-8')
message['Cc'] = Header(cc_to, 'utf-8')
message['Subject'] = Header(time1+'年'+time2+'月'+time3+'日CIT采购申请发起提醒')
msg_content = MIMEMultipart('alternative')
mail_msg = """
<p>各位领导、同事，上午好：</p>
<p style="text-indent:2em;">
<font size="4">以下是截止到"""+time1+"年"+time2+"月"+time3+"日"+time4+"""点前需要发起采购申请的CIT预算项</font></p>
<p style="text-indent:2em;">
<font size="4">"""+data+"""</font></p>
"""
msg_content.attach(MIMEText(mail_msg, 'html', 'utf-8'))
message.attach(msg_content)

if fnmatch(data, "<br>*<br>*"):
    try:
        smtp = smtplib.SMTP('172.18.3.10', 25)
        smtp.login(sender, password)
        smtp.sendmail(sender, receiver, message.as_string())
        print('邮件已发送！')
    except smtplib.SMTPException as e:
        print('出现错误！', e.args[1].decode('gbk'))
else:
    print('没有预算项需要提醒！')

