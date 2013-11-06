# encoding=utf-8
import sys 
import smtplib
import poplib

def send_mail():
    try:
        handle = smtplib.SMTP('smtp.163.com', 25)
        handle.login('memcached_warning@163.com', 'memcached123456')
        msg = 'Subject:hello\r\n\nContent:sdfsdf'
        handle.sendmail('memcached_warning@163.com','zhiyongzhao@sohu-inc.com', msg)
        handle.close()
        return 1
    except Exception, e:
        print e
        return 0

def accpet_mail():
    try:
        p = poplib.POP3('pop.163.com')
        p.user('memcached_warning@163.com')
        p.pass_('memcached123456')
        ret = p.stat()  # 返回一个元组:(邮件数,邮件尺寸)
        print ret
    except poplib.error_proto, e:
        print "Login failed:", e
        sys.exit(1)


if __name__ == "__main__":
    send_mail()
    accpet_mail()
