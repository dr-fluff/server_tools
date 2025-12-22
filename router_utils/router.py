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
        pass
    
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
        

    def get_bandwidth_usage(self):
        pass

def init_router_ip_watcher(router, logger=None):
    pass

def init_router_connection(config, logger=None):
    router = Router(config, logger)
    return router
    