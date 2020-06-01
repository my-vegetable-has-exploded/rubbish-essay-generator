# -*- encoding=UTF-8
import re
import json
import random
import requests
from goose3 import Goose
from goose3.text import StopWordsChinese  # 导入停用词
from bs4 import BeautifulSoup
from lxml import etree
import tkinter as tk  # 使用Tkinter前需要先导入
from tkinter import ttk
import sys
import time


def get_access_result(target_url="https://cn.bing.com/", search_word=None):
    """
        Args:
            str:输入搜索字符串

        Returns:
            res:requests返回的response对象

        Raises:
            statuserror:爬取失败

    """
    args = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    url = target_url
    search = {}
    if search_word is not None:
        search['q'] = search_word
    try:
        res = requests.get(url, headers=args, params=search,
                           timeout=10)  # 设置访问时间，超时便访问失败
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        # print(res.text[:1000])
        return res
    # except TimeoutError as tout:
    #     print('Can\'t access to website:'+target_url)
    #     return None
    except Exception as e:
        print(e)
        print("spider failed")
        return None


class Ciba:
    '''使用金山词霸翻译

    Attributes:
        url: 金山词霸post方法的url
        headers: 报头参数

    '''

    def __init__(self):
        # self.word = word
        self.url = 'http://fy.iciba.com/ajax.php?a=fy'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
        }

    # 发送请求
    def request_post(self, word, from_lang='auto', to_lang='auto'):
        """
            Args:
                word:翻译内容
                from_lang：源语言
                to_lang：目标语言

            return：
                None：访问失败
                res.content.decode()：解码后的文本

            Raises：
                statuserror:爬取失败            
        """
        payload = {
            'f': from_lang,
            't': to_lang,
            'w': word
        }
        try:
            res = requests.post(
                url=self.url, headers=self.headers, data=payload)
            res.raise_for_status()
            # print(res.content.decode())
            return res.content.decode()
        except Exception as e:
            print(e)
            return None
    # 解析数据
    @staticmethod
    def parse_data(data):
        """
            Args：
                data：爬虫解码后的文本

            return：
                dict_data['content']['out']:文字段翻译结果
                dict_data['content']['word_mean']：词语翻译结果
        """
        dict_data = json.loads(data)  # 使用json解析
        if 'out' in dict_data['content']:  # 文字段翻译
            return dict_data['content']['out']
        elif 'word_mean' in dict_data['content']:  # 词语翻译
            return dict_data['content']['word_mean']

    def translate(self, word, from_lang='auto', to_lang='auto'):
        """
            Args:
                word:翻译内容
                from_lang：源语言
                to_lang：目标语言

            return：
                None：访问失败
                res.content.decode()：解码后的文本           
        """
        data = self.request_post(word, from_lang, to_lang)
        if(data == None):
            return ''
        return self.parse_data(data)


class Bing:
    '''使用金山词霸翻译

    Attributes:
        url: bing翻译post方法的url
        headers: 报头参数

    '''

    def __init__(self):
        # self.word = word
        self.url = 'https://cn.bing.com/ttranslatev3?'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
        }

    # 发送请求

    def request_post(self, word, from_lang='auto-detect', to_lang='auto-detect'):
        """
            Args:
                word:翻译内容
                from_lang：源语言
                to_lang：目标语言

            return：
                None：访问失败
                res.content.decode()：解码后的文本

            Raises：
                statuserror:爬取失败            
        """
        if(from_lang == 'zh'):
            from_lang = 'zh-Hans'
        if(to_lang == 'zh'):
            to_lang = 'zh-Hans'
        data = {
            'fromLang': from_lang,
            'text': word,
            'to': to_lang
        }
        try:
            res = requests.post(url=self.url, headers=self.headers, data=data)
            res.raise_for_status()
            # print(res.content.decode())
            return res.content.decode()
        except Exception as e:
            print(e)
            return None
    # 解析数据
    @staticmethod
    def parse_data(data):
        """
            Args：
                data：爬虫解码后的文本

            return：
                dict_data[0]['translations'][0]['text']:翻译结果
        """
        dict_data = json.loads(data)  # 使用json解析
        return dict_data[0]['translations'][0]['text']

    def translate(self, word, from_lang='auto-detect', to_lang='auto-detect'):
        """
            Args:
                word:翻译内容
                from_lang：源语言
                to_lang：目标语言

            return：
                None：访问失败
                res.content.decode()：解码后的文本           
        """
        data = self.request_post(word, from_lang, to_lang)
        if(data == None):
            return ''
        return self.parse_data(data)


