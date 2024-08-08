import sqlite3


class KeyStorage:
    def __init__(self, db_path="keys.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        # 使用SQL语句创建表（如果表不存在），请设置device_id为主键！
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS keys (
            device_id TEXT PRIMARY KEY,
            key TEXT
        );
        '''
        # 执行创建表的SQL语句
        self.cursor.execute(create_table_query)

    def get_key(self, key_name):
        self.cursor.execute("SELECT key FROM keys WHERE device_id = ?", (key_name,))
        key = self.cursor.fetchone()
        return key[0] if key else None

    def set_key(self, key_name, key):
        self.cursor.execute("INSERT OR REPLACE INTO keys (device_id, key) VALUES (?, ?)", (key_name, key))


        self.cursor.execute("INSERT OR REPLACE INTO keys (device_id, key) VALUES (?, ?)", (key_name, key))
        self.conn.commit()

    def delete_key(self, key_name):
        self.cursor.execute("DELETE FROM keys WHERE device_id = ?", (key_name,))
        self.conn.commit()

    def get_all_key_name(self):
        self.cursor.execute("SELECT device_id FROM keys")
        devices = self.cursor.fetchall()
        id_list = [tup[0] for tup in devices]
        return id_list

    def close(self):
        self.conn.close()
