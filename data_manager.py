import json
import os

class DataManager:
    def __init__(self, json_file):
        self.json_file = json_file
        self.data = self.load_data()
        

    def load_data(self):
        init_value = {
            "list": []
        }
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"데이터 로드 중 오류 발생: {e}")
                return init_value
        return init_value

    def save_data(self):
        try:
            # 디렉토리가 존재하지 않으면 생성
            os.makedirs(os.path.dirname(self.json_file), exist_ok=True)
            
            # 데이터 저장
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, sort_keys=True)
            print(f"데이터가 성공적으로 저장되었습니다: {self.json_file}")
            return True
        except Exception as e:
            print(f"데이터 저장 중 오류 발생: {e}")
            return Falsepip
        
    def refresh_data(self):
        self.data = self.load_data()

    def add_item(self, key, value):
        self.data["list"].append({"key": key, "value": value})
        self.save_data()

    def get_items(self):
        return self.data["list"]
    
    def delete_data(self, index):
        if 0 <= index < len(self.data["list"]):
            del self.data["list"][index]
            self.save_data()