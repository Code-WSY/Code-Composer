import os
import fnmatch
import logging
from termcolor import colored
from rich.console import Console
from rich.table import Table
import difflib
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
import re
import time
from dotenv import load_dotenv

load_dotenv()

def is_binary_file(file_path):
    """通过读取文件的一小部分来检查文件是否为二进制文件。"""
    try:
        with open(file_path, 'rb') as file:
            chunk = file.read(1024)  # 读取前1024个字节
            if b'\0' in chunk:
                return True  # 如果包含空字节，则认为是二进制文件
            # 使用启发式方法检测二进制内容
            text_characters = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)))
            non_text = chunk.translate(None, text_characters)
            if len(non_text) / len(chunk) > 0.30:
                return True  # 如果非文本字符超过30%，则认为是二进制文件
    except Exception as e:
        logging.error(f"阅读文件时发生错误: {file_path}: {e}")
        return True  # 如果发生错误，则认为是二进制文件
    return False  # 文件可能是文本

def load_gitignore_patterns(directory):
    """如果在一个git仓库中，加载.gitignore模式"""
    gitignore_path = os.path.join(directory, '.gitignore')
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns

def should_ignore(file_path, patterns):
    """检查文件是否应被忽略"""
    for pattern in patterns:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False

def add_file_to_context(file_path, added_files, action='to context'): 
    """
    将文件添加到给定的字典中，应用排除规则。
    Args:
        file_path: 文件路径
        added_files: 给定的字典
        action: 添加到上下文

    """
    # 如果在一个git仓库中，加载.gitignore模式
    gitignore_patterns = []
    #如果当前目录下有.gitignore文件，则加载.gitignore模式
    if os.path.exists('.gitignore'):
        gitignore_patterns = load_gitignore_patterns('.') # 加载.gitignore模式
    # 如果file_path是一个文件，则添加到上下文
    if os.path.isfile(file_path):
        # 基于目录排除
        if any(ex_dir in file_path for ex_dir in os.getenv("EXCLUDED_DIRS").split(',')):
            #如果file_path包含在excluded_dirs中，则跳过
            print(colored(f"跳过排除目录文件: {file_path}", "yellow"))
            logging.info(f"跳过排除目录文件: {file_path}")
            return
        # 基于.gitignore模式排除
        if gitignore_patterns and should_ignore(file_path, gitignore_patterns):
            #如果file_path在.gitignore文件中，则跳过
            print(colored(f"跳过匹配.gitignore模式的文件: {file_path}", "yellow"))
            logging.info(f"跳过匹配.gitignore模式的文件: {file_path}")
            return
        if is_binary_file(file_path):
            #如果file_path是一个二进制文件，则跳过
            print(colored(f"跳过二进制文件: {file_path}", "yellow"))
            logging.info(f"跳过二进制文件: {file_path}")
            return
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                added_files[file_path] = content
                print(colored(f"添加文件: {file_path} {action}.", "green"))
                logging.info(f"添加文件: {file_path} {action}.")

        except Exception as e:
            print(colored(f"读取文件错误: {file_path}: {e}", "red"))
            logging.error(f"读取文件错误: {file_path}: {e}")
    else:
        print(colored(f"错误: {file_path} 不是文件。", "red"))
        logging.error(f"{file_path} 不是文件。")

def display_diff(old_content, new_content, file_path):
    """显示文件的差异"""
    diff = list(difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"a/{file_path}", 
        tofile=f"b/{file_path}",
        lineterm='',
        n=5
    ))
    if not diff:
        print(f"未检测到 {file_path} 的更改")
        return
    console = Console()
    table = Table(title=f"Diff for {file_path}")  
    table.add_column("状态", style="bold")
    table.add_column("行")
    table.add_column("内容")
    line_number = 1
    for line in diff:
        status = line[0]
        content = line[2:].rstrip()
        if status == ' ':
            continue  # Skip unchanged lines
        elif status == '-':
            table.add_row("删除", str(line_number), content, style="red")
        elif status == '+':
            table.add_row("添加", str(line_number), content, style="green")
        line_number += 1
    console.print(table)
def apply_modifications(new_content, file_path):
    """将新内容应用到指定文件"""
    if not os.path.exists(file_path):
        #创建空文件
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('')
        print(colored(f"创建文件: {file_path}", "green"))
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            old_content = file.read()

        if old_content.strip() == new_content.strip():
            print(colored(f"未检测到 {file_path} 的更改", "red"))
            return True
        # 显示差异
        display_diff(old_content, new_content, file_path) # 显示差异

        confirm = prompt(f"应用这些更改到 {file_path}? (yes/no): ", style=Style.from_dict({'prompt': 'orange'})).strip().lower() # 确认是否应用更改
        # 应用更改
        if confirm == 'yes':
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(colored(f"成功应用更改到 {file_path}.", "green"))
            logging.info(f"成功应用更改到 {file_path}.")
            return True
        else:
            print(colored(f"未应用更改到 {file_path}.", "red"))
            logging.info(f"用户选择不应用更改到 {file_path}.")
            return False

    except Exception as e:
        print(colored(f"在应用更改到 {file_path} 时发生错误: {e}", "red"))
        logging.error(f"在应用更改到 {file_path} 时发生错误: {e}")
        return False
    
