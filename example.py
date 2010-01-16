from sfpy.superfeedr import SuperFeedr

def sf_message(event):
    print 'received this event: ', str(event)
    return 1

        
def main():
    user = 'user'
    password = 'password'
    s = SuperFeedr(user, password)
    s.on_notification(sf_message)
    s.monitor() 

if __name__=='__main__':
    main()