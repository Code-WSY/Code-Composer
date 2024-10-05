# 介绍

Coder Composer 是一个智能项目编码助手，旨在通过利用先进的大模型（如o1模型、Claude 3.5 Sonnet）来提升开发者的工作效率。它能够帮助开发者进行代码审查、项目规划、文件创建和编辑等任务，为软件开发过程提供智能化支持。这个工具特别适合那些希望提高编码效率、获得即时编程建议或需要协助进行项目管理的开发者。

# 功能

Coder Composer 提供了多种功能来支持开发者的工作：

1. 项目规划：通过 `/planning` ，AI可以帮助规划项目结构和任务。
2. 项目创建：通过 `/create` 命令，AI 可以根据需求自动创建项目文件，加速项目初始化过程。
3. 项目编辑：通过 `/edit` 命令，AI 可以对项目选择的代码文件或目录进行智能修改和优化，提高代码质量和效率。
4. 项目对话：使用 `/chat` 命令，可以基于选中的文件或目录与AI进行交流。
5. 代码审查：使用 `/review` 命令可以启动自动化代码审查，AI 将识别潜在问题并提供改进建议。

# 安装

## 环境变量配置

在项目根目录创建 `.env` 文件，并设置以下环境变量：

```bash
#你的OpenAI API密钥
OPENAI_API_KEY=
OPENAI_API_BASE_URL=
#使用的模型名称，建议使用claude-3.5-sonnet-20240620/o1-mini
MODEL=
#要排除的目录，多个目录用逗号分隔，如：.git,.idea,venv
EXCLUDED_DIRS=
```

## 安装依赖

```bash
pip install -r requirements.txt
```

# 使用

## 应用启动

在配置好环境变量后，使用以下命令启动应用程序：

```bash
python main.py
```

注意：

1. 启动时会跳出目录选择栏，这是选择根目录，后面所有的项目的创建、编辑都是在该目录下进行的。
2. 确保在启动应用前已正确配置所有必要的环境变量。

## 使用示例

### 创建一个网页贪吃蛇项目

首先通过 `/planning` 让AI帮忙规划项目结构：

```bash
/planning 我想创建一个网页版的连连看游戏
```

输出：

![img](https://sylearn.notion.site/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2Fea7343fb-f1bd-449d-b9b7-642a920c157b%2F75a9067d-3fc4-4fb4-8352-cef27babd7c8%2Fimage.png?table=block&id=1169513a-d132-8016-aaa3-c52d579d6fa9&spaceId=ea7343fb-f1bd-449d-b9b7-642a920c157b&width=1420&userId=&cache=v2)

接着，我们可以基于上面的规划，创建项目了

```bash
/create 基于上述内容创建连连看项目
```

输出：

![image.png](https://sylearn.notion.site/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2Fea7343fb-f1bd-449d-b9b7-642a920c157b%2Fb7f17fe8-51c7-47d9-aaed-2c9f537e817e%2Fimage.png?table=block&id=1169513a-d132-8038-b25a-d7600b9045a8&spaceId=ea7343fb-f1bd-449d-b9b7-642a920c157b&width=1420&userId=&cache=v2)

如果选择创建，则输入 `yes` ，连连看游戏则创建成功：

![image.png](https://sylearn.notion.site/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2Fea7343fb-f1bd-449d-b9b7-642a920c157b%2F6d6300a3-0690-4acd-9a26-d8e91e0e4351%2Fimage.png?table=block&id=1169513a-d132-8008-8353-d933b19b9868&spaceId=ea7343fb-f1bd-449d-b9b7-642a920c157b&width=1420&userId=&cache=v2)

如果有bug也可以通过 `/edit` 命令进行编辑。


## 注意事项

- 使用前请确保已正确配置API密钥和其他必要的环境变量。
- 对于大型项目或文件，处理时间可能会较长，请耐心等待。
- AI生成的代码和建议仍需人工审核，以确保其准确性和适用性。
- 定期备份重要文件，特别是在使用编辑功能时。

## 许可证

该项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。