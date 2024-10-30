# PySS 编译器

PySS（**Python Simple Syntax**）是一门专为特殊架构设计的编程语言。通过 PySS，您可以编写高级语言代码，并将其编译为指定的指令集，以便在特定的处理器架构上运行。

## 特性

- **简单直观的语法**：采用类似 Python 的语法风格，降低学习门槛。
- **变量定义和赋值**：支持整数和字符串类型的变量定义和赋值操作。
- **算术运算**：支持加、减、乘、除等基本算术运算。
- **逻辑运算**：支持基本的逻辑判断，如 `>`、`<`、`==` 等。
- **条件判断**：支持 `if`、`else` 语句，实现程序的逻辑控制。
- **循环结构**：支持 `while` 和 `for` 循环，方便实现重复性任务。
- **字符串操作**：支持字符串的定义、赋值、拼接和比较等操作。
- **编译为指令集**：将 PySS 代码编译为特定的指令集，展示从源代码到可执行代码的完整过程。

## 项目结构

- `pyss_compiler.py`：PySS 编译器的主程序，包含了编译器的全部功能和 GUI 界面。
- `README.md`：项目的介绍文档，帮助您了解 PySS 的特性和使用方法。

## 安装与运行

### 环境要求

- **Python 3.x**
- **tkinter 库**（通常随 Python 一起安装）

### 运行编译器

在命令行中进入项目目录并运行：

```bash
python pyss_compiler.py
```

如果您的系统中有多个 Python 版本，可能需要使用 `python3` 命令：

```bash
python3 pyss_compiler.py

```

## 使用方法

1. **编写代码**：在编译器窗口的上方文本框中输入您的 PySS 代码。例如：
    
    ```python
    # 定义变量
    a = 10
    b = 5
    
    # 算术运算
    sum_result = a + b
    
    # 条件判断
    if a > b:
        max_value = a
    else:
        max_value = b
    
    # 循环结构
    total = 0
    for i in range(1, 6):
        total = total + i
    
    # 字符串操作
    greeting = "Hello"
    name = "PySS"
    message = greeting + ", " + name + "!"
    
    ```
    
2. **编译代码**：点击窗口中的 **“编译”** 按钮，编译器会将您的 PySS 代码转换为指令集代码。
3. **查看结果**：在下方的输出窗口中查看生成的指令集代码。

## 示例

以下是一个完整的示例代码，涵盖了 PySS 的主要功能：

```python
# 测试变量定义和赋值
a = 10
b = 20
c = 0

# 测试算术运算
sum_result = a + b
diff_result = a - b
prod_result = a * b
div_result = a / b

# 测试条件判断
if a < b:
    min_value = a
else:
    min_value = b

# 测试循环结构
counter = 0
while counter < 5:
    c = c + counter
    counter = counter + 1

# 测试 for 循环
total = 0
for i in range(1, 11):
    total = total + i

# 测试字符串操作
greeting = "Hello"
name = "PySS"
message = greeting + ", " + name + "!"

# 测试字符串比较
if greeting == "Hello":
    str_compare_result = 1
else:
    str_compare_result = 0

```

编译器会将上述代码转换为指令集代码，您可以在输出窗口中查看并分析生成的指令。

## 贡献指南

欢迎对 PySS 编译器的开发和完善做出贡献：

## 许可证

本项目采用 GPL-3 许可证

---

感谢您对 PySS 的关注和支持！希望 PySS 能够帮助您更好地理解编译器的原理和实现。
