import json


class File:

    def __init__(self, name, size, host):
        self.name = name
        self.size = size
        self.host = host

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        return File(data["name"], data["size"], data["host"])