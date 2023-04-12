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
        opcode_inst_jump_methods = {
            "CALL" : runner.execute_call,                   # Function calls
            "JUMP" : runner.execute_jump,                   # Program flow
            "JUMPIFEQ" : runner.execute_jumpifeq,
            "JUMPIFNEQ" : runner.execute_jumpifneq,
        }

        # [3] - methods which don't need instruction data
        opcode_methods = {
            "CREATEFRAME" : runner.execute_createframe,     # Data frames
            "PUSHFRAME" : runner.execute_pushframe,
            "POPFRAME" : runner.execute_popframe,
        }

        # [4] - methods which return a jump value
        opcode_jump_methods = {
            "RETURN" : runner.execute_return,               # Function calls
        }

        # [5] - methods which returns a request value
        opcode_request_methods = {
            "BREAK" : runner.execute_break,                 # Debugging
        }



        # reading instructions and calling the corresponding execution method
        i = 0
        while i < len(inst):

            # [1]
            if inst[i].opcode in opcode_inst_methods:
                opcode_inst_methods[inst[i].opcode](inst[i])

            # [2]
            #if inst[i].opcode in opcode_inst_jump_methods:
            #    i = opcode_inst_jump_methods[inst[i].opcode](inst[i])

            # [3]
            if inst[i].opcode in opcode_methods:
                opcode_methods[inst[i].opcode]()

            # [4]
            #if inst[i].opcode in opcode_jump_methods:
            #    i = opcode_jump_methods[inst[i].opcode]()

            # [5]
            #if inst[i].opcode in opcode_request_methods:
            #    opcode_request_methods[inst[i].opcode]()

            # debug print
            #print(inst[i].order, " - ", inst[i].opcode)
            #print("\t",inst[i].arg1_type, " - ", inst[i].arg1_text)
            #print("\t",inst[i].arg2_type, " - ", inst[i].arg2_text)
            #print("\t",inst[i].arg3_type, " - ", inst[i].arg3_text, "\n")
            #runner.debug_print()
            i += 1



# private classes called by method run_code_xml in interpret class
class ExecuteInstruction:

    # Constructor
    def __init__(self):

        # data object initialization
        self.data_stack = DataStack()            # data stack
        self.func_stack = FuncCallStack()        # function call stack
        self.frame_data = FrameStackProtocol()   # interface for the frame stack
        self.symt_jump = SymbolTableJump()       # symbol table for jumps
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
            print("Error: DEFVAR - invalid argument type")
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
    def execute_call(self, inst):
        pass
    
    # RETURN
    def execute_return(self):
        pass


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
            print("Error: IDIV - unleageal division by zero")
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
            print("Error: invalid value of type int")
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
            print("Error: string index out of range")
            exit(58)            

        # update value
        self.frame_data.symt_update_var(inst.arg1_text, "int", ord(char))


    # - - - - - - - - - - - - #
    #      Input/Output       #
    # - - - - - - - - - - - - #

    # READ
    def execute_read(self, inst):

        # get variable data
        new_data = input()

        # if there is no input
        if new_data == "" or new_data == None:
            new_data = 
        else
            data_type = inst.arg2_text
            

        # update variable data
        self.frame_data.symt_update_var(inst.arg1_text, inst.arg2_text, new_data)
    
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
        var_concat_1, var_concat_2, _ = self.frame_data.symt_get_symb1_symb2(inst, "string_string", "same")

        # check if the string are not empty
        if (var_concat_1 == None):
            var_concat_1 = ""
        elif (var_concat_2 == None):
            var_concat_2 = ""

        # concatenate strings
        self.frame_data.symt_update_var(inst.arg1_text, "string", var_concat_1 + var_concat_2)

    # STRLEN
    def execute_strlen(self, inst):

        # get the variables
        var_strlen, _ = self.frame_data.symt_get_symb(inst, "strlen")

        # get the string length
        if var_strlen == None:
            self.frame_data.symt_update_var(inst.arg1_text, "int", 0)
        else:
            self.frame_data.symt_update_var(inst.arg1_text, "int", len(var_strlen))

    # GETCHAR
    def execute_getchar(self, inst):
        
        # get the variables
        getchar_string, getchar_int, _ = self.frame_data.symt_get_symb1_symb2(inst, "string_int", "different")
        
        # check the string index with char_pos position
        if len(getchar_string) < int(getchar_int):
            print("Error: string index out of range")
            exit(58)

        # get the char
        try:
            char = getchar_string[int(getchar_int)]
        except IndexError:
            print("Error: string index out of range")
            exit(58)

        # update value
        self.frame_data.symt_update_var(inst.arg1_text, "string", char)


    # SETCHAR
    def execute_setchar(self, inst):

        # get the variables
        setchar_int, setchar_string, _ = self.frame_data.symt_get_symb1_symb2(inst, "int_string", "same")

        # check the var and get the data
        if inst.arg1_type == "var":
            var_data = self.frame_data.symt_gather_var(inst.arg1_text)
            
            if var_data[1] == "string":
                setchar = var_data[0]
            else:
                print("Error: invalid type of variable")
                exit(53) 
        else:
            print("Error: invalid type of variable")
            exit(53)

        # check the string index with char_pos position
        if len(setchar) < int(setchar_int):
            print("Error: string index out of range")
            exit(58)

        # check if setchar_string is not empty
        try:
            setchar_string = setchar_string[0] 
        except IndexError:
            print("Error: invalid value of type string")
            exit(58)

        # modify the setchar string  with char setchar_string[0] on position setchar_int
        setchar = setchar[:int(setchar_int)] + setchar_string + setchar[int(setchar_int)+1:]

        # update value
        self.frame_data.symt_update_var(inst.arg1_text, "string", setchar)


    # - - - - - - - - - - - - #
    #         Types           #
    # - - - - - - - - - - - - #

    # TYPE
    def execute_type(self, inst):

        # get variable data
        var_data = self.frame_data.symt_gather_var(inst.arg2_text)        

        # update variable data
        self.frame_data.symt_update_var(inst.arg1_text, "string", var_data[1])


    # - - - - - - - - - - - - #
    #      Program flow       #
    # - - - - - - - - - - - - #

    # LABEL
    def execute_label(self, inst):
        pass

    # JUMP
    def execute_jump(self, inst):
        pass
    
    # JUMPIFEQ
    def execute_jumpifeq(self, inst):
        pass

    # JUMPIFNEQ
    def execute_jumpifneq(self, inst):
        pass

    # EXIT
    def execute_exit(self, inst):

        # get the variables
        var_exit, _ = self.frame_data.symt_get_symb(inst, "integer")

        # check if the integer is in interval <0,49>
        if int(var_exit) < 0 or int(var_exit) > 49:
            print("Error: wrong value of exit code")
            exit(57)

        # exit the program
        exit(int(var_exit))


    # - - - - - - - - - - - - #
    #        Debugging        #
    # - - - - - - - - - - - - #

    # DPRINT
    def execute_dprint(self, inst):
        # get variable data
        if inst.arg1_type == "var":
            var_data = self.frame_data.symt_gather_var(inst.arg1_text)
            sys.stderr.write(var_data[0], end="")

        # print string from given data
        else:

            # decodes string and then prints it
            if inst.arg1_type == "string":
                string = self.decode.string(inst.arg1_text)
                sys.stderr.write(string, end="")
            else:
                sys.stderr.write(inst.arg1_text, end="")

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
            print("Error: symt_insert_var - nowhere to insert variable")
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
            print("Error: symt_update_var - nowhere to update the variable")
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
            print("Error: symt_gather_var - nowhere to gather the variable")
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
            print("Error: ExecuteInstruction - Private method symtget_arithmetic - invalid type option")
            exit(99)


        # get the second var data from the symbol table
        if arg_type == "var":
            var_type, var_data = self.symt_gather_var(arg_text)
            
            # check if the variable is int
            if var_type not in check_type:
                print("Error: ", inst.opcode," - invalid second variable type")
                exit(53)

        # get the var data from the instruction
        elif arg_type in check_type:
            var_data = arg_text
            var_type = arg_type
        else:
            print("Error: ", inst.opcode," - invalid second variable type")
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
            print("Error: ExecuteInstruction - Private method symtget_arithmetic - invalid type option")
            exit(99)


        # [1] - get the second var data from the symbol table
        if inst.arg2_type == "var":
            var_type_1, var_data_1 = self.symt_gather_var(inst.arg2_text)
            
            # check if the variable is int
            if var_type_1 not in check_type_1:
                print("Error: ", inst.opcode," - invalid second variable type")
                exit(53)

        # get the var data from the instruction
        elif inst.arg2_type in check_type_1:
            var_data_1 = inst.arg2_text
            var_type_1 = inst.arg2_type
        else:
            print("Error: ", inst.opcode," - invalid second variable type")
            exit(53)


        # [2] - get the third var data from the symbol table
        if inst.arg3_type == "var":
            var_type_2, var_data_2 = self.symt_gather_var(inst.arg3_text)
            
            # they should be the same type  
            if type_similarity == "same":
                if var_type_2 != var_type_1:
                    print("Error: ", inst.opcode," - invalid third variable type")
                    exit(53)
        
            # they can be different types
            elif type_similarity == "different":
                if var_type_2 not in check_type_2:
                    print("Error: ", inst.opcode," - invalid third variable type")
                    exit(53)
            
            # internal error wrong type_similarity
            else:
                print("Error: ExecuteInstruction - Private method symtget_arithmetic - invalid type similarity")
                exit(99)


        # [3] - get the third var data from the instruction
        else:
            # they should be the same type
            if type_similarity == "same":
                if inst.arg3_type == var_type_1:
                    var_data_2 = inst.arg3_text
                else:
                    print("Error: ", inst.opcode," - invalid second variable type")
                    exit(53)
            
            # they can be different types
            elif type_similarity == "different":
                if inst.arg3_type in check_type_2:
                    var_data_2 = inst.arg3_text
                else:
                    print("Error: ", inst.opcode," - invalid second variable type")
                    exit(53)
            
            # internal error wrong type_similarity
            else:
                print("Error: ExecuteInstruction - Private method symtget_arithmetic - invalid type similarity")
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
            print("Error: FrameStack - push_frame_to_stack - no temporary frame")
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
            print("Error: FrameStack - pop_frame_from_stack - stack is empty")
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
            print("Variable already exists - ", key)
            exit(52)

    # inserts or replaces the value and the type of the key
    def set_var(self, key, data, data_type):
        if key in self.table:
            self.table[key] = (data, data_type)
        else:
            # raise an error or handle the case where the key is not found
            print("Key not found", key)
            exit(52)
    
    # return the value and the type of the key
    def get_var(self, key):
        
        if key in self.table:
            var_data, var_value = self.table.get(key)
            return var_data, var_value
        else:
            # raise an error or handle the case where the key is not found
            print("Key not found - ", key)
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
    pass




# - - -  - - - - - - - - - - - - - - - #
#       SYMBOL-TABLE-JUMP CLASS        #
# - - -  - - - - - - - - - - - - - - - #
# Implemention of symbol table which stores where to jump to with labels

class SymbolTableJump:
    pass



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