
import logging
import os
import json
import logging

logging.basicConfig(
            filename="router.log", 
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

class Router:
    def __init__(self, config_path: str):
        self.config = {}
        self.config_path = config_path

    def load_config(self):
            try:
                # Check if the file exists and is not empty
                if not os.path.exists(self.config_path):
                    raise FileNotFoundError(f"File '{self.config_path}' does not exist.")
                if os.stat(self.config_path).st_size == 0:
                    raise ValueError(f"File '{self.config_path}' is empty.")

                # Open and load JSON content
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    logging.info(f"Successfully read the file: {self.config_path}")
                    self.config = data.get("router", {})

            except FileNotFoundError as e:
                logging.error(f"Error: {e}")
                print(f"Error: {e}")

            except ValueError as e:
                logging.error(f"Error: {e}")
                print(f"Error: {e}")
        
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON: {e}")
                print(f"Error decoding JSON: {e}")
        
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                print(f"Unexpected error: {e}")
    
    def restart(self):
        # Simulate router restart
        print("Router is restarting...")
        # Here would be the actual restart logic
    
    def print_status(self):
        print("Router configuration:")
        for key, value in self.config.items():
            print(f"{key}: {value}")
    
    def print_wan_ip(self):
        pass

def main():
    file_name = "config.json"
    config_file_path = os.path.join(os.path.dirname(__file__), file_name)
    
    print("Router restart script executed.")
    router = Router(config_file_path)
    router.load_config()
    router.print_status()

if __name__ == "__main__":
    main()