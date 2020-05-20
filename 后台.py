#   由于微信验证方式的原因，只能爬取文章，不能爬取评论和点赞数等详细信息
#   一个挺失败的项目，代码中会含有大量尝试获取评论、点赞但失败的残留
#   有空的话会处理一下残留的，现在就先这样吧……
import json
import requests
import re
import copy
import time
class params_data():
    def __init__(self):
        self.msgcookie = {} #为提取不同行为用的不同cookie分配空间
        self.msgparams = {}
        self.msgheaders = {}
        #self.commentcookie = {}
        #self.commentparams = {}
        #self.commentheaders = {}
        #self.appmsgcookie = {}
        #self.appmsgparams = {}
        #self.appmsgheaders = {}
        self.headers = {}
        self.prefix = 'https://mp.weixin.qq.com/mp/'    #网址前缀
        self.suffix = ''    #网址后缀
        self.url = ''       #完整网址
        self.msgparams['offset'] = 0   #默认偏移量为0
        self.msgparams['count'] = 10   #默认步进为10
        self.json_data = {}
        self.data_decoded = []

    def information_init(self):
        print("注意，下列输入均输入至cookie行（包含该行）结束，如果有多余数据请勿输入，防止数据污染")
        print("请输入action = getmsg的header")
        self.decode_headers('getmsg')
        #下方函数已废弃，第一次release后删除
        #print("请输入action = getcomment的header")
        #self.decode_headers('getcomment')
        #print("请输入后缀为getappmsgext的header")
        #self.decode_headers('getappmsg')

    def decode_url(self,url,flag):   #获取网址信息函数，flag请填写成'getmsg'
        temp = url.split('?')   #将网址数据区剥离
        data = temp[1]          #提取数据
        temp = data.split('&')  #将数据分块
        for i in temp:
            data = i.split('=',1) #提取变量名和值
            if flag == 'getmsg':
                self.msgparams[data[0]] = data[1]  #向数据字典中添加数据
            #elif flag == 'getcomment':
            #    self.commentparams[data[0]] = data[1]
            #else :
            #    self.appmsgparams[data[0]] = data[1]

    def decode_cookie(self,cookie,flag): #获取cookie函数（cookie需要ctrl+c复制自fiddler）,cookie形如 Cookie: rewardsn=;wxtokenkey=777;
        temp = cookie.split(': ')   #将cookie分块
        cookie = temp[1]            #去掉无用的Cookie: 前缀
        temp = cookie.split('; ')
        for i in temp:              #处理所有cookie数据
            temp2 = i.split('=',1)
            if flag == 'getmsg':
                self.msgcookie[temp2[0]] = temp2[1]
            #elif flag == 'getcomment':
            #    self.commentcookie[temp2[0]] = temp2[1]  #提取action = getcomment的cookie数据
            #else: 
            #    self.appmsgcookie[temp2[0]] = temp2[1]


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
                    #elif flag == 'getcomment':
                    #    self.commentheaders[temp[0]] = temp[1]
                    #else:
                    #    self.appmsgheaders[temp[0]] = temp[1]                        
            except:
                break

    def decode_response_getmsg(self,response):  #解析action = getmsg时获取的json
        self.json_data = json.loads(response.text)
        self.json_urls = json.loads(self.json_data['general_msg_list'])

    #def decode_response_appmsg(self,response):  #解析后缀为getappmsgext时获取的json
    #    #do something
    #    return

    #def decode_response_comment():              #解析action = getcomment时获取的json
    #    #do something
    #    return

    def getmsg(self,count=-1,offset=-1):   #获取公众号历史文章列表，调用时offset不为负，count为正，count最大为10（未验证），初次调用一定要指定调用参数
        if offset == -1 :   #不指定偏移量
            if count == -1: #无参数重复调用
                self.msgparams['offset']+=self.msgparams['count']
            else:           #指定count参数大小
                self.msgparams['count'] = count
                self.msgparams['offset']+=count
        else:               #完全指定参数调用
            self.msgparams['offset'] = offset
            self.msgparams['count'] = count
        url = self.prefix+'profile_ext' 
        params = {  #构造params,因为self.params中含有过多参数，可能引发异常
            'action':'getmsg',
            '__biz':self.msgparams['__biz'],
            'offset':self.msgparams['offset'],
            'count':self.msgparams['count'],
            'is_ok':self.msgparams['is_ok'],
            'scene':'124',
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
        response = requests.get(url = url,params = params,headers = headers,cookies = cookies,verify = False)
        return response

    #def get_article_info(self,appmsg_token,wapsid2):    #获取文章详细信息（如点赞数、评论数）
    #    url = self.prefix+'getappmsgext'
    #    appmsgparams = {
    #        'f':'json',
    #        'uin': self.appmsgparams['uin'],
    #        'key':self.appmsgparams['key'],
    #        'pass_ticket':self.appmsgparams['pass_ticket'],
    #        'wxtoken':self.appmsgparams['wxtoken'],
    #        '__biz':self.appmsgparams['__biz'],
    #        'devicetype':self.appmsgparams['devicetype'],
    #        'clientversion':self.appmsgparams['clientversion'],
    #        'appmsg_token':appmsg_token,
    #        }
    #    headers = {
    #        'User-Agent':self.appmsgheaders['User-agent']
    #        }
    #    cookies = { #构造专用cookie
    #        'rewardsn':self.appmsgcookie['rewardsn'],
    #        'wxtokenkey':self.appmsgcookie['wxtokenkey'],
    #        'wxuin':self.appmsgcookie['wxuin'],
    #        'devicetype':self.appmsgcookie['devicetype'],
    #        'version':self.appmsgcookie['version'],
    #        'lang':self.appmsgcookie['lang'],
    #        'pass_ticket':self.appmsgcookie['pass_ticket'],
    #        'wap_sid2':wapsid2
    #        }
    #    response = requests.post(url = url,headers = headers,params = params,cookies = cookies,verify = False)
    #    return response
    #def get_article_exactinfo(self,url):    #get_article_info的封装函数
    #    #do something
    #    return

    #def get_comment_info(self,appmsg_token,wapsid2,offset = 0,limit = 100):  #获取评论用，默认获取前100条评论
    #    url = self.prefix+'appmsg_comment'
    #    params = {
    #        'action':'getcomment',
    #        'scene':self.commentparams['scene'],
    #        'appmsgid':self.commentparams['appmsgid'],
    #        'idx':self.commentparams['idx'],
    #        'comment_id':self.commentparams['comment_id'],
    #        'offset':0,
    #        'limit':limit,
    #        'send_time': '',
    #        'uin':self.commentparams['uin'],
    #        'key':self.commentparams['key'],
    #        'pass_ticket':self.commentparams['pass_ticket'],
    #        'wxtoken':self.commentparams['wxtoken'],
    #        'devicetype':self.commentparams['devicetype'],
    #        'clientversion':self.commentparams['clientversion'],
    #        '__biz':self.commentparams['__biz'],
    #        'appmsgtoken':appmsg_token,
    #        'f':'json'
    #        }
    #    headers = {
    #        'User-Agent':self.commentheaders['User-Agent']
    #        }
    #    cookies = { #构造专用cookie
    #        'rewardsn':self.commentcookie['rewardsn'],
    #        'wxtokenkey':self.commentcookie['wxtokenkey'],
    #        'wxuin':self.commentcookie['wxuin'],
    #        'devicetype':self.commentcookie['devicetype'],
    #        'version':self.commentcookie['version'],
    #        'lang':self.commentcookie['lang'],
    #        'pass_ticket':self.commentcookie['pass_ticket'],
    #        'wap_sid2':wapsid2
    #        }
    #    response = requests.get(url = url,params = params,headers = headers,cookies = cookies,verify = False)
    #    return response

    #def get_comment(self,url):  #get_comment_info的封装函数
    #    appmsg_token,comment_id = self.get_message_for_appmsg_comment(url)  #获取所需的appmsg_token和commentid
    #    response = self.get_comment_info(appmsg_token,self.commentcookie['wap_sid2'])
    #    json_data = json.loads(response)

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
           #data_temp['comment'] = self.get_comment(data_temp['contenturl'])
           #data_temp['article_info'] = self.get_article_exactinfo()
           self.data_decoded.append(copy.deepcopy(data_temp))
           multi = data['is_multi'] 
           if multi == 1:       #如果本次推送含有多篇文章
               for k in i['app_msg_ext_info']['multi_app_msg_item_list']:
                   data_temp['title'] = k['title'].replace('&amp','&')
                   data_temp['digest'] = k['digest']
                   data_temp['fileid'] = k['fileid']
                   data_temp['content_url'] = k['content_url']
                   data_temp['source_url'] = k['source_url']
                   data_temp['cover'] = k['cover']
                   data_temp['author'] = k['author']
                   self.data_decoded.append(copy.deepcopy(data_temp))

    def spider(self,count = 10,offset = -10):   #爬取文章的封装函数，输入offset非负，count不大于10
        self.information_init()
        self.msgparams['count'] = count
        self.msgparams['offset'] = offset
        self.json_data['can_msg_continue'] = 1  #设定初始值，使while可以开始，该值在加载操作中会被覆盖掉，不影响后面的处理
        while (self.json_data['can_msg_continue'] == 1):
            try:
                response = self.getmsg()                #请求json
                self.decode_response_getmsg(response)   #加载返回的json
                self.decode_list()                      #解析json数据
            except:
                return (self.data_decoded,self.msgparams['offset'],self.msgparams['count'],False)   #出错退出，返回已经获取的数据
        return (self.data_decoded,self.msgparams['offset'],self.msgparams['count'],True)    #完成爬取，返回信息

    #def get_message_for_appmsg_comment(self,url):   #为提取阅读量获取参数：appmsg_token,comment_id
    #    url = url.replace('http','https').replace('amp;','').replace('#wechat_redirect','')
    #    response =  requests.get(url = url,cookies = {'wap_sid2':self.commentcookie['wap_sid2']},verify = False)
    #    appmsg_token = re.search('var appmsg_token   = "(.*)";',response.text).group(0)
    #    comment_id = re.search('var comment_id = "(.*)" \|\|',response.text).group(0)
    #    appmsg_token = appmsg_token.replace('var appmsg_token   = "','').replace('";','')
    #    comment_id = comment_id.replace('var comment_id = "','').replace('" ||','')
    #    return (appmsg_token,comment_id)

a = params_data()
a.spider()