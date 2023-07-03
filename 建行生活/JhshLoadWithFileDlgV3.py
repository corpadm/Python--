'''
版本3.0
1、修改程序不合理的地方，尤其是数据表类的定义；
2、修改消息提示杂乱问题；
3、统一输出规范；
4、合理布置例外。

以下是版本2.0新增内容：
1、增加商户明细导入；
2、商户明细为个人金融部提供的Excel表格，必须严格按格式提供；
3、核券明细从新一代“商户权益岗”下载，为zip格式，解压后使用utf-8编码（支持其他编码）。

以下是版本1.0描述
建行生活核券明细数据装载程序
1、包含了图形界面；
2、可受理压缩文件（.zip）、文本文件（各种编码）；
3、检索流水号重复的连续核券记录，合并入库；
4、检索流水号重复的冲正记录，合并入库；
5、数据文件可以重复装载（暂未考虑部分退款问题）；
6、暂未考虑部分退款（部分冲正）问题；
7、暂未考虑商户明细导入问题。
'''
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import time
import sys
import chardet
import pymysql
import zipfile
from pymysql.err import IntegrityError
import pandas as pd
from configparser import ConfigParser
 
class DBUtil:
    # 设置连接参数
    config={
        'host':'数据库服务器IP地址',
        'port':3306,
        'user':'root',
        'passwd':'6611513',
        'db':'logistics',
        #'db':'lgstest',
        'charset':'gbk'
    }
    def __init__(self):
        '''
        获取链接
        获取游标
        '''
        cp=ConfigParser()
        jhshList=cp.read("jhsh.ini")
        mysqlList=cp.items("mysql")
        mysqlDict=dict(mysqlList)
        print(mysqlDict)
        DBUtil.config['host']=mysqlDict['host']
        DBUtil.config['port']=int(mysqlDict['port'])
        DBUtil.config['user']=mysqlDict['user']
        DBUtil.config['passwd']=mysqlDict['passwd']
        DBUtil.config['db']=mysqlDict['db']
        DBUtil.config['charset']=mysqlDict['charset']
        print(DBUtil.config)
                
        self.connt = pymysql.connect(**DBUtil.config)
        self.cursor = self.connt.cursor()
 
    def close(self):
        '''
        关闭链接与游标
        '''
        if self.cursor:
            self.cursor.close()
        if self.connt:
            self.connt.close()
 
 
    def execute_sql(self,sql,*args):
        '''
        可以执行sql语句，用于数据的增加、删除、修改
        '''
        actRecordCount=0
        actRecordCount=self.cursor.execute(sql,args)
        # 提交事务
        self.connt.commit()
        return actRecordCount
 
    def query_one(self,sql,*args):
        '''
        查询一条数据        
        '''
        # 执行SQL
        self.cursor.execute(sql,args)
        # 获取结果
        rs = self.cursor.fetchone()
        # 返回数据
        return rs
 
    def query_all(self,sql,*args):
        '''
        查询所有数据
        '''
        # 执行SQL
        self.cursor.execute(sql,args)
        # 获取结果,并返回数据
        return self.cursor.fetchall()


class DailyRecord :
    def __init__(self,strList):     #列表构造函数
        self.mc_id=strList[0]
        self.sp_id=strList[1]
        self.mc_name=strList[2]
        self.ticket_id=strList[3]
        self.ticket_name=strList[4]
        self.user_id=strList[5]
        self.card_no=strList[6]
        self.get_time=strList[7]
        self.use_flag=strList[8]
        self.use_time=strList[9]
        self.use_order=strList[10]
        self.order_amt=float(strList[11])
        self.reduce_amt=float(strList[12])
        self.pay_type=strList[13]
        self.use_mc_id=strList[14]
        self.use_src_id=strList[15]
        self.ticket_beg_time=strList[16]
        self.ticket_end_time=strList[17]
        self.use_user_id=strList[18]
        self.user_mobile=strList[19]
        self.real_use_amt=float(strList[20])
        self.use_limit=strList[21]
        self.card_bin=strList[22]
        self.is_uionpay=strList[23]
        self.is_settle=strList[24]
        self.settle_amt=float(strList[25])
        self.sp_amt=float(strList[26])
        self.bp_amt=float(strList[27])

    def add(self,otherRecord):      #订单号相同才能相加
        if(self.use_order==otherRecord.use_order):
             self.reduce_amt+=otherRecord.reduce_amt       
             self.real_use_amt+=otherRecord.real_use_amt       
             self.settle_amt+=otherRecord.settle_amt       
             self.sp_amt+=otherRecord.sp_amt       
             self.bp_amt+=otherRecord.bp_amt      
              
    def __str__(self) -> str:
        return (
            f"mc_id:[{self.mc_id}] "
            f"sp_id:[{self.sp_id}] "
            f"mc_name:[{self.mc_name}] "
            f"ticket_id:[{self.ticket_id}] "
            f"ticket_name:[{self.ticket_name}] "
            f"user_id:[{self.user_id}] "
            f"card_no:[{self.card_no}] "
            f"get_time:[{self.get_time}] "
            f"use_flag:[{self.use_flag}] "
            f"use_time:[{self.use_time}] "
            f"use_order:[{self.use_order}] "
            f"order_amt:[{self.order_amt}] "
            f"reduce_amt:[{self.reduce_amt}] "
            f"pay_type:[{self.pay_type}] "
            f"use_mc_id:[{self.use_mc_id}] "
            f"use_src_id:[{self.use_src_id}] "
            f"ticket_beg_time:[{self.ticket_beg_time}] "
            f"ticket_end_time:[{self.ticket_end_time}] "
            f"use_user_id:[{self.use_user_id}] "
            f"user_mobile:[{self.user_mobile}] "
            f"real_use_amt:[{self.real_use_amt}] "
            f"use_limit:[{self.use_limit}] "
            f"card_bin:[{self.card_bin}] "
            f"is_uionpay:[{self.is_uionpay}] "
            f"is_settle:[{self.is_settle}] "
            f"settle_amt:[{self.settle_amt}] "
            f"sp_amt:[{self.sp_amt}] "
            f"bp_amt:[{self.bp_amt}]"
        )
    
class MccRecord :
    '''
    处理要点：
    1、支行取前两位，只能是简称【靖江、泰兴、姜堰、兴化、高港、海陵、新区、药城】
    2、商户编号、门店号、支行、商户名、门店名等字段不能为空值
    3、商户号、门店号不能是科学计数法，必须是字符串格式
    4、任何字段不能出现单引号'、双引号"，必须替换这些符号
    '''
    def __init__(self,strList):     #列表构造函数,入参数组委个金部提供的“建行生活商家商户信息明细表”，从第4行开始为商户数据。
        self.isValid=True           #内容是否合法
        self.bp_name=str(strList[2]).strip()[0:2].encode("GBK",errors='ignore').decode("GBK",errors='ignore')    #支行
        self.b_id=str(strList[3]).strip().encode("GBK",errors='ignore').decode("GBK",errors='ignore')	    #银行机构或网点        
        self.mc_id=str(strList[4]).strip().encode("GBK",errors='ignore').decode("GBK",errors='ignore')	    #商户号        
        self.tm_id=str(strList[5]).strip().encode("GBK",errors='ignore').decode("GBK",errors='ignore')	    #终端号
        self.th_id=str(strList[6]).strip().encode("GBK",errors='ignore').decode("GBK",errors='ignore')	    #特惠号
        self.sp_id=str(strList[13]).strip().encode("GBK",errors='ignore').decode("GBK",errors='ignore')	    #门店号
        self.mc_name=str(strList[7]).strip().encode("GBK",errors='ignore').decode("GBK",errors='ignore')	#商户名
        self.sp_name=str(strList[14]).strip().encode("GBK",errors='ignore').decode("GBK",errors='ignore')	#门店名
        self.b_id=self.dropDot(self.b_id)
        self.mc_id=self.dropDot(self.mc_id)
        self.tm_id=self.dropDot(self.tm_id)
        self.th_id=self.dropDot(self.th_id)
        self.sp_id=self.dropDot(self.sp_id)
        if not (self.mc_id.isdigit() and self.sp_id.isdigit()):
            self.isValid=False
        if len(self.bp_name)*len(self.mc_name)*len(self.sp_name)*len(self.mc_id)*len(self.sp_id)==0:
            self.isValid=False    

    def dropDot(self,str):
        index=str.rfind('.')
        if index == -1 :
            return str
        else :
            #print(f"{str}:{index}:{str[0:index]}")
            return str[0:index]                    

    def __str__(self) -> str:
        return (
            f"bp_name:[{self.bp_name}]"
            f"b_id:[{self.b_id}]"
            f"mc_id:[{self.mc_id}]"
            f"tm_id:[{self.tm_id}]"
            f"th_id:[{self.th_id}]"
            f"sp_id:[{self.sp_id}]"
            f"mc_name:[{self.mc_name}]"
            f"sp_name:[{self.sp_name}]"
        )
    

class TextReader:
    def __init__(self, master):
        #读取配置文件
        try :
            cp=ConfigParser()
            jhshList=cp.read("jhsh.ini")
            mysqlList=cp.items("mysql")
            mysqlDict=dict(mysqlList)
        except Exception as e :
            self.text_box_insert_top(f"缺少数据库配置，请先配置程序所在目录的jhsh.ini，再运行本程序。\n")
            mysqlDict=DBUtil.config
        
        self.master = master
        master.title(f"建行生活核券明细数据导入V3.0:[{mysqlDict['host']}]")
        master.iconbitmap('jhsh.ico')

        # 创建布局
        self.file_label = tk.Label(master, text="文件:")
        self.file_label.grid(row=0, column=0)

        self.file_path = tk.StringVar()
        self.file_entry = tk.Entry(master, textvariable=self.file_path)
        self.file_entry.grid(row=0, column=1,sticky="nsew")
        
        #其他输出文件
        self.file_path_log=''
        self.file_path_data=''
    
        self.browse_button = tk.Button(master, text="...", command=self.browse_file)
        self.browse_button.grid(row=0, column=2)
        
        # #单选按钮
        # self.data_type_radio_value=tk.IntVar()
        # self.data_type_radio_ticket=tk.Radiobutton(self.master,variable=self.data_type_radio_value,text='核券明细',value=0)
        # self.data_type_radio_mcc=tk.Radiobutton(self.master,variable=self.data_type_radio_value,text='商户明细',value=1)
        # self.data_type_radio_ticket.grid(row=1,column=1,sticky='ws')
        # self.data_type_radio_mcc.grid(row=1,column=1,sticky='es')

        self.progress_state_context=tk.StringVar()
        self.progress_state = tk.Label(master, textvariable=self.progress_state_context)
        self.progress_state.grid(row=2, column=1,sticky='sw')

        #导入按钮
        self.submit_button = tk.Button(master, text="导入", command=self.read_file)
        self.submit_button.grid(row=2, column=1)

        #进度条
        self.progress_label = tk.Label(master, text="进度:")
        self.progress_label.grid(row=3, column=0)

        self.progress_bar = ttk.Progressbar(master)
        #self.progress_bar.grid(row=3, column=1, sticky="nsew")
        self.progress_bar.grid(row=3, column=1, sticky=tk.E+tk.W)

        #日志框
        self.text_label = tk.Label(master, text="日志:")
        self.text_label.grid(row=4, column=0)

        self.text_box_context=tk.StringVar()
        self.text_box = tk.Text(master,wrap="none",state='disabled')
        #self.text_box.grid(row=4, column=1, sticky="nsew")
        self.text_box.grid(row=4, column=1, sticky=tk.E+tk.W+tk.N+tk.S)

        self.scrollbar_x = tk.Scrollbar(master, orient=tk.HORIZONTAL, command=self.text_box.xview)
        self.scrollbar_x.grid(row=5, column=1, sticky="ew")
        self.text_box.configure(xscrollcommand=self.scrollbar_x.set)

        self.scrollbar_y = tk.Scrollbar(master, orient=tk.VERTICAL, command=self.text_box.yview)
        self.scrollbar_y.grid(row=4, column=2, sticky="ns")
        self.text_box.configure(yscrollcommand=self.scrollbar_y.set)
        
        # 设置布局
        master.columnconfigure(1, weight=1)
        master.rowconfigure(3, weight=1)
        
        self.text_box_insert_top(f"\t数据库：{mysqlDict['db']}\n")
        self.text_box_insert_top(f"\t主  机：{mysqlDict['host']}:{DBUtil.config['port']}\n")
        self.text_box_insert_top(f"当前配置：\n")

    def browse_file(self):
        file_path = filedialog.askopenfilename(title='打开建行生活数据文件',filetypes=[('核券明细', '*.zip'),('核券明细', '*.txt'),('商户清单', '*.xlsx'),('商户清单', '*.xls')])
        if file_path:
            self.file_path.set(file_path)


    def text_box_insert_top(self,context):
        self.text_box.config(state='normal')
        self.text_box.insert('1.0',context)
        self.text_box.config(state='disabled')
        self.master.update()

    def update_progress_bar(self,i):
        self.progress_bar['value']=i
        self.master.update()


    '''
    按行读文件到列表，生成订单字典
    建立字典：key=订单号，value=列表
    '''
    def genOrderDictByFile(self,sFileName,sOutFile):
        orderDict={}    #订单字典：key=订单号,value=列表
        currentList=[]
        totalRecord=-1
        failRecord=0
        succRecord=0
        of=open(sOutFile,'w',encoding='gbk')
        of.write("genOrderDict begin:\n")
        self.text_box_insert_top("genOrderDict begin:\n")
        self.progress_state_context.set("第一步：正在分析数据文件")
        with open(sFileName,'rb') as fp:
            context=fp.readlines()
            self.progress_bar['maximum']=len(context)
            encoding=chardet.detect(context[0])['encoding']
            print(f"encoding:{encoding}")
            self.text_box_insert_top(f"encoding:{encoding}\n")
            if(encoding.lower()=='gb2312' or encoding.lower()=='ansi'):
                encoding='gbk'
        with open(sFileName,'r',encoding=encoding) as sf:
            for line in sf:
                totalRecord+=1
                self.update_progress_bar(totalRecord)
                if(totalRecord==0):     #忽略第一行标题行
                    # reDict=chardet.detect(b'{line}')
                    # print(f"confidence:{reDict['confidence']};encoding:{reDict['encoding']};language:{reDict['language']}")
                    continue
                line=line.encode("GBK",errors='ignore').decode("GBK",errors='ignore')
                #of.write(line)
                line=line.rstrip('\n')
                currentList=line.split("|")
                #of.write(f"line[{totalRecord}],fieldCount[{len(currentList)}]\n")
                if(len(currentList)<28):
                    of.write(f"fieldCount[{len(currentList)}]Error，No.[{totalRecord}]Line[{line}]\n")
                    self.text_box_insert_top(f"fieldCount[{len(currentList)}]Error，No.[{totalRecord}]Line[{line}]\n")
                    failRecord+=1
                    continue
                
                currentOrder=currentList[10]
                dR=DailyRecord(currentList)
                if(currentOrder not in orderDict):  #增加新订单
                    orderDict[currentOrder]=[1,dR]
                else:
                    orderDict[currentOrder][1].add(dR)  #金额相加
                    orderDict[currentOrder][0]+=1
                
                if(orderDict[currentOrder][0]>1):   #多条记录则记录日志
                    #of.write('['+str(orderDict[currentOrder][0])+']['+line+']\n')
                    of.write('['+str(orderDict[currentOrder][0])+']'+str(orderDict[currentOrder][1])+'\n')    
                    self.text_box_insert_top('['+str(orderDict[currentOrder][0])+']'+str(orderDict[currentOrder][1])+'\n')            
                succRecord+=1
        resultStr=f"totalRecord[{totalRecord}]success[{succRecord}]failRecord[{failRecord}]summaryRecord[{len(orderDict)}]\n" 
        self.update_progress_bar(0)   
        self.progress_state_context.set("第二步：正在装载数据文件")
        self.progress_bar['maximum']=len(orderDict)    
        of.write(resultStr)            
        print(resultStr)    
        self.text_box_insert_top(resultStr)        
        self.analysisOrderDict(of,orderDict)
        of.close()      
        return orderDict             

    def analysisOrderDict(self,of,orderDict):
        of.write("\n\nanalysisOrderDict begin:\n")
        succRecord=0
        failRecord=0
        skipRecord=0
        db = DBUtil()
        print(f"Now[{time.strftime('%Y%m%d %H:%M:%S',time.localtime(time.time()))}]!")
        self.text_box_insert_top(f"Now[{time.strftime('%Y%m%d %H:%M:%S',time.localtime(time.time()))}]!\n")
        i=0
        for k,v in orderDict.items():
            execu=0
            i+=1
            self.update_progress_bar(i)
            if((succRecord+failRecord+skipRecord)%1000==0):
                print(f"Now[{time.strftime('%Y%m%d %H:%M:%S',time.localtime(time.time()))}] deal No.[{succRecord+failRecord+skipRecord}] record.")
                self.text_box_insert_top(f"Now[{time.strftime('%Y%m%d %H:%M:%S',time.localtime(time.time()))}] deal No.[{succRecord+failRecord+skipRecord}] record.\n")
            if(v[1].reduce_amt<0): #先考虑冲正业务,且包含了多笔冲正
                sql=f"select mc_id,sp_id,mc_name,ticket_id,ticket_name,user_id,card_no,get_time,use_flag,use_time,use_order,order_amt,reduce_amt,pay_type,use_mc_id,use_src_id,ticket_beg_time,ticket_end_time,use_user_id,user_mobile,real_use_amt,use_limit,card_bin,is_uionpay,is_settle,settle_amt,sp_amt,bp_amt from jhsh_ticket_tz where use_order='{k}'";
                qryRecord=None
                try:
                    qryRecord=db.query_one(sql)
                except Exception as e:
                    qryRecone=None                    
                if(qryRecord==None):
                    of.write(sql+"\n")
                    self.text_box_insert_top(sql+"\n")
                    of.write(f"[{k}]:[{str(v[1])}]\n")
                    self.text_box_insert_top(f"[{k}]:[{str(v[1])}]\n")
                    of.write(f"record [{k}] not found ,update error,skipped.\n")
                    self.text_box_insert_top(f"record [{k}] not found ,update error,skipped.\n")
                    skipRecord+=1
                    continue
                qR=DailyRecord(qryRecord)
                of.write(str(qryRecord)+'\n')
                self.text_box_insert_top(str(qryRecord)+'\n')
                v[1].add(qR)
                currentTime=time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
                #,card_bin='reduce_amt[{qryRecord[12]}]',use_limit='oper[auto]time[{currentTime}]'
                sql=f"update jhsh_ticket_tz set reduce_amt={v[1].reduce_amt},real_use_amt={v[1].real_use_amt},settle_amt={v[1].settle_amt},sp_amt={v[1].sp_amt},bp_amt={v[1].bp_amt},card_bin='amt[{qryRecord[12]}|{qryRecord[20]}|{qryRecord[25]}|{qryRecord[26]}|{qryRecord[27]}]',use_limit='oper[auto]time[{currentTime}]' where use_order='{k}'"
                if(v[1].reduce_amt<0.00):     #本次优惠金额小于0，说明该字段已经计算过优惠额，不要再重复计算
                    of.write("reduce_amt less zero begin!!!\n")
                    self.text_box_insert_top("reduce_amt less zero begin!!!\n")
                    of.write(sql+"\n")
                    self.text_box_insert_top(sql+"\n")
                    of.write(f"[{k}]:[{str(v[1])}]\n")
                    self.text_box_insert_top(f"[{k}]:[{str(v[1])}]\n")
                    of.write("reduce_amt less zero end!!!\n")
                    self.text_box_insert_top("reduce_amt less zero end!!!\n")
                    skipRecord+=1
                    continue
                #of.write(sql+"\n")
                try:
                    execu = db.execute_sql(sql)
                    succRecord+=1
                except Exception as e:
                    failRecord+=1
                    of.write("Reduce_amt less zero update error begin!!!\n")
                    of.write(sql+"\n")
                    of.write(f"[{k}]:[{str(v[1])}]\n")
                    of.write(f"Reduce_amt less zero update error end:{str(e)}!!!!!!\n")
                    of.write("Reduce_amt less zero update error begin!!!\n")
                    self.text_box_insert_top(sql+"\n")
                    self.text_box_insert_top(f"[{k}]:[{str(v[1])}]\n")
                    self.text_box_insert_top(f"Reduce_amt less zero update error end:{str(e)}!!!!!!\n")
            elif(v[0]==1):           #正常单笔新增交易
                sql=f"insert into jhsh_ticket_tz (mc_id,sp_id,mc_name,ticket_id,ticket_name,user_id,card_no,get_time,use_flag,use_time,use_order,order_amt,reduce_amt,pay_type,use_mc_id,use_src_id,ticket_beg_time,ticket_end_time,use_user_id,user_mobile,real_use_amt,use_limit,card_bin,is_uionpay,is_settle,settle_amt,sp_amt,bp_amt) values ('{v[1].mc_id}','{v[1].sp_id}','{v[1].mc_name}','{v[1].ticket_id}','{v[1].ticket_name}','{v[1].user_id}','{v[1].card_no}','{v[1].get_time}','{v[1].use_flag}','{v[1].use_time}','{v[1].use_order}','{v[1].order_amt}','{v[1].reduce_amt}','{v[1].pay_type}','{v[1].use_mc_id}','{v[1].use_src_id}','{v[1].ticket_beg_time}','{v[1].ticket_end_time}','{v[1].use_user_id}','{v[1].user_mobile}','{v[1].real_use_amt}','{v[1].use_limit}','{v[1].card_bin}','{v[1].is_uionpay}','{v[1].is_settle}','{v[1].settle_amt}','{v[1].sp_amt}','{v[1].bp_amt}')"; 
                try:
                    execu = db.execute_sql(sql)
                    succRecord+=1
                except Exception as e:
                    if(isinstance(e,IntegrityError)):
                        skipRecord+=1
                        continue
                        
                    failRecord+=1
                    of.write("Insert error begin!!!\n")
                    of.write(sql+"\n")
                    of.write(f"[{k}]:[{str(v[1])}]\n")
                    of.write(f"Insert error end:{str(e)}!!!!!!\n")
                    self.text_box_insert_top("Insert error begin!!!\n")
                    self.text_box_insert_top(sql+"\n")
                    self.text_box_insert_top(f"[{k}]:[{str(v[1])}]\n")
                    self.text_box_insert_top(f"Insert error end:{str(e)}!!!!!!\n")
            elif(v[0]>1):   #多条记录仅作为新增数据，已考虑多笔冲正情况。
                #sql=f"update jhsh_ticket_tz set reduce_amt={v[1].reduce_amt},real_use_amt={v[1].real_use_amt},settle_amt={v[1].settle_amt},sp_amt={v[1].sp_amt},bp_amt={v[1].bp_amt} where use_order='{k}'"
                sql=f"insert into jhsh_ticket_tz (mc_id,sp_id,mc_name,ticket_id,ticket_name,user_id,card_no,get_time,use_flag,use_time,use_order,order_amt,reduce_amt,pay_type,use_mc_id,use_src_id,ticket_beg_time,ticket_end_time,use_user_id,user_mobile,real_use_amt,use_limit,card_bin,is_uionpay,is_settle,settle_amt,sp_amt,bp_amt) values ('{v[1].mc_id}','{v[1].sp_id}','{v[1].mc_name}','{v[1].ticket_id}','{v[1].ticket_name}','{v[1].user_id}','{v[1].card_no}','{v[1].get_time}','{v[1].use_flag}','{v[1].use_time}','{v[1].use_order}','{v[1].order_amt}','{v[1].reduce_amt}','{v[1].pay_type}','{v[1].use_mc_id}','{v[1].use_src_id}','{v[1].ticket_beg_time}','{v[1].ticket_end_time}','{v[1].use_user_id}','{v[1].user_mobile}','{v[1].real_use_amt}','{v[1].use_limit}','{v[1].card_bin}','{v[1].is_uionpay}','{v[1].is_settle}','{v[1].settle_amt}','{v[1].sp_amt}','{v[1].bp_amt}')"; 
                try:
                    execu = db.execute_sql(sql)                
                    # of.write("Summary record begin!!!\n")
                    # of.write(sql+"\n")
                    # of.write(f"[{v[0]}][{k}]:[{str(v[1])}]\n")
                    # of.write(f"Summary record end[{execu}]!!!!!!\n")
                    succRecord+=1
                except Exception as e:
                    if(isinstance(e,IntegrityError)):
                        skipRecord+=1
                        continue
                    of.write("Summary record update error begin!!!\n")
                    of.write(sql+"\n")
                    of.write(f"[{v[0]}][{k}]:[{str(v[1])}]\n")
                    of.write(f"Summary record update error end:{str(e)}!!!!!!\n")
                    self.text_box_insert_top("Summary record update error begin!!!\n")
                    self.text_box_insert_top(sql+"\n")
                    self.text_box_insert_top(f"[{v[0]}][{k}]:[{str(v[1])}]\n")
                    self.text_box_insert_top(f"Summary record update error end:{str(e)}!!!!!!\n")
                    failRecord+=1
        db.close()
        of.write(f"summary[{len(orderDict)}]success[{succRecord}]skipRecord[{skipRecord}]failRecord[{failRecord}]\n")
        print(f"summary[{len(orderDict)}]success[{succRecord}]skipRecord[{skipRecord}]failRecord[{failRecord}]\n")
        self.text_box_insert_top(f"导入成功：summary[{len(orderDict)}]success[{succRecord}]skipRecord[{skipRecord}]failRecord[{failRecord}]\n")
        

    def read_file(self):
        self.submit_button.config(state='disabled')
        file_path = self.file_path.get()
        if not os.path.isfile(file_path):
            self.text_box_insert_top(f"请确认文件[{file_path}]是否规范的建行生活核券/商户明细数据文件。\n")
            self.submit_button.config(state='normal')
            return
        elif (file_path.lower().rstrip().endswith('.xls') or file_path.lower().rstrip().endswith('.xlsx')) :
            self.text_box_insert_top(f"开始导入商户明细。\n")
            self.read_mcc_file()
            self.text_box_insert_top(f"导入商户明细结束。\n")
        else:
            self.text_box_insert_top(f"开始导入核券明细。\n")
            self.read_ticket_file() 
            self.text_box_insert_top(f"导入核券明细结束。\n")
        self.submit_button.config(state='normal')
        return

    #商户明细开始
    def read_mcc_file(self):
        self.submit_button.config(state='disabled')
        file_path = self.file_path.get()
        if not os.path.isfile(file_path):
            self.text_box_insert_top(f"请确认文件[{file_path}]\n是否规范的建行生活商户明细数据文件（个金部excel表格）。\n")
            self.submit_button.config(state='normal')
            return
        
        if not (file_path.lower().endswith('.xls') or file_path.lower().endswith('.xlsx')):
            self.text_box_insert_top(f"请确认文件[{file_path}]\n是否规范的建行生活商户明细数据文件。\n")
            self.submit_button.config(state='normal')
            return
        
        file_path=os.path.abspath(file_path)
        file_path_cur=os.path.dirname(file_path)
        file_name=os.path.basename(file_path)
        file_path_out=file_path_cur+os.sep+'OUT'
        if(not os.path.isdir(file_path_out)):
            os.makedirs(file_path_out)
            
        self.file_path_log=file_path_out+os.sep+file_name+'.out'
        print(self.file_path_log)
        self.text_box_insert_top(f"日志文件：{self.file_path_log}\n")

        of=open(self.file_path_log,'w',encoding='gbk')
        of.write("processMccDtl begin:\n")
        self.text_box_insert_top("开始处理商户明细:\n")
        self.progress_state_context.set("正在处理商户数据文件")
        
        try :
            xlsData=pd.read_excel(file_path,header=[0,2])
        except Exception as e:
            self.text_box_insert_top(f"打开商户明细表[{self.file_path.get()}]\n\t错误[{e}]\n")
            self.submit_button.config(state='normal')
            return
        
        xlsList=xlsData.values.tolist()
        procCount=0
        totalCount=len(xlsList)
        succRecord=0
        skipRecord=0
        failRecord=0
        self.progress_bar['maximum']=totalCount
        db=None
        try:
            db = DBUtil()
        except Exception as e:
            self.text_box_insert_top(f"打开数据库出错，请检查jhsh.ini配置文件配置是否正确！]\n[{e}]\n")
            self.text_box_insert_top(f"jhsh.ini配置文件,需包括[mysql]段，如下键：host、port、user、passwd、db、charset！]\n")
            self.submit_button.config(state='normal')
            self.progress_state_context.set("处理商户数据失败，检查jhsh.ini配置文件。")
            return
            
        for row in xlsList:
            procCount+=1
            self.update_progress_bar(procCount)
            mR=MccRecord(row)
            #print(mR)
            if not mR.isValid:
                self.text_box_insert_top(f"商户数据非法：{mR}\n")
                of.write(f"商户数据非法：{mR}\n")
                of.write(f"失败|[{failRecord}[{mR}]\n")
                failRecord+=1
                continue
            sql=f"insert into jhsh_mcc_dtl (bp_name,b_id,mc_id,tm_id,th_id,sp_id,mc_name,sp_name) values ('{mR.bp_name}','{mR.b_id}','{mR.mc_id}','{mR.tm_id}','{mR.th_id}','{mR.sp_id}','{mR.mc_name}','{mR.sp_name}')"; 
            try:
                execu = db.execute_sql(sql)
                of.write(f"成功|[{succRecord}[{mR}]\n")
                succRecord+=1
            except Exception as e:
                if(isinstance(e,IntegrityError)):
                    of.write(f"忽略|[{skipRecord}[{mR}]\n")
                    skipRecord+=1
                    continue
                else:
                    of.write(f"失败|[{failRecord}[{mR}]\n")
                    failRecord+=1
                    self.text_box_insert_top(f"商户表插入错误[{e}]\n商户数据：{mR}\n")
                    of.write(f"商户表插入错误[{e}]\n商户数据：{mR}\n")
                    self.text_box_insert_top(f"{sql}\n")
                    of.write(f"{sql}\n")
                    continue
        self.text_box_insert_top(f"商户表插入成功，合计[{totalCount}]条记录：插入[{succRecord}]条，跳过[{skipRecord}]条，错误[{failRecord}]条记录。\n")
        of.write(f"商户表插入成功，合计[{totalCount}]条记录：插入[{succRecord}]条，跳过[{skipRecord}]条，错误[{failRecord}]条记录。\n")
        self.progress_state_context.set("商户清单装载成功")
        db.close()    
        of.close()
        self.submit_button.config(state='normal')
        
    #商户明细结束
    

    #核券明细开始
    def read_ticket_file(self):     
        self.submit_button.config(state='disabled')
        file_path = self.file_path.get()
        if not os.path.isfile(file_path):
            self.text_box_insert_top(f"请确认文件[{file_path}]\n是否规范的建行生活核券明细数据文件。\n")
            self.submit_button.config(state='normal')
            return

        if not (file_path.lower().endswith('.zip') or file_path.lower().endswith('.txt')):
            self.text_box_insert_top(f"请确认文件[{file_path}]\n是否规范的建行生活核券明细数据文件。\n")
            self.submit_button.config(state='normal')
            return

        file_path=os.path.abspath(file_path)
        #file_path_cur=file_path[0:file_path.rfind(os.sep)]
        file_path_cur=os.path.dirname(file_path)
        print(file_path)
        file_path_zip=file_path_cur+os.sep+'zip'
        #file_name=file_path[file_path.rfind(os.sep,)+1:]
        file_name=os.path.basename(file_path)
        print(file_name)
        file_path_out=file_path_cur+os.sep+'OUT'
        if(not os.path.isdir(file_path_out)):
            os.makedirs(file_path_out)
            
        self.file_path_log=file_path_out+os.sep+file_name+'.out'
        if(file_name.lower().endswith('.zip')):
            zip_handle = zipfile.ZipFile(file_path,'r')
            namelist=zip_handle.namelist()
            self.file_path_data=file_path_zip+os.sep+namelist[0]
            zip_handle.extractall(file_path_zip)
        else:
            self.file_path_data=file_path
        print(self.file_path_log)
        print(self.file_path_data)
        self.text_box_insert_top(f"日志文件：{self.file_path_log}\n")
        self.text_box_insert_top(f"数据文件：{self.file_path_data}\n")

        try :
            orderDict=self.genOrderDictByFile(self.file_path_data,self.file_path_log)
            self.progress_state_context.set("数据装载成功！")
        except Exception as e :
            print(f"Exception:[{e}]")
            self.progress_state_context.set("数据装载失败！")
            self.text_box_insert_top(f"啊呀，出错啦：\n{e}\n\n")

        self.submit_button.config(state='normal')


        # with open(self.file_path_data,'rb') as fp:
        #     context=fp.readline()
        #     encoding=chardet.detect(context)['encoding']
        #     print(f"encoding:{encoding}")
        #     if(encoding.lower()=='gb2312' or encoding.lower()=='ansi'):
        #         encoding='gbk'
        
        # with open(self.file_path_data, "r",encoding=encoding) as f:
        #     lines = f.readlines()
        #     total_lines = len(lines)
        #     self.progress_bar['maximum']=total_lines

        #     for i, line in enumerate(lines):
        #         line_length = len(line)
        #         self.text_box.insert('1.0', f"第{i+1}行：{line_length}\n")
        #         # self.progress_bar.set(i / total_lines,1)
        #         self.progress_bar['value']=i
        #         self.master.update()
    #核券明细结束            

                
        
if __name__ == "__main__":
    root = tk.Tk()
    app = TextReader(root)
    root.mainloop()
