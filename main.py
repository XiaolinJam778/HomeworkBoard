from database import create_tables
from ui.main_window import HomeworkBoardApp


def main():
    create_tables()

    app = HomeworkBoardApp()
    app.run()


if __name__ == "__main__":
    main()
    