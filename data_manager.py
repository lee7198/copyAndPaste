import json
import os

class DataManager:
    def __init__(self, json_file):
        self.json_file = json_file
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return self._convert_to_dict(data)
            except:
                return {}
        return {}

    def _convert_to_dict(self, data):
        if isinstance(data, list):
            return {str(i): item for i, item in enumerate(data)}
        return data

    def save_data(self):
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_item(self, key, value):
        self.data[key] = value

    def get_items(self):
        return self.data.items() 