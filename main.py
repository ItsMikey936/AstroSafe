"""Start the Astronaut Health Monitor.

    python main.py
"""
import logging

from app.frontend.main_window import MainWindow


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    window = MainWindow()
    window.mainloop()


if __name__ == "__main__":
    main()
