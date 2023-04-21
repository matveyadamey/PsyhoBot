import json


class Config:
    # достать данные
    def put(self, data):
        with open("config.json", "r") as read_file:
            self.config = json.load(read_file)
            return self.config[data]

    # записать данные
    def push(self, k, data):
        with open("config.json", "r") as f:
            x = json.load(f)
        x[k] = data
        with open("config.json", "w") as read_file:
            json.dump(x, read_file)
