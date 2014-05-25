
# coding: utf-8

# In[7]:

# Use this version for Python 2
import os
from multiprocessing import Process, Lock
import urllib2
import thread, Queue, time
from bs4 import BeautifulSoup


# In[8]:

class NubiaN5(object):

    def __init__(self, url):
        self.url = url
        self.html_doc = urllib2.urlopen(self.url).read()
        self.soup = BeautifulSoup(self.html_doc, from_encoding="gb18030")
        self.comm_unit = ''
        self.column = [u'用户名',u'等级',u'省份',u'购买日期',u'标签',u'心得']

    def u_name(self):
        try:
            u_name = self.comm_unit.find('div',class_="u-name").text.strip()
        except AttributeError:
            return 'None'
        else:
            return u_name

    def u_level_address(self):
        try:
            temp = self.comm_unit.find('span',class_="u-level").text
        except AttributeError:
            return 'None','None'
        else:
            u_level = temp[:4]
            u_address = temp[-2:] if len(temp) else 'None'
            return u_level,u_address

    def order_date(self):
        try:
            order_date = self.comm_unit.find('div',class_="dl-extra").text.strip().split('\n')[-1]
        except AttributeError:
            return 'None'
        else:
            return order_date

    def comm_label(self):
        try:
            comm_label_t = self.comm_unit.find_all('span',class_="comm-tags")
        except AttributeError:
            return 'None'
        else:
            comm_label = ';'.join([lab.text.strip() for lab in comm_label_t])
            return comm_label

    def comm_cont(self):
        try:
            comm_cont = self.comm_unit.find('dt',text=u'心　　得：').nextSibling.next.text
        except AttributeError:
            return 'None'
        else:
            return comm_cont

    def comm_all(self,idx):
        comm_unit = self.soup.find('div',id="comment-%d" % idx)
        self.comm_unit = comm_unit
        u_name = self.u_name()
        u_level,u_address = self.u_level_address()
        order_date = self.order_date()
        comm_label = self.comm_label()
        comm_cont = self.comm_cont()
        data = [u_name, u_level,u_address, order_date, comm_label, comm_cont]
        return data


# In[10]:

def test(p,dataQueue):
    page = p+1
    # xlsname = 'jd_hw3c%s.xlsx' % str(page)
    url = 'http://club.jd.com/review/1024343-0-%d-0.html' % page
    try:
        jdnubian5 = NubiaN5(url)
    except IOError:
#         comm = pd.DataFrame(data=dataQueue,columns=jdnubian5.column)
#         comm.to_excel(xlsname,'comment')
        print 'IOError'
    else:
        for idx in range(30):
            data=jdnubian5.comm_all(idx)
            idx += p * 30
            data.insert(0,str(idx))
            dataQueue.put(data)

# In[12]:

numconsumers = 4                  # how many consumers to start
numproducers = 4                  # how many producers to start
nummessages  = 420                  # messages per producer to put

safeprint = thread.allocate_lock()    # else prints may overlap
dataQueue = Queue.Queue()             # shared global, infinite size

def producer(idnum, dataQueue):
    for msgnum in range(nummessages):
#         time.sleep(idnum)
        msgnum += idnum * nummessages
        test(msgnum,dataQueue)

def consumer(idnum, dataQueue):
    while True:
        time.sleep(0.1)
        try:
            data = dataQueue.get(block=False)
        except Queue.Empty:
            pass
        else:
            with safeprint:
                with open('temp.txt','a+') as fileout:
                    fileout.write('consumer %s got => %s+\n' % (str(idnum), '\t'.join(data).encode('utf-8')))
                print 'consumer', idnum, 'got =>',data[0]

if __name__ == '__main__':
    with open('temp.txt','w') as fileout:
        fileout.write('')
    for i in range(numconsumers):
        thread.start_new_thread(consumer, (i, dataQueue))
    for i in range(numproducers):
        thread.start_new_thread(producer, (i, dataQueue))
    # time.sleep(((numproducers-1) * nummessages) + 1)
    print 'Main thread exit.'



# In[ ]:

# comm = pd.DataFrame(data=alldata,columns=jdnubian5.column)
# comm.to_excel('jd_hw3c.xlsx','comment')

def test(p):
    alld = []
    page = p+1
    url = 'http://club.jd.com/review/1024343-0-%d-0.html' % page
    try:
        jdnubian5 = NubiaN5(url)
    except IOError:
        print 'IOError'
    else:
        for idx in range(30):
            data=jdnubian5.comm_all(idx)
            idx += p * 30
            data.insert(0,str(idx))
            alld.append(data)
    return alld

def whoami(p,label, lock):
    msg = '%s--%s: name:%s, pid:%s'
    with lock:
        data = test(p)
        with open('temp1.txt','a+') as fileout:
            for x in data:
                fileout.write('%s+\n' % '\t'.join(x).encode('utf-8'))
                print (msg % (x[0], label, __name__, os.getpid()))

def main():
    with open('temp1.txt','w') as fileout:
        fileout.write('')
    lock = Lock()
    ps = []
    print('\nloop4 (updates in parallel children)...')
    for i in range(1681):
        p = Process(target=whoami, args=(i, ('run process %s' % i), lock))
        p.start()
        ps.append(p)
    for p in ps: p.join()
    with lock:
        print('Main process exit.')

if __name__ == '__main__':
    main()