class bing_engine:
    '''使用bing搜索

    Attributes:
        url: bing搜索根目录url
        headers: 报头参数

    '''

    def __init__(self):
        self.url = "https://bing.com/"
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}

    def search(self, search_word=None):
        """
            Args:
                search_word:输入搜索字符串

            Returns:
                clean_res:返回一组搜索结果和链接

            Raises:
                statuserror:爬取失败

        """
        search_para = {}
        if str is not None:
            search_para['q'] = search_word
        try:
            res = requests.get(
                url=self.url, headers=self.headers, params=search_para)
            res.raise_for_status()
            res.encoding = res.apparent_encoding
            # print(res.text[:1000])
            soup = BeautifulSoup(res.text, 'lxml')
            clean_res = []
            for i in soup.findAll(name=['a'], target='_blank', text=re.compile('[^帮助]')):
                # print(i.string,'\n',i.attrs['href'])
                clean_res.append((i.string, i.attrs['href']))
            return clean_res
        except Exception as e:
            print(e)
            print("spider failed")
            return []


class san60_engine:
    '''使用360搜索

    Attributes:
        url: 360搜索根目录url
        headers: 报头参数

    '''

    def __init__(self):
        self.url = "https://www.so.com/s"
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}

    def search(self, search_word=None):
        """
            Args:
                search_word:输入搜索字符串

            Returns:
                clean_res:返回一组搜索结果和链接

            Raises:
                statuserror:爬取失败
        """
        search_para = {}
        if search_word is not None:
            search_para['q'] = search_word
        try:
            res = requests.get(
                url=self.url, headers=self.headers, params=search_para)
            res.raise_for_status()
            res.encoding = res.apparent_encoding

            tree = etree.HTML(res.text)
            url_list = tree.xpath('//h3[@class]/a[@href]/@href')
            for i in range(0, len(url_list)):
                if 'link' in url_list[i]:
                    try:
                        tmp_url = requests.get(url_list[i])
                        # print(tmp_url.text)
                        patt = re.compile('replace(.*?)</script>')
                        url_list[i] = eval(re.findall(patt, tmp_url.text)[0])
                        # print(eval(re.findall(patt,tmp_url.text)[0]))
                    except Exception as e:
                        print(e)
                        print("spider failed")
            content_list = tree.xpath('//h3[@class]/a[@href]/text()')
            clean_res = list(zip(content_list[:-1], url_list[:-1]))
            return clean_res

        except Exception as e:
            print(e)
            print("spider failed")
            return None


class sogou_engine:
    '''使用搜狗搜索

     Attributes:
        url: bing搜索根目录url
        headers: 报头参数
    '''

    def __init__(self):
        self.url0 = "https://www.sogou.com"
        self.url = "https://www.sogou.com/web"
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}

    def search(self, search_word=None):
        """
            Args:
                search_word:输入搜索字符串

            Returns:
                clean_res:返回一组搜索结果和链接

            Raises:
                statuserror:爬取失败

        """
        search_para = {}
        if search_word is not None:
            search_para['query'] = search_word
        try:
            res = requests.get(
                url=self.url, headers=self.headers, params=search_para)
            res.raise_for_status()
            res.encoding = res.apparent_encoding
            tree = etree.HTML(res.text)
            # soup=BeautifulSoup(res.text,'lxml')
            # print(res.url)
            # print(soup.prettify())
            url_list = tree.xpath(
                '//h3/a[@id and @target="_blank" and @href]/@href')
            for i in range(0, len(url_list)):
                if 'link' in url_list[i]:
                    url_list[i] = self.url0+url_list[i]
                    try:
                        tmp_url = requests.get(url_list[i])
                        # print(tmp_url.text)
                        patt = re.compile('replace(.*?)</script>')
                        url_list[i] = eval(re.findall(patt, tmp_url.text)[0])
                        # print(eval(re.findall(patt,tmp_url.text)[0]))
                    except:
                        pass
            content_list = tree.xpath(
                '//h3/a[@id and @target="_blank" and @href]/text()')
            clean_res = list(zip(content_list, url_list))
            return clean_res
        except Exception as e:
            print(e)
            print("spider failed")
            return None


def get_paragrams(search_res):
    """
        Args:
            search_res:返回一组搜索结果和链接

        Returns:
            clean_res:返回所有链接的正文段落

        Raises:
            e:文章段落分割异常
    """
    paras = []
    goose = Goose({'browser_user_agent': 'Mozilla', 'parser_class': 'soup',
                   'stopwords_class': StopWordsChinese})  # 设置goose参数
    for ind, res_elem in enumerate(search_res):
        try:
            res_herf = res_elem[1]
            if get_access_result(target_url=res_herf) == None:  # 测试是否可以访问
                print('Can\'t access to website:'+res_herf)
                continue
            article = goose.extract(url=res_herf)  # 正文提取 异常处理
            paras.extend(list(article.cleaned_text.split()))  # 分割成段
        except Exception as e:
            print("Fail to split paragrams in", res_elem[1], end='  ')
            print(e)
            continue
    return paras


def gene_shuffle_article(search_res, word_limit=800):
    """
        Args:
            search_res:返回一组搜索结果和链接
            word_limit:文章最低字数限制
        Returns:
            article_gene:返回随机打乱后组合的文章

        Raises:
            e:段落组合失败

    """
    paragrams = get_paragrams(search_res)  # 获取段落
    # print(len(paragrams))
    total_paras = len(paragrams)  # 总段落
    article_gene, total_words = '', 0  # 生成文章与已加入段落数
    st, total_st = set(), 0  # 使用过的段落集合
    try:
        while total_words <= word_limit and total_st <= 0.2*total_paras:  # 使用不超过20%的段落，字数超过后停止
            i = random.randint(0, total_paras-1)  # 生成不重复的随机数
            if(i not in st):  # 不重复
                st.add(i)  # 插入集合
                total_words += len(paragrams[i])  # 总字数增加
                total_st += 1  # 总段落数增加
                article_gene += paragrams[i]+'\n'  # 段落拼接
            else:
                continue  # 重复则略过
    except Exception as e:
        print(e)
    return article_gene


def rubbish_essay(search_word=' ', search_engine='bing', trans_engine='ciba', word_limit=800, text1=' ',  confusion_level=1):
    """
        Args:
            search_word:搜索主题
            search_engine: 搜索引擎
            trans_engine: 翻译引擎
            word_limit: 最少字数
            confusion_level: 混淆程度
        Returns:
            warning: engine doesn't exist or word_limit is too large 
            article_gene:返回随机打乱后组合的文章

    """
    if search_engine == 'bing':  # 选择搜索引擎
        s_engine = bing_engine()
    elif search_engine == '360':
        s_engine = san60_engine()
    elif search_engine == 'sogou':
        s_engine = sogou_engine()
    else:
        return 'Please use a supported translation engine.'
    search_res = s_engine.search(search_word)
    text1.insert('end', "搜索完成\n")
    text1.update()
    article_gene = gene_shuffle_article(search_res, word_limit)
    text1.insert('end', "爬取搜索结果完成\n")
    text1.update()
    if trans_engine == 'ciba':  # 选择翻译引擎
        t_engine = Ciba()
    elif trans_engine == 'bing':
        t_engine = Bing()
    else:
        return "Please use a supported translation engine."
    if len(article_gene) == 0:  # 无搜索结果返回
        return 'No result for {}'.format(search_word)

    text1.insert('end', "随机生成文本完成\n")
    text1.update()
    article_final = ''
    for paragram in article_gene.split():  # 按段落翻译，防止超字数限制
        paragram_zh = paragram
        while confusion_level:
            confusion_level -= 1
            paragram_en = t_engine.translate(
                word=paragram_zh, from_lang='zh', to_lang='en')
            paragram_zh = t_engine.translate(
                word=paragram_en, from_lang='en', to_lang='zh')
        article_final += paragram_zh+'\n'
    text1.insert('end', "文章互译完成\n")
    text1.update()
    if len(article_final) < word_limit:  # 小于最小字长
        article_final = "The required number of words is too large.\n"+article_final
    return article_final


