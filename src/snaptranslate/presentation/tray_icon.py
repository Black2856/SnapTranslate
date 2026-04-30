from __future__ import annotations

import logging
import threading
from collections.abc import Callable

logger = logging.getLogger(__name__)


class TrayIcon:
    WM_TRAY = 1024 + 20

    def __init__(self, on_settings: Callable[[], None], on_quit: Callable[[], None]) -> None:
        self.on_settings = on_settings
        self.on_quit = on_quit
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, name="tray-icon", daemon=True)
        self._thread.start()

    def _run(self) -> None:
        try:
            self._run_win32()
        except Exception:
            logger.exception("Tray icon failed")

    def _run_win32(self) -> None:
        import win32api
        import win32con
        import win32gui

        menu = None

        def wnd_proc(hwnd, msg, wparam, lparam):
            nonlocal menu
            if msg == self.WM_TRAY and lparam == win32con.WM_RBUTTONUP:
                menu = win32gui.CreatePopupMenu()
                win32gui.AppendMenu(menu, win32con.MF_STRING, 1, "Settings")
                win32gui.AppendMenu(menu, win32con.MF_STRING, 2, "Quit")
                pos = win32gui.GetCursorPos()
                win32gui.SetForegroundWindow(hwnd)
                command = win32gui.TrackPopupMenu(
                    menu,
                    win32con.TPM_LEFTALIGN | win32con.TPM_RETURNCMD,
                    pos[0],
                    pos[1],
                    0,
                    hwnd,
                    None,
                )
                if command == 1:
                    self.on_settings()
                elif command == 2:
                    self.on_quit()
            elif msg == win32con.WM_DESTROY:
                win32gui.PostQuitMessage(0)
            return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

        class_name = "SnapTranslateTrayWindow"
        wc = win32gui.WNDCLASS()
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = class_name
        wc.lpfnWndProc = wnd_proc
        atom = win32gui.RegisterClass(wc)
        hwnd = win32gui.CreateWindow(atom, class_name, 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)
        icon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (hwnd, 0, flags, self.WM_TRAY, icon, "SnapTranslate")
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        try:
            win32gui.PumpMessages()
        finally:
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)

