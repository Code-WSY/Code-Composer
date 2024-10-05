import os
import logging
from openai import OpenAI
from termcolor import colored
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import WordCompleter
from rich import print as rprint
from rich.markdown import Markdown
import os
import dotenv
from utils.utils import apply_modifications, add_file_to_context, parse_edit_instructions,apply_creation_steps
# 加载环境变量
dotenv.load_dotenv()
class CodeComposer:
    def __init__(self, current_dir):
        # 当前目录
        self.root_dir = current_dir
        #获取项目所在目录
        self.project_dir = os.getcwd() 
        # 初始化全局变量
        self.last_ai_response = None 
        self.conversation_history = []
        self.style = Style.from_dict({'prompt': 'cyan'}) 
        # 获取根目录中的文件列表
        self.files = [
            os.path.relpath(os.path.join(dp, f), self.root_dir) # 获取文件的相对路径
            for dp, dn, filenames in os.walk(self.root_dir)
            for f in filenames
            if os.path.isfile(os.path.join(dp, f))
        ]
        # 排除目录
        self.excluded_dirs = set(os.getenv("EXCLUDED_DIRS").split(',')) 
        # 添加的文件
        self.added_files = {}
        # 文件内容
        self.file_contents = {}
        # 模型
        self.MODEL = os.getenv("MODEL")
        # 初始化OpenAI客户端
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE_URL")) 
        # 创建系统提示
        self.prompt_files = {
            'CREATE_SYSTEM_PROMPT': 'create_system_prompt.md',
            'CODE_REVIEW_PROMPT': 'code_review_prompt.md',
            'EDIT_INSTRUCTION_PROMPT': 'edit_instruction_prompt.md',
            'APPLY_EDITS_PROMPT': 'apply_edits_prompt.md',
            'PLANNING_PROMPT': 'planning_prompt.md',
            'CHAT_INSTRUCTION_PROMPT': 'chat_instruction_prompt.md'
        }
        # 加载系统提示
        self.core_dir = os.path.join(self.project_dir, "core") #获取core目录
        self.prompts_dir = os.path.join(self.core_dir, "prompt") #获取prompt目录
        for prompt_var, prompt_file in self.prompt_files.items():
            with open(os.path.join(self.prompts_dir, prompt_file), 'r', encoding='utf-8') as file:
                setattr(self, prompt_var, file.read())
        print(colored("根目录: ", "cyan"), self.root_dir)
        #print(colored("运行成功: ", "cyan"), os.getcwd())
        #print(colored("文件: ", "cyan"), self.files)
    # 应用编辑指令
    def apply_edit_instructions(self, edit_instructions, original_files):
        """ 
        应用编辑指令

        参数:
            edit_instructions (dict): 编辑指令 {文件路径: 编辑指令}
            original_files (dict): 原始文件 {文件路径: 文件内容}
        返回:
            modified_files (dict): 修改后的文件路径和内容
        """
        modified_files = {}
        # 遍历original_files中的每一对文件路径和内容
        for file_path, content in original_files.items():
            # 如果file_path在edit_instructions中，则应用编辑指令
            if file_path in edit_instructions:
                # 获取编辑指令
                instructions = edit_instructions[file_path] # 编辑指令
                # 生成提示
                prompt = f"{self.APPLY_EDITS_PROMPT}\n\n\
                            原始文件: {file_path}\n\
                            内容:\n{content}\n\n\
                            编辑指令:\n{instructions}\n\n\
                            更新后的文件内容:"
                response = self.chat_with_ai(prompt) 
                # 如果response不为空，则将response添加到modified_files中
                if response:
                    # 将response添加到modified_files中
                    modified_files[file_path] = response.strip()
            else:
                # 没有更改: 将content添加到modified_files中
                modified_files[file_path] = content 
        #如果edit_instructions有新建的文件，则将新建的文件添加到modified_files中    
        for file_path, content in edit_instructions.items():
            if file_path not in original_files:
                #print(colored(f"创建文件: {file_path}", "green"))
                response = self.chat_with_ai(f"{self.APPLY_EDITS_PROMPT}\n\n\
                                            创建文件: {file_path}\n\
                                            编辑指令:\n{content}\n\n\
                                            写入内容:")
                modified_files[file_path] = response.strip()
        # 返回modified_files
        return modified_files

    # 与AI聊天
    def chat_with_ai(self, user_message):
        """
        与AI进行对话或编辑请求

        参数:
            user_message (str): 用户输入
            is_edit_request (bool): 是否为编辑请求
            retry_count (int): 重试次数
        """

        try:
            messages = self.conversation_history + [{"role": "user", "content": user_message}]
            # 获取AI响应
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=messages,
                #max_completion_tokens=60000
            )
            logging.info("收到AI的响应。")
            self.last_ai_response = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": self.last_ai_response})
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            return self.last_ai_response
        except Exception as e:
            error_message = f"与OpenAI通信时发生错误: {e}"
            print(colored(error_message, "red"))
            logging.error(error_message)
            return None
    

    # 退出程序
    def quit(self):
        print(colored("再见！", "green"))
        logging.info("用户退出程序。")
        exit()

    # 调试
    def debug(self):
        if self.last_ai_response:
            print(colored("最后AI响应:", "blue"))
            print(self.last_ai_response)
        else:
            print(colored("没有AI响应可用。", "red"))
            logging.warning("用户在没有AI响应的情况下发出/debug命令。")
    
    # 重置聊天上下文
    def reset(self):
        """
        重置聊天上下文和添加的文件
        """
        self.conversation_history = []
        self.added_files.clear()
        self.last_ai_response = None
        print(colored("聊天上下文和添加的文件已重置。", "green"))
        logging.info("用户重置聊天上下文和添加的文件。")
    
    # 添加文件
    def add_files(self, paths):
        """
        添加文件或文件夹到上下文

        参数:
            paths (list): 文件或文件夹路径列表
        """
        if not paths:
            print(colored("请提供至少一个文件或文件夹路径。", "red"))
            logging.warning("用户没有提供文件或文件夹路径。")
            return
        #所有路径输入时都是相对self.root_dir的路径,这里需要转换为绝对路径
        paths = [os.path.abspath(os.path.join(self.root_dir, path)) for path in paths]
        for path in paths:
            if os.path.isfile(path):
                #print(colored(f"文件: {path}", "green"))
                add_file_to_context(path, self.added_files)
            elif os.path.isdir(path):
                for root, dirs, files_in_dir in os.walk(path):
                    dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
                    for file in files_in_dir:
                        file_path = os.path.join(root, file)
                        #print(colored(f"文件: {file_path}", "green"))
                        add_file_to_context(file_path, self.added_files)
            else:
                print(colored(f"错误: {path} 既不是文件也不是目录。", "red"))
                logging.error(f"{path} 既不是文件也不是目录。")
        total_size = sum(len(content) for content in self.added_files.values())
        if total_size > 1000000:
            print(colored("警告: 添加的文件的总大小很大，可能会影响性能。", "red"))
            logging.warning("添加的文件的总大小超过了100KB。")

    def edit_files(self, paths):
        """
        编辑文件或目录

        参数:
            paths (list): 文件或文件夹路径列表
        """
        if not paths:
            print(colored("请提供至少一个文件或文件夹路径。", "red"))
            logging.warning("用户在没有文件或文件夹路径的情况下发出/edit命令。")
            return
        # 将输入的文件路径添加到added_files中
        self.add_files(paths)
        # 编辑指令为所有文件
        edit_instruction = prompt(f"为所有文件编辑指令: ", style=self.style).strip() 
        # 编辑请求的提示
        edit_prompt=self.EDIT_INSTRUCTION_PROMPT
        # 编辑请求
        edit_request = f"""{edit_prompt}\n\n用户请求: {edit_instruction}\n  
                            可能需要修改的文件: 
                                        """
        for file_path, content in self.added_files.items():
            edit_request += f"\n文件： {file_path}\n内容：\n{content}\n\n" 

        ai_response = self.chat_with_ai(edit_request) 
        
        if ai_response:
            print(f"以下是 {self.MODEL} 建议的编辑指令:")
            rprint(Markdown(ai_response))
            # 应用编辑指令
            confirm = prompt("您想应用这些编辑指令吗? (yes/no): ", style=self.style).strip().lower()
            if confirm == 'yes':
                # 解析编辑指令
                edit_instructions = parse_edit_instructions(ai_response)
                # 应用编辑指令
                modified_files = self.apply_edit_instructions(edit_instructions, self.added_files)
                for file_path, new_content in modified_files.items():
                    apply_modifications(new_content, file_path)
            else:
                print(colored("编辑指令未应用。", "red"))
                logging.info("用户选择不应用编辑指令。")

    # 创建文件
    def create_project(self, creation_instruction):
        if not creation_instruction:
            print(colored("请在/create之后提供创建指令。", "red"))
            logging.warning("用户在没有指令的情况下发出/create命令。")
            return
        # 生成创建请求
        create_request = f"{self.CREATE_SYSTEM_PROMPT}\n\n用户请求: {creation_instruction}"
        ai_response = self.chat_with_ai(create_request)
        if ai_response:
            while True:
                print(f"以下是 {self.MODEL} 建议的创建结构:")
                markdown_ai_response = ai_response.replace("%%%", "```")
                rprint(Markdown(markdown_ai_response))

                confirm = prompt("您想执行这些创建步骤吗? (yes/no): ", style=self.style).strip().lower()
                if confirm == 'yes':
                    success = apply_creation_steps(ai_response, self.added_files, chat_with_ai=self.chat_with_ai,root_dir=self.root_dir)
                    if success:
                        break
                    else:
                        retry = prompt("创建失败。您想让AI再次尝试吗? (yes/no): ", style=self.style).strip().lower()
                        if retry != 'yes':
                            break
                        ai_response = self.chat_with_ai("之前的创建尝试失败。请尝试不同的方法。")
                else:
                        print(colored("创建步骤未执行。", "red"))
                        logging.info("用户选择不执行创建步骤。")
                        break
    def code_review(self, paths):
        if not paths:
            print(colored("请提供至少一个文件或文件夹路径。", "red"))
            logging.warning("用户在没有文件或文件夹路径的情况下发出/review命令。")
            return
        # 将输入的文件路径添加到added_files中
        self.add_files(paths)
        if not self.added_files:
            print(colored("没有有效的文件可以审查。", "red"))
            logging.warning("用户在没有文件的情况下发出/review命令。")
            return
        # 审查请求
        review_request = f"{self.CODE_REVIEW_PROMPT}\n\n要审查的文件:\n"
        for file_path, content in self.added_files.items():
            review_request += f"\n文件: {file_path}\n内容:\n{content}\n\n"  
        print(colored("分析代码并生成审查...", "magenta"))
        ai_response = self.chat_with_ai(review_request)
            
        if ai_response:
            print()
            print(colored("代码审查:", "blue"))
            rprint(Markdown(ai_response))
            logging.info("提供了代码审查。")    
    
    def chat_with_files(self, paths):
        """
        基于内容的聊天
        参数:
            user_message (str): 用户输入
        """
        if not paths:
            print(colored("请提供至少一个文件或文件夹路径。", "red"))
            logging.warning("用户在没有文件或文件夹路径的情况下发出/chat命令。")
            return
        # 将输入的文件路径添加到added_files中
        self.add_files(paths)
        # 聊天请求
        chat_instruction = prompt(f"User: ", style=self.style).strip() 
        # 聊天请求的提示
        chat_prompt=self.CHAT_INSTRUCTION_PROMPT
        # 聊天请求
        chat_request = f"""{chat_prompt}\n\n用户请求: {chat_instruction}\n  
                            相关文件: 
                                        """
        for file_path, content in self.added_files.items():
            chat_request += f"\n文件： {file_path}\n内容：\n{content}\n\n" 

        
        ai_response = self.chat_with_ai(chat_request) 
            
        if ai_response:
            print()
            print(colored(f"{self.MODEL}: ", "blue"))
            rprint(Markdown(ai_response)) 

    def planning_project(self, planning_instruction):
        """
        根据用户提供的指令规划项目结构和任务

        参数:
            paths (list): 文件或文件夹路径列表
        """

        if not planning_instruction:
            print(colored("请在/planning之后提供计划请求。", "red"))
            logging.warning("用户在没有指令的情况下发出/planning命令。")
            return

        planning_request = f"{self.PLANNING_PROMPT}\n\n计划请求: {planning_instruction}"
        ai_response = self.chat_with_ai(planning_request)
        if ai_response:
            print()
            print(colored(f"{self.MODEL}: ", "blue")) 
            rprint(Markdown(ai_response))
            logging.info("提供了详细计划。")
            
    def start(self):
        print(colored("命令:", "cyan"))
        print(colored("-"*50, "cyan"))
        commands = {
            "/planning": "规划项目结构和任务 (后跟指令)",
            "/create": "创建文件或文件夹 (后跟指令)",
            "/edit": "编辑文件或目录 (后跟路径)",
            "/reset": "重置聊天上下文并清除添加的文件",
            "/review": "审查代码文件 (后跟路径)",
            "/chat": "与AI聊天 (后跟路径)",
            "/debug": "打印最后AI响应",
            "/quit": "退出程序"
        }
        command_list = list(commands.keys())
        for cmd, desc in commands.items():
            print(f"{colored(cmd, 'magenta'):<10} {colored(desc, 'dark_grey')}")
        # 创建一个WordCompleter，自动补全命令
        completer = WordCompleter(
            command_list + self.files,
            ignore_case=True  # 忽略大小写
        )
        while True:
            print(colored("-"*50, "cyan"))
            user_input = prompt("You: ", style=self.style, completer=completer).strip()

            if user_input.lower() == '/quit':
                self.quit()  
            # 调试
            elif user_input.lower() == '/debug':
                self.debug()
            # 重置
            elif user_input.lower() == '/reset':
                self.reset()
            # 编辑
            elif user_input.startswith('/edit'):
                paths = user_input.split()[1:]
                self.edit_files(paths)
                self.added_files.clear()
            # 审查
            elif user_input.startswith('/review'):
                paths = user_input.split()[1:]
                self.code_review(paths) 
                self.added_files.clear()
            # 需要指令
            elif user_input.startswith('/create'):
                creation_instruction = user_input.split()[1:]
                self.create_project(creation_instruction)
                self.added_files.clear()
            # 计划
            elif user_input.startswith('/planning'):
                planning_instruction = user_input.split()[1:]
                self.planning_project(planning_instruction)
            # 聊天
            elif user_input.startswith('/chat'):
                paths = user_input.split()[1:]
                self.chat_with_files(paths)
                self.added_files.clear()
            else:
                ai_response = self.chat_with_ai(user_input)
                print(colored("-"*50, "cyan"))
                print(colored(f"{self.MODEL}", "cyan"))
                if ai_response:
                    print()
                    print(colored(f"{self.MODEL}:", "blue"))
                    rprint(Markdown(ai_response)) 