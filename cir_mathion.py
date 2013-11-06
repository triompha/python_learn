#!/usr/bin/evn python
#*-* encoding:utf-8 -*-
#Filename:ssh.py
#自动登录服务器，实现服务器巡检工作
import sys
import paramiko
import smtplib
import datetime
reload(sys)




def send_mail(message):
    try:
        handle = smtplib.SMTP('smtp.163.com', 25)
        handle.login('memcached_warning@163.com', 'memcached123456')
        handle.sendmail('memcached_warning@163.com','zhiyongzhao@sohu-inc.com', 'Subject:播放列表每日循检\r\n\n'+message.read())
        handle.close()
        message.close()
        return 1
    except Exception, e:
        print e
        return 0

#使用public key的登录服务器，将巡检结果输出到特定的目录中
def login_by_pubkey(serverHost,serverPort,userName,keyFile):
    known_host = "/home/triompha/.ssh/known_hosts"
    ssh = paramiko.SSHClient();
    ssh.load_system_host_keys(known_host)
    #设置默认接收主机信任的策略，但是可能报告“不信任主机的”异常
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    ssh.connect(serverHost,serverPort,username = userName)
    
    fname = '/home/triompha/cir_result/result_%s_%s' % (serverHost,datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
    f = file(fname,'w')
     
    f.write('%s information..............\n' % serverHost)
    
    f.write('disk\n')
    write_output(f, ssh.exec_command('df -h')[1])
    f.write('.............................................\n')
    
    f.write('Memory\n')
    write_output(f, ssh.exec_command('free -g')[1])
    f.write('.............................................\n')
    
    f.write('Top\n')
    write_output(f, ssh.exec_command('vmstat 2 10')[1])
    f.write('.............................................\n')
    
    f.write('Resin Tail\n')
    write_output(f, ssh.exec_command('tail /usr/local/resin/log/hot-vis-web.log')[1])
    f.write('.............................................\n')
    
    f.write('Resin Exception\n')
    write_output(f, ssh.exec_command('cat /usr/local/resin/log/hot-vis-web.log /usr/local/resin/log/stdout.log|grep Exception')[1])
    f.write('.............................................\n')
    
    f.write('nginx Error\n')
    stdin, stdout, stderr = ssh.exec_command('cat /usr/local/nginx/logs/error.log /usr/local/nginx/logs/error.2013`date+\'%m%d\'* |grep \'10.10.52.112\|10.10.52.113\|10.11.132.190\|10.11.132.216\'')
    write_output(f, stdout)
    f.write('.............................................\n')
    
    #关闭文件和ssh连接
    f.close()
    ssh.close()
    print 'say bye to host %s' % serverHost

    #发送email邮件
    send_mail(open(fname));

def write_output(fi, lines):
    for line in lines:
        if len(line)>0:
            fi.write(line)
    

if __name__ == '__main__':
    #如果有多个服务器，这个列表中需要配置多条这种配置,实际使用中请将 ip,port,username,public key path替换下面的变量
    ips = ['10.10.52.112,22,root,#pubkey_path#','10.10.52.113,22,root,#pubkey_path#','10.11.132.190,22,root,#pubkey_path#','10.11.132.216,22,root,#pubkey_path#']

    for ip in ips:
        host,port,user,path = ip.split(',')

        print '==========start %s============' % host
        login_by_pubkey(host,int(port),user,path)
        print '>>>>>>>>>>end %s<<<<<<<<<<<<<<' % host

