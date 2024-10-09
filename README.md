# 介绍

Code Composer 是一个智能项目编码助手，旨在通过利用先进的大模型（如o1模型、Claude 3.5 Sonnet）来提升开发者的工作效率。它能够帮助开发者进行代码审查、项目规划、文件创建和编辑等任务，为软件开发过程提供智能化支持。这个工具特别适合那些希望提高编码效率、获得即时编程建议或需要协助进行项目管理的开发者。

## 功能
目前支持以下命令的调用：

```
/planning 规划项目结构和任务 (后跟指令)
/create   创建项目需要的文件或文件夹 (后跟指令)
/edit     编辑项目文件或目录 (后跟路径)
/reset    重置聊天上下文并清除添加的文件
/review   审查代码文件 (后跟路径)
/chat     与AI聊天 (后跟路径)
/debug    打印最后AI响应
/quit     退出程序
```

## 安装
### 环境变量配置
在项目根目录创建 .env 文件，并设置以下环境变量：
```
#你的OpenAI API密钥
OPENAI_API_KEY=
OPENAI_API_BASE_URL=
#使用的模型名称，建议使用claude-3.5-sonnet-20240620/o1-mini
MODEL=
#要排除的目录，多个目录用逗号分隔，如：.git,.idea,venv
EXCLUDED_DIRS=
```
### 安装依赖
```
pip install -r requirements.txt
```
## 使用
在配置好环境变量后，在项目根目录运行：
```
python main.py
```
注意：
启动时会跳出目录选择栏，这是选择根目录，后面所有的项目的创建、编辑都是在该目录下进行的。
确保在启动应用前已正确配置所有必要的环境变量。


## 使用示例:写一个贪吃蛇项目
1. 可以通过`/palnning`命令让AI帮忙规划项目结构
```
/planning 我想创建一个网页贪吃蛇项目
```
AI会帮你详细规划该项目，效果如下：

![](https://files.mdnice.com/user/4432/33aab384-578a-4491-a94e-b42e7fab44d1.png)

2. 接着，我们就可以让AI基于上面的规划，创建项目了:
```
/create 基于上面的规划，请创建该项目
```
于是，AI会将所有需要创建的目录/文件列出，如果统一，键入yes即可创建：

![](https://files.mdnice.com/user/4432/0c874b75-03f0-4aa1-9c7c-239e07e81f2c.png)

键入后：

![](https://files.mdnice.com/user/4432/77fb867a-55a1-4e9d-971b-a3e6984e784f.png)

我们来看看该目录，可以发现，文件已经全部被创建：

![](https://files.mdnice.com/user/4432/72ce2832-203d-4f87-9a9b-d5077c4e067f.png)

最后我们点击`index.html`就可以发现，生成代码可以正常运行：

![](https://files.mdnice.com/user/4432/bbe4b93a-886a-44ee-a03b-57756d3386d0.png)

当然，还有其他的功能，如代码文件的审查和修改等等，这里就不作过多演示，小伙伴们可以自己尝试。


## 注意事项

- 使用前请确保已正确配置API密钥和其他必要的环境变量。
- 对于大型项目或文件，处理时间可能会较长，请耐心等待。
- AI生成的代码和建议仍需人工审核，以确保其准确性和适用性。
- 定期备份重要文件，特别是在使用编辑功能时。

## 参考

本项目参考了以下项目：

- [o1-engineer](https://github.com/Code-WSY/o1-engineer)

## 许可证

该项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。