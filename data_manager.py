"""
데이터 관리 기능을 담당하는 모듈입니다.
JSON 파일을 통한 데이터 저장 및 로드를 처리합니다.
"""

import json
import os
from typing import List, Dict, Any, Optional
from constants import DEFAULT_DATA_FILE, DEFAULT_INIT_DATA


class DataManager:
    """JSON 파일을 통한 데이터 관리 클래스"""

    def __init__(self, json_file: str = DEFAULT_DATA_FILE):
        self.json_file = json_file
        self.data = self.load_data()

    def load_data(self) -> Dict[str, Any]:
        """JSON 파일에서 데이터를 로드합니다."""
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    # 데이터 구조 검증
                    if isinstance(loaded_data, dict) and "list" in loaded_data:
                        return loaded_data
                    else:
                        print(f"잘못된 데이터 구조: {self.json_file}")
                        return DEFAULT_INIT_DATA.copy()
            except json.JSONDecodeError as e:
                print(f"JSON 파싱 오류: {e}")
                return DEFAULT_INIT_DATA.copy()
            except Exception as e:
                print(f"데이터 로드 중 오류 발생: {e}")
                return DEFAULT_INIT_DATA.copy()
        return DEFAULT_INIT_DATA.copy()

    def save_data(self) -> bool:
        """데이터를 JSON 파일에 저장합니다."""
        try:
            # 디렉토리가 존재하지 않으면 생성
            os.makedirs(os.path.dirname(self.json_file), exist_ok=True)

            # 데이터 저장
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            print(f"데이터가 성공적으로 저장되었습니다: {self.json_file}")
            return True
        except Exception as e:
            print(f"데이터 저장 중 오류 발생: {e}")
            return False

    def refresh_data(self) -> None:
        """데이터를 다시 로드합니다."""
        self.data = self.load_data()

    def add_item(self, key: str, value: str) -> bool:
        """새로운 항목을 추가합니다."""
        try:
            self.data["list"].append({"key": key, "value": value})
            return self.save_data()
        except Exception as e:
            print(f"항목 추가 중 오류 발생: {e}")
            return False

    def get_items(self) -> List[Dict[str, str]]:
        """모든 항목을 반환합니다."""
        return self.data.get("list", [])

    def delete_data(self, index: int) -> bool:
        """지정된 인덱스의 항목을 삭제합니다."""
        try:
            if 0 <= index < len(self.data["list"]):
                del self.data["list"][index]
                return self.save_data()
            else:
                print(f"잘못된 인덱스: {index}")
                return False
        except Exception as e:
            print(f"항목 삭제 중 오류 발생: {e}")
            return False

    def update_item(self, index: int, key: str, value: str) -> bool:
        """지정된 인덱스의 항목을 업데이트합니다."""
        try:
            if 0 <= index < len(self.data["list"]):
                self.data["list"][index] = {"key": key, "value": value}
                return self.save_data()
            else:
                print(f"잘못된 인덱스: {index}")
                return False
        except Exception as e:
            print(f"항목 업데이트 중 오류 발생: {e}")
            return False

    def get_item_count(self) -> int:
        """항목 개수를 반환합니다."""
        return len(self.data.get("list", []))

    def clear_all(self) -> bool:
        """모든 데이터를 삭제합니다."""
        try:
            self.data["list"] = []
            return self.save_data()
        except Exception as e:
            print(f"데이터 초기화 중 오류 발생: {e}")
            return False
