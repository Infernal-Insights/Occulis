import tkinter as tk
import os
import redis
from typing import Dict


class StatusDisplay:
    """Simple Tkinter GUI to show rig statistics on a small display.

    Parameters
    ----------
    redis_host : str
        Hostname for the Redis server.
    redis_port : int
        Port of the Redis server.
    refresh_interval : int
        Polling interval in milliseconds.
    """

    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379,
                 refresh_interval: int = 5000):
        redis_host = os.getenv('OCCULIS_REDIS_HOST', redis_host)
        redis_port = int(os.getenv('OCCULIS_REDIS_PORT', redis_port))
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=0)
        self.root = tk.Tk()
        self.root.title("Occulis Status")
        self.labels: Dict[str, tk.Label] = {}
        # typical resolution of the official 7" touchscreen
        self.root.geometry("800x480")
        self.refresh_interval = refresh_interval

    def _fetch_stats(self) -> Dict[str, Dict[str, str]]:
        """Retrieve rig stats from Redis using scan_iter to avoid blocking."""
        data: Dict[str, Dict[str, str]] = {}
        for key in self.redis.scan_iter():
            name = key.decode("utf-8")
            stats = {
                k.decode("utf-8"): v.decode("utf-8")
                for k, v in self.redis.hgetall(key).items()
            }
            data[name] = stats
        return data

    def _update_labels(self) -> None:
        """Refresh labels with the latest rig statistics."""
        stats = self._fetch_stats()
        for name, rig_stats in sorted(stats.items()):
            temp = rig_stats.get('temp', '?')
            hashrate = rig_stats.get('hashrate', '?')
            text = f"{name}: {temp}C, {hashrate}H/s"
            if name not in self.labels:
                lbl = tk.Label(self.root, text=text, font=("Helvetica", 20))
                lbl.pack(anchor='w')
                self.labels[name] = lbl
            else:
                self.labels[name].config(text=text)
        self.root.after(self.refresh_interval, self._update_labels)

    def run(self):
        self._update_labels()
        self.root.mainloop()


if __name__ == "__main__":
    StatusDisplay().run()
