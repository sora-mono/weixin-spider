    def save_data(self,offset):     #保存数据
        print("正在保存数据，请稍候")
        fp = open('./result.csv','w',encoding='utf-8')
        writer = csv.writer(fp)
        temp_list = []
        writer.writerow(['序号','发布时间','作者','永久链接','临时链接','封面网址'])
        for i in self.data_decoded:
            temp_list.clear()
            temp_list.append(i['inside_id'])
            temp_list.append(i['time'])
            temp_list.append(i['author'])
            temp_list.append(i['source_url'])   #文章永久链接
            temp_list.append(i['contenturl'])  #文章临时链接
            temp_list.append(i['cover'])        #文章封面网址
            writer.writerow(temp_list)
        fp.close()
        fp = open('./ext.ini','w',encoding='utf-8')
        fp.write('offset ='+str(offset))
        fp.close()