def apply_creation_steps(creation_response, added_files, retry_count=0,chat_with_ai=None,root_dir=os.getcwd()):
    """从AI响应中提取代码块，并创建文件或文件夹"""
    max_retries = 3 # 最大重试次数
    try:
        # 提取内容中的所有代码块
        code_blocks = re.findall(r'```(?:\w+)?\s*([\s\S]*?)```', creation_response)
        # 如果没有代码块，则抛出错误
        if not code_blocks:
            raise ValueError("未在AI响应中找到代码块。")

        print("成功提取代码块:")
        logging.info("成功从创建响应中提取代码块。")
        # 遍历所有代码块
        for code in code_blocks:
            # 提取文件/文件夹信息
            info_match = re.match(r'### (文件|文件夹): (.+)', code.strip()) 
            # 如果匹配成功，提取文件夹或文件
            if info_match:
                item_type, path = info_match.groups() # 提取文件夹或文件，item_type是文件夹或文件，path是路径
                path = os.path.join(root_dir, path) # 将路径与根目录拼接
                # 如果item_type是文件夹，则创建文件夹
                if item_type == '文件夹':
                    # 创建文件夹
                    os.makedirs(path, exist_ok=True)
                    print(colored(f"文件夹创建: {path}", "green"))
                    logging.info(f"文件夹创建: {path}")
                # 如果item_type是文件，则创建文件
                elif item_type == '文件':
                    # 提取文件内容：匹配`### 文件: `的后面的内容
                    file_content = re.sub(r'### 文件: .+\n', '', code, count=1).strip() 

                    # 检查目录是否存在，如果不存在则创建目录
                    directory = os.path.dirname(path) 
                    if directory and not os.path.exists(directory):
                        os.makedirs(directory, exist_ok=True) # 创建目录
                        print(colored(f"文件夹创建: {directory}", "green"))
                        logging.info(f"文件夹创建: {directory}")

                    # 将内容写入文件
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(file_content) # 写入文件内容
                    print(colored(f"文件创建: {path}", "green"))
                    logging.info(f"文件创建: {path}")
            else:
                print(colored("错误: 无法从代码块中确定文件或文件夹信息。", "red"))
                logging.error("无法从代码块中确定文件或文件夹信息。")
                continue
        return True

    except ValueError as e:
        # 如果重试次数小于最大重试次数，则重试
        if retry_count < max_retries:
            print(colored(f"错误: {str(e)} 重试... (尝试 {retry_count + 1})", "red"))
            logging.warning(f"创建解析失败: {str(e)}. 重试... (尝试 {retry_count + 1})")
            error_message = f"{str(e)} 请再次提供创建指令，使用指定的格式。"
            time.sleep(2 ** retry_count)  # Exponential backoff
            new_response = chat_with_ai(error_message, is_edit_request=False, added_files=added_files)
            if new_response:
                return apply_creation_steps(new_response, added_files, retry_count + 1, chat_with_ai)
            else:
                return False
        else:
            print(colored(f"创建指令解析失败: {str(e)}", "red"))
            logging.error(f"创建指令解析失败: {str(e)}")
            print("创建响应失败:")
            print(creation_response)
            return False
    except Exception as e:
        print(colored(f"在创建期间发生意外错误: {e}", "red"))
        logging.error(f"在创建期间发生意外错误: {e}")
        return False

def parse_edit_instructions(response):
    """
    解析编辑指令
    返回格式化：{文件路径: 编辑指令}
    """
    instructions = {} # 存储编辑指令
    current_file = None # 当前文件
    current_instructions = [] # 当前文件的编辑指令
    # 遍历响应中的每一行
    for line in response.split('\n'):
        if line.startswith("文件: "):

            # 将上一次的文件的编辑指令添加到instructions中
            if current_file:
                # 将current_file的编辑指令添加到instructions中
                instructions[current_file] = "\n".join(current_instructions)
            # 获取文件路径
            current_file = line.split("文件: ", 1)[1].strip() 
            # 初始化current_instructions
            current_instructions = [] 
        #读取编辑指令
        elif line.strip() and current_file:
            current_instructions.append(line.strip())

    # 最后一次的文件的编辑指令添加到instructions中
    if current_file:
        # 将current_file的编辑指令添加到instructions中
        instructions[current_file] = "\n".join(current_instructions)
    # 返回编辑指令{文件路径: 编辑指令}
    return instructions


def select_root_directory():
    import tkinter as tk
    from tkinter import filedialog
    """
    选择根目录

    该函数会弹出一个选择目录的对话框，用户可以选择需要的目录
    如果用户未选择任何目录，程序将退出

    Returns:
        str: 选择的目录
    """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    root.attributes("-topmost", True)  # 确保对话框在最前面
    directory = filedialog.askdirectory(title="请选择根目录")
    if not directory:
        logging.error("未选择任何目录，程序将退出。")
        exit(1)
    return directory