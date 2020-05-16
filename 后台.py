import json
import requests
class params_data():
    def __init__(self):
        self.cookie = {}
        self.headers = {}
        self.params = {}    
        self.prefix = 'https://mp.weixin.qq.com/mp/'    #网址前缀
        self.suffix = ''    #网址后缀
        self.url = ''       #完整网址

    def decode_url(self,url):   #获取网址信息函数
        #print("网址信息提取中")
        temp = url.split('?')   #将网址数据区剥离
        data = temp[1]          #提取数据
        temp = data.split('&')  #将数据分块
        for i in temp:
            data = i.split('=',1) #提取变量名和值
            self.params[data[0]] = data[1]  #向数据字典中添加数据
        self.suffix = 'profile_ext'
        self.url = self.prefix + self.suffix
        #print("网址信息提取完成")
        print(self.params)

    def decode_cookie(self,cookie): #获取cookie函数（cookie需要ctrl+c复制自fiddler）,cookie形如 Cookie: rewardsn=;
                                    #wxtokenkey=777;
        #print("Cookie 提取中")
        temp = cookie.split(': ')   #将cookie分块
        cookie = temp[1]            #去掉无用的Cookie: 前缀
        temp = cookie.split('; ')
        for i in temp:              #处理所有cookie数据
            temp2 = i.split('=',1)
            self.cookie[temp2[0]] = temp2[1]  #提取cookie数据
        #print("Cookie 提取完成")
                                                    #print(self.cookie)

    def decode_headers(self):
        print("请输入header,其中action = getmsg")
        temp = 'NULL'
        while(temp != ''):
            try:
                temp = input()
                if 'GET' in temp:
                    temp.replace('HTTP/1.1','')
                    self.decode_url(temp)
                elif 'Cookie' in temp:
                    self.decode_cookie(temp)
                else:
                    temp = temp.split(': ')
                    self.headers[temp[0]] = temp[1]
            except:
                break

    def getmsg(self,offset=-10,count=10):   #调用时offset不为负，count为正
        self.params['action'] = 'getmsg'
        if offset == -10 :   #重复无参数调用
            self.params['offset']+=count
            self.params['count'] = count
        else:               #指定参数调用
            self.params['offset'] = offset
            self.params['count'] = count
            #headers = {
            #    'User-Agent':self.headers['User-Agent'],
            #    'Referer' :self.headers['Referer']
            #    }
            #params = { #构造params
            #    '__biz' :self.params['__biz'],
            #    'uin' :self.params['uin'],
            #    'key' :self.params['key'],
            #    'offset':self.params['offset'],
            #    'count' :self.params['count'],
            #    'action':self.params['action'],
            #    'f' :self.params['f']
            #    }
        self.params['f'] = 'json'
        self.response = requests.get(self.url,params = self.params,headers = self.headers,cookies = self.cookie,verify = False)
    def decode_response(self):
        self.data = json.loads(self.response.text)

a = params_data()
a.decode_headers()
a.getmsg(0,10)  #初始化并获取第一段
a.decode_response()
