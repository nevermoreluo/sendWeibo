# -*- coding: utf-8 -*-


from config import User_name,Password,Send_email,To,From,Email_password,Smtpserver,SMTPPort
#from WeiBo import Weibo
from movieFactory import Douban_info,BucketList,NewMovie
from mail import Mail
from fuck_login import *

if __name__ == '__main__':
    new = NewMovie().update()
    session, uid = login(User_name,Password)
    for i in new:
        text = Douban_info(i).info()
        print(text)
        #Weibo(User_name,Password).sendWeibo(text)
        sendWeibo(text,session,uid)
    if Send_email:
      downloads = BucketList().refresh()
      model_t = ''
      for k in downloads:
          model_t += 'Movie: %s\ndown_urls: %s\n\n'%(k,downloads[k])
      if model_t:
          m = Mail(To,From,Email_password,Smtpserver,SMTPPort)
          m.make_message(model_t)
          m.send()
