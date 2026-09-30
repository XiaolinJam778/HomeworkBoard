import sys
from pathlib import Path
import winreg


APP_NAME = "HomeworkBoard"

RUN_KEY = (
    r"Software\Microsoft\Windows"
    r"\CurrentVersion\Run"
)


def get_startup_command():
    """
    生成 HomeworkBoard 的开机启动命令。

    开发阶段使用 pythonw.exe 启动 main.py，
    避免弹出命令行窗口。

    未来打包为 exe 后，也兼容 exe。
    """

    # PyInstaller 等方式打包以后
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'

    python_executable = Path(sys.executable)

    # 尽量使用 pythonw.exe
    pythonw_executable = (
        python_executable.parent / "pythonw.exe"
    )

    if pythonw_executable.exists():
        launcher = pythonw_executable
    else:
        launcher = python_executable

    project_dir = Path(__file__).resolve().parent
    main_file = project_dir / "main.py"

    return f'"{launcher}" "{main_file}"'


def enable_startup():
    """启用 HomeworkBoard 开机自启动。"""

    command = get_startup_command()

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        RUN_KEY,
        0,
        winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(
            key,
            APP_NAME,
            0,
            winreg.REG_SZ,
            command
        )

    print("HomeworkBoard startup enabled.")
    print(command)


def disable_startup():
    """关闭 HomeworkBoard 开机自启动。"""

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY,
            0,
            winreg.KEY_SET_VALUE
        ) as key:
            winreg.DeleteValue(
                key,
                APP_NAME
            )

        print("HomeworkBoard startup disabled.")

    except FileNotFoundError:
        print(
            "HomeworkBoard startup "
            "was not enabled."
        )


def is_startup_enabled():
    """检查开机启动是否已经启用。"""

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY,
            0,
            winreg.KEY_READ
        ) as key:
            winreg.QueryValueEx(
                key,
                APP_NAME
            )

        return True

    except FileNotFoundError:
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  python startup_manager.py enable\n"
            "  python startup_manager.py disable\n"
            "  python startup_manager.py status"
        )

    elif sys.argv[1] == "enable":
        enable_startup()

    elif sys.argv[1] == "disable":
        disable_startup()

    elif sys.argv[1] == "status":
        if is_startup_enabled():
            print("Startup: enabled")
        else:
            print("Startup: disabled")

    else:
        print("Unknown command.")