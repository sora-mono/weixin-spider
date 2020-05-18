import json
import requests
import re
class params_data():
    def __init__(self):
        self.msgcookie = {} #为提取不同行为用的不同cookie分配空间
        self.commentcookie = {}
        self.appmsgcookie = {}
        self.headers = {}
        self.params = {}    
        self.prefix = 'https://mp.weixin.qq.com/mp/'    #网址前缀
        self.suffix = ''    #网址后缀
        self.url = ''       #完整网址
        self.params['offset'] = 0   #默认偏移量为0
        self.params['count'] = 10   #默认步进为10
        self.data_decoded = []

    def information_init(self):
        print("注意，下列输入均输入至cookie行（包含该行）结束，如果有多余数据请勿输入，防止数据污染")
        print("请输入action = getmsg的header")
        self.decode_headers('getmsg')
        print("请输入action = getcomment的header")
        self.decode_headers('getcomment')
        print("请输入后缀为getappmsgext的header")
        self.decode_headers('getappmsg')

    def decode_url(self,url):   #获取网址信息函数
        temp = url.split('?')   #将网址数据区剥离
        data = temp[1]          #提取数据
        temp = data.split('&')  #将数据分块
        for i in temp:
            data = i.split('=',1) #提取变量名和值
            self.params[data[0]] = data[1]  #向数据字典中添加数据

    def decode_getmsg_cookie(self,cookie): #获取cookie函数（cookie需要ctrl+c复制自fiddler）,cookie形如 Cookie: rewardsn=;wxtokenkey=777;
        temp = cookie.split(': ')   #将cookie分块
        cookie = temp[1]            #去掉无用的Cookie: 前缀
        temp = cookie.split('; ')
        for i in temp:              #处理所有cookie数据
            temp2 = i.split('=',1)
            self.msgcookie[temp2[0]] = temp2[1]  #提取action = getmsg中的cookie数据

    def decode_getcomment_cookie(self,cookie): #获取cookie函数（cookie需要ctrl+c复制自fiddler）,cookie形如 Cookie: rewardsn=;wxtokenkey=777;
        temp = cookie.split(': ')   #将cookie分块
        cookie = temp[1]            #去掉无用的Cookie: 前缀
        temp = cookie.split('; ')
        for i in temp:              #处理所有cookie数据
            temp2 = i.split('=',1)
            self.commentcookie[temp2[0]] = temp2[1]  #提取action = getcomment的cookie数据

    def decode_getappmsg_cookie(self,cookie): #获取cookie函数（cookie需要ctrl+c复制自fiddler）,cookie形如 Cookie: rewardsn=;wxtokenkey=777;
        temp = cookie.split(': ')   #将cookie分块
        cookie = temp[1]            #去掉无用的Cookie: 前缀
        temp = cookie.split('; ')
        for i in temp:              #处理所有cookie数据
            temp2 = i.split('=',1)
            self.appmsgcookie[temp2[0]] = temp2[1]  #提取网址后缀为getappmsgext的cookie数据

    def decode_headers(self,cookie_flag):   #分析header的raw数据，cookie_flag代表cookie类型
        temp = 'NULL'
        while(temp != ''):
            try:
                temp = input()
                if ('GET' in temp) or ('POST' in temp): #属于params的部分
                    temp.replace('HTTP/1.1','')
                    self.decode_url(temp)
                elif 'Cookie' in temp:
                    if cookie_flag == 'getmsg':             #action = getmsg时的cookie
                        self.decode_getmsg_cookie(temp)
                    elif cookie_flag == 'getcomment':       #action = getcomment时的cookie
                        self.decode_getcomment_cookie(temp)
                    elif cookie_flag == 'getappmsg':        #后缀为getappmsgext时的cookie
                        self.decode_getappmsg_cookie(temp)
                else:   #属于header的部分
                    temp = temp.split(': ')
                    self.headers[temp[0]] = temp[1]
            except:
                break

    def decode_response_getmsg(self,response):  #解析action = getmsg时获取的json
        self.json_data = json.loads(response.text)
        self.json_urls = json.loads(self.json_data['general_msg_list'])

    def decode_response_appmsg(self,response):  #解析后缀为getappmsgext时获取的json
        #do something
        return

    def decode_response_comment():              #解析action = getcomment时获取的json
        #do something
        return

    #def decode_article_url(self,url):
    #    temp = url.split('?')
    #    temp = temp[1]
    #    for i in temp:
    #        temp2 = i.split('=',1)
    #        self.decoded_article_url[temp2[0]] = temp2[1]
    #该函数已废弃，在第一个release后会删除

    def getmsg(self,offset=-10,count=10):   #获取公众号历史文章列表，调用时offset不为负，count为正，count最大为10（未验证）
        if offset == -10 :   #重复无参数调用
            self.params['offset']+=count
            self.params['count'] = count
        else:               #指定参数调用
            self.params['offset'] = offset
            self.params['count'] = count
        url = self.prefix+'profile_ext' 
        params = {  #构造params,因为self.params中含有过多参数，可能引发异常
            'action':'getmsg',
            '__biz':self.params['__biz'],
            'offset':self.params['offset'],
            'count':self.params['count'],
            'is_ok':self.params['is_ok'],
            'scene':self.params['scene'],
            'uin':self.params['uin'],
            'key':self.params['key'],
            'wxtoken':self.params['wxtoken'],
            'f':'json',
            'pass_ticket':self.params['pass_ticket'],
            'appmsg_token':self.params['appmsg_token']
            }
        headers = { #构造header
            'User-Agent':self.headers['User-Agent'],
            }
        cookies = { #构造专用cookie
            'rewardsn':self.appmsgcookie['rewardsn'],
            'wxtokenkey':self.appmsgcookie['wxtokenkey'],
            'wxuin':self.appmsgcookie['wxuin'],
            'devicetype':self.appmsgcookie['devicetype'],
            'version':self.appmsgcookie['version'],
            'lang':self.appmsgcookie['lang'],
            'pass_ticket':self.appmsgcookie['pass_ticket'],
            'wap_sid2':self.appmsgcookie['wap_sid2']
            }
        response = requests.get(url = url,params = params,headers = headers,cookies = cookies,verify = False)
        return response

    def get_article_info(self,appmsg_token,wapsid2):    #获取文章详细信息（如点赞数、评论数）用
        url = self.prefix+'getappmsgext'
        params = {
            'f':'json',
            'uin': self.params['uin'],
            'key':self.params['key'],
            'pass_ticket':self.params['pass_ticket'],
            'wxtoken':self.params['wxtoken'],
            '__biz':self.params['__biz'],
            'devicetype':self.params['devicetype'],
            'clientversion':self.params['clientversion'],
            'appmsg_token':appmsg_token,
            }
        headers = {
            'User-Agent':self.headers['User-agent']
            }
        cookies = { #构造专用cookie
            'rewardsn':self.appmsgcookie['rewardsn'],
            'wxtokenkey':self.appmsgcookie['wxtokenkey'],
            'wxuin':self.appmsgcookie['wxuin'],
            'devicetype':self.appmsgcookie['devicetype'],
            'version':self.appmsgcookie['version'],
            'lang':self.appmsgcookie['lang'],
            'pass_ticket':self.appmsgcookie['pass_ticket'],
            'wap_sid2':wapsid2
            }
        response = requests.post(url = url,headers = headers,params = params,cookies = cookies,verify = False)
        return response
    def get_article_exactinfo(self,url):    #get_article_info的封装函数
        #do something
        return

    def get_comment_info(self,appmsg_token,wapsid2,offset = 0,limit = 100):  #获取评论用，默认获取前100条评论
        url = self.prefix+'appmsg_comment'
        params = {
            'action':'getcomment',
            'scene':self.params['scene'],
            'appmsgid':self.params['appmsgid'],
            'idx':self.params['idx'],
            'comment_id':self.params['comment_id'],
            'offset':0,
            'limit':limit,
            'send_time': '',
            'uin':self.params['uin'],
            'key':self.params['key'],
            'pass_ticket':self.params['pass_ticket'],
            'wxtoken':self.params['wxtoken'],
            'devicetype':self.params['devicetype'],
            'clientversion':self.params['clientversion'],
            '__biz':self.params['__biz'],
            'appmsgtoken':appmsg_token,
            'f':'json'
            }
        headers = {
            'User-Agent':self.headers['User-Agent']
            }
        cookies = { #构造专用cookie
            'rewardsn':self.appmsgcookie['rewardsn'],
            'wxtokenkey':self.appmsgcookie['wxtokenkey'],
            'wxuin':self.appmsgcookie['wxuin'],
            'devicetype':self.appmsgcookie['devicetype'],
            'version':self.appmsgcookie['version'],
            'lang':self.appmsgcookie['lang'],
            'pass_ticket':self.appmsgcookie['pass_ticket'],
            'wap_sid2':wapsid2
            }
        response = requests.get(url = url,params = params,headers = headers,cookies = cookies,verify = False)
        return response

    def get_comment(self,url):  #get_comment_info的封装函数
        appmsg_token,comment_id = self.get_message_for_appmsg_comment(url)  #获取所需的appmsg_token和commentid
        response = self.get_comment_info(appmsg_token,self.commentcookie['wap_sid2'])
        json_data = json.loads(response)

    def decode_list(self):  #解析decode_response得到的json并提取相应数据存到data_decoded
       for i in self.json_urls['list']:
           data = i['comm_msg_info']
           data_temp = {}
           data_temp['id'] = data['id']
           data_temp['type'] = data['type']
           data_temp['time'] = data['datetime']
           data_temp['fakeid'] = data['fakeid']
           data_temp['status'] = data['status']
           data = i['app_msg_ext_info']
           data_temp['title'] = data['title'].replace('&amp','&')   #文章标题
           data_temp['digest'] = data['digest']
           data_temp['fileid'] = data['fileid']
           data_temp['contenturl'] = data['content_url'] #含有用户信息的临时链接
           data_temp['source_url'] = data['source_url'] #文章永久链接
           data_temp['cover'] = data['cover']
           data_temp['subtype'] = data['subtype']
           data_temp['author'] = data['author']
           data_temp['comment'] = self.get_comment(data_temp['contenturl'])
           data_temp['article_info'] = self.get_article_exactinfo()
           self.data_decoded.append(data_temp)
           multi = data['is_multi'] 
           if multi == 1:       #如果本次推送含有多篇文章
               for k in i['multi_app_msg_item_list']:
                   data_temp['title'] = k['title'].replace('&amp','&')
                   data_temp['digest'] = k['digest']
                   data_temp['fileid'] = k['fileid']
                   data_temp['contenturl'] = k['contenturl']
                   data_temp['source_url'] = k['source_url']
                   data_temp['cover'] = k['cover']
                   data_temp['subtype'] = k['subtype']
                   data_temp['author'] = k['author']
                   self.data_decoded.append(data_temp)

    def get_message_for_appmsg_comment(self,url):   #为提取阅读量获取参数：appmsg_token,comment_id
        url = url.replace('http','https').replace('amp;','').replace('#wechat_redirect','')
        response =  requests.get(url = url,cookies = {'wap_sid2':self.commentcookie['wap_sid2']},verify = False)
        appmsg_token = re.search('var appmsg_token   = "(.*)";',response.text).group(0)
        comment_id = re.search('var comment_id = "(.*)" \|\|',response.text).group(0)
        appmsg_token = appmsg_token.replace('var appmsg_token   = "','').replace('";','')
        comment_id = comment_id.replace('var comment_id = "','').replace('" ||','')
        return (appmsg_token,comment_id)

a = params_data()
a.information_init()
response = a.getmsg(0,10)  #初始化并获取第一段
a.decode_response_getmsg(response)
a.decode_list()