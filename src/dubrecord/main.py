from dubrecord.settings import ModeEnum, get_settings
from dubrecord.startup import polling, webhook


def start() -> None:
    if get_settings().app.mode == ModeEnum.WEBHOOK:
        webhook()
    else:
        polling()

if __name__ == "__main__":
    start()