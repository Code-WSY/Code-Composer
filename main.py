import logging
from termcolor import colored
from core.Code_Composer import CodeComposer
from utils.utils import select_root_directory


def main():
    logging.basicConfig(level=logging.INFO)  # 设置日志级别为INFO
    print(colored("选择根目录: ", "cyan"))
    root_dir = select_root_directory()
    ai_engine = CodeComposer(current_dir=root_dir) 
    ai_engine.start()
    logging.info("程序结束。")

if __name__ == "__main__":
    main()