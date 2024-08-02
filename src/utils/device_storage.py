import sqlite3
import time

from src.device import device
from src.device.device import Device
from src.screen_manager.position import Position
from src.screen_manager.screen import Screen


def create_table():
    delete_table()
    conn = sqlite3.connect("temp.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE devices (device_id TEXT PRIMARY KEY, ip TEXT, pub_key TEXT, screen_width INTEGER, screen_height INTEGER, position INTEGER, last_heartbeat REAL)")
    conn.commit()
    conn.close()


def delete_table():
    conn = sqlite3.connect("temp.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE devices")
    conn.commit()
    conn.close()


class DeviceStorage:

    def __init__(self, db_path="temp.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def update_heartbeat(self, ip):
        self.cursor.execute("UPDATE devices SET last_heartbeat = ? WHERE ip = ?", (time.time(), ip))
        self.conn.commit()

    def add_device(self, device: device.Device):
        for p in Position:
            temp = self.get_device_by_position(p)
            if temp is None:
                device.position = p
                break
        self.cursor.execute("INSERT OR REPLACE INTO devices VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (device.device_id, device.ip, device.pub_key, device.screen.screen_width,
                             device.screen.screen_height, device.position.value, time.time()))
        self.conn.commit()

    def update_device(self, device: device.Device):
        self.cursor.execute("UPDATE devices SET position = ? WHERE device_id = ?",
                            (device.position.value,))
        self.conn.commit()

    def get_all_devices(self):
        self.cursor.execute("SELECT * FROM devices")
        devices = self.cursor.fetchall()
        device_list = []
        for dev in devices:
            device_list.append(Device(dev[1], Screen(dev[3], dev[4]), Position(dev[5]), dev[0], dev[2]))
        return device_list


    def get_device(self, device_id):
        self.cursor.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
        device = self.cursor.fetchone()
        if device:
            return Device(device[1], Screen(device[3], device[4]), Position(device[5]), device[0], device[2])
        return None

    def get_device_by_ip(self, ip):
        self.cursor.execute("SELECT * FROM devices WHERE ip = ?", (ip,))
        device = self.cursor.fetchone()
        if device:
            return Device(device[1], Screen(device[3], device[4]), Position(device[5]), device[0], device[2])
        return None

    def get_device_by_position(self, position):
        self.cursor.execute("SELECT * FROM devices WHERE position = ?", (int(position),))
        device = self.cursor.fetchone()
        if device:
            return Device(device[1], Screen(device[3], device[4]), Position(device[5]), device[0], device[2])
        return None

    def close(self):
        self.conn.close()