# 第1步，实例化object，建立窗口window
window = tk.Tk()

# 第2步，给窗口的可视化起名字
window.title('文章生成器')

# 第3步，设定窗口的大小(长 * 宽)
window.geometry('1500x1300')  # 这里的乘是小x

# 第4步，在图形界面上设定标签
l1 = tk.Label(window, text='请在您将要查询的主题后加上所需的文章类型，如“抗击疫情感想”，以免影响到文章的生成效果',
              bg='white', font=('Arial', 12), width=130, height=2)
# 说明： bg为背景，font为字体，width为长，height为高，这里的长和高是字符的长和高，比如height=2,就是标签有2个字符这么高

# 第5步，放置标签
l1.place(x=150, y=10)    # Label内容content区域放置位置，自动调节尺寸
# 放置lable的方法有：1）l.pack(); 2)l.place()


gettopic = tk.Entry(window, show=None, font=('宋体', 24), width=40)  # 输入的主题
gettopic.place(x=300, y=60)

getnumber = tk.Entry(window, show=None, font=('宋体', 24), width=5)  # 输入需要的字符数量
getnumber.place(x=700, y=120)
l3 = tk.Label(window, text='请输入需要的字符数量 ：', bg='white',
              font=('宋体', 12), width=30, height=2)
l3.place(x=430, y=120)


cv = tk.StringVar()
getengine = ttk.Combobox(window, width=12, height=3)  # 搜索引擎的下拉框
getengine.place(x=945, y=60)
# 设置下拉数据
getengine["value"] = ("请选择搜索引擎", "360", "bing", "sogou")
getengine.current(0)


cv1 = tk.StringVar()
getsoftware = ttk.Combobox(window, width=12, height=3)   # 翻译软件的下拉框
getsoftware.place(x=790, y=120)
# 设置下拉数据
getsoftware["value"] = ("请选择翻译软件", "ciba", "bing")
getsoftware.current(0)

text = tk.Text(window, font=('宋体', 14), width=110, height=30)  # 最后输出文章的文本框
text.place(x=300, y=200)

l4 = tk.Label(window, text='进度提示 ：', bg='white',
              font=('宋体', 12), width=25, height=2)
l4.place(x=50, y=300)
text1 = tk.Text(window, font=('宋体', 14), width=20, height=10)  # 进度提示的文本框
text1.place(x=50, y=340)


def show():
    text.tk.call(text._w, 'delete', 1.0, 'end')
    text1.tk.call(text1._w, 'delete', 1.0, 'end')
    text.update()
    text1.update()
    topic = gettopic.get()
    number = getnumber.get()
    engine = getengine.get()
    software = getsoftware.get()
    artical = rubbish_essay(search_word=topic, search_engine=engine,
                            trans_engine=software, word_limit=int(number), text1=text1)
    text.insert('end', artical)
    text.update()
    return None


botton = tk.Button(window, text='开始生成文章', bg='white', font=(
    '宋体', 12), width=15, height=2, command=show)  # 开始生成文章的按钮
botton.place(x=900, y=120)

# 第6步，主窗口循环显示
window.mainloop()
