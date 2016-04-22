#coding:utf-8
_author = 'frokaikan'
'''
thx:frokaikan and liaoxuefeng

http://www.liaoxuefeng.com/
别人那里抄的 廖雪峰官网有写 所以我就不写注释了
'''
from config import Title
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr,parseaddr
from email import encoders
import smtplib


class Mail:
    '''
    Mail=mail('****@**.com','****@**.com','******','smtp.**.com',25)
    Mail.make_message('123456')
    Mail.send()
    '''
    def __init__(self,To,From='',Password='',SMTPServer='',SMTPPort=25):
        self.from_=From
        self.From='Nevermore <%s>'%From
        self.to=To
        self.To='None <%s>'%To
        self.Password=Password
        self.SMTPServer=SMTPServer
        self.SMTPPort=SMTPPort
    
    def to_list(self):
        return self.to.split(',')

    def _formataddr(self,s):
        name,addr=parseaddr(s)
        return formataddr((Header(name,'utf-8').encode(),addr))
    
    def make_message(self,Content,Type='plain',Subject=Title,Base=None):
        if not Base:
            self.msg=MIMEText(Content,Type,'utf-8')
        else:
            self.msg=MIMEMultipart()
            self.msg.attach(MIMEText(Content,Type,'utf-8'))
            for base in Base.split(','):
                self.Base=MIMEBase('application', 'octet-stream')
                self.Base.add_header('Content-Disposition', 'attachment', filename=base)
                self.Base.add_header('Content-ID', '<0>')
                self.Base.add_header('X-Attachment-Id', '0')
                with open(base,'rb') as f:
                    self.Base.set_payload(f.read())
                    encoders.encode_base64(self.Base)
                    self.msg.attach(self.Base)
        self.msg['From']=self._formataddr(self.From)
        self.msg['To']=self._formataddr(self.To)
        self.msg['Subject']=Header(Subject,'utf-8').encode()
    
    def send(self):
        if not hasattr(self,'msg'):
            raise RuntimeError('Please Make Message First!')
        server=smtplib.SMTP(self.SMTPServer,self.SMTPPort)
        server.starttls()
        server.login(self.from_,self.Password)
        server.sendmail(self.from_,self.to_list(),self.msg.as_string())
        server.quit()
