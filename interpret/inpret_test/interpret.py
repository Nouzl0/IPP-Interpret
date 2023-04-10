import sys
import re
import argparse
import xml.etree.ElementTree as ET


# stack class -> stack interface
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        else:
            raise Exception("Stack is empty")

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)


# hash table class -> hash table interface
class HashTable:
    def __init__(self):
        self.table = {}
    
    def put(self, key, value):
        self.table[key] = value

    def replace_value(self, key, value):
        if key in self.table:
            self.table[key] = value
        else:
            self.table[key].append(value)
        
    def get(self, key):
        return self.table.get(key, None)
    
    def reset(self):
        self.table = {}

    def print_table(self):
        print(self.table)



# interpret class -> interpret interface
class Interpret:

    # instruction class -> for saving instruction data
    class Instruction:
        def __init__(self, opcode, order, arg1_type, arg1_text, arg2_type, arg2_text, arg3_type, arg3_text):
            self.opcode = opcode
            self.order = order
            self.arg1_type = arg1_type
            self.arg1_text = arg1_text
            self.arg2_type = arg2_type
            self.arg2_text = arg2_text
            self.arg3_type = arg3_type
            self.arg3_text = arg3_text


    # main public func. - runs the code
    def run_code_xml(self, str_ippcode23_xml): 

        inst = self.parse_instructions(str_ippcode23_xml)
        run_instructions = self.run_instructions(inst)


    # private func. - parses the instructions into an array of instructions
    def parse_instructions(self, str_ippcode23_xml):

        # initialize instruction data
        inst = []

        # get xml_tree children data
        tree_root = ET.fromstring(str_ippcode23_xml)
        tree_children = list(tree_root)

        # reading tree_children -> instruction data
        for child in tree_children:
            
            # get instruction data
            instruction = self.Instruction(child.attrib.get("opcode"), child.attrib.get("order"), None, None, None, None, None, None)

            # get xml_tree sub_children data
            tree_sub_children = list(child)
            sub_child_index = 0

            # reading tree_sub_children -> instruction arguments
            for sub_child_index, sub_child in enumerate(tree_sub_children):
                
                # get instruction argument data
                if sub_child_index == 0:
                    instruction.arg1_type = sub_child.attrib.get("type")
                    instruction.arg1_text = sub_child.text
                elif sub_child_index == 1:
                    instruction.arg2_type = sub_child.attrib.get("type")
                    instruction.arg2_text = sub_child.text
                elif sub_child_index == 2:
                    instruction.arg3_type = sub_child.attrib.get("type")
                    instruction.arg3_text = sub_child.text

            inst.append(instruction) 
        return inst


    # private func. - runs the instructions
    def run_instructions(self, inst):
        
        runner = ExecuteInstruction()

        opcode_methods = {
            "DEFVAR" : runner.execute_defvar,
            "MOVE" : runner.execute_move,
            #"CREATEFRAME" : runner.execute_createframe,
            #"PUSHFRAME" : runner.execute_pushframe,
            #"POPFRAME" : runner.execute_popframe,
            #"RETURN" : runner.execute_return,
            #"BREAK" : runner.execute_break,
            #"CALL" : runner.execute_call,
            #"EXIT" : runner.execute_exit,
            #"PUSHS" : runner.execute_pushs,
            #"POPS" : runner.execute_pops,
            #"LABEL" : runner.execute_label,
            #"JUMP" : runner.execute_jump,
            #"JUMPIFEQ" : runner.execute_jumpifeq,
            #"JUMPIFNEQ" : runner.execute_jumpifneq,
            #"DPRINT" : runner.execute_dprint,
            "WRITE" : runner.execute_write,
            #"READ" : runner.execute_read,
            #"CONCAT" : runner.execute_concat,
            #"STRLEN" : runner.execute_strlen,
            #"GETCHAR" : runner.execute_getchar,
            #"SETCHAR" : runner.execute_setchar,
            #"TYPE" : runner.execute_type,
            #"ADD" : runner.execute_add,
            #"SUB" : runner.execute_sub,
            #"MUL" : runner.execute_mul,
            #"IDIV" : runner.execute_idiv,
            #"LT" : runner.execute_lt,
            #"GT" : runner.execute_gt,
            #"EQ" : runner.execute_eq,
            #"AND" : runner.execute_and,
            #"OR" : runner.execute_or,
            #"NOT" : runner.execute_not,
            #"INT2CHAR" : runner.execute_int2char,
            #"STRI2INT" : runner.execute_stri2int,
        }

        # reading instructions
        i = 0
        while i < len(inst):

            # get instruction data
            if inst[i].opcode in opcode_methods:
                opcode_methods[inst[i].opcode](inst[i])

            print(inst[i].order, " - ", inst[i].opcode)
            print("\t",inst[i].arg1_type, " - ", inst[i].arg1_text)
            print("\t",inst[i].arg2_type, " - ", inst[i].arg2_text)
            print("\t",inst[i].arg3_type, " - ", inst[i].arg3_text, "\n")
            i += 1

        runner.debug_print()



# private classes called by method run_code_xml in interpret class
class ExecuteInstruction:

    def __init__(self):
        self.stack = Stack()
        self.symt_gf = HashTable()
        self.symt_tf = HashTable()
        self.symt_lf = HashTable()

    def debug_print(self):
        # debug print
        print("LF:")
        self.symt_lf.print_table()
        print("\nTF:")
        self.symt_tf.print_table()
        print("\nGF:")
        self.symt_gf.print_table()

    def execute_defvar(self, inst):
        
        if inst.arg1_type == "var":
            str_tmp = inst.arg1_text
            str_tmp = str_tmp.split("@", 1)
            var_type = str_tmp[0]
            var_name = str_tmp[1]

            if var_type == "GF":
                self.symt_gf.put(var_name, None)
            elif var_type == "TF":
                self.symt_tf.put(var_name, None)
            elif var_type == "LF":
                self.symt_lf.put(var_name, None)
            else:
                print("Error: invalid variable type")
        else: 
            print("Error: invalid argument type")

    def execute_move(self, inst):

        if inst.arg1_type == "var":
            str_tmp = inst.arg1_text
            str_tmp = str_tmp.split("@", 1)
            var_type = str_tmp[0]
            var_name = str_tmp[1]

            if var_type == "GF":
                self.symt_gf.replace_value(var_name, inst.arg2_text)
            elif var_type == "TF":
                self.symt_tf.replace_value(var_name, inst.arg2_text)
            elif var_type == "LF":
                self.symt_lf.replace_value(var_name, inst.arg2_text)
            else:
                print("Error: invalid variable type")
        else:
            print("Error: invalid argument type")

    def execute_write(self, inst):

        if inst.arg1_type == "var":
            str_tmp = inst.arg1_text
            str_tmp = str_tmp.split("@", 1)
            var_type = str_tmp[0]
            var_name = str_tmp[1]

        if var_type == "GF":
            print(self.symt_gf.get(var_name), end="")
        elif var_type == "TF":
            print(self.symt_tf.get(var_name), end="")
        elif var_type == "LF":
            print(self.symt_lf.get(var_name), end="")

# calling the interpret class
if __name__ == "__main__":
    interpret = Interpret()
    interpret.run_code_xml(sys.stdin.read())