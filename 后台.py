#   由于微信验证方式的原因，只能爬取文章，不能爬取评论和点赞数等详细信息
import json
import requests
import re
import copy
import time
import csv
import os
import traceback
import urllib
import requests

class NoQuoteSession(requests.Session): #这个类用于解决requests.get会自动编码=等特殊字符的问题（copy来的，分析过程深入库的源码，看不懂也懒得看了）
    def send(self, prep, **send_kwargs):
        table = {
            urllib.parse.quote('{'): '{',
            urllib.parse.quote('}'): '}',
            urllib.parse.quote(':'): ':',
            urllib.parse.quote(','): ',',
            urllib.parse.quote('='): '=',
            urllib.parse.quote('%'): '%',
        }
        for old, new in table.items():
            prep.url = prep.url.replace(old, new)
        return super(NoQuoteSession, self).send(prep, **send_kwargs)

class  weixin_spider():
    def __init__(self):
        self.msgcookie = {} #为提取不同行为用的不同cookie分配空间
        self.msgparams = {}
        self.msgheaders = {}
        self.headers = {}
        self.prefix = 'https://mp.weixin.qq.com/mp/'    #网址前缀
        self.suffix = ''    #网址后缀
        self.url = ''       #完整网址
        self.msgparams['offset'] = 0   #默认偏移量为0
        self.msgparams['count'] = 10   #默认步进为10
        self.json_data = {}
        self.data_decoded = []         #完成一个完整的数据提取循环的数据
        self.data_decoded_temp = []    #临时存储当前循环的数据，网址返回错误信息时丢弃，防止污染已提取数据
        self.id = 0                    #初始化程序内部ID

    def information_init(self):
        print("注意，下列输入均输入至cookie行（包含该行）结束，如果有多余数据请勿输入，防止数据污染")
        print("请输入action = getmsg的header")
        self.decode_headers('getmsg')

    def decode_url(self,url,flag):   #获取网址信息函数，flag请填写成'getmsg'
        temp = url.split('?')   #将网址数据区剥离
        data = temp[1]          #提取数据
        temp = data.split('&')  #将数据分块
        for i in temp:
            data = i.split('=',1) #提取变量名和值
            if flag == 'getmsg':
                self.msgparams[data[0]] = data[1]  #向数据字典中添加数据

    def decode_cookie(self,cookie,flag): #获取cookie函数（cookie需要ctrl+c复制自fiddler）,cookie形如 Cookie:
                                         #rewardsn=;wxtokenkey=777;
        temp = cookie.split(': ')   #将cookie分块
        cookie = temp[1]            #去掉无用的Cookie: 前缀
        temp = cookie.split('; ')
        for i in temp:              #处理所有cookie数据
            temp2 = i.split('=',1)
            if flag == 'getmsg':
                self.msgcookie[temp2[0]] = temp2[1]

    def decode_headers(self,flag):   #分析header的raw数据，flag是一个已经废弃的参数，请填写'getmsg'
        temp = 'NULL'
        while(temp != ''):
            try:
                temp = input()
                if ('GET' in temp) or ('POST' in temp): #属于params的部分
                    temp = temp.replace('HTTP/1.1','')
                    self.decode_url(temp,flag)
                elif 'Cookie' in temp:
                    self.decode_cookie(temp,flag)
                else:   #属于header的部分
                    temp = temp.split(': ')
                    if flag == 'getmsg':
                        self.msgheaders[temp[0]] = temp[1]
            except:
                break

    def decode_response_getmsg(self,response):  #解析action = getmsg时获取的json
        self.json_data = json.loads(response.text)
        if self.json_data['ret'] != 0:
            print("出现错误，程序正在退出,data = {:}".format(self.json_data))
            raise Exception('返回结果有误，请检查header是否有效')
        self.json_urls = json.loads(self.json_data['general_msg_list'])

    def decode_list(self):  #解析decode_response得到的json并提取相应数据存到data_decoded_temp
        num = 0
        for i in self.json_urls['list']:
            num+=1
            data = i['comm_msg_info']
            self.data_decoded_temp = {}
            self.data_decoded_temp['inside_id'] = self.id    #程序内部的ID
            self.id+=1
            self.data_decoded_temp['id'] = data['id']        #文章在微信中的ID
            self.data_decoded_temp['type'] = data['type']
            self.data_decoded_temp['datetime'] = data['datetime']
            self.data_decoded_temp['time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(data['datetime']))
            self.data_decoded_temp['fakeid'] = data['fakeid']
            self.data_decoded_temp['status'] = data['status']
            data = i['app_msg_ext_info']
            self.data_decoded_temp['title'] = data['title'].replace('&amp','&')   #文章标题
            self.data_decoded_temp['digest'] = data['digest']
            self.data_decoded_temp['fileid'] = data['fileid']
            self.data_decoded_temp['content_url'] = data['content_url'] #含有用户信息的临时链接
            self.data_decoded_temp['source_url'] = data['source_url'] #文章永久链接
            self.data_decoded_temp['cover'] = data['cover']
            self.data_decoded_temp['subtype'] = data['subtype']
            self.data_decoded_temp['author'] = data['author']
            if self.data_decoded_temp['cover'] != '':
                self.get_icon(self.data_decoded_temp['cover'],self.id - 1) #下载图片并命名为 文章标题.png
            self.data_decoded.append(copy.deepcopy(self.data_decoded_temp))
            print("{:^21}  {:^12}\t{:^14}\t{:>20}\n".format('当前系统时间','推送时间','作者','标题'))
            print("{systime:^24}  {datetime:^19}\t{author:<{len1}}\t{title:}".format(   
                systime = time.ctime(time.time()),datetime = self.data_decoded_temp['time'],    
                author = self.data_decoded_temp['author'],len1 = 16-len(self.data_decoded_temp['author']),   
                title = self.data_decoded_temp['title']))
            multi = data['is_multi'] 
            if multi == 1:       #如果本次推送含有多篇文章
                for k in i['app_msg_ext_info']['multi_app_msg_item_list']:
                    num+=1
                    self.data_decoded_temp['inside_id'] = self.id
                    self.id+=1
                    self.data_decoded_temp['title'] = k['title'].replace('&amp','&')
                    self.data_decoded_temp['digest'] = k['digest']
                    self.data_decoded_temp['fileid'] = k['fileid']
                    self.data_decoded_temp['content_url'] = k['content_url']
                    self.data_decoded_temp['source_url'] = k['source_url']
                    self.data_decoded_temp['cover'] = k['cover']
                    self.data_decoded_temp['author'] = k['author']
                    if self.data_decoded_temp['cover'] != '':
                        self.get_icon(self.data_decoded_temp['cover'],self.id - 1) #下载图片并命名为 $(inside_id).png
                    self.data_decoded.append(copy.deepcopy(self.data_decoded_temp))
                    print("{systime:^24}  {datetime:^19}\t{author:<{len1}}\t{title:}".format(   
                    systime = time.ctime(time.time()),datetime = self.data_decoded_temp['time'],    
                    author = self.data_decoded_temp['author'],len1 = 16-len(self.data_decoded_temp['author']),   
                    title = self.data_decoded_temp['title']))
                print('')
        print('本次请求共获取{:}条推送（以文章计）'.format(num))

    def getmsg(self,count=-1,offset=-1):   #获取公众号历史文章列表，调用时offset不为负，count为正，count最大为10（未验证），初次调用一定要指定调用参数
        if offset == -1 :   #不指定偏移量
            if count == -1: #无参数重复调用
                self.msgparams['offset']+=self.msgparams['count']
            else:           #指定count参数大小
                self.msgparams['offset']+=count #先加上一次的偏移量，然后将偏移量设为指定值
                self.msgparams['count'] = count
        else:               #完全指定参数调用
            self.msgparams['offset'] = offset
            self.msgparams['count'] = count
        url = self.prefix + 'profile_ext' 
        params = {  #构造params,因为self.params中含有过多参数，可能引发异常
            'action':'getmsg',
            '__biz':self.msgparams['__biz'],
            'offset':self.msgparams['offset'],
            'count':self.msgparams['count'],
            'is_ok':self.msgparams['is_ok'],
            'scene':self.msgparams['scene'],
            'uin':self.msgparams['uin'],
            'key':self.msgparams['key'],
            'wxtoken':self.msgparams['wxtoken'],
            'f':'json',
            'pass_ticket':self.msgparams['pass_ticket'],
            'appmsg_token':self.msgparams['appmsg_token']
            }
        headers = { #构造header
            'User-Agent':self.msgheaders['User-Agent'],
            }
        cookies = { #构造专用cookie
            'rewardsn':self.msgcookie['rewardsn'],
            'wxtokenkey':self.msgcookie['wxtokenkey'],
            'wxuin':self.msgcookie['wxuin'],
            'devicetype':self.msgcookie['devicetype'],
            'version':self.msgcookie['version'],
            'lang':self.msgcookie['lang'],
            'pass_ticket':self.msgcookie['pass_ticket'],
            'wap_sid2':self.msgcookie['wap_sid2']
            }
        s = NoQuoteSession()    #为了解决requests会自动编码=导致请求失败的问题而引入
        response = s.get(url = url,params = params,headers = headers,cookies = cookies
                         ,verify = False       #这句话防止开启fiddler时无法获取请求
                         )
        return response

    def get_icon(self,url,name):    #下载icon图片,默认保存在image文件夹
        path = "./image/" + str(name) + ".png"
        if os.path.exists(path) == True :    #如果文件存在就返回（防止抓取次数过多被封，同时提高效率）
            if os.path.getsize(path) != 0:
                return
        response = requests.get(url)
        try:
            fp = open(path,mode = 'wb')
        except:
            os.mkdir("./image")
            fp = open(path,mode = 'wb')
        fp.write(response.content)
        fp.close()

    def spider(self,count=10,offset=-10):   #爬取文章的封装函数，输入offset非负，count不大于10
        self.information_init()
        self.msgparams['count'] = count
        self.msgparams['offset'] = offset
        print("如果读取之前的配置请输入非空字符")
        if input() != "":
            print("正在读取数据，请稍候")
            self.id = self.load_csv() + 1
            offset,count = self.load_ext()
            self.msgparams['offset'] = offset
            self.msgparams['count'] = count
        self.json_data['can_msg_continue'] = 1  #设定初始值，使while可以开始，该值在加载操作中会被覆盖掉，不影响后面的处理
        while (self.json_data['can_msg_continue'] == 1):
            try:
                response = self.getmsg()                #请求json
                self.decode_response_getmsg(response)   #加载返回的json
                self.decode_list()
                self.save_data(self.msgparams['offset'],self.msgparams['count'])
                if self.json_data['can_msg_continue']!=1:
                    print("已达到文章末尾，程序即将退出")
                print("休眠3s防止被封")
                time.sleep(3)
            except:
                traceback.print_exc()
                self.save_data(self.msgparams['offset'],self.msgparams['count'])
                print('offset = ',self.msgparams['offset'],'count = ',self.msgparams['count'],'inside_id = ',self.id)
                return (self.data_decoded_temp,self.msgparams['offset'],self.msgparams['count'],False)
                #出错退出，返回当前循环获取的数据
        print("数据采集完成，程序正在退出")
        return (self.data_decoded,self.msgparams['offset'],self.msgparams['count'],True)    #完成爬取，返回信息

    def load_ext(self):     #读取配置，目前仅支持读取offset和count
        fp = open('./ext.ini','r',encoding='utf-8')
        offset = fp.readline().split(' = ')[1]
        count = fp.readline().split(' = ')[1]
        fp.close()
        return (int(offset),int(count))
  
    def load_csv(self):     #从文件中加载数据（适用于被微信封IP等操作后过一段时间继续爬取）
        print("正在加载CSV，请稍候")
        fp = open('./_result.csv','r',encoding='utf-8')
        reader = csv.reader(fp)
        temp_list = {}
        for row in reader:
            temp_list.clear()
            temp_list['inside_id'] = row[0]
            temp_list['time'] = row[1]
            temp_list['title'] = row[2]
            temp_list['author'] = row[3]
            temp_list['source_url'] = row[4]
            temp_list['content_url'] = row[5]
            temp_list['cover'] = row[6]
            self.data_decoded.append(copy.deepcopy(temp_list))
        self.data_decoded.remove({'author': '作者', 'content_url': '临时链接', 'title':'标题', 'cover': '封面网址', 'inside_id': '序号', 'source_url': '永久链接', 'time': '发布时间'})
        return int(temp_list['inside_id'])   #返回最后一条数据对应的内部ID

    def save_data(self,offset,count):     #保存数据
        print("正在保存数据，请稍候")
        fp = open('./_result.csv','w',encoding='utf-8',newline = '')
        writer = csv.writer(fp)
        temp_list = []
        writer.writerow(['序号','发布时间','标题','作者','永久链接','临时链接','封面网址'])
        for i in self.data_decoded:
            temp_list.clear()
            temp_list.append(i['inside_id'])
            temp_list.append(i['time'])
            temp_list.append(i['title'])
            temp_list.append(i['author'])
            temp_list.append(i['source_url'])   #文章永久链接
            temp_list.append(i['content_url'])   #文章临时链接
            temp_list.append(i['cover'])        #文章封面网址
            writer.writerow(temp_list)
        fp.close()
        fp = open('./ext.ini','w',encoding='utf-8')
        temp_list = []
        temp_list.append('offset = '+str(offset)+'\n')
        temp_list.append('count = '+str(count)+'\n')
        #temp_list.append('can_msg_continue = '+str(self.json_data['can_msg_continue'])+'\n')
        fp.writelines(temp_list)
        fp.close()
        self.utf8_to_ansi()

    def utf8_to_ansi(self):     #使用ansi编码save_data会报错，utf8在excel里表示中文是乱码，所以需要转换
        fp_ansi = open('./输出.csv','wb')
        fp_utf8 = open('./_result.csv','rb')
        data = ""
        data = fp_utf8.read()
        data = data.decode('utf-8')
        data = data.encode('mbcs',errors = 'ignore')
        fp_ansi.write(data)
        fp_ansi.close()
        fp_utf8.close()

obj = weixin_spider()
obj.spider()
