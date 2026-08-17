import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.header import Header
import datetime

sender = 'Grafana_APPCHQ'
password = 'Grafana89'
sender_from = 'Grafana_APPCHQ@app.com.cn'

time1 = datetime.datetime.now().strftime('%Y')
time2 = datetime.datetime.now().strftime('%m')
time3 = datetime.datetime.now().strftime('%d')
time4 = datetime.datetime.now().strftime('%H')

p1 = 'GEHAIFENG@APP.COM.CN'
p2 = 'FENGYUANYUAN@APP.COM.CN' 
p3 = 'OWENYANG@APP.COM.CN'
p4 = 'CAIJIANXI@APP.COM.CN'
p5 = 'ZHUANGJIANFENG@APP.COM.CN'
p6 = 'LUZHENGWEI@APP.COM.CN'
p7 = 'XUYAN_CHQ@APP.COM.CN'
p8 = 'WANGLINGJIE@APP.COM.CN'
p9 = 'YANGYIJUN@APP.COM.CN'
p10 = 'CIT-LEADERS@APP.COM.CN'

receiver = { p1, p2, p3, p4, p5, p6, p7, p8, p9 ,p10 }
#receiver = { p8 }
receiver_to = p1+'; '+p2
#receiver_to = p8
cc_to = p3+'; '+p4+'; '+p5+'; '+p6+'; '+p7+'; '+p8+'; '+p9+'; '+p10
#cc_to = p8

#print(receiver)

#采用related定义内嵌资源的邮件体
message = MIMEMultipart('related')

message['From'] = Header(sender_from, 'utf-8')
message['To'] = Header(receiver_to, 'utf-8')
message['Cc'] = Header(cc_to, 'utf-8')
message['Subject'] = Header(time1+'年'+time2+'月'+time3+'日网络及IT支持系统状态')
msg_content = MIMEMultipart('alternative')
mail_msg = """
<p>各位领导，下午好</p>
<p style="text-indent:2em;">
<font size="4">以下是截止到"""+time1+"年"+time2+"月"+time3+"日"+time4+"""点的网络及支持系统具体状态，网络及各项系统都处于</font><font size="4" style = "color:#228B22;font-weight:bolder">可控</font><font size="4">状态。如需了解更多信息，可以访问如下链接查询(推荐使用Google Chrome 或 Microsoft Edge 浏览器)：http://infra-dashboard.app.com.cn:32000/d/njNLyI54k/network-graphs?orgId=1&refresh=5m</font>
</p>
<p style="text-indent:2em;">
<font size="4">☆此邮件由系统自动发出,请勿直接回复，谢谢。</font>
</p>
<p>
<img src="cid:img1">
</p>
"""
msg_content.attach(MIMEText(mail_msg, 'html', 'utf-8'))
message.attach(msg_content)
with open('/data/smtpweekly.jpg', 'rb') as f:
    img1 = MIMEImage(f.read())

img1.add_header('Content-ID', 'img1')
message.attach(img1)
try:
    smtp = smtplib.SMTP('172.18.3.10', 25)
    smtp.login(sender, password)
    smtp.sendmail(sender, receiver, message.as_string())
    print('邮件已发送！')
except smtplib.SMTPException as e:
    print('出现错误！', e.args[1].decode('gbk'))

