# coding:utf-8

#_author = Nevermore_luo

import json
import requests
import time
import tushare as ts
from bs4 import BeautifulSoup
from urllib import quote
from config import Dirname

def simple_soup(url,cookies=None,timeout=0.001,retry_count=3,features=''):
    '''
    url->str:accord with URL standards
    cookies->dict: give cookies if necessary
    timeout->float: avoid the tragedy 's happening again 
    retry_count->int:repeat times if failed
    features->str:'lxml','html.parser','xml','html5lib'
    normally we don't need it,unless bs4 get many features and raise an error
    you can solve it with this kw
    
    return->soup if succeed
    
    use requests,bs4 to read HTML,lazy soup for me :)
    '''
    #set headers user_agent,chrome F12
    user_agent = (
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
    )
    #repeat if necessary
    for i in range(retry_count):
        try:
            #create session
            session = requests.session()
            session.headers['User-Agent'] = user_agent
            html = session.get(url,cookies=cookies).content
            #normally we dont use this('lxml'),unless system install two version bs4
            soup = BeautifulSoup(html,features)
        except:
            soup = None
        if soup:
            return soup
        #print an error if we got nothing
        print('Alreadly try %s times,but failed, url:%s...'%(i,url))
        #take a break
        time.sleep(timeout)
    raise RuntimeError('Please check your URL or BeautifulSoup...')

    
    
def _update(name,new):
    '''
    new->dict:
    '''
    with open(name,'a') as f:pass
    with open(name) as f1:fr = f1.read()
    data = json.loads(fr) if fr else {}
    n = {i.encode('utf8'):data[i] for i in data}
    n.update(new)
    with open(name,'w') as f2:json.dump(n,f2)
    
    
class Douban_info(object):
    
    def __init__(self,name):
        self.name = name.encode('utf-8') if isinstance(name,unicode) else name
        kw = quote(self.name)
        basicurl = 'https://movie.douban.com/subject_search?search_text=%s&cat=1002'%kw
        soup = simple_soup(basicurl,features='lxml')
        self.douban_url = soup.select('td > div > a')[0]['href']
        self.soup = simple_soup(self.douban_url,features='lxml')
        self.message = (
            'Movie: %s\nDouban-Star: %s\n'
            'Genre: %s\nDirector: %s\n'
            'Starring: %s\n'
            'More information: %s\n'
            )
        self.model = {
                        'genre':['span',{'property':"v:genre"}],
                        'director':['a',{'rel':"v:directedBy"}],
                        'starring':['a',{'rel':"v:starring"}]
                    }
        
    def get_summary(self):
        text = self.soup.find('span',property="v:summary").text.lstrip()
        self.summary = text[:70].encode('utf8')+'......'
        return self.summary
    
    def get_star(self):
        self.star = self.soup.find('strong',property="v:average").text.encode('utf8')
        return self.star
    
    def _get_m(self,y,tag,**kw):
        text = '/'.join(i.text for i in 
                             self.soup.find_all(tag,**kw)).encode('utf8')
        setattr(self,y,text)
        
    def info(self):
        self.get_summary()
        self.get_star()
        [self._get_m(i,self.model[i][0],**self.model[i][1]) for i in self.model]
        self.starring = (self.starring.decode('utf8')[:20]+'......').encode('utf-8')
        output = self.message%(self.name, self.star, self.genre, 
                                self.director, self.starring, 
                                self.douban_url)
        return output
    
    
    
class BucketList(object):
    
    def __init__(self):
        with open(Dirname,'a') as f:pass
        with open(Dirname) as f1:fr = f1.read()
        data = json.loads(fr) if fr else {}
        self.bucket_list = [a.encode('utf8') for a,b in data.items() if b]
        for i in self.bucket_list:print i
    
    def _search_download(self,movie):
        basicurl = 'http://www.quqifun.com/movie/?focus=af&type=at&region=ar&q=%s'%quote(movie)
        soup = simple_soup(basicurl,features='lxml')
        url = 'http://www.quqifun.com/%s'%soup.find('div',{'class':'movie_name'}).a['href']
        soup = simple_soup(url,features='lxml')
        download = soup.find('input',{'id':'down_url'})['value']
        return download
        
        
    def refresh(self):
        self.new = {}
        for i in self.bucket_list:
            try:
                self.new[i] = self._search_download()
            except:
                pass
        if self.new:
            _update(Dirname,self.new)
        return self.new


class NewMovie(object):

    def __init__(self):
        pass
        
    def today_top_movies(self):
        #获得当日电影实时票房数据DF
        movie_df = ts.realtime_boxoffice()
        #将票房数据转化为int和float以便调用
        movie_df[['Irank','movieDay']] = movie_df[['Irank','movieDay']].astype(int)
        movie_df[['BoxOffice','boxPer','sumBoxOffice']] = movie_df[['BoxOffice','boxPer','sumBoxOffice']].astype(float)
        #计算前十名日均票房
        movie_df['dayboxoffice'] = movie_df.sumBoxOffice/movie_df.movieDay
        #返回所需数据,上映两周之内日均票房一千万以上，当日票房占比百分之十以上
        result = movie_df.ix[(movie_df.movieDay<15) & (movie_df.dayboxoffice>1000) & (movie_df.boxPer>10)]
        self.today_goods = [i.encode('utf8') for i in list(result.MovieName)]
        return self.today_goods
        
    def update(self):
        if not hasattr(self,'today_goods'):
            self.today_top_movies()
        with open(Dirname,'a') as f:pass
        with open(Dirname) as f1:fr = f1.read()
        data = json.loads(fr) if fr else {}
        
        if self.today_goods:
            self.new = [i for i in self.today_goods if i.decode('utf-8') not in data]
            _update(Dirname,{x:None for x in self.today_goods})
        else:
            self.new = []
        return self.new





