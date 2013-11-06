#!/usr/bin/evn python
#*-* encoding:utf-8 -*-
#Filename:ssh.py
#自动登录服务器，实现服务器巡检工作
import os
import sys
import paramiko

#设置一下字符编码
reload(sys)

#使用public key的登录服务器，将巡检结果输出到特定的目录中
def login_by_pubkey(serverHost,serverPort,userName,keyFile):
    known_host = "/home/triompha/.ssh/known_hosts"
    ssh = paramiko.SSHClient();
    ssh.load_system_host_keys(known_host)
    #设置默认接收主机信任的策略，但是可能报告“不信任主机的”异常
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print 'Connectting host %s......' % serverHost
    ssh.connect(serverHost,serverPort,username = userName)
    print 'Connect host %s sucess' % serverHost

    fname = '/home/triompha/result_%s' % serverHost
    f = file(fname,'w')
    #执行系统命令，获取输出
    stdin, stdout, stderr = ssh.exec_command('df -h')
    #print stdout.readlines()
    f.write('step1:check disk:\n')
    for line in stdout.readlines():
        if len(line) > 0:
            print line
            f.write(line)

    vmstat_stdin,vmstat_stdout,vmstat_stderr = ssh.exec_command('vmstat 2 10')
    f.write('step2:check system:\n')
    for line in vmstat_stdout.readlines():
        if len(line) > 0:
            f.write(line)

    process_stdin,process_stdout,process_stderr = ssh.exec_command('ps -aux | grep java | head -n 10')
    f.write('step3:check process:\n')
    for line in process_stdout.readlines():
        if len(line) > 0:
            f.write(line)

    #关闭文件和ssh连接
    f.close()
    ssh.close()
    print 'say bye to host %s' % serverHost

    #生成截图文件(采用Java实现，需要调用本地的Java文件,依赖了commons-io.jar)
    print 'generate image file of %s' % serverHost
    try:
        java_cmd = '/usr/bin/env java -cp $CLASSPATH:/home/triompha/.m2/repository/commons-io/commons-io/1.4/commons-io-1.4.jar:/home/triompha/workspace/testpy/img.jar com.umessage.datareport.util.CeateCheckPic %s' % fname
        os.system(java_cmd)
    except Exception, e:
        print 'error when generate image file of %s : %s' % (serverHost,e)
    finally:
        print '===generate image file of %s over===' % serverHost

def login_by_prikey():
    pass

if __name__ == '__main__':
    #如果有多个服务器，这个列表中需要配置多条这种配置,实际使用中请将 ip,port,username,public key path替换下面的变量
    ips = ['10.22.10.129,22,root,#pubkey_path#']

    for ip in ips:
        host,port,user,path = ip.split(',')

        print '==========start %s============' % host
        login_by_pubkey(host,int(port),user,path)
        print '>>>>>>>>>>end %s<<<<<<<<<<<<<<' % host

