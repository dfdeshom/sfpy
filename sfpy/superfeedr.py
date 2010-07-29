import time
import xmpp
from xmpp.protocol import Iq
import xml.etree.ElementTree as ET

class SuperFeedr(object):
    def __init__(self, jid, password, debug=False, hostname=None):
        if not hostname:
            hostname = 'superfeedr.com'
        self.hostname = hostname
        if debug:
            kwargs = {}
        else:
            kwargs = {'debug': []}
        self.client = xmpp.Client(server=self.hostname, **kwargs)
        self.client.connect(server=(self.hostname, 5222))
        self.jid = jid
        self.client.auth(xmpp.protocol.JID(jid).getNode(), password)
        self.client.sendInitPresence()
        # give this client the greatest priority
        self.client.send(xmpp.protocol.Presence(priority='127'))
        
        self.client.RegisterHandler('message', self.superfeedr_msg)
        self.callback = lambda x: x

    def _action(self, action, feed, hostname=None, sleep_time=1):
        if not hostname:
            hostname = 'firehoser.superfeedr.com'
        data = Iq(typ='set', to=hostname, frm=str(self.jid))
        child = data.addChild('pubsub',
            namespace='http://jabber.org/protocol/pubsub')
        child.addChild(action, {'node': feed, 'jid': str(self.jid)})
        self.client.send(data)
        if sleep_time:
            time.sleep(sleep_time)
        self.client.Process(1)
        self.client.disconnect()
        
    def subscribe(self, feed, hostname=None, sleep_time=1):
        self._action('subscribe', feed, hostname=hostname,
            sleep_time=sleep_time)

    def unsubscribe(self, feed, hostname=None, sleep_time=1):
        self._action('unsubscribe', feed, hostname=hostname,
            sleep_time=sleep_time)
    
    def monitor(self):
        while True:
            self.client.Process(1)

    def superfeedr_msg(self,con,m):
        mstr = m.__str__()
        s = mstr.encode('utf8')
        xml = ET.fromstring(s)
        event = {}
        statusx = xml.find('{http://jabber.org/protocol/pubsub#event}event/{http://superfeedr.com/xmpp-pubsub-ext}status')
        httpx = xml.find('{http://jabber.org/protocol/pubsub#event}event/{http://superfeedr.com/xmpp-pubsub-ext}status/{http://superfeedr.com/xmpp-pubsub-ext}http')
        next_fetchx = xml.find('{http://jabber.org/protocol/pubsub#event}event/{http://superfeedr.com/xmpp-pubsub-ext}status/{http://superfeedr.com/xmpp-pubsub-ext}next_fetch')
        itemsx = xml.find('{http://jabber.org/protocol/pubsub#event}event/{http://jabber.org/protocol/pubsub#event}items')
        entriesx = xml.findall('{http://jabber.org/protocol/pubsub#event}event/{http://jabber.org/protocol/pubsub#event}items/{http://jabber.org/protocol/pubsub}item/{http://www.w3.org/2005/Atom}entry')

        if None not in (statusx, httpx, next_fetchx, itemsx, entriesx):
            event.update({
                'xml': xml,
                'feed': itemsx.get('node'),
                'http': (httpx.get('code'), httpx.text),
                'next_fetch': next_fetchx.text,
                'entries': [],
            })
            
            for entryx in entriesx:
                entry = {}
                titlex = entryx.find('{http://www.w3.org/2005/Atom}title')
                summaryx = entryx.find('{http://www.w3.org/2005/Atom}summary')
                linkx = entryx.find('{http://www.w3.org/2005/Atom}link')
                idx = entryx.find('{http://www.w3.org/2005/Atom}id')
                publishedx = entryx.find('{http://www.w3.org/2005/Atom}published')
                authorx = entryx.find('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name')
                
                if titlex is not None:
                    entry['title'] = titlex.text
                if summaryx is not None:
                    entry['summary'] = summaryx.text
                if linkx is not None:
                    entry['link'] = linkx.get('href')
                if idx is not None:
                    entry['id'] = idx.text
                if publishedx is not None:
                    entry['published'] = publishedx.text
                if authorx is not None:
                    entry['author'] = authorx.text
                    
                event['entries'].append(entry)
	
        return self.callback(event)
    
    def on_notification(self, callback):
        self.callback = callback
	
