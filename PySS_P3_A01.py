import tkinter as tk
from tkinter import scrolledtext
import re

class Compiler:
    def __init__(self):
        self.variables = {}          # 变量名到内存地址的映射
        self.string_variables = {}   # 字符串变量的起始地址
        self.string_literals = {}    # 字符串常量及其起始地址
        self.temp_address = 500      # 临时变量起始地址
        self.next_address = 100      # 数值变量地址起始值
        self.string_address = 1000   # 字符串变量地址起始值
        self.instructions = []       # 存储生成的指令
        self.label_count = 0         # 标签计数器
        self.zero_address = 0        # ZERO 常量的地址

    def compile(self, code):
        self.reset()
        lines = code.strip().split('\n')
        self.parse_lines(lines)
        return '\n'.join(self.instructions)

    def reset(self):
        self.variables = {}
        self.string_variables = {}
        self.string_literals = {}
        self.temp_address = 500
        self.next_address = 100
        self.string_address = 1000
        self.instructions = []
        self.label_count = 0
        # 定义 ZERO 常量
        self.zero_address = self.get_temp_address()
        self.instructions.append(f'WRITE #0, {self.zero_address}')

    def parse_lines(self, lines, indent_level=0):
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()
            current_indent = len(line) - len(stripped_line)
            if current_indent < indent_level:
                # 返回到上一级
                break
            if not stripped_line or stripped_line.startswith('#'):
                i += 1
                continue
            elif stripped_line.startswith('if'):
                i = self.handle_if(lines, i, indent_level)
            elif stripped_line.startswith('while'):
                i = self.handle_while(lines, i, indent_level)
            elif stripped_line.startswith('for'):
                i = self.handle_for(lines, i, indent_level)
            else:
                self.parse_line(stripped_line)
                i += 1
        return i

    def parse_line(self, line):
        if '=' in line and not line.startswith('if'):
            # 赋值语句
            var, expr = line.split('=', 1)
            var = var.strip()
            expr = expr.strip()
            self.handle_assignment(var, expr)
        else:
            # 其他语句（未实现）
            pass

    def handle_assignment(self, var, expr):
        if expr.startswith('"') and expr.endswith('"'):
            # 字符串常量赋值
            string_value = expr.strip('"')
            start_address = self.store_string_literal(string_value)
            dest_start_address = self.allocate_string_variable(var, len(string_value))
            self.copy_string(start_address, dest_start_address)
        elif var in self.string_variables or '"' in expr:
            # 字符串操作
            # 处理字符串拼接
            self.handle_string_operation(var, expr)
        else:
            # 数值变量赋值或运算
            if var not in self.variables:
                self.variables[var] = self.next_address
                self.next_address += 1
            dest_addr = self.variables[var]
            tokens = re.findall(r'\w+|\+|\-|\*|\/', expr)
            if len(tokens) == 1:
                value = tokens[0]
                if value.isdigit():
                    # 立即数赋值
                    self.instructions.append(f'WRITE #{value}, {dest_addr}')
                else:
                    # 变量赋值
                    src_addr = self.get_operand_address(value)
                    self.instructions.append(f'COPY {src_addr}, {dest_addr}')
            elif len(tokens) == 3:
                op1, operator, op2 = tokens
                op1_addr = self.get_operand_address(op1)
                op2_addr = self.get_operand_address(op2)
                if operator == '+':
                    self.instructions.append(f'ADD {op1_addr}, {op2_addr}')
                elif operator == '-':
                    self.instructions.append(f'SUB {op1_addr}, {op2_addr}')
                elif operator == '*':
                    self.instructions.append(f'MUL {op1_addr}, {op2_addr}')
                elif operator == '/':
                    self.instructions.append(f'DIV {op1_addr}, {op2_addr}')
                self.instructions.append(f'COPY c1, {dest_addr}')
            else:
                # 更复杂的表达式（未实现）
                pass

    def handle_string_operation(self, var, expr):
        # 处理字符串拼接
        parts = self.split_string_expr(expr)
        dest_start_address = self.allocate_string_variable(var)
        temp_address = dest_start_address
        for part in parts:
            if part.startswith('"') and part.endswith('"'):
                # 字符串常量
                string_value = part.strip('"')
                start_address = self.store_string_literal(string_value)
                self.copy_string(start_address, temp_address)
                temp_address += len(string_value)
            elif part in self.string_variables:
                # 字符串变量
                start_address = self.string_variables[part]
                length = self.get_string_length(start_address)
                self.copy_string(start_address, temp_address)
                temp_address += length
            else:
                # 非法操作
                pass
        # 添加字符串结束符
        self.instructions.append(f'WRITE #0, {temp_address}')

    def split_string_expr(self, expr):
        # 分割字符串表达式，例如："Hello" + ", " + name + "!"
        tokens = []
        current = ''
        in_string = False
        i = 0
        while i < len(expr):
            char = expr[i]
            if char == '"':
                if in_string:
                    current += char
                    tokens.append(current.strip())
                    current = ''
                    in_string = False
                else:
                    if current.strip():
                        tokens.append(current.strip())
                    current = char
                    in_string = True
            elif char in '+':
                if not in_string:
                    if current.strip():
                        tokens.append(current.strip())
                    tokens.append('+')
                    current = ''
                else:
                    current += char
            else:
                current += char
            i += 1
        if current.strip():
            tokens.append(current.strip())
        # 移除 '+'
        return [token for token in tokens if token != '+']

    def get_string_length(self, start_address):
        # 获取字符串长度（直到结束符 0）
        length = 0
        # 此处假设字符串长度已知，在实际实现中，需要在存储字符串时记录长度
        # 为了简化，我们假设每个字符串的最大长度为 100
        length = 100
        return length

    def allocate_string_variable(self, var, length=100):
        if var not in self.string_variables:
            start_address = self.string_address
            self.string_variables[var] = start_address
            self.string_address += length + 1  # 预留空间
        return self.string_variables[var]

    def copy_string(self, src_start, dest_start):
        # 字符串复制操作
        src_index = self.get_temp_address()
        dest_index = self.get_temp_address()
        one_addr = self.get_temp_address()
        self.instructions.append(f'WRITE #{src_start}, {src_index}')
        self.instructions.append(f'WRITE #{dest_start}, {dest_index}')
        self.instructions.append(f'WRITE #1, {one_addr}')
        loop_start = len(self.instructions)
        # 读取字符
        self.instructions.append(f'COPY [{src_index}], c1')
        # 写入字符
        self.instructions.append(f'COPY c1, [{dest_index}]')
        # 判断是否为结束符
        self.instructions.append(f'NUMB c1, {self.zero_address}')
        self.instructions.append(f'PUR N1, {self.zero_address}')
        jump_out_index = len(self.instructions)
        self.instructions.append(f'WRITE #{{jump_out}}, J1')
        self.instructions.append('JUMP')
        # 增加索引
        self.instructions.append(f'ADD {src_index}, {one_addr}')
        self.instructions.append(f'COPY c1, {src_index}')
        self.instructions.append(f'ADD {dest_index}, {one_addr}')
        self.instructions.append(f'COPY c1, {dest_index}')
        # 跳回循环开始
        steps_back = -(len(self.instructions) - loop_start + 2)
        self.instructions.append(f'WRITE #{steps_back}, J1')
        self.instructions.append('JUMP')
        # 计算跳出循环的指令数
        jump_out_steps = len(self.instructions) - jump_out_index - 2
        self.instructions[jump_out_index] = self.instructions[jump_out_index].replace('{{jump_out}}', str(jump_out_steps))

    def store_string_literal(self, string):
        if string in self.string_literals:
            return self.string_literals[string]
        start_address = self.string_address
        for char in string:
            char_code = ord(char)
            self.instructions.append(f'WRITE #{char_code}, {self.string_address}')
            self.string_address += 1
        # 添加字符串结束符（0）
        self.instructions.append(f'WRITE #0, {self.string_address}')
        self.string_address += 1
        self.string_literals[string] = start_address
        return start_address

    def get_operand_address(self, operand):
        if operand.isdigit():
            # 立即数
            temp_addr = self.get_temp_address()
            self.instructions.append(f'WRITE #{operand}, {temp_addr}')
            return temp_addr
        elif operand in self.variables:
            return self.variables[operand]
        elif operand in self.string_variables:
            return self.string_variables[operand]
        else:
            # 未定义的变量
            self.variables[operand] = self.next_address
            self.next_address += 1
            return self.variables[operand]

    def get_temp_address(self):
        addr = self.temp_address
        self.temp_address += 1
        return addr

    def handle_if(self, lines, index, indent_level):
        line = lines[index]
        stripped_line = line.strip()
        condition = re.findall(r'if\s+(.*):', stripped_line)[0]
        # 解析条件
        match = re.findall(r'(\w+)\s*(==|!=|>|<|>=|<=)\s*(.+)', condition)
        if not match:
            raise SyntaxError(f"无法解析的条件语句：{condition}")
        cond_left, operator, cond_right = match[0]
        # 生成条件判断指令
        cond_code = self.generate_condition(cond_left.strip(), operator, cond_right.strip())
        # 创建标签
        else_label = f'ELSE_{self.label_count}'
        end_label = f'ENDIF_{self.label_count}'
        self.label_count += 1
        # 添加条件判断指令
        self.instructions.extend(cond_code)
        # 添加跳转指令
        self.instructions.append(f'PUR N1, {self.zero_address}')
        self.instructions.append(f'WRITE #{{jump_else}}, J1')
        self.instructions.append('JUMP')
        # 保存当前指令位置以计算跳转步数
        jump_instr_index = len(self.instructions) - 2

        # 处理 if 块
        index += 1
        if_block = []
        while index < len(lines):
            current_line = lines[index]
            current_indent = len(current_line) - len(current_line.lstrip())
            if current_indent <= indent_level:
                break
            if_block.append(current_line)
            index += 1
        self.parse_lines(if_block, indent_level + 4)

        # 添加跳过 else 块的跳转
        self.instructions.append(f'WRITE #{{jump_end}}, J1')
        self.instructions.append('JUMP')
        # 保存跳转位置
        jump_end_instr_index = len(self.instructions) - 2

        # 计算跳转到 else 的指令数
        jump_else_steps = len(self.instructions) - jump_instr_index - 2
        self.instructions[jump_instr_index] = self.instructions[jump_instr_index].replace('{{jump_else}}', str(jump_else_steps))

        # 处理 else 块
        if index < len(lines) and lines[index].strip().startswith('else'):
            index += 1
            else_block = []
            while index < len(lines):
                current_line = lines[index]
                current_indent = len(current_line) - len(current_line.lstrip())
                if current_indent <= indent_level:
                    break
                else_block.append(current_line)
                index += 1
            self.parse_lines(else_block, indent_level + 4)

        # 计算跳转到结束的指令数
        jump_end_steps = len(self.instructions) - jump_end_instr_index - 2
        self.instructions[jump_end_instr_index] = self.instructions[jump_end_instr_index].replace('{{jump_end}}', str(jump_end_steps))

        return index

    def handle_while(self, lines, index, indent_level):
        line = lines[index]
        stripped_line = line.strip()
        condition = re.findall(r'while\s+(.*):', stripped_line)[0]
        loop_start_index = len(self.instructions)
        # 解析条件
        match = re.findall(r'(\w+)\s*(==|!=|>|<|>=|<=)\s*(.+)', condition)
        if not match:
            raise SyntaxError(f"无法解析的条件语句：{condition}")
        cond_left, operator, cond_right = match[0]
        # 生成条件判断指令
        cond_code = self.generate_condition(cond_left.strip(), operator, cond_right.strip())
        # 添加条件判断指令
        self.instructions.extend(cond_code)
        # 添加跳出循环的指令
        self.instructions.append(f'PUR N1, {self.zero_address}')
        self.instructions.append(f'WRITE #{{jump_out}}, J1')
        self.instructions.append('JUMP')
        # 保存跳转位置
        jump_out_instr_index = len(self.instructions) - 2

        # 处理循环体
        index += 1
        loop_block = []
        while index < len(lines):
            current_line = lines[index]
            current_indent = len(current_line) - len(current_line.lstrip())
            if current_indent <= indent_level:
                break
            loop_block.append(current_line)
            index += 1
        self.parse_lines(loop_block, indent_level + 4)

        # 跳回循环开始
        steps_back = -(len(self.instructions) - loop_start_index + 3)
        self.instructions.append(f'WRITE #{steps_back}, J1')
        self.instructions.append('JUMP')

        # 计算跳出循环的指令数
        jump_out_steps = len(self.instructions) - jump_out_instr_index - 2
        self.instructions[jump_out_instr_index] = self.instructions[jump_out_instr_index].replace('{{jump_out}}', str(jump_out_steps))

        return index

    def handle_for(self, lines, index, indent_level):
        line = lines[index]
        stripped_line = line.strip()
        # 解析 for 循环
        match = re.findall(r'for\s+(\w+)\s+in\s+range\((.*)\):', stripped_line)
        if match:
            var, range_expr = match[0]
            # 解析 range 参数
            range_params = [param.strip() for param in range_expr.split(',')]
            if len(range_params) == 1:
                start = 0
                end = int(range_params[0])
                step = 1
            elif len(range_params) == 2:
                start = int(range_params[0])
                end = int(range_params[1])
                step = 1
            elif len(range_params) == 3:
                start = int(range_params[0])
                end = int(range_params[1])
                step = int(range_params[2])
            else:
                raise SyntaxError(f"无法解析的 range 参数：{range_expr}")

            # 初始化循环变量
            if var not in self.variables:
                self.variables[var] = self.next_address
                self.next_address += 1
            var_addr = self.variables[var]
            self.instructions.append(f'WRITE #{start}, {var_addr}')

            # 设置循环条件
            loop_start_index = len(self.instructions)

            # 比较 var 与 end
            end_addr = self.get_temp_address()
            self.instructions.append(f'WRITE #{end}, {end_addr}')
            self.instructions.append(f'SUB {var_addr}, {end_addr}')  # c1 = var - end
            self.instructions.append(f'NUMB c1, {self.zero_address}')  # N1 = 比较结果

            # 如果 var >= end，跳出循环
            self.instructions.append(f'PUR N1, {self.zero_address}')
            self.instructions.append(f'WRITE #{{jump_out}}, J1')
            self.instructions.append('JUMP')

            # 保存跳转位置
            jump_out_instr_index = len(self.instructions) - 2

            # 处理循环体
            index += 1
            loop_block = []
            while index < len(lines):
                current_line = lines[index]
                current_indent = len(current_line) - len(current_line.lstrip())
                if current_indent <= indent_level:
                    break
                loop_block.append(current_line)
                index += 1
            self.parse_lines(loop_block, indent_level + 4)

            # 增加循环变量
            step_addr = self.get_temp_address()
            self.instructions.append(f'WRITE #{step}, {step_addr}')
            self.instructions.append(f'ADD {var_addr}, {step_addr}')
            self.instructions.append(f'COPY c1, {var_addr}')

            # 跳回循环开始
            steps_back = -(len(self.instructions) - loop_start_index + 3)
            self.instructions.append(f'WRITE #{steps_back}, J1')
            self.instructions.append('JUMP')

            # 计算跳出循环的指令数
            jump_out_steps = len(self.instructions) - jump_out_instr_index - 2
            self.instructions[jump_out_instr_index] = self.instructions[jump_out_instr_index].replace('{{jump_out}}', str(jump_out_steps))

            return index
        else:
            raise SyntaxError(f"无法解析的 for 循环：{line}")

    def generate_condition(self, left, operator, right):
        code = []
        left_addr = self.get_operand_address(left)
        right_addr = self.get_operand_address(right)
        zero_addr = self.zero_address
        temp_addr = self.get_temp_address()

        if operator == '==':
            code.append(f'SUB {left_addr}, {right_addr}')
            code.append(f'NUMB c1, {zero_addr}')
        elif operator == '!=':
            code.append(f'SUB {left_addr}, {right_addr}')
            code.append(f'NUMB c1, {zero_addr}')
            code.append(f'WRITE #1, {temp_addr}')
            code.append(f'SUB {zero_addr}, N1')  # N1 = -N1
            code.append(f'ADD N1, {temp_addr}')  # N1 = -N1 + 1
        elif operator == '>':
            code.append(f'SUB {left_addr}, {right_addr}')
            code.append(f'NUMB c1, {zero_addr}')
        elif operator == '<':
            code.append(f'SUB {right_addr}, {left_addr}')
            code.append(f'NUMB c1, {zero_addr}')
        elif operator == '>=':
            code.append(f'SUB {right_addr}, {left_addr}')
            code.append(f'NUMB c1, {zero_addr}')
            code.append(f'WRITE #1, {temp_addr}')
            code.append(f'SUB {zero_addr}, N1')
            code.append(f'ADD N1, {temp_addr}')
        elif operator == '<=':
            code.append(f'SUB {left_addr}, {right_addr}')
            code.append(f'NUMB c1, {zero_addr}')
            code.append(f'WRITE #1, {temp_addr}')
            code.append(f'SUB {zero_addr}, N1')
            code.append(f'ADD N1, {temp_addr}')
        else:
            raise SyntaxError(f"不支持的操作符：{operator}")

        return code

def main():
    root = tk.Tk()
    root.title("PySS 编译器")

    editor = scrolledtext.ScrolledText(root, width=80, height=20)
    editor.pack()

    output = scrolledtext.ScrolledText(root, width=80, height=20)
    output.pack()

    compiler = Compiler()

    def compile_code():
        code = editor.get('1.0', tk.END)
        try:
            asm_code = compiler.compile(code)
            output.delete('1.0', tk.END)
            output.insert(tk.END, asm_code)
        except Exception as e:
            output.delete('1.0', tk.END)
            output.insert(tk.END, f'编译错误：{e}')

    compile_button = tk.Button(root, text="编译", command=compile_code)
    compile_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
