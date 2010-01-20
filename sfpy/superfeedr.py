import time
import xmpp
from xmpp.protocol import Iq
import xml.etree.ElementTree as ET
SF_HOST = "superfeedr.com"
# import logging
# log = logging.getLogger("superfeedr")
# log.debug('starting SuperFeedr')

class SuperFeedr(object):
    def __init__(self,jid,password):
        self.client = xmpp.Client(server=SF_HOST,debug=[])
        self.client.connect(server=(SF_HOST,5222))
        self.jid = jid
        name = xmpp.protocol.JID(jid)
        self.client.auth(name.getNode(), password)
        self.client.sendInitPresence()
        
        self.client.RegisterHandler('message',self.superfeedr_msg)
        self.func = str
        return

    def subscribe(self,feed):
        data = Iq(typ='set',to=SF_HOST,frm=self.jid)
        child = data.addChild('pubsub',namespace='http://jabber.org/protocol/pubsub')
        child.addChild('subscribe', {'node': feed, 'jid': self.jid})
        self.client.send(data)
        time.sleep(1)
        self.client.Process(1)
        return 1

    def unsubscribe(self,feed):
        data = Iq(typ='set',to=SF_HOST,frm=self.jid)
        child = data.addChild('pubsub',namespace='http://jabber.org/protocol/pubsub')
        child.addChild('unsubscribe', {'node': feed, 'jid': self.jid})
        self.client.send(data)
        time.sleep(1)
        self.client.Process(1)
        return 1
    
    def monitor(self):
        while True:
            try:
                r= self.client.Process(1)
            except Exception as e:
		#log.debug( 'exception occurred:'+ str(e))
                #log.debug('continuing...')
                pass
        return

    def superfeedr_msg(self,con,m):
        mstr = m.__str__()
        s = mstr.encode('utf8')
        xml = ET.fromstring(s)
        event = {}
        statusx = xml.find('{http://jabber.org/protocol/pubsub#event}event/{http://superfeedr.com/xmpp-pubsub-ext}status')
        httpx = xml.find('{http://jabber.org/protocol/pubsub#event}event/{http://superfeedr.com/xmpp-pubsub-ext}status/{http://superfeedr.com/xmpp-pubsub-ext}http')
        next_fetchx = xml.find('{http://jabber.org/protocol/pubsub#event}event/{http://superfeedr.com/xmpp-pubsub-ext}status/{http://superfeedr.com/xmpp-pubsub-ext}next_fetch')
        itemsx = xml.find('{http://jabber.org/protocol/pubsub#event}event/{http://jabber.org/protocol/pubsub#event}items')
        entriesx = xml.findall('{http://jabber.org/protocol/pubsub#event}event/{http://jabber.org/protocol/pubsub#event}items/{http://jabber.org/protocol/pubsub#event}item/{http://www.w3.org/2005/Atom}entry')
        #print dict(statusx=statusx, httpx=httpx, next_fetchx=next_fetchx, itemsx=itemsx,entriesx= entriesx)
        if None not in (statusx, httpx, next_fetchx, itemsx, entriesx):
            event['xml'] = xml
            event['feed'] = itemsx.get('node')
            event['http'] = (httpx.get('code'), httpx.text)
            event['next_fetch'] = next_fetchx.text
            event['entries'] = []
            for entryx in entriesx:
                entry = {'title': '', 'summary':'','link':('','',''), 'id':'','published':''}
                titlex = entryx.find('{http://www.w3.org/2005/Atom}title')
                summaryx = entryx.find('{http://www.w3.org/2005/Atom}summary')
                linkx = entryx.find('{http://www.w3.org/2005/Atom}link')
                idx = entryx.find('{http://www.w3.org/2005/Atom}id')
                publishedx = entryx.find('{http://www.w3.org/2005/Atom}published')
                if titlex is not None:
                    entry['title'] = titlex.text
                    if summaryx is not None:
                        entry['summary'] = summaryx.text
                    if linkx is not None:
                        entry['link'] = (linkx.get('rel'), linkx.get('type'), linkx.get('href'))
                    if idx is not None:
                        entry['id'] = idx.text
                    if publishedx is not None:
                        entry['published'] = publishedx.text
                    event['entries'].append(entry)
	        
        return self.func(event)
    
    def on_notification(self,func):
        self.func = func
	
