
# coding: utf-8

# In[11]:


from datetime import datetime
from bs4 import BeautifulSoup
import requests
import json
import re




#获取评论数函数式
def getCommentCount(newsurl):
    commentURL = 'http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel=gn&newsid=comos-{}&group=&compress=0&ie=utf-8&oe=utf-8&page=1&page_size=20'
    m = re.search('doc-i(.+).shtml',newsurl)
    newsid = m.group(1)
    comments = requests.get(commentURL.format(newsid))
    jd = json.loads(comments.text.strip('var data='))
    return jd['result']['count']['total']



#抓取内文信息函数式
def getNewsDetail(newsurl):
    res = requests.get(newsurl)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text,'html.parser')
    result = {}
    result['newssource'] = soup.select('.time-source span a')[0].text
    time = soup.select('.time-source')[0].contents[0].strip()
    result['dt'] = datetime.strptime(time,'%Y年%m月%d日%H:%M')
    result['article'] = ' '.join([p.text.strip() for p in soup.select('#artibody p')[:-1]])
    result['title'] = soup.select('#artibodyTitle')[0].text
    result['comment'] = getCommentCount(newsurl) 
    return result





#将解析的每条新闻放入list
def parseListLinks(url):
    newsdetails = []
    res  = requests.get(url)
    jd = json.loads(res.text.lstrip('  newsloadercallback(').rstrip(');'))
    for ent in jd['result']['data']:
        newsdetails.append(getNewsDetail(ent['url']))
    return newsdetails



url = 'http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=gnxw&cat_2==gdxw1||=gatxw||=zs-pl||=mtjj&level==1||=2&show_ext=1&show_all=1&show_num=22&tag=1&format=json&page={}&callback=newsloadercallback&_=1509009134105'

news_total = []
for i in range(1,3):
    newsurl = url.format(i)
    newsary = parseListLinks(newsurl)
    news_total.extend(newsary)




import pandas
df = pandas.DataFrame(news_total)
df.head(5)




# In[2]:


#存入xml表格
df.to_excel('news.xlsx')


# In[4]:


#存入数据库
import sqlite3
with sqlite3.connect('news.sqlite') as db:
    df.to_sql('news',con=db)


# In[6]:


#从数据库中取出
with sqlite3.connect('news.sqlite') as db:
    df2 = pandas.read_sql_query('select title from news',con=db)
    
df2

