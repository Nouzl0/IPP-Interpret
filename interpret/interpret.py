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


# hash table
class HashTable:
    def __init__(self):
        self.table = {}
    
    # insert the key and nothing else
    def insert_key(self, key):
        self.table[key] = (None, None)

    # inserts or replaces the value and the type of the key
    def set_var(self, key, data, data_type):
        if key in self.table:
            self.table[key] = (data, data_type)
        else:
            # raise an error or handle the case where the key is not found
            print("Key not found", key)
            exit(1)
    
    # return the value and the type of the key
    def get_var(self, key):
        
        if key in self.table:
            return self.table.get(key)
        else:
            # raise an error or handle the case where the key is not found
            print("Key not found - ", key)
            exit(1)
    
    # clears the hash table
    def empty_table(self):
        self.table = {}

    # prints the hash table, for debugging purposes
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

        # run the code
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

        # methods which need instruction data
        opcode_data_methods = {
            "DEFVAR" : runner.execute_defvar,
            "MOVE" : runner.execute_move,
            "WRITE" : runner.execute_write,
            "TYPE" : runner.execute_type,
            "READ" : runner.execute_read,
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
            #"CONCAT" : runner.execute_concat,
            #"STRLEN" : runner.execute_strlen,
            #"GETCHAR" : runner.execute_getchar,
            #"SETCHAR" : runner.execute_setchar,
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

        # methods which don't need instruction data
        opcode_switch_methods = {
            "CREATEFRAME" : runner.execute_createframe,
            "PUSHFRAME" : runner.execute_pushframe,
            "POPFRAME" : runner.execute_popframe,
        }

        # reading instructions
        i = 0
        while i < len(inst):

            # get instruction data
            if inst[i].opcode in opcode_data_methods:
                opcode_data_methods[inst[i].opcode](inst[i])

            if inst[i].opcode in opcode_switch_methods:
                opcode_switch_methods[inst[i].opcode]()

            #print(inst[i].order, " - ", inst[i].opcode)
            #print("\t",inst[i].arg1_type, " - ", inst[i].arg1_text)
            #print("\t",inst[i].arg2_type, " - ", inst[i].arg2_text)
            #print("\t",inst[i].arg3_type, " - ", inst[i].arg3_text, "\n")
            #runner.debug_print()
            i += 1



# private classes called by method run_code_xml in interpret class
class ExecuteInstruction:

    def __init__(self):
        self.temporary_frame = "none"
        self.stack = Stack()
        self.symt_gf = HashTable()
        self.symt_tf = HashTable()
        self.symt_lf = HashTable()

    def debug_print(self):
        # debug print
        print("LF: ", end=" ")
        self.symt_lf.print_table()
        print("TF: ", end=" ")
        self.symt_tf.print_table()
        print("GF: ", end=" ")
        self.symt_gf.print_table()
        print("\n")

    # USED IN: MOVE  

    # text is the variable name with scope
    # type is the variable type
    # value is the variable value
    def update_symt(self, var_text, var_type, var_value):
        
        # get variable scope and name
        str_tmp = var_text.split("@", 1)
        var_scope = str_tmp[0]
        var_name = str_tmp[1]


        # temporary frame i active
        if var_scope == "LF" and self.temporary_frame == "active":
            self.symt_tf.set_var(var_name, var_value, var_type)

        # go according to variable scope
        else:
            # move value and type onto existing variable
            if var_scope == "GF":
                self.symt_gf.set_var(var_name, var_value, var_type)
            elif var_scope == "TF":
                self.symt_tf.set_var(var_name, var_value, var_type)
            elif var_scope == "LF":
                self.symt_lf.set_var(var_name, var_value, var_type)
            else:
                print("Error: invalid variable type")   
    

    # var text is the variable name with scope
    # returns the variable data[0] = [value]
    # returns the variable data[1] = [type]
    def gather_symt(self, var_text):

        # get variable scope and name
        str_tmp = var_text.split("@", 1)
        var_scope = str_tmp[0]
        var_name = str_tmp[1]


        # temporary frame is active
        if var_scope == "LF" and self.temporary_frame == "active":
            var_data = self.symt_tf.get_var(var_name)

        # go accoring to scope
        else:
            if var_scope == "GF":
                var_data = self.symt_gf.get_var(var_name)
            elif var_scope == "TF" or self.temporary_frame == "active":
                var_data = self.symt_tf.get_var(var_name)
            elif var_scope == "LF" and self.temporary_frame != "active":
                self.symt_lf.get_var(var_name)
            else:
                print("Error: invalid variable type")

        return var_data

    # DEFVAR
    def execute_defvar(self, inst):
        
        if inst.arg1_type == "var":

            # get variable scope and name
            str_tmp = inst.arg1_text
            str_tmp = str_tmp.split("@", 1)
            var_scope = str_tmp[0]
            var_name = str_tmp[1]

            # insert variable into the symbol table depening on the scope
            if var_scope == "GF":
                self.symt_gf.insert_key(var_name)
            elif var_scope == "TF" or self.temporary_frame == "active":
                self.symt_tf.insert_key(var_name)
            elif var_scope == "LF" and self.temporary_frame != "active":
                self.symt_lf.insert_key(var_name)
            else:
                print("Error: invalid variable type")
        else: 
            print("Error: invalid argument type")


    # MOVE
    def execute_move(self, inst):
        
        if inst.arg2_type == "var":
            var_data = self.gather_symt(inst.arg2_text)
            self.update_symt(inst.arg1_text, var_data[1], var_data[0])

        else:
            self.update_symt(inst.arg1_text, inst.arg2_type, inst.arg2_text)    


    # WRITE
    def execute_write(self, inst):

        # get variable data
        if inst.arg1_type == "var":
            var_data = self.gather_symt(inst.arg1_text)
            print(var_data[0], end="")

        # print string from given data
        else:
            print(inst.arg1_text, end="")


    # READ
    def execute_read(self, inst):

        # get variable data
        new_data = input()

        # update variable data
        self.update_symt(inst.arg1_text, inst.arg2_text, new_data)
    

    # TYPE
    def execute_type(self, inst):

        # get variable data
        var_data = self.gather_symt(inst.arg2_text)        

        # update variable data
        self.update_symt(inst.arg1_text, "string", var_data[1])


    # CREATEFRAME
    def execute_createframe(self):
        self.symt_tf.empty_table()
        self.temporary_frame = "exists"


    # PUSHFRAME
    def execute_pushframe(self):
        self.temporary_frame = "active"
    

    # POPFRAME
    def execute_popframe(self):
        self.temporary_frame = "inactive"





# calling the interpret class
if __name__ == "__main__":

    # stdin is not empty
    if not sys.stdin.isatty():
        
        # get input from stdin
        str_ippcode23_xml = sys.stdin.read()

        # debug - create file with input from stdin
        with open("ippcode23.xml", "w") as f:
            f.write(str_ippcode23_xml)
    
    # stdin is empty
    else:
        # debug - check if str_ippcode23_xml is not empty
        with open("ippcode23.xml", "r") as f:
            str_ippcode23_xml = f.read()


    # run interpret
    interpret = Interpret()
    interpret.run_code_xml(str_ippcode23_xml)