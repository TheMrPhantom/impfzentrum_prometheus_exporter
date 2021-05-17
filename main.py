from prometheus_client import metrics
from vac_center_handler import get_vac_centers
from checker import checker_thread
from envir import proxy_port as PROXY_PORT
import threading
import prometheus_client

metrics = dict()
metrics['impfzentrum_status'] = prometheus_client.Gauge(
    'impfzentrum_status', 'Impfstoffverfügbarkeit', ['zentrum'])
metrics['lasttimechecked'] = prometheus_client.Gauge(
    'impfzentrum_lastCheck', 'Letze prüfung', ['zentrum'])

prometheus_client.start_http_server(8080)

vac_centers = get_vac_centers()
print("[CONTROL FLOW] Vac Centers loaded.")

port_offset = 0
for vac_center in vac_centers:
    print("[CONTROL FLOW] Vac Center in " + vac_center["PLZ"] +
          ". Starting a new thread.")
    prometheus = [metrics['impfzentrum_status'], metrics['lasttimechecked']]

    arguments = (PROXY_PORT + port_offset, vac_center, prometheus)
    thread = threading.Thread(target=checker_thread, args=arguments)
    port_offset += 1
    thread.start()
