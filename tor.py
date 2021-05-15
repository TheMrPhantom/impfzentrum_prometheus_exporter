import subprocess
import envir
import time

class Proxy_Handler:
    
    def __init__(self):
        self.proc=None

    def start_proxy(self):
        self.proc = subprocess.Popen(['torpy_socks', '-p', str(envir.proxy_port), '--hops', str(envir.proxy_hops)])
        print()
        print()
        print()
        print()
        print("Sleeeeep")
        time.sleep(30)
        print("Sleeeeep")
    
    def stop_proxy(self):
        self.proc.terminate()
    
    def restart_proxy(self):
        self.proc.terminate()
        self.proc = subprocess.Popen(['torpy_socks', '-p', str(envir.proxy_port), '--hops', str(envir.proxy_hops)])