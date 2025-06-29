"""
복붙 관리 애플리케이션의 메인 모듈입니다.
"""

import wx
import sys
from typing import Optional
from data_manager import DataManager
from ui_manager import UIManager
from constants import DEFAULT_DATA_FILE


class CopyAndPasteApp(wx.App):
    """복붙 관리 애플리케이션의 메인 클래스"""

    def __init__(self, data_file: str = DEFAULT_DATA_FILE):
        self.data_file = data_file
        self.data_manager: Optional[DataManager] = None
        self.ui_manager: Optional[UIManager] = None
        super().__init__()

    def OnInit(self) -> bool:
        """애플리케이션 초기화"""
        try:
            # 데이터 매니저 초기화
            self.data_manager = DataManager(self.data_file)

            # UI 매니저 초기화
            self.ui_manager = UIManager(self, self.data_manager)

            return True
        except Exception as e:
            print(f"애플리케이션 초기화 중 오류 발생: {e}")
            wx.MessageBox(
                f"애플리케이션을 시작할 수 없습니다.\n오류: {e}",
                "초기화 오류",
                wx.OK | wx.ICON_ERROR,
            )
            return False

    def OnExit(self) -> int:
        """애플리케이션 종료 시 정리 작업"""
        try:
            if self.data_manager:
                # 마지막 데이터 저장
                self.data_manager.save_data()
        except Exception as e:
            print(f"종료 시 데이터 저장 중 오류: {e}")

        return 0


def main():
    """메인 함수"""
    try:
        app = CopyAndPasteApp()
        app.MainLoop()
    except Exception as e:
        print(f"애플리케이션 실행 중 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
