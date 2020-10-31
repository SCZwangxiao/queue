"""
Referece code:
————————————————
https://blog.csdn.net/leviopku/article/details/102958166
https://blog.csdn.net/metheir/article/details/86748852
"""
#### Log for new features
"""

"""
import os
import sys
import time
import datetime
import argparse
import smtplib
import subprocess
import logging
import traceback
from email.mime.text import MIMEText

import pynvml
import numpy as np

from user import run_command
from user import COMPUTER_NAME


def send_mail(mailtype, extra_subject=None, extra_content=None, extra_dict=None):
    """
    content = MIMEText(mail_content, 'plain', 'utf-8') # 第一个参数：邮件的内容；第二个参数：邮件内容的格式，普通的文本，可以使用:plain,如果想使内容美观，可以使用:html；第三个参数：设置内容的编码，这里设置为:utf-8
    reveivers = "1216740594@qq.com"
    content['To'] = reveivers # 设置邮件的接收者，多个接收者之间用逗号隔开
    content['From'] = str("ptilopsis1998@163.com") # 邮件的发送者,最好写成str("这里填发送者")，不然可能会出现乱码
    """
    reveivers = "1216740594@qq.com"
    
    mail_content = COMPUTER_NAME + ':'
    if mailtype == 'failed':
        mail_content = mail_content + "程序出错！捕捉到以下错误：\n" + extra_content
        content = MIMEText(mail_content, 'plain', 'utf-8')
        content['Subject'] = "警告！iLearn服务器程序出错"
    elif mailtype == 'report':
        mail_content = mail_content + "报告内容如下:\n"
        if extra_content:
            mail_content = mail_content + extra_content
        if extra_dict:
            for key, value in  extra_dict.items():
                mail_content + '\n' + str(key) + ':' + str(value)
        content = MIMEText(mail_content, 'plain', 'utf-8')
        content['Subject'] = "报告：" + extra_subject
    elif mailtype == 'test':
        mail_content = mail_content + "正在适应dell-PowerEdge-T630环境...\n"
        content = MIMEText(mail_content, 'plain', 'utf-8')
        content['Subject'] = "白面鸮发来的测试"
    
    content['To'] = reveivers # 设置邮件的接收者，多个接收者之间用逗号隔开
    content['From'] = str("ptilopsis1998@163.com") # 邮件的发送者,最好写成str("这里填发送者")，不然可能会出现乱码
    try:
        ##############使用qq邮箱的时候，记得要去开启你的qq邮箱的smtp服务；##############
        # 方法：
        # 1）登录到你的qq邮箱；
        # 2）找到首页顶部的【设置】并点击；
        # 3）找到【账户】这个选项卡并点击，然后在页面中找到“SMTP”相关字样，找到【开启】的超链接，点击后会告诉你开启方法（需要发个短信），然后按照指示操作，最终会给你一个密码，这个密码可以用于在代码中当作邮箱密码
        # 注意!!!:163邮箱之类的不知道要不要这些操作，如果是163邮箱你可以忽略此步骤
        ###########################################################################
        smtp_server = smtplib.SMTP_SSL("smtp.163.com", 465) # 第一个参数：smtp服务地址（你发送邮件所使用的邮箱的smtp地址，在网上可以查到，比如qq邮箱为smtp.qq.com） 第二个参数：对应smtp服务地址的端口号
        smtp_server.login("ptilopsis1998@163.com", "CHXSLTPWDIHKLXZA") # 第一个参数：发送者的邮箱账号 第二个参数：对应邮箱账号的密码
        #################################
 
        smtp_server.sendmail("ptilopsis1998@163.com", ["1216740594@qq.com"], content.as_string()) # 第一个参数：发送者的邮箱账号；第二个参数是个列表类型，每个元素为一个接收者；第三个参数：邮件内容
        smtp_server.quit() # 发送完成后加上这个函数调用，类似于open文件后要跟一个close文件一样
        logging.info('E-mail sent!')
    except Exception as e:
        print(str(e))

####################### Core Codes ########################## 
def avg_gpu_info(measure_duration, print_info=False):
    """
    Input:
        measure_duration: int
    Output:
        avg_free_memory: numpy.array[int], len=gpu_count
        avg_gpu_util: numpy.array[int], len=gpu_count
    """
    # Get average gpu status
    pynvml.nvmlInit()     #初始化
    gpu_count = pynvml.nvmlDeviceGetCount()
    handles = [pynvml.nvmlDeviceGetHandleByIndex(i) for i in range(gpu_count)]
    avg_free_memory = [0.0] * gpu_count
    avg_gpu_util = [0.0] * gpu_count
    for _ in range(int(measure_duration)):
        for id, handle in enumerate(handles):
            avg_free_memory[id] = avg_free_memory[id] + pynvml.nvmlDeviceGetMemoryInfo(handle).free/1e6
            avg_gpu_util[id] = avg_gpu_util[id] + pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
            
        time.sleep(1)
    avg_free_memory = np.array([int(memory/measure_duration) for memory in avg_free_memory])
    avg_gpu_util = np.array([int(power/measure_duration) for power in avg_gpu_util])
    if print_info:
        present_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info(present_time)
        for gpu_id in range(gpu_count):
            gpu_info = 'GPU%d: gpu util:%d%% | free memory:%dMiB' % (gpu_id, avg_gpu_util[gpu_id], avg_free_memory[gpu_id])
            logging.info(gpu_info)
    return avg_free_memory, avg_gpu_util
 
def queue_protocol(args):
    free_gpu_id = None
    free_gpu_info = ""
    # monitor and judge condition
    while True:
        # monitor
        avg_free_memory, avg_gpu_util = avg_gpu_info(args.measure_duration, print_info=True)
        # judge condition
        gpu_available_uitl = avg_gpu_util <= args.max_util
        gpu_available_mem = avg_free_memory >= args.min_memory
        gpu_available = gpu_available_uitl * gpu_available_mem
        free_gpu_id = np.argwhere(gpu_available==True)
        num_gpu_available = len(free_gpu_id)
        if num_gpu_available >= args.min_gpu:
            logging.info('>>>>>>>>>>>>>>>>>>>>Condition satisfied, command initiated:<<<<<<<<<<<<<<<<<<')
            for gpu_id in free_gpu_id:
                free_gpu_info = free_gpu_info + 'GPU%d: gpu util:%d%% | free memory:%dMiB\n' % (gpu_id, avg_gpu_util[gpu_id], avg_free_memory[gpu_id])
            break
        else:
            logging.info('<<<<<<<<<<<<<<<<<<<<<<<<<<<<Condition not satisfied>>>>>>>>>>>>>>>>>>>>>>>>>>')
            time.sleep(args.monitor_interval)
    
    # run command
    send_mail(mailtype='report', extra_subject="恭喜，服务器空闲！正在提交程序... ...", extra_content="白面鸮监测到iLearn服务器空闲:\n" + free_gpu_info)
    logging.info('>>>>>>>Waitng for the task<<<<<<<')
    return_code, task_out, task_err = run_command(free_gpu_id, avg_free_memory, avg_gpu_util)

    return return_code, task_out, task_err


def argument_parser(epilog=None):
    parser = argparse.ArgumentParser()

    parser.add_argument("--monitor-interval", type=int, default=60, help="interval of checking gpu information (sec)")
<<<<<<< HEAD
    parser.add_argument("--measure-duration", type=int, default=10, help="duration of time-averaged gpu information (sec)")
    parser.add_argument("--allow-retry", type=bool, default=False, help="Whether to retry when error occurred")
    parser.add_argument("--max-retry", type=int, default=1, help="maximun retry of the command")
=======
    parser.add_argument("--measure-duration", type=int, default=5, help="duration of time-averaged gpu information (sec)")
    parser.add_argument("--allow-retry", action="store_false", help="Whether to retry when error occurred")
    parser.add_argument("--max-retry", type=int, default=10, help="maximun retry of the command")
>>>>>>> c3fd59f482967299b142fdd0147bb62ce392e304

    parser.add_argument("--min-memory", type=int, default=6000, help="minimum gpu free memory of a gpu (MB)")
    parser.add_argument("--max-util", type=int, default=80, help="maximum gpu utilization rate of a gpu (%)")
    parser.add_argument("--min-gpu", type=int, default=1, help="minimun gpu number that satisfy condition")
    
    #parser.add_argument("--eval-only", action="store_true", help="perform evaluation only")

    return parser


if __name__ == '__main__':
    args = argument_parser().parse_args()
    #Initialization
    logging.basicConfig(level=logging.INFO,
                        filename='./{}_queue.log'.format(datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')),
                        filemode='a',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.info("PID:%d" % os.getpid())
    print("Command Line Args:\n", args)
    exception_list = {}
    total_retry = 0
    #Queue loop
    while True:
        try:
            return_code, out, err = queue_protocol(args)
            if return_code is not 0: # If failed, send report and queue again
                print('>>>>>>>>>>>>>>>>>>>>Task error occured:<<<<<<<<<<<<<<<<<<')
                logging.error(err)
                send_mail(mailtype='failed', extra_content=err)
                if not args.allow_retry:
                    exit(0)
                elif total_retry >= args.max_retry:
                    logging.critical('程序尝试次数超过%d次，自动终止' % args.max_retry)
                    send_mail(mailtype='report', extra_subject='程序尝试次数超过%d次，自动终止' % args.max_retry, extra_dict = exception_list)
                    exit(1)
            else:   # If success, send report and exit
                send_mail(mailtype='report', extra_subject=' 任务运行结束', extra_content=out)
                exit(0)
        except Exception as e:  # Handle unexpected error
            print('>>>>>>>>>>>>>>>>>>>>Exception<<<<<<<<<<<<<<<<<<')
            traceback.print_exc()
            logging.error(str(e))
            total_exception = total_retry + 1
            if e in exception_list:
                exception_list[e] = exception_list[e] + 1
            else:
                exception_list[e] = 1
                send_mail(mailtype='failed', extra_content="Unknown exception:\n"+str(e))
            exit(0)
        
        total_retry += 1
        time.sleep(args.monitor_interval)
