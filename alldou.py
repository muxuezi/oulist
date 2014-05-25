# coding: utf-8

# In[7]:

# Use this version for Python 2
import urllib2
import thread, Queue, time
from bs4 import BeautifulSoup

def test(idx, name, url,allpage, dataQueue):
    for page in allpage:
        aurl = '%s?start=%d' % (url.split('?')[0],page)
        html_doc = urllib2.urlopen(aurl).read()
        soup = BeautifulSoup(html_doc, from_encoding="gb18030")
        for itemchild in soup.findAll('li', class_='carditem card-story-large'):
            name = itemchild.find('a').get('title').strip()
            link = itemchild.find('a').get('href')
            price = itemchild.find('span', class_="commodity-price").text
            cons = soup.find('ul', class_="stats-list").text.split()
            data= [str(idx), name, link, price]+cons
            dataQueue.put(data)

# In[12]:

numconsumers = 4                  # how many consumers to start
numproducers = 4                  # how many producers to start
nummessages  = 748                  # messages per producer to put

safeprint = thread.allocate_lock()    # else prints may overlap
dataQueue = Queue.Queue()             # shared global, infinite size

def producer(life_name_link, idnum, dataQueue):
    for msgnum in range(nummessages):
        msgnum += idnum * nummessages
        name, url = life_name_link[msgnum].split('\t')
        url = url.strip()
        # print url
        html_doc = urllib2.urlopen(url).read()
        soup = BeautifulSoup(html_doc, from_encoding="gb18030")
        try:
            tempage = soup.find('div',class_='paginator').text
        except AttributeError:
            allpage = [0]
        else:
            lenpage = int(tempage.split()[-2])
            allpage = map(lambda x: 20*x, range(lenpage))
        finally:
            print url,allpage
            test(msgnum,name, url,allpage, dataQueue)

def consumer(idnum, dataQueue):
    while True:
        time.sleep(0.1)
        try:
            data = dataQueue.get(block=False)
        except Queue.Empty:
            pass
        else:
            with safeprint:
                with open('doutemp2.txt','a+') as fileout:
                    fileout.write('consumer %s got => %s+\n' % (str(idnum), '\t'.join(data).encode('utf-8')))
                print 'consumer', idnum, 'got =>',data[0]

if __name__ == '__main__':
    life_name_link = open('doulist.txt','r').readlines()
    with open('doutemp2.txt','w') as fileout:
        fileout.write('')
    for i in range(numconsumers):
        thread.start_new_thread(consumer, (i, dataQueue))
    for i in range(numproducers):
        thread.start_new_thread(producer, (life_name_link, i, dataQueue))
    # time.sleep(((numproducers-1) * nummessages) + 1)
    print 'Main thread exit.'
