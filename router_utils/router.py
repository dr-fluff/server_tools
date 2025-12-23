import os
import logging
import tomllib
import tomli_w
import threading
from rich import print
import paramiko

class Router:
    def __init__(self, config, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.config = config
        self.lock = threading.Lock()
        self.ssh_client = None
        self.ip = None
        self.devices = []
        self.message_callback = None
        self.last_ip_file = "last_ip.txt"
        self.watcher_thread = None
        
        try:
            self.ssh_connect()
        except Exception as e:
            self.logger.error(f"Failed to connect to router: {e}")
            raise e
        
        try:
            self.ip = self.get_ip_address()
        except Exception as e:
            self.logger.error(f"Failed to get router IP address: {e}")
            raise e
        
        try:
            self.devices = self.get_connected_devices()
        except Exception as e:
            self.logger.error(f"Failed to get connected devices: {e}")
            raise e
        
        # Load last known IP
        self.load_last_ip()
        
        # Start IP watcher if enabled
        if self.config.get("ip_watcher_enabled", False):
            self.start_ip_watcher()
    
    def print_config(self):
        print("Router config:")
        for key, value in self.config.config.items():
            print(f"[cyan]{key}[/cyan]: {value}")

    def ssh_connect(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        hostname = self.config.get("ssh_hostname")
        port = self.config.get("ssh_port", 22)
        username = self.config.get("username")
        password = self.config.get("password")
        key_filename=self.config.get("ssh_key_path")

        if self.config.get("ssh_key_path") is not None and os.path.exists(self.config.get("ssh_key_path")):
            self.ssh_client.connect(
                hostname=hostname,
                port=port,
                username=username,
                key_filename=key_filename,
            )
        else:
            self.ssh_client.connect(
                hostname=hostname,
                port=port,
                username=username,
                password=password,
            )
        
    def get_status(self):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command("uptime")
            status = stdout.read().decode()
            return status
        except Exception as e:
            self.logger.error(f"Failed to get router status: {e}")
            raise e
    
    def restart(self):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command("reboot")
            self.logger.info("Router is restarting")
        except Exception as e:
            self.logger.error(f"Failed to restart router: {e}")
            raise e

    def disconnect(self):
        if self.ssh_client:
            self.ssh_client.close()
            self.logger.info("SSH connection closed")
    
    def get_ip_address(self):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command("ifconfig")
            return stdout.read().decode()
        except Exception as e:
            self.logger.error(f"Failed to get IP address: {e}")
            raise e 

    def get_connected_devices(self):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command("arp -a")
            if stderr.read():
                raise Exception(stderr.read().decode())
            devices = []
            for line in stdout:
                devices.append(line.strip())
            return devices
        except Exception as e:
            self.logger.error(f"Failed to get connected devices: {e}")
            raise e    

    def set_message_callback(self, callback):
        self.message_callback = callback

    def load_last_ip(self):
        try:
            if os.path.exists(self.last_ip_file):
                with open(self.last_ip_file, 'r') as f:
                    self.last_ip = f.read().strip()
                self.logger.info(f"Loaded last IP: {self.last_ip}")
            else:
                self.last_ip = None
        except Exception as e:
            self.logger.error(f"Failed to load last IP: {e}")
            self.last_ip = None

    def save_last_ip(self, ip):
        try:
            with open(self.last_ip_file, 'w') as f:
                f.write(ip)
            self.logger.info(f"Saved last IP: {ip}")
        except Exception as e:
            self.logger.error(f"Failed to save last IP: {e}")

    def start_ip_watcher(self):
        if self.watcher_thread and self.watcher_thread.is_alive():
            return
        self.watcher_thread = threading.Thread(target=self.ip_watcher_loop, daemon=True)
        self.watcher_thread.start()
        self.logger.info("IP watcher started")

    def stop_ip_watcher(self):
        if self.watcher_thread:
            # Note: Since it's daemon, it will stop with the process
            self.logger.info("IP watcher stopped")

    def ip_watcher_loop(self):
        import time
        while True:
            if not self.config.get("ip_watcher_enabled", False):
                break
            try:
                current_ip = self.get_external_ip()
                if self.last_ip and current_ip != self.last_ip:
                    message = f"🚨 Router IP changed!\nOld: {self.last_ip}\nNew: {current_ip}"
                    if self.message_callback:
                        self.message_callback(message)
                    self.logger.warning(f"IP changed: {self.last_ip} -> {current_ip}")
                if current_ip:
                    self.save_last_ip(current_ip)
                    self.last_ip = current_ip
            except Exception as e:
                self.logger.error(f"IP watcher error: {e}")
            time.sleep(300)  # Check every 5 minutes

    def get_external_ip(self):
        # For now, assume get_ip_address returns external IP
        # In reality, might need to parse or use a different command
        return self.get_ip_address().split('\n')[1].split()[1] if '\n' in self.get_ip_address() else None

def init_router_connection(config, logger=None):
    router = Router(config, logger)
    return router
    