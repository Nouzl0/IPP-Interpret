import sys
import re
import argparse
import xml.etree.ElementTree as ET


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

        # parse the instructions
        inst = self.parse_instructions(str_ippcode23_xml)

        # run the instructions
        self.run_instructions(inst)


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
        
        # initialize the symt_jump class for jumps
        symt_jump = SymbolTableJump()       # symbol table for jumps

        # initialize the symt_jump table for jumps
        i = 0
        while i < len(inst):    
            if inst[i].opcode == "LABEL":
                symt_jump.add_label(inst[i].arg1_text, i)

            i += 1


        # initialize the instruction execution class -> executes one instruction per method call
        runner = ExecuteInstruction()

        # [1] - methods with instrusction data
        opcode_inst_methods = {
            "MOVE" : runner.execute_move,               # Data frames
            "DEFVAR" : runner.execute_defvar,
            "PUSHS" : runner.execute_pushs,             # Data stack
            "POPS" : runner.execute_pops,
            "ADD" : runner.execute_add,                 # Arithmetic
            "SUB" : runner.execute_sub,
            "MUL" : runner.execute_mul,
            "IDIV" : runner.execute_idiv,
            "LT" : runner.execute_lt,                   # Relational
            "GT" : runner.execute_gt,
            "EQ" : runner.execute_eq,
            "AND" : runner.execute_and,                 # Logical
            "OR" : runner.execute_or,
            "NOT" : runner.execute_not,
            "INT2CHAR" : runner.execute_int2char,       # Conversion
            "STRI2INT" : runner.execute_stri2int,            
            "READ" : runner.execute_read,               # Input/Output
            "WRITE" : runner.execute_write,
            "CONCAT" : runner.execute_concat,           # String operations
            "STRLEN" : runner.execute_strlen,
            "GETCHAR" : runner.execute_getchar,
            "SETCHAR" : runner.execute_setchar,
            "TYPE" : runner.execute_type,               # Type           
            "LABEL" : runner.execute_label,             # Program flow
            "EXIT" : runner.execute_exit,                        
            "DPRINT" : runner.execute_dprint,           # Debugging
        }

        # [2] - methods with instrusction data which return a jump value
        opcode_jump_methods = {
            "JUMP" : runner.execute_jump,                   # Program flow
            "JUMPIFEQ" : runner.execute_jumpifeq,
            "JUMPIFNEQ" : runner.execute_jumpifneq,
        }

        # [3] - methods which don't need instruction data
        opcode_frame_methods = {
            "CREATEFRAME" : runner.execute_createframe,     # Data frames
            "PUSHFRAME" : runner.execute_pushframe,
            "POPFRAME" : runner.execute_popframe,
        }

        # [4] - call method
        opcode_call_method = {
            "CALL" : runner.execute_call,                   # Function calls         
        }

        # [5] - return method
        opcode_return_method = {
            "RETURN" : runner.execute_return,               # Function calls
        }

        # [6] - methods which returns a request value
        opcode_request_methods = {
            "BREAK" : runner.execute_break,                 # Debugging
        }



        # reading instructions and calling the corresponding execution method
        i = 0
        while i < len(inst):
            
            # [0] - debug print
            #print(i, "\n")
            #print(inst[i].order, " - ", inst[i].opcode)
            #print("\t",inst[i].arg1_type, " - ", inst[i].arg1_text)
            #print("\t",inst[i].arg2_type, " - ", inst[i].arg2_text)
            #print("\t",inst[i].arg3_type, " - ", inst[i].arg3_text, "\n")

            # [1] - basic instructions
            if inst[i].opcode in opcode_inst_methods:
                opcode_inst_methods[inst[i].opcode](inst[i])
                i += 1

            # [2] - jump instructions
            elif inst[i].opcode in opcode_jump_methods:
                
                # get the next instruction index
                inst_order = opcode_jump_methods[inst[i].opcode](inst[i], symt_jump)
                
                # if the instruction is not a jump, then continue with the next instruction
                if inst_order == -1:
                    i += 1
                else:
                    i = inst_order

            # [3] - frame instruction
            elif inst[i].opcode in opcode_frame_methods:
                opcode_frame_methods[inst[i].opcode]()
                i += 1

            # [4] - call instruction
            elif inst[i].opcode in opcode_call_method:

                # get the next instruction index
                inst_order = opcode_call_method[inst[i].opcode](inst[i], symt_jump, i)

                # if the instruction is not a jump, then continue with the next instruction
                if inst_order == -1:
                    i += 1
                else:
                    i = inst_order

            # [5] - return instruction
            elif inst[i].opcode in opcode_return_method:

                # get the next instruction index
                inst_order = opcode_return_method[inst[i].opcode]()

                # if the instruction is not a jump, then continue with the next instruction
                if inst_order == -1:
                    i += 1
                else:
                    i = inst_order

            # [6] - request instruction
            elif inst[i].opcode in opcode_request_methods:
                opcode_request_methods[inst[i].opcode]()
                i += 1
            
            # [7] - uknown opcode
            else: 
                sys.stderr.write("Error: unknown opcode\n")
                exit(53)



# private classes called by method run_code_xml in interpret class
class ExecuteInstruction:

    # Constructor
    def __init__(self):

        # data object initialization
        self.data_stack = DataStack()            # data stack
        self.func_stack = FuncCallStack()        # function call stack
        self.frame_data = FrameStackProtocol()   # interface for the frame stack
        self.decode = DecodeVariables()          # decode variable quirks


    # Debug print -> this method is temporary, will be removed in the future
    def debug_print(self):
        # debug print
        print("LF: ", end=" ")
        self.symt_lf.print_table()
        print("TF: ", end=" ")
        self.symt_tf.print_table()
        print("GF: ", end=" ")
        self.symt_gf.print_table()
        print("\n")


    # - - - - - - - - - - - - #
    #       Data frames       #
    # - - - - - - - - - - - - #

    # DEFVAR
    def execute_defvar(self, inst):
        
        # check the variable type
        if inst.arg1_type == "var":

            # insert the variable into the symbol table
            self.frame_data.symt_insert_var(inst.arg1_text)
        else: 
            sys.stderr.write("Error: DEFVAR - invalid argument type\n")
            exit(56)

    # MOVE
    def execute_move(self, inst):
        
        # check the variable type
        if inst.arg2_type == "var":

            # get the variable data from the symbol table and update the variable
            var_type, var_data = self.frame_data.symt_gather_var(inst.arg2_text)
            self.frame_data.symt_update_var(inst.arg1_text, var_type, var_data)
        else:
            # get the variable data from the instruction and update the variable
            self.frame_data.symt_update_var(inst.arg1_text, inst.arg2_type, inst.arg2_text)    

    # CREATEFRAME
    def execute_createframe(self):
        self.frame_data.frame_stack_create()

    # PUSHFRAME
    def execute_pushframe(self):
        self.frame_data.frame_stack_push()

    # POPFRAME
    def execute_popframe(self):
        self.frame_data.frame_stack_pop()


    # - - - - - - - - - - - - - #
    #       Function calls      # 
    # - - - - - - - - - - - - - #

    # CALL
    def execute_call(self, inst, symt_jump, push_inst_order):

        # get inst order
        inst_order = symt_jump.get_label(inst.arg1_text)

        # push the current instruction order to the stack
        self.func_stack.push(push_inst_order)

        # return the instruction order
        return inst_order
    
    # RETURN
    def execute_return(self):
        
        # get the instruction order from the stack
        inst_order = self.func_stack.pop()
        inst_order += 1

        # return the instruction order
        return inst_order


    # - - - - - - - - - - - - #
    #       Data stack        #
    # - - - - - - - - - - - - #

    # PUSHS
    def execute_pushs(self, inst):

        # get the variable
        var_type, var_data = self.frame_data.symt_get_symb(inst, "universal", "arg1")

        # push the variable to the stack
        self.data_stack.push(var_data, var_type)


    # POPS
    def execute_pops(self, inst):

        # get the variables from the stack
        var_type, var_data = self.data_stack.pop()

        # update the variable
        self.frame_data.symt_update_var(inst.arg1_text, var_data, var_type)
    

    # - - - - - - - - - - - - #
    #       Arithmetic        #
    # - - - - - - - - - - - - #

    # ADD
    def execute_add(self, inst):

        # get the variables
        _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "arithmetic", "same")

        # add the variables
        var_add = int(var_data_1) + int(var_data_2)

        # update the variable
        self.frame_data.symt_update_var(inst.arg1_text, "int", str(var_add))

    # SUB
    def execute_sub(self, inst):
        
        # get the variables
        _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "arithmetic", "same")

        # add the variables
        var_sub = int(var_data_1) - int(var_data_2)

        # update the variable
        self.frame_data.symt_update_var(inst.arg1_text, "int", str(var_sub))

    # MUL
    def execute_mul(self, inst):

        # get the variables
        _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "arithmetic", "same")

        # add the variables
        var_mul = int(var_data_1) * int(var_data_2)

        # update the variable
        self.frame_data.symt_update_var(inst.arg1_text, "int", str(var_mul))

    # IDIV
    def execute_idiv(self, inst):

        # get the variables
        _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "arithmetic", "same")

        # catch division by zero
        if var_data_2 == "0":
            sys.stderr.write("Error: IDIV - unleageal division by zero\n")
            exit(57)

        else:
            # add the variables
            var_idiv = int(var_data_1) // int(var_data_2)

            # update the variable
            self.frame_data.symt_update_var(inst.arg1_text, "int", str(var_idiv))


    # - - - - - - - - - - - - #
    #       Relational        #
    # - - - - - - - - - - - - #

    # LT
    def execute_lt(self, inst):
        
        # get the variables
        var_type, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "relational", "same")

        # compare the int variables
        if var_type == "int":
            if int(var_data_1) < int(var_data_2):
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

        # compare the string variables
        elif var_type == "string":
            if var_data_1 < var_data_2:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

        # compare the bool variables
        elif var_type == "bool":
            if var_data_1 == "false" and var_data_2 == "true":
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

    # GT
    def execute_gt(self, inst):
    
        # get the variables
        var_type, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "relational", "same")

        # compare the int variables
        if var_type == "int":
            if int(var_data_1) > int(var_data_2):
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

        # compare the string variables
        elif var_type == "string":
            if var_data_1 > var_data_2:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

        # compare the bool variables
        elif var_type == "bool":
            if var_data_1 == "true" and var_data_2 == "false":
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

    # EQ
    def execute_eq(self, inst):
        
        # get the variables
        var_type, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "relational", "same")

        # compare the int variables
        if var_type == "int":
            if int(var_data_1) == int(var_data_2):
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

        # compare the string variables
        elif var_type == "string":
            if var_data_1 == var_data_2:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

        # compare the bool variables
        elif var_type == "bool":
            if var_data_1 == var_data_2:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")


    # - - - - - - - - - - - - #
    #         Logical         #
    # - - - - - - - - - - - - #

    # AND
    def execute_and(self, inst):
        
        # get the variables
        _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "logical", "same")

        # compare the bool variables
        if var_data_1 == "true" and var_data_2 == "true":
            self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
        else:
            self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

    # OR
    def execute_or(self, inst):

        # get the variables
        _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "logical", "same")

        # compare the bool variables
        if var_data_1 == "false" and var_data_2 == "false":
            self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")
        else:
            self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")

    # NOT
    def execute_not(self, inst):
        
        # get the variables
        _, var_data = self.frame_data.symt_get_symb(inst, "boolean", "arg2")

        # compare the bool variables
        if var_data == "true":
            self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")
        else:
            self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")


    # - - - - - - - - - - - - #
    #       Conversions       #
    # - - - - - - - - - - - - #

    # INT2CHAR
    def execute_int2char(self, inst):
        
        # get the variables
        _, var_data = self.frame_data.symt_get_symb(inst, "integer", "arg2")

        # convert the int to char
        try:
            char = chr(int(var_data))
        except ValueError:
            sys.stderr.write("Error: invalid value of type int\n")
            exit(58)

        # update value
        self.frame_data.symt_update_var(inst.arg1_text, "string", str(char))

    # STRI2INT
    def execute_stri2int(self, inst):

        # get the variables
        _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "string_int", "different")
        char_pos = int(var_data_2)

        # check the string index with char_pos position
        if char_pos < len(var_data_1):
            char = var_data_1[char_pos]
        else:
            sys.stderr.write("Error: string index out of range\n")
            exit(58)            

        # update value
        self.frame_data.symt_update_var(inst.arg1_text, "int", ord(char))


    # - - - - - - - - - - - - #
    #      Input/Output       #
    # - - - - - - - - - - - - #

    # READ
    def execute_read(self, inst):

        # check if there is input
        try: 
            new_data = input()
            data_type = inst.arg2_text

        except EOFError:
            data_type = "nil"
            new_data = "nil"


        # check the type and value of input
        if new_data == None:
            data_type = "nil"
            new_data = "nil"

        # if is int
        elif data_type == "int":
            try:
                int(new_data)
            except ValueError:
                data_type = "nil"
                new_data = "nil"  

        # if is bool
        elif data_type == "bool":
            new_data = new_data.lower()
            if new_data != "true" and new_data != "false":
                data_type = "nil"
                new_data = "nil"
        
        # if is string
        elif data_type == "string":
            print("string")
            if not re.match(r'^([^\s#\\\\]|\\\\[0-9]{3})*$', new_data):
                data_type = "nil"
                new_data = "nil"
        else:
            data_type = "nil"
            new_data = "nil"

        # update variable data
        self.frame_data.symt_update_var(inst.arg1_text, data_type, new_data)
    
    # WRITE
    def execute_write(self, inst):

        # get variable data
        if inst.arg1_type == "var":
            var_type, var_data = self.frame_data.symt_gather_var(inst.arg1_text)
            
            # print empty string
            if var_type == "nil":
                print("", end="")

            # print the value of variable
            elif var_data == None:
                print("", end="")

            # print the value of variable
            else:
                print(var_data, end="")

        # print string from given data
        else:

            # print None value
            if inst.arg1_text == None:
                print("", end="")
            
            # print by type
            else:
                # print string type
                if inst.arg1_type == "string":
                    string = self.decode.string(inst.arg1_text)
                    print(string, end="")

                # print nil type
                elif inst.arg1_type == "nil":
                    print("", end="")

                # print other types
                else:
                    print(inst.arg1_text, end="")

    # - - - - - - - - - - - - #
    #    String operations    #
    # - - - - - - - - - - - - #

    # CONCAT
    def execute_concat(self, inst):
            
        # get the variables
        _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "string_string", "same")

        # decode the strings
        var_data_1 = self.decode.string(var_data_1)
        var_data_2 = self.decode.string(var_data_2)

        # check if the string are not empty
        if (var_data_1 == None):
            var_data_1 = ""
        elif (var_data_2 == None):
            var_data_2 = ""

        # concatenate strings
        self.frame_data.symt_update_var(inst.arg1_text, "string", var_data_1 + var_data_2)

    # STRLEN
    def execute_strlen(self, inst):

        # get the variables
        _, var_data = self.frame_data.symt_get_symb(inst, "string", "arg2")

        # decode the string
        var_data = self.decode.string(var_data)

        # get the string length
        if var_data == None:
            self.frame_data.symt_update_var(inst.arg1_text, "int", 0)
        else:
            self.frame_data.symt_update_var(inst.arg1_text, "int", len(var_data))

    # GETCHAR
    def execute_getchar(self, inst):
        
        # get the variables
        _, var_string, _, var_int = self.frame_data.symt_get_symb1_symb2(inst, "string_int", "different")
        
        # decode the string
        var_string = self.decode.string(var_string)

        # check the string index with char_pos position
        if len(var_string) < int(var_int):
            sys.stderr.write("Error: string index out of range\n")
            exit(58)

        # get the char
        try:
            char = var_string[int(var_int)]
        except IndexError:
            sys.stderr.write("Error: string index out of range\n")
            exit(58)

        # update value
        self.frame_data.symt_update_var(inst.arg1_text, "string", char)


    # SETCHAR
    def execute_setchar(self, inst):

        # get the variables
        _, var_int, _, var_string = self.frame_data.symt_get_symb1_symb2(inst, "int_string", "different")

        # check the var and get the data
        if inst.arg1_type == "var":
            var_type, var_data = self.frame_data.symt_gather_var(inst.arg1_text)
            
            if var_type != "string":
                sys.stderr.write("Error: invalid type of variable\n")
                exit(53) 
        else:
            sys.stderr.write("Error: invalid type of variable\n")
            exit(53)

        # check the string index with char_pos position
        # check the var_int
        if var_int == None:
            var_int = "0"

        # check var_data
        if var_data == None:
            var_data = ""

        # check the var_string
        if var_string == None:
            var_string = ""

        elif len(var_string) <= int(var_int):
            sys.stderr.write("Error: string index out of range\n")
            exit(58)

        # check if var_string is not empty
        if var_string == None:
            sys.stderr.write("Error: invalid value of type string\n")
            exit(58)

        # modify the var data string
        var_data = var_data[:int(var_int)] + var_string[0] + var_data[int(var_int) + 1:]

        # update value
        self.frame_data.symt_update_var(inst.arg1_text, "string", var_data)


    # - - - - - - - - - - - - #
    #         Types           #
    # - - - - - - - - - - - - #

    # TYPE
    def execute_type(self, inst):

        # get variable data
        var_type, _ = self.frame_data.symt_get_symb(inst, "universal", "arg2")        

        # update variable data
        self.frame_data.symt_update_var(inst.arg1_text, "string", var_type)


    # - - - - - - - - - - - - #
    #      Program flow       #
    # - - - - - - - - - - - - #

    # LABEL
    def execute_label(self, inst):
        pass

    # JUMP
    def execute_jump(self, inst, symt_jump):
        
        # return the opcode order
        return symt_jump.get_label(inst.arg1_text)
    
    # JUMPIFEQ
    def execute_jumpifeq(self, inst, symt_jump):

        # get the variables
        var_type, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "relational", "same")

        # compare the int variables
        if var_type == "int":
            if int(var_data_1) == int(var_data_2):
                return symt_jump.get_label(inst.arg1_text)
            else:
                return -1

        # compare the string variables
        elif var_type == "string":
            if var_data_1 == var_data_2:
                return symt_jump.get_label(inst.arg1_text)
            else:
                return -1

        # compare the bool variables
        elif var_type == "bool":
            if var_data_1 == var_data_2:
                return symt_jump.get_label(inst.arg1_text)
            else:
                return -1

    # JUMPIFNEQ
    def execute_jumpifneq(self, inst, symt_jump):

        # get the variables
        var_type, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "relational", "same")

        # compare the int variables
        if var_type == "int":
            if int(var_data_1) != int(var_data_2):
                return symt_jump.get_label(inst.arg1_text)
            else:
                return -1

        # compare the string variables
        elif var_type == "string":
            if var_data_1 != var_data_2:
                return symt_jump.get_label(inst.arg1_text)
            else:
                return -1

        # compare the bool variables
        elif var_type == "bool":
            if var_data_1 != var_data_2:
                return symt_jump.get_label(inst.arg1_text)
            else:
                return -1

    # EXIT
    def execute_exit(self, inst):

        # get the variables
        _, var_data = self.frame_data.symt_get_symb(inst, "integer", "arg1")

        # check if the integer is in interval <0,49>
        if int(var_data) < 0 or int(var_data) > 49:
            sys.stderr.write("Error: wrong value of exit code\n")
            exit(57)

        # exit the program
        exit(int(var_data))


    # - - - - - - - - - - - - #
    #        Debugging        #
    # - - - - - - - - - - - - #

    # DPRINT
    def execute_dprint(self, inst):
        # get variable data
        if inst.arg1_type == "var":
            _, var_data = self.frame_data.symt_gather_var(inst.arg1_text)
            sys.stderr.write(var_data)

        # print string from given data
        else:

            # decodes string and then prints it
            if inst.arg1_type == "string":
                string = self.decode.string(inst.arg1_text)
                sys.stderr.write(string)
            else:
                sys.stderr.write(inst.arg1_text)

    # BREAK
    def execute_break(self):
        pass




# - - -  - - - - - - - - - - - - - - #
#        FRAME-STACK-Protocol        #
# - - -  - - - - - - - - - - - - - - #
# Get/Insert/Update/Delete from the frame-stack
# Uses: - FrameStack class  - for accessing the frame-stack

class FrameStackProtocol:

    # constructor
    def __init__(self):

        # initialize frame-stack
        self.frame_stack = FrameStack()

        # initialize symtables
        self.symt_gf = SymbolTableData()
        self.symt_tf = None
        self.symt_lf = None

        # init decode object
        self.decode = DecodeVariables()


    # - - - - - - - - - - #
    # FRAME-STACK METHODS #
    # - - - - - - - - - - #

    # creates temporary frame
    def frame_stack_create(self):

        # create temporary frame
        self.symt_tf = SymbolTableData()


    # push temporary frame to frame-stack
    def frame_stack_push(self):
        
        # push and return the head of the frame-stack
        self.symt_lf = self.frame_stack.push_frame(self.symt_tf)

        # delete temporary frame
        self.symt_tf = None

    # pop temporary frame from frame-stack
    def frame_stack_pop(self):

        # pop and return the head and the popped frame
        self.symt_lf, self.symt_tf = self.frame_stack.pop_frame()


    # - - - - - - - - - - - - #
    #   SET/GET-SYMT METHODS  #
    # - - - - - - - - - - - - #

    # symt_insert_var
    # text is the variable with scope
    def symt_insert_var(self, var_text):

        # get variable scope and name
        str_tmp = var_text.split("@", 1)
        var_scope = str_tmp[0]
        var_name = str_tmp[1]


        # insert variable into the symbol table depening on the scope
        if var_scope == "GF" and self.symt_gf != None:
            self.symt_gf.insert_key(var_name)
        elif var_scope == "TF" and self.symt_tf != None:
            self.symt_tf.insert_key(var_name)
        elif var_scope == "LF" and self.symt_lf != None:
            self.symt_lf.insert_key(var_name)
        else:
            sys.stderr.write("Error: symt_insert_var - nowhere to insert variable\n")
            exit(52)


    # text is the variable name with scope
    # type is the variable type
    # value is the variable value
    def symt_update_var(self, var_text, var_type, var_value):
        
        # get variable scope and name
        str_tmp = var_text.split("@", 1)
        var_scope = str_tmp[0]
        var_name = str_tmp[1]

        # decodes string var type 
        if var_type == "string":
            var_value = self.decode.string(var_value)

        # move value and type onto existing variable
        if var_scope == "GF" and self.symt_gf != None:
            self.symt_gf.set_var(var_name, var_value, var_type)
        elif var_scope == "TF" and self.symt_tf != None:
            self.symt_tf.set_var(var_name, var_value, var_type)
        elif var_scope == "LF" and self.symt_lf != None:
            self.symt_lf.set_var(var_name, var_value, var_type)
        else:
            sys.stderr.write("Error: symt_update_var - nowhere to update the variable\n")
            exit(52)   
    

    # var text is the variable name with scope
    # returns the variable data[0] = [value]
    # returns the variable data[1] = [type]
    def symt_gather_var(self, var_text):

        # return var defalut initalization
        var_type = ""
        var_data = ""

        # get variable scope and name
        str_tmp = var_text.split("@", 1)
        var_scope = str_tmp[0]
        var_name = str_tmp[1]

        # go accoring to scope
        if var_scope == "GF" and self.symt_gf != None:
            var_data, var_type = self.symt_gf.get_var(var_name)
        elif var_scope == "TF" and self.symt_tf != None:
            var_data, var_type = self.symt_tf.get_var(var_name)
        elif var_scope == "LF" and self.symt_lf != None:
            var_data, var_type = self.symt_lf.get_var(var_name)
        else:
            sys.stderr.write("Error: symt_gather_var - nowhere to gather the variable\n")
            exit(52)

        return var_type, var_data


    # - - - - - - - - - - - - - - #
    #  INSTRUCTION SYMT METHODS   #
    # - - - - - - - - - - - - - - #

    # type_options
    # WRITE, DPRINT, PUSHS      - type_option =  "universal" - any 
    # STRLEN,                   - type_option =  "string" - str
    # EXIT, STRLEN              - type_option =  "integer" - int
    # NOT,                      - type_option =  "boolean" - bool

    # arg_num
    # arg1 - first argument
    # arg2 - second argument
    # arg3 - third argument
    def symt_get_symb(self, inst, type_option, arg_num):
        
        # saving the var_type
        var_type = ""
        var_data = ""
        
        # get type options
        check_type_dict = {
            "universal":        (["int", "bool", "string", "nil"]),
            "string":           (["string"]),
            "integer":          (["int"]),
            "boolean":          (["bool"]),
        }

        # arg_num options
        arg_num_dict = {
            "arg1":             (inst.arg1_type, inst.arg1_text),
            "arg2":             (inst.arg2_type, inst.arg2_text),
            "arg3":             (inst.arg3_type, inst.arg3_text),
        }

        # internal error check
        try:
            check_type = check_type_dict[type_option]
            arg_type, arg_text = arg_num_dict[arg_num]
        except KeyError:
            sys.stderr.write("Error: ExecuteInstruction - Private method symtget_arithmetic - invalid type option\n")
            exit(99)


        # get the second var data from the symbol table
        if arg_type == "var":
            var_type, var_data = self.symt_gather_var(arg_text)
            
            # check if the variable is int
            if var_type not in check_type:
                sys.stderr.write("Error: - invalid second variable type\n")
                exit(53)

        # get the var data from the instruction
        elif arg_type in check_type:
            var_data = arg_text
            var_type = arg_type
        else:
            sys.stderr.write("Error: - invalid second variable type\n")
            exit(53)

        return var_type, var_data


    # type_options
    # ADD, SUB, MUL, IDIV   - type_check =  "arithmetic" - int, int
    # AND, OR, NOT          - type_check =  "logical" - bool, bool
    # LT, GT, EQ            - type_check =  "relational" - string or int or bool, string or int or bool
    # JUMPIFEQ, JUMPIFNEQ   - type_check =  "jump" - string or int or bool
    # STR2INT, GETCHAR      - type_check =  "string_int" - string, int
    # SETCHAR               - type_check =  "int_string" - int, string
    # CONCAT                - type_check =  "concat" - string, string

    # type_similarity
    # ADD, SUB, MUL, IDIV, AND, OR, NOT, LT, GT, EQ, JUMPIFEQ, JUMPIFNEQ, CONCAT   
    # - type_similarity =  "same" 
    # STR2INT, GETCHAR      
    # - type_similarity =  "different"           
    def symt_get_symb1_symb2(self, inst, type_option, type_similarity):

        # [0] - parse function arguments
        # saving the var_type
        var_type_1 = ""
        var_type_2 = ""
        var_data_1 = ""
        var_data_2 = ""
        
        # get type option
        check_type_dict = {
            "arithmetic":       (["int"], ["int"]),
            "logical":          (["bool"], ["bool"]),
            "relational":       (["string", "int", "bool"], ["string", "int", "bool"]),
            "jump":             (["string", "int", "bool"], ["string", "int", "bool"]),
            "string_int":       (["string"], ["int"]),
            "int_string":       (["int"], ["string"]),
            "string_string":    (["string"], ["string"])
        }

        try:
            check_type_1, check_type_2 = check_type_dict[type_option]
        except KeyError:
            sys.stderr.write("Error: ExecuteInstruction - Private method symtget_arithmetic - invalid type option\n")
            exit(99)


        # [1] - get the second var data from the symbol table
        if inst.arg2_type == "var":
            var_type_1, var_data_1 = self.symt_gather_var(inst.arg2_text)
            
            # check if the variable is int
            if var_type_1 not in check_type_1:
                sys.stderr.write("Error: - invalid second variable type\n")
                exit(53)

        # get the var data from the instruction
        elif inst.arg2_type in check_type_1:
            var_data_1 = inst.arg2_text
            var_type_1 = inst.arg2_type
        else:
            sys.stderr.write("Error: - invalid second variable type\n")
            exit(53)


        # [2] - get the third var data from the symbol table
        if inst.arg3_type == "var":
            var_type_2, var_data_2 = self.symt_gather_var(inst.arg3_text)
            
            # they should be the same type  
            if type_similarity == "same":
                if var_type_2 != var_type_1:
                    sys.stderr.write("Error: - invalid third variable type\n")
                    exit(53)
        
            # they can be different types
            elif type_similarity == "different":
                if var_type_2 not in check_type_2:
                    sys.stderr.write("Error: - invalid third variable type\n")
                    exit(53)
            
            # internal error wrong type_similarity
            else:
                sys.stderr.write("Error: ExecuteInstruction - Private method symtget_arithmetic - invalid type similarity\n")
                exit(99)


        # [3] - get the third var data from the instruction
        else:
            # they should be the same type
            if type_similarity == "same":
                if inst.arg3_type == var_type_1:
                    var_data_2 = inst.arg3_text
                else:
                    sys.stderr.write("Error: - invalid second variable type\n")
                    exit(53)
            
            # they can be different types
            elif type_similarity == "different":
                if inst.arg3_type in check_type_2:
                    var_data_2 = inst.arg3_text
                else:
                    sys.stderr.write("Error: - invalid second variable type\n")
                    exit(53)
            
            # internal error wrong type_similarity
            else:
                sys.stderr.write("Error: ExecuteInstruction - Private method symtget_arithmetic - invalid type similarity\n")
                exit(99)
            
        return var_type_1, var_data_1, var_type_2, var_data_2 
        


# - - -  - - - - - - - - - - - - #
#        FRAME-STACK CLASS       #
# - - -  - - - - - - - - - - - - #
# Implemention of the frame stack
# Uses: - SymbolTableData class  - for storing the actual data 

class FrameStack:
    
    # initialisation -> global frame is always created and never deleted
    def __init__(self):
        self.__frame_stack = []                 # stack of frames -> stack of symtables  

    # pushes the temporary frame to stack and lf will point to the head of the stack
    def push_frame(self, symt_tf):
        
        # check if the temporary frame exists and push it to the stack
        if symt_tf is not None:
            self.__frame_stack.append(symt_tf)
            symt_lf = symt_tf
        else:
            sys.stderr.write("Error: FrameStack - push_frame_to_stack - no temporary frame\n")
            exit(55)

        # returns symt_lf -> new local frame
        return symt_lf
        

    # pops the frame from the stack and lf will point to the head of the stack
    def pop_frame(self):

        # check if the stack is not empty
        if len(self.__frame_stack) > 0:
            symt_tf = self.__frame_stack.pop()

            # check if symt_lf can be set to the head of the stack
            if len(self.__frame_stack) > 0:
                symt_lf = self.__frame_stack[-1]
            else:
                symt_lf = None
        
        # stack is empty
        else:
            sys.stderr.write("Error: FrameStack - pop_frame_from_stack - stack is empty\n")
            exit(55)

        # returns symt_lf -> new local frame, symt_tf -> popped frame
        return symt_lf, symt_tf        



# - - -  - - - - - - - - - - - - - - #
#       SYMBOL-TABLE-DATA CLASS      #
# - - -  - - - - - - - - - - - - - - #
# Symbol table class for storing variables

class SymbolTableData:

    # init the symbol table
    def __init__(self):
        self.table = {}
    
    # insert the key and nothing else
    def insert_key(self, key):

        # check if the key is already in the table
        if key not in self.table:
            self.table[key] = (None, None)
        else:
            sys.stderr.write("Variable already exists \n")
            exit(52)

    # inserts or replaces the value and the type of the key
    def set_var(self, key, data, data_type):
        if key in self.table:
            self.table[key] = (data, data_type)
        else:
            # raise an error or handle the case where the key is not found
            sys.stderr.write("Key not found \n")
            exit(52)
    
    # return the value and the type of the key
    def get_var(self, key):
        
        if key in self.table:
            var_data, var_value = self.table.get(key)
            return var_data, var_value
        else:
            # raise an error or handle the case where the key is not found
            sys.stderr.write("Key not found \n")
            exit(52)
    
    # clears the hash table
    def empty_table(self):
        self.table = {}

    # prints the hash table, for debugging purposes
    def print_table(self):
        print(self.table)



# - - -  - - - - - - - - - - - - #
#        DATA-STACK CLASS        #
# - - -  - - - - - - - - - - - - #
# Implemention of the data stack for storing variables

# stack class -> stack interface
class DataStack:
    def __init__(self):
        self.items = []

    def push(self, data, data_type):
        self.items.append((data, data_type))

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        else:
            raise Exception("Stack is empty")

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)


# - - -  - - - - - - - - - - - - - - #
#       FUNC-CALL-STACK CLASS        #
# - - -  - - - - - - - - - - - - - - #
# Implemention of stack which stores where to jump with instructions CALL and RETURN

class FuncCallStack:

    # init the stack
    def __init__(self):
        self.stack = []
    
    # push the instruction order to the stack
    def push(self, inst_order):
        self.stack.append(inst_order)

    # pop the instruction order from the stack
    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        else:
            sys.stderr.write("Error: FuncCallStack - pop - stack is empty\n")
            exit(56)

    # check if the stack is empty
    def is_empty(self):
        return len(self.stack) == 0
    
    # get the size of the stack
    def size(self):
        return len(self.stack)
    




# - - -  - - - - - - - - - - - - - - - #
#       SYMBOL-TABLE-JUMP CLASS        #
# - - -  - - - - - - - - - - - - - - - #
# Implemention of symbol table which stores where to jump to with labels

class SymbolTableJump:

    # init the symbol table
    def __init__(self):
        self.table = {}

    # add label to the table
    def add_label(self, label, inst_order):

        # if the label is already in the table, raise an error
        if label in self.table:
            sys.stderr.write("Error: SymbolTableJump - add_label - label already exists\n")
            exit(52)

        # add the label to the table
        else:
            self.table[label] = int(inst_order)

    # get label inst_order from the table
    def get_label(self, label):

        # if the label is not in the table, raise an error
        if label not in self.table:
            sys.stderr.write("Error: SymbolTableJump - get_label - label not found\n")
            exit(52)
        
        # return the label inst_order
        else:
            return self.table[label]
    
    # clears the table
    def empty_table(self):
        self.table = {}



# - - -  - - - - - - - - - - - - #
#        DECODE-VARIABLES        #
# - - -  - - - - - - - - - - - - #
# Used to decode many quirks of IPPcode23 -> decodes IPPcode23 syntax for variables

class DecodeVariables:
    
    # decodes ippcode23 string to normal string
    def string(self, string):
        
        # return empty string
        if string == "" or string == None:
            return string
        
        # change exisiting string
        else:
            string = string.replace("\\032", " ")
            string = string.replace("\\092", "\\")
            string = string.replace("\\010", "\n")
            string = string.replace("\\035", "#")

        return string
    


# - - -  - - - - - - - - - - - - #
#              MAIN              #
# - - -  - - - - - - - - - - - - #
# Runs the interpret class

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