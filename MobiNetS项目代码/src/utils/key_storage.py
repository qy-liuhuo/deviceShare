"""
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.

 Author: MobiNets
"""
import sqlite3


class KeyStorage:
    """
    用于存储设备ID和密钥的类
    """
    def __init__(self, db_path="keys.db"):
        """
        初始化
        :param db_path:
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        # 使用SQL语句创建表（如果表不存在），请设置device_id为主键！
        create_table_query = """
        CREATE TABLE IF NOT EXISTS keys (
            device_id TEXT PRIMARY KEY,
            key TEXT
        );
        """
        # 执行创建表的SQL语句
        self.cursor.execute(create_table_query)

    def get_key(self, key_name):
        """
        获取密钥
        :param key_name:  设备id
        :return: public key
        """
        self.cursor.execute("SELECT key FROM keys WHERE device_id = ?", (key_name,))
        key = self.cursor.fetchone()
        return key[0] if key else None

    def set_key(self, key_name, key):
        """
        设置密钥
        :param key_name: 设备id
        :param key: public key
        :return:
        """
        self.cursor.execute("INSERT OR REPLACE INTO keys (device_id, key) VALUES (?, ?)", (key_name, key))


        self.cursor.execute("INSERT OR REPLACE INTO keys (device_id, key) VALUES (?, ?)", (key_name, key))
        self.conn.commit()

    def delete_key(self, key_name):
        """
        删除密钥
        :param key_name: 设备id
        :return:
        """
        self.cursor.execute("DELETE FROM keys WHERE device_id = ?", (key_name,))
        self.conn.commit()

    def get_all_key_name(self):
        """
        获取所有设备id
        :return: 获取id list
        """
        self.cursor.execute("SELECT device_id FROM keys")
        devices = self.cursor.fetchall()
        id_list = [tup[0] for tup in devices]
        return id_list

    def close(self):
        """
        关闭数据库连接
        :return:
        """
        self.conn.close()
