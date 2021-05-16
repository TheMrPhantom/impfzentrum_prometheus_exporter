import subprocess
import envir
import time
import os

class Proxy_Handler:
    
    def __init__(self):
        self.proc=None
        self.FNULL = open(os.devnull, 'w')


    def start_proxy(self,output=False):
        # with output to console
        print("Start tor connection")
        if output:
            self.proc = subprocess.Popen(['torpy_socks', '-p', str(envir.proxy_port), '--hops', str(envir.proxy_hops)])
        else:
            self.proc = subprocess.Popen(['torpy_socks', '-p', str(envir.proxy_port), '--hops', str(envir.proxy_hops)],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        for i in range(6):
            print("sleeping",i,"/","6")
            time.sleep(1)
        print("Done connecting")
    
    def stop_proxy(self):
        try:
            self.proc.terminate()
            return True
        except:
            return False
    
    def restart_proxy(self,output=False):
        self.stop_proxy()
        self.start_proxy(output)