import serial
import time
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSignal

class SerialThread(QThread):
    uid_scanned = pyqtSignal(str)

    def __init__(self, port="COM4", baud=9600):
        super().__init__()
        self.port = port
        self.baud = baud
        self.ser = None
        self._is_running = True

    def run(self):
        """Main loop that listens for serial data."""
        try:
             #Check if the port is available first
            available_ports = [p.device for p in serial.tools.list_ports.comports()]
            if self.port not in available_ports:
                print(f"Warning: Serial port {self.port} not found. Available: {available_ports}")
                # Don't return, try anyway in case of dynamic mapping
            
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            
            # Arduino resets when serial opens; wait 2 seconds for it to boot up
            time.sleep(2) 
            
            while self._is_running:
                if self.ser and self.ser.is_open and self.ser.in_waiting:
                    try:
                        # Read raw data, decode, and strip whitespace/newlines
                        raw_data = self.ser.readline().decode(errors="ignore").strip()
                        
                        if raw_data:
                            # Handle common Arduino formats like "Card UID: 12 34 56 78"
                            # Extracts only the part after the last colon
                            clean_uid = raw_data.split(":")[-1].strip()
                            
                            if clean_uid:
                                self.uid_scanned.emit(clean_uid)
                    except Exception as e:
                        print(f"Data read error: {e}")
                
                # Small sleep to prevent high CPU usage in the while loop
                self.msleep(50)

        except Exception as e:
            print(f"Serial connection error on {self.port}: {e}")
        finally:
            self.stop()

    def write(self, message):
        """Sends a string command to the Arduino (e.g., 'AUTHORIZED')."""
        if self.ser and self.ser.is_open:
            try:
                formatted_msg = (message + "\n").encode()
                self.ser.write(formatted_msg)
            except Exception as e:
                print(f"Serial write error: {e}")

    def stop(self):
        """Safely shuts down the thread and closes the port."""
        self._is_running = False
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except:
                pass
        self.quit()