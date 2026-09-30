import json
import os
from pathlib import Path


APP_NAME = "HomeworkBoard"

DEFAULT_SETTINGS = {
    "x": 400,
    "y": 584,
    "width": 645,
    "height": 270,
    "locked": False,
}


def get_settings_dir():
    """
    返回 HomeworkBoard 的用户配置目录。

    Windows:
    C:\\Users\\用户名\\AppData\\Roaming\\HomeworkBoard
    """
    appdata = os.getenv("APPDATA")

    if appdata:
        settings_dir = Path(appdata) / APP_NAME
    else:
        settings_dir = Path.home() / f".{APP_NAME}"

    settings_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return settings_dir


def get_settings_path():
    return get_settings_dir() / "settings.json"


def load_settings():
    """
    读取 Widget 设置。

    如果配置不存在或损坏，
    使用默认设置。
    """
    path = get_settings_path()

    if not path.exists():
        return DEFAULT_SETTINGS.copy()

    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        settings = DEFAULT_SETTINGS.copy()
        settings.update(data)

        return settings

    except (
        json.JSONDecodeError,
        OSError,
        TypeError
    ):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """
    保存 Widget 设置。
    """
    path = get_settings_path()

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            settings,
            file,
            ensure_ascii=False,
            indent=4
        )