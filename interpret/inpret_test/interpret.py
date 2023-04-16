import sys
import re
import argparse
import xml.etree.ElementTree as ET


# interpret class -> interpret interface
class Interpret:

    def __init__(self):

        # intepret arguments
        self.input_parse = InputParser()
        self.source = sys.stdin         # default = stdin -> xml_file source
        self.input = None               # default = None  -> read input
        self.stati = None               # default = None  -> stati file
        self.stati_args = None          # default = None  -> stati arguments

    # public func. - reads the arguments -> interface
    #
    #  = 11 - can't open source file -> file not found, permission denied, ect.
    #  = 12 - can't write to output file -> permission denied, ect.
    def read_args(self):

        # parse the arguments
        self.source, self.input, self.stati, self.stati_args = self.input_parse.parse_arguments()
        
        # setup stdin as defalut for source file
        if self.source == None:
            self.source = sys.stdin

        # open source file if possible
        if self.source != sys.stdin:
            try:
                self.source = open(self.source, "r")
            except FileNotFoundError or PermissionError:
                sys.stderr.write(f"[interpret.py]: ERROR (11) - Can't open source file {self.source}\n")
                sys.exit(11)
        
        # open input file if possible
        if self.input != None:
            try:
                self.input = open(self.input, "r")
            except FileNotFoundError or PermissionError:
                sys.stderr.write(f"[interpret.py]: ERROR (11) - Can't open input file {self.input}\n")
                sys.exit(11)

        # set stdin for the input file
        if self.input == None:
            self.input = sys.stdin

        # set up the stati file
        if self.stati != None:
            try:
                self.stati = open(self.stati, "w")
            except FileNotFoundError or PermissionError:
                sys.stderr.write(f"[interpret.py]: ERROR (12) - Can't write to stati file {self.stati}\n")
                sys.exit(12)


    # main public func. - runs the script -> interface
    # the manager class
    def run_script(self): 

        # parse the instructions onto an array of instructions
        inst = self.input_parse.parse_instructions(self.source)

        # run the instructions
        symt_jump = self.init_symt_jump(inst)       # searches for labels and saves their position
        self.run_instructions(inst, symt_jump)      # runs every instruction in the array of instructions



    # private func. - initializes the symt_jump class
    def init_symt_jump(self, inst):

        # initialize the symt_jump class for jumps
        symt_jump = SymbolTableJump()       # symbol table for jumps

        # initialize the symt_jump table for jumps
        i = 0
        while i < len(inst):    
            if inst[i].opcode == "LABEL":
                symt_jump.add_label(inst[i].arg1_text, i)

            i += 1

        return symt_jump


    # private func. - runs every instruction in the array of instructions
    def run_instructions(self, inst, symt_jump):

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
            "WRITE" : runner.execute_write,             # I/O  
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
        opcode_break_method = {
            "BREAK" : runner.execute_break,                 # Debugging
        }

        # [7] - methods which require input/output
        opcode_read_method = {
           "READ" : runner.execute_read,                   # Input/Output
        }



        # reading instructions and calling the corresponding execution method
        i = 0
        while i < len(inst):

            # debug
            sys.stderr.write(f"{inst[i].order} - {inst[i].opcode}\n")
            sys.stderr.write(f"   {inst[i].arg1_type} {inst[i].arg1_text}\n")
            sys.stderr.write(f"   {inst[i].arg2_type} {inst[i].arg2_text}\n")
            sys.stderr.write(f"   {inst[i].arg3_type} {inst[i].arg3_text}\n\n")

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
            elif inst[i].opcode in opcode_break_method:
                opcode_break_method[inst[i].opcode]()
                i += 1

            # [7] - read instruction
            elif inst[i].opcode in opcode_read_method:
                opcode_read_method[inst[i].opcode](inst[i], self.input)
                i += 1
            else:
                sys.stderr.write(f"[interpret.py]: ERROR (32) - Interpret - run_instructions()\n")
                sys.stderr.write(f"                NOTE - Unknown instruction ({inst[i].opcode})\n")
                sys.exit(32)

class InputParser:

    # instruction data structure
    # -> for saving instruction data
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

    # public func. - parses the instructions into an array of instructions
    def parse_instructions(self, source):

        # initialize instruction data
        inst = []

        # get xml_tree children data
        try:
            tree_root = ET.fromstring(source.read())
        except:
            sys.stderr.write(f"[interpret.py]: ERROR (31) - InputParser - parse_instructions()\n")
            sys.stderr.write(f"                NOTE - Source file is not in xml format\n")
            sys.exit(31)
        
        # get xml_tree children data
        tree_children = list(tree_root)

        # check root arg
        if tree_root.tag != "program" or tree_root.attrib.get("language") != "IPPcode23":
            sys.stderr.write(f"[interpret.py]: ERROR (32) - InputParser - parse_instructions()\n")
            sys.stderr.write(f"                NOTE - Unknown root xml argument ({tree_root.tag})\n")
            sys.exit(32)

        # reading tree_children -> instruction data
        order = 1
        for child in tree_children:

            # check if the root arg is valid
            if (child.tag != "instruction"):
                sys.stderr.write(f"[interpret.py]: ERROR (32) - InputParser - parse_instructions()\n")
                sys.stderr.write(f"                NOTE - Unknown child xml argument ({child.tag})\n")
                sys.exit(32)

            # check if the order is valid
            if (child.attrib.get is None) or (int(child.attrib.get('order')) != order):

                # increace order if if order is higher than the current order
                if (int(child.attrib.get('order')) > order):
                    order = int(child.attrib.get('order'))
                else:
                    sys.stderr.write(f"[interpret.py]: ERROR (32) - InputParser - parse_instructions()\n")
                    sys.stderr.write(f"                NOTE - Wrong xml instruction order ({child.attrib.get('order')})\n")
                    sys.exit(32)
            
            # get instruction data
            instruction = self.Instruction(child.attrib.get("opcode"), child.attrib.get("order"), None, None, None, None, None, None)

            # get xml_tree sub_children data
            tree_sub_children = list(child)
            sub_child_index = 0

            # reading tree_sub_children -> instruction arguments
            for sub_child_index, sub_child in enumerate(tree_sub_children):
                
                # check if the argument is valid
                if sub_child.tag != "arg" + str(sub_child_index + 1):
                    sys.stderr.write(f"[interpret.py]: ERROR (32) - InputParser - parse_instructions()\n")
                    sys.stderr.write(f"                NOTE - Unknown subchild xml argument ({sub_child.tag})\n")
                    sys.exit(32)
                
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
                else:
                    sys.stderr.write(f"[interpret.py]: ERROR (31) - InputParser - parse_instructions()\n")
                    sys.stderr.write(f"                NOTE - Too many arguments , the maximum number of arguments is 3\n")
                    sys.exit(31)

            inst.append(instruction) 
            order += 1
        return inst
    

    ## Public func. - parses the arguments
    #  - uses the argparse library
    #  - returns the arguments (source_file, input_file, stati_file, stati_args[])
    #
    ## Returns errors
    #  = 10 - missing/wrong arguments
    def parse_arguments(self):

        # initialize the argument parser
        parser = argparse.ArgumentParser()

        # default arguments
        parser.add_argument("--source", help="source file", required=False)      # source file input
        parser.add_argument("--input", help="input file", required=False)        # input file input
        
        # stati arguments -> to be implemented
        parser.add_argument("--stati", help="stati", required=False)             # stati file output
        parser.add_argument("--insts", help="insts", required=False)             # insts
        parser.add_argument("--vars", help="vars", required=False)               # vars
        parser.add_argument("--hot", help="hot", required=False)                 # hot
        parser.add_argument("--frequent", help="frequent", required=False)       # frequent
        parser.add_argument("--eol", help="eol", required=False)                 # eol

        # parse the arguments
        arg_source = parser.parse_args().source
        arg_input = parser.parse_args().input
        arg_stati = parser.parse_args().stati
        stati_args = [arg_stati, parser.parse_args().insts, parser.parse_args().vars, parser.parse_args().hot, parser.parse_args().frequent, parser.parse_args().eol]

        # check arg_souce and arg_input args -> one must be present
        if arg_source == None and arg_input == None:
            sys.stderr.write("[interpret.py]: ERROR (10) - Missing arguments: --source and --input\n")
            sys.exit(10)

        # return the arguments
        return arg_source, arg_input, arg_stati, stati_args


class VariableAnalysis:

    def __init__(self):
        pass

    # public func. - analyzes the variable
    def analyze_arg(self, inst_arg, inst_type):

        var_scope = None 
        var_value = None

        # check the use case
        if inst_type == None:
            sys.stderr.write("[interpret.py]: ERROR (99) - VariableAnalysis - analyze_arg()\n")
            sys.stderr.write(f"               NOTE - (internal error) - Var type = None - wrong usecase of the function\n")
            sys.exit(99)

        # change inst_arg_type to ""
        if inst_arg == None:
            inst_arg = ""

        # var type
        if inst_type == "var":
            var_scope, var_value = self.analyze_var(inst_arg)

        # string type
        elif inst_type == "string":
            var_value = self.analyze_string(inst_arg)

        # int type
        elif inst_type == "int":
            var_value = self.analyze_int(inst_arg)
                    
        # bool type
        elif inst_type == "bool":
            var_value = self.analyze_bool(inst_arg)
                    
        # nil type
        elif inst_type== "nil":
            var_value = self.analyze_nil(inst_arg)
                    
        # label type
        elif inst_type== "label":
            var_value = self.analyze_label(inst_arg)
                    
        # type typo
        elif inst_type == "type":
            var_value = self.analyze_type(inst_arg)

        # unknown type
        else:
            sys.stderr.write("[interpret.py]: ERROR (32) - VariableAnalysis - analyze_arg()\n")
            sys.stderr.write(f"               NOTE - Unknown var type was used\n")
            sys.stderr.write(f"               VAR  - <{inst_type}>, {inst_arg}\n")
            sys.exit(32)

        # return value
        return var_value, var_scope


    def analyze_var(self, input_var):

        # regex for checkign the input_var format
        if not re.match(r"^(GF|LF|TF)@([a-zA-Z0-9-_&%$*!?]+)$", input_var):
            sys.stderr.write("[interpret.py]: ERROR (53) - VariableAnalysis - analyze_var()\n")
            sys.stderr.write(f"               NOTE   - Wrong var operand format\n")
            sys.stderr.write(f"               BAR - {input_var}\n")
            sys.exit(53)

        # check if the variable does not start with a number
        if re.match(r"^(GF|LF|TF)@[0-9]", input_var):
            sys.stderr.write("[interpret.py]: ERROR (53) - VariableAnalysis - analyze_var()\n")
            sys.stderr.write(f"               NOTE   - Wrong var operand format\n")
            sys.stderr.write(f"               BAR - {input_var}\n")
            sys.exit(53)

        # split the string into parts -> first @ indicates the split symbol
        var_data = input_var.split("@", 1)

        return var_data[0], var_data[1]


    def analyze_string(self, input_string):

        # check if the string is empty
        if input_string == "" or input_string is None:
            return ""

        # check if the string var starts with string@ and does not contain ["#", " "]
        if not re.match(r"^[^# ]*$", input_string):
            sys.stderr.write("[interpret.py]: ERROR (53) - VariableAnalysis - analyze_string()\n")
            sys.stderr.write(f"               NOTE   - Wrong string operand format\n")
            sys.stderr.write(f"               STRING - {input_string}\n")
            sys.exit(53)

        # if '\' is in the string allow use only with the combination '[\][0-9]{3}'
        if not re.match(r"^(?!.*\\(?![0-9]{3})).*$", input_string):
            sys.stderr.write("[interpret.py]: ERROR (53) - VariableAnalysis - analyze_string()\n")
            sys.stderr.write(f"               NOTE   - Wrong string operand format\n")
            sys.stderr.write(f"               STRING - {input_string}\n")
            sys.exit(53)

        # decode the "[\][0-9]{3}" into the correct characters the three digits represent UTF-8 code
        input_string = re.sub(r"\\([0-9]{3})", lambda x: chr(int(x.group(1))),input_string)

        # return the new string
        return input_string

    def analyze_int(self, input_int):

        # check if the string var starts with int@
        if not re.match(r"^[-+]?[0-9]+$", input_int):
            sys.stderr.write("[interpret.py]: ERROR (53) - VariableAnalysis - analyze_int()\n")
            sys.stderr.write(f"               NOTE - Wrong int operand format\n")
            sys.stderr.write(f"               INT  - {input_int}\n")
            sys.exit(53)
        
        # try to convert the string into int
        try:
            input_int = int(input_int)
        except ValueError:
            sys.stderr.write("[interpret.py]: ERROR (53) - VariableAnalysis - analyze_int()\n")
            sys.stderr.write(f"               NOTE - Wrong int operand format\n")
            sys.stderr.write(f"               INT  - {input_int}\n")
            sys.exit(53)

        # return the new int
        return str(input_int)
    
    def analyze_bool(self, input_bool):

        # check if the string var starts with bool@
        if not re.match(r"^(true|false)$", input_bool):
            sys.stderr.write("[interpret.py]: ERROR (53) - VariableAnalysis - analyze_bool()\n")
            sys.stderr.write(f"               NOTE - Wrong bool operand format\n")
            sys.stderr.write(f"               BOOL - {input_bool}\n")
            sys.exit(53)

        # return the new bool
        return input_bool

    def analyze_nil(self, input_nil):

        # check if the string var starts with nil@
        if input_nil == "nil" or input_nil == "":
            pass
        else:
            sys.stderr.write("[interpret.py]: ERROR (53) - VariableAnalysis - analyze_string()\n")
            sys.stderr.write(f"               NOTE - Wrong nil operand format\n")
            sys.stderr.write(f"               NIL  - {input_nil}\n")
            sys.exit(53)

        # return the new nil
        return ""

    def analyze_label(self, input_label):
            
        # check if the string var starts with label@ and does not contain ["#", " "]
        if not re.match(r"^[^# ]*$", input_label):
            sys.stderr.write("[interpret.py]: ERROR (53) - VariableAnalysis - analyze_label()\n")
            sys.stderr.write(f"               NOTE  - Wrong label operand format\n")
            sys.stderr.write(f"               LABEL - {input_label}\n")
            sys.exit(53)

        # return the new label
        return input_label

    def analyze_type(self, input_type):
            
        # check if the string var starts with type@ and does not contain ["#", " "]
        if not re.match(r"^[^# ]*$", input_type):
            sys.stderr.write("[interpret.py]: ERROR (53) - VariableAnalysis - analyze_type()\n")
            sys.stderr.write(f"               NOTE  - Wrong label operand format\n")
            sys.stderr.write(f"               TYPE - {input_type}\n")
            sys.exit(53)

        # return the new type
        return input_type


# private classes called by method run_code_xml in interpret class
class ExecuteInstruction:

    # Constructor
    def __init__(self):

        # data object initialization
        self.data_stack = DataStack()            # data stack
        self.func_stack = FuncCallStack()        # function call stack
        self.frame_data = FrameStackProtocol()   # interface for the frame stack
        self.inspect = VariableAnalysis()        # decode variable quirks
        
        self.decode = DecodeVariables()           # decode variables


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
        
        # insert the variable into the symbol table
        self.frame_data.symt_insert_var(inst.arg1_text)


    # MOVE
    def execute_move(self, inst):
        
        # get the variable data from the symbol table and update the variable
        var_type, var_data = self.frame_data.symt_get_symb(inst, "universal", "arg2")

        # update the variable
        self.frame_data.symt_update_var(inst.arg1_text, var_type, var_data)


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

        self.inspect.analyze_arg(inst.arg1_text, "label")
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

        if inst.arg1_type == "var":

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
            sys.stderr.write(f"[interpret.py]: ERROR (57) - ExecuteInstruction - execute_idiv()\n")
            sys.stderr.write(f"                NOTE - Illegal division by zero\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} - {inst.arg2_type} {inst.arg3_type}\n")
            sys.exit(57)

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
        else:
            sys.stderr.write(f"[interpret.py]: ERROR (53) - ExecuteInstruction - execute_lt()\n")
            sys.stderr.write(f"                NOTE - Wrong variable types, expected <int, bool, string>\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} - {inst.arg2_type} {inst.arg3_type}\n")
            sys.exit(53)   

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
        
        # compare the nil variables
        else:
            sys.stderr.write(f"[interpret.py]: ERROR (53) - ExecuteInstruction - execute_gt()\n")
            sys.stderr.write(f"                NOTE - Wrong variable types, expected <int, bool, string>\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} - {inst.arg2_type} {inst.arg3_type}\n")
            sys.exit(53)   

    # EQ
    def execute_eq(self, inst):
        
        # get the variables
        var_type_1, var_data_1, var_type_2, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "relational", "different")

        # if var_data_1 or var_data_2 is nil
        if var_type_1 == "nil" or var_type_2 == "nil":

            # compare the nil variables
            if var_type_1 == var_type_2:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

        # compare other types
        else:

            # compare the int variables
            if var_type_1 == "int" and var_type_2 == "int":
                if int(var_data_1) == int(var_data_2):
                    self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
                else:
                    self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

            # compare the string variables
            elif var_type_1 == "string" and var_type_2 == "string":
                if var_data_1 == var_data_2:
                    self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
                else:
                    self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

            # compare the bool variables
            elif var_type_1 == "bool" and var_type_2 == "bool":
                if var_data_1 == var_data_2:
                    self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
                else:
                    self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")
            
            # wrong types
            else:
                sys.stderr.write(f"[interpret.py]: ERROR (53) - ExecuteInstruction - execute_eq()\n")
                sys.stderr.write(f"                NOTE - Wrong variable types, expected two same types as second and third argument\n")
                sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} - {inst.arg2_type} {inst.arg3_type}\n")
                sys.exit(53)                


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
            sys.stderr.write(f"[interpret.py]: ERROR (58) - ExecuteInstruction - execute_int2char()\n")
            sys.stderr.write(f"                NOTE - Int can't be converted into chat\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} {inst.arg2_text}\n")
            sys.exit(58)

        # update value
        self.frame_data.symt_update_var(inst.arg1_text, "string", str(char))

    # STRI2INT
    def execute_stri2int(self, inst):

        # get the variables
        _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "string_int", "different")
        char_pos = int(var_data_2)

        # check the string index with char_pos position
        if char_pos < len(var_data_1) and char_pos > -1:
            char = var_data_1[char_pos]
        else:
            sys.stderr.write(f"[interpret.py]: ERROR (58) - ExecuteInstruction - execute_stri2int()\n")
            sys.stderr.write(f"                NOTE - String index out of range\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} {inst.arg2_text}\n")
            sys.exit(58)

        # update value
        self.frame_data.symt_update_var(inst.arg1_text, "int", str(ord(char)))


    # - - - - - - - - - - - - #
    #      Input/Output       #
    # - - - - - - - - - - - - #

    # READ
    def execute_read(self, inst, input_source):
        
        # check the variable type
        if inst.arg2_text == "int" or inst.arg2_text == "bool" or inst.arg2_text == "string":
            data_type = inst.arg2_text
        else:
            sys.stderr.write(f"[interpret.py]: ERROR (53) - ExecuteInstruction - execute_read()\n")
            sys.stderr.write(f"                NOTE - Wrong variable type, expected int, bool or string\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} {inst.arg2_text}\n")
            sys.exit(53)

        # get the right source - stdin or file
        if input_source == None:
            data_type = "nil"

        elif input_source == sys.stdin:
            new_data = input()
        else:
            new_data = input_source.readline()

        # check if the new_data are empty
        if new_data == "" or new_data is None:
            data_type = "nil"

        # remove \n from the end of the string
        if new_data != "" and new_data[-1] == "\n":
            new_data = new_data[:-1]

        # check the new given data
        # string
        if data_type == "string":

            # change every non-alphanumeric character to its ASCII code in formal \[0-9][0-9][0-9]
            new_data = re.sub(r"([\W\s])", lambda m: fr"\{ord(m.group(1)):03d}", new_data)

            # update value
            self.frame_data.symt_update_var(inst.arg1_text, "string", new_data)
            
        # int
        elif data_type == "int":
            if re.match(r"^[-+]?[0-9]+$", new_data):
                self.frame_data.symt_update_var(inst.arg1_text, "int", new_data)
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "nil", "")
            
        # bool
        elif data_type == "bool":
            new_data = new_data.lower()
            if re.match(r"^(true|false)$", new_data):
                self.frame_data.symt_update_var(inst.arg1_text, "bool", new_data)
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

        # nil
        else:
            self.frame_data.symt_update_var(inst.arg1_text, "nil", "")
    

    # WRITE
    def execute_write(self, inst):

        # get variable data
        _, var_data = self.frame_data.symt_get_symb(inst, "universal", "arg1")

        # print variable
        print(var_data, end="")


    # - - - - - - - - - - - - #
    #    String operations    #
    # - - - - - - - - - - - - #

    # CONCAT
    def execute_concat(self, inst):
            
        # get the variables
        _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "string_string", "same")

        # concatenate strings
        self.frame_data.symt_update_var(inst.arg1_text, "string", var_data_1 + var_data_2)

    # STRLEN
    def execute_strlen(self, inst):

        # get the variables
        _, var_data = self.frame_data.symt_get_symb(inst, "string", "arg2")

        # get the string length
        self.frame_data.symt_update_var(inst.arg1_text, "int", str(len(var_data)))

    # GETCHAR
    def execute_getchar(self, inst):
        
        # get the variables
        _, var_string, _, var_int = self.frame_data.symt_get_symb1_symb2(inst, "string_int", "different")
        
        # decode the string
        var_string = self.decode.string(var_string)

        # check the string index with char_pos position
        if len(var_string) < int(var_int) or int(var_int) < 0:
            sys.stderr.write(f"[interpret.py]: ERROR (58) - ExecuteInstruction - execute_getchar()\n")
            sys.stderr.write(f"                NOTE - String index out of range\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} {var_string} {var_int}\n")
            sys.exit(58)

        # get the char
        try:
            char = var_string[int(var_int)]
        except IndexError:
            sys.stderr.write(f"[interpret.py]: ERROR (58) - ExecuteInstruction - execute_getchar()\n")
            sys.stderr.write(f"                NOTE - String index out of range\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} {var_string} {var_int}\n")
            sys.exit(58)

        # update value
        self.frame_data.symt_update_var(inst.arg1_text, "string", char)


    # SETCHAR
    def execute_setchar(self, inst):

        # get the variables
        _, var_int, _, var_string = self.frame_data.symt_get_symb1_symb2(inst, "int_string", "different")

        # check the var and get the data
        var_type, var_data = self.frame_data.symt_gather_var(inst.arg1_text)

        # check the var type
        if var_type != "string":
            sys.stderr.write(f"[interpret.py]: ERROR (53) - ExecuteInstruction - execute_setchar()\n")
            sys.stderr.write(f"                NOTE - String index out of range\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} {inst.arg1_text} {var_int} {var_string}\n")
            sys.exit(53)

        # check var_string, var_data and var_int
        if len(var_data) <= int(var_int) or int(var_int) < 0 or var_data == "" or var_string == "":
            sys.stderr.write(f"[interpret.py]: ERROR (58) - ExecuteInstruction - execute_setchar()\n")
            sys.stderr.write(f"                NOTE - String index out of range\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} {inst.arg1_text} {var_int} {var_string}\n")
            sys.exit(58)

        # modify the var data string
        var_data = var_data[:int(var_int)] + var_string[0] + var_data[int(var_int)+1:]

        # update values
        self.frame_data.symt_update_var(inst.arg1_text, "string", var_data)


    # - - - - - - - - - - - - #
    #         Types           #
    # - - - - - - - - - - - - #

    # TYPE
    def execute_type(self, inst):

        # get variable data
        if inst.arg2_type == "var":
            var_type = self.frame_data.symt_gather_type(inst.arg2_text)   
        else:
            var_type = inst.arg2_type

        # none variable type
        if var_type is None:
            self.frame_data.symt_update_var(inst.arg1_text, "string", "")

        # right variable type
        elif var_type == "int" or var_type == "bool" or var_type == "string" or var_type == "nil":
            self.frame_data.symt_update_var(inst.arg1_text, "string", var_type)
        
        # wrong variable type
        else:
            sys.stderr.write(f"[interpret.py]: ERROR (53) - ExecuteInstruction - execute_type()\n")
            sys.stderr.write(f"                NOTE - Invalid type as second argument\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} {inst.arg1_text} {inst.arg2_text}\n")
            sys.exit(53)


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
        var_type_1, var_data_1, var_type_2, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "relational", "different")

        # check if label exists
        symt_jump.check_label(inst.arg1_text)

        # if var_data_1 or var_data_2 is nil
        if var_type_1 == "nil" or var_type_2 == "nil":
            
            # compare the nil variables
            if var_type_1 == var_type_2:
                return symt_jump.get_label(inst.arg1_text)
            else:
                return -1

        # compare other types
        else:
            # compare the int variables
            if var_type_1 == "int" and var_type_2 == "int":
                if int(var_data_1) == int(var_data_2):
                    return symt_jump.get_label(inst.arg1_text)
                else:
                    return -1

            # compare the string variables
            elif var_type_1 == "string" and var_type_2 == "string":
                if var_data_1 == var_data_2:
                    return symt_jump.get_label(inst.arg1_text)
                else:
                    return -1

            # compare the bool variables
            elif var_type_1 == "bool" and var_type_2 == "bool":
                if var_data_1 == var_data_2:
                    return symt_jump.get_label(inst.arg1_text)
                else:
                    return -1
            
            # wrong types
            else:
                sys.stderr.write(f"[interpret.py]: ERROR (53) - ExecuteInstruction - execute_jumpifneq()\n")
                sys.stderr.write(f"                NOTE - Wrong variable types, expected two same types as second and third argument\n")
                sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} - {inst.arg2_type} {inst.arg3_type}\n")
                sys.exit(53)   

    # JUMPIFNEQ
    def execute_jumpifneq(self, inst, symt_jump):

        # get the variables
        var_type_1, var_data_1, var_type_2, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "relational", "different")

        # check if label exists
        symt_jump.check_label(inst.arg1_text)

        # if var_data_1 or var_data_2 is nil
        if var_type_1 == "nil" or var_type_2 == "nil":
            
            # compare the nil variables
            if var_type_1 != var_type_2:
                return symt_jump.get_label(inst.arg1_text)
            else:
                return -1

        # compare other types
        else:
            # compare the int variables
            if var_type_1 == "int" and var_type_2 == "int":
                if int(var_data_1) != int(var_data_2):
                    return symt_jump.get_label(inst.arg1_text)
                else:
                    return -1

            # compare the string variables
            elif var_type_1 == "string" and var_type_2 == "string":
                if var_data_1 != var_data_2:
                    return symt_jump.get_label(inst.arg1_text)
                else:
                    return -1

            # compare the bool variables
            elif var_type_1 == "bool" and var_type_2 == "bool":
                if var_data_1 != var_data_2:
                    return symt_jump.get_label(inst.arg1_text)
                else:
                    return -1
            
            # wrong types
            else:
                sys.stderr.write(f"[interpret.py]: ERROR (53) - ExecuteInstruction - execute_jumpifneq()\n")
                sys.stderr.write(f"                NOTE - Wrong variable types, expected two same types as second and third argument\n")
                sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} - {inst.arg2_type} {inst.arg3_type}\n")
                sys.exit(53)   

    # EXIT
    def execute_exit(self, inst):

        # get the variables
        _, var_data = self.frame_data.symt_get_symb(inst, "integer", "arg1")

        # check if the integer is in interval <0,49>
        if int(var_data) < 0 or int(var_data) > 49:
            sys.stderr.write(f"[interpret.py]: ERROR (57) - ExecuteInstruction - execute_exit()\n")
            sys.stderr.write(f"                NOTE - Wrong value of the exit code, return value has to be in <0,49>\n")
            sys.stderr.write(f"                VAR  - <{inst.arg2_type}>, {inst.arg2_text}\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} {var_data}\n")
            sys.exit(57)

        # exit the program
        exit(int(var_data))


    # - - - - - - - - - - - - #
    #        Debugging        #
    # - - - - - - - - - - - - #

    # DPRINT
    def execute_dprint(self, inst):
        
        # get variable data
        _, var_data = self.frame_data.symt_get_symb(inst, "universal", "arg1")

        # print variable data    
        sys.stderr.write(var_data)


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
        self.inspect = VariableAnalysis() 


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
        var_scope, var_name = self.inspect.analyze_var(var_text)

        # insert variable into the symbol table depening on the scope
        if var_scope == "GF" and self.symt_gf != None:
            self.symt_gf.insert_key(var_name)
        elif var_scope == "TF" and self.symt_tf != None:
            self.symt_tf.insert_key(var_name)
        elif var_scope == "LF" and self.symt_lf != None:
            self.symt_lf.insert_key(var_name)
        else:
            sys.stderr.write(f"[interpret.py]: ERROR (55) - FrameStackProtocol - symt_insert_var()\n")
            sys.stderr.write(f"                NOTE  - Variable isn't accesable in the frame\n")
            sys.stderr.write(f"                VAR   - {var_text}\n")
            sys.stderr.write(f"                FRAME - {var_scope} - Doesn't exists \n")
            sys.exit(55)   


    # text is the variable name with scope
    # type is the variable type
    # value is the variable value
    def symt_update_var(self, var_text, var_type, var_value):
        
        # decodes string var type and value
        var_scope, var_name = self.inspect.analyze_var(var_text)
        var_value, _ = self.inspect.analyze_arg(var_value, var_type)

        # move value and type onto existing frame symtable
        if var_scope == "GF" and self.symt_gf != None:
            self.symt_gf.set_var(var_name, var_value, var_type)
        elif var_scope == "TF" and self.symt_tf != None:
            self.symt_tf.set_var(var_name, var_value, var_type)
        elif var_scope == "LF" and self.symt_lf != None:
            self.symt_lf.set_var(var_name, var_value, var_type)
        else:
            sys.stderr.write(f"[interpret.py]: ERROR (55) - FrameStackProtocol - symt_update_var()\n")
            sys.stderr.write(f"                NOTE  - Variable isn't accesable in the frame\n")
            sys.stderr.write(f"                VAR   - {var_text} - <{var_type}>, {var_value}\n")
            sys.stderr.write(f"                FRAME - {var_scope} - Doesn't exists \n")
            sys.exit(55)   
    

    # var text is the variable name with scope
    # returns the variable data[0] = [value]
    # returns the variable data[1] = [type]
    def symt_gather_var(self, var_text):

        # return var defalut initalization
        var_type = None 
        var_data = None                            

        # get variable scope and name
        var_scope, var_name = self.inspect.analyze_var(var_text)

        # go accoring to scope
        if var_scope == "GF" and self.symt_gf != None:
            var_data, var_type = self.symt_gf.get_var(var_name)
        elif var_scope == "TF" and self.symt_tf != None:
            var_data, var_type = self.symt_tf.get_var(var_name)
        elif var_scope == "LF" and self.symt_lf != None:
            var_data, var_type = self.symt_lf.get_var(var_name)
        else:
            sys.stderr.write(f"[interpret.py]: ERROR (55) - FrameStackProtocol - symt_gather_var()\n")
            sys.stderr.write(f"                NOTE  - Variable isn't accesable in the frame\n")
            sys.stderr.write(f"                VAR   - {var_text} - <{var_type}>, {var_data}\n")
            sys.stderr.write(f"                FRAME - {var_scope} - Doesn't exists \n")
            sys.exit(55)   

        # check if the var is not none
        if var_type is None:
            sys.stderr.write(f"[interpret.py]: ERROR (56) - FrameStackProtocol - symt_gather_var()\n")
            sys.stderr.write(f"                NOTE  - Variable has no data_type\n")
            sys.stderr.write(f"                VAR   - {var_text} - <{var_type}>, {var_data}\n")
            sys.stderr.write(f"                FRAME - {var_scope} - Doesn't exists \n")
            sys.exit(56)

        return var_type, var_data


    # get the variable type
    def symt_gather_type(self, var_text):
        
        var_type = None

        # get variable scope and name
        var_scope, var_name = self.inspect.analyze_var(var_text)

        # go accoring to scope
        if var_scope == "GF" and self.symt_gf != None:
            _, var_type = self.symt_gf.get_var(var_name)
        elif var_scope == "TF" and self.symt_tf != None:
            _, var_type = self.symt_tf.get_var(var_name)
        elif var_scope == "LF" and self.symt_lf != None:
            _, var_type = self.symt_lf.get_var(var_name)
        else:
            sys.stderr.write(f"[interpret.py]: ERROR (55) - FrameStackProtocol - symt_gather_type()\n")
            sys.stderr.write(f"                NOTE  - Variable isn't accesable in the frame\n")
            sys.stderr.write(f"                VAR   - {var_text} - <{var_type}> \n")
            sys.stderr.write(f"                FRAME - {var_scope} - Doesn't exists \n")
            sys.exit(55)   

        return var_type

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
            sys.stderr.write(f"[interpret.py]: ERROR (99) - FrameStackProtocol - symt_get_symb()\n")
            sys.stderr.write(f"                NOTE - (Internal error), invalid type_option argument  \n")
            sys.exit(99)


        # get the second var data from the symbol table
        if arg_type == "var":
            var_type, var_data = self.symt_gather_var(arg_text)

            # check if the variable is not None
            if var_type is None:
                sys.stderr.write(f"[interpret.py]: ERROR (56) - FrameStackProtocol - symt_get_symb()\n")
                sys.stderr.write(f"                NOTE - Variable <symb> has no data_type\n")
                sys.stderr.write(f"                VAR  - {inst.arg2_text} - <{var_type}>, {var_data}\n")
                sys.exit(56)
            
            # check if the variable is in the correct type
            if var_type not in check_type:
                sys.stderr.write(f"[interpret.py]: ERROR (53) - FrameStackProtocol -> symt_get_symb()\n")
                sys.stderr.write(f"                NOTE - Invalid <symb> variable type\n")
                sys.stderr.write(f"                VAR  - {arg_text} - <{var_type}>, {var_data}\n")
                sys.exit(53)

        # get the var data from the instruction
        elif arg_type in check_type:
            var_data, _ = self.inspect.analyze_arg(arg_text, arg_type)
            var_type = arg_type
        else:
            sys.stderr.write(f"[interpret.py]: ERROR (53) - FrameStackProtocol -> symt_get_symb()\n")
            sys.stderr.write(f"                NOTE - Invalid <symb> variable type\n")
            sys.stderr.write(f"                VAR  - {arg_text} - <{var_type}>, {var_data}\n")
            sys.exit(53)

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
            "relational":       (["string", "int", "bool", "nil"], ["string", "int", "bool", "nil"]),
            "jump":             (["string", "int", "bool"], ["string", "int", "bool"]),
            "string_int":       (["string"], ["int"]),
            "int_string":       (["int"], ["string"]),
            "string_string":    (["string"], ["string"])
        }

        try:
            check_type_1, check_type_2 = check_type_dict[type_option]
        except KeyError:
            sys.stderr.write(f"[interpret.py]: ERROR (99) - FrameStackProtocol - symt_get_symb1_symb2()\n")
            sys.stderr.write(f"                NOTE - (Internal error), invalid type_option argument  \n")
            sys.exit(99)


        # [1] - get the second var data from the symbol table
        if inst.arg2_type == "var":
            var_type_1, var_data_1 = self.symt_gather_var(inst.arg2_text)

            # check if the variable has a data type
            if var_type_1 is None:
                sys.stderr.write(f"[interpret.py]: ERROR (56) - FrameStackProtocol - symt_get_symb1_symb2()\n")
                sys.stderr.write(f"                NOTE - Variable <symb1> has no data_type\n")
                sys.stderr.write(f"                VAR  - {inst.arg2_text} - <{var_type_1}>, {var_data_1}\n")
                sys.stderr.write(f"                INST - [{inst.order}] - {inst.opcode} <{var_type_1}> <{inst.arg3_type}>\n")
                sys.exit(56)
            
            # check if the variable is int
            if var_type_1 not in check_type_1:
                sys.stderr.write(f"[interpret.py]: ERROR (53) - FrameStackProtocol -> symt_get_symb1_symb2()\n")
                sys.stderr.write(f"                NOTE - Invalid <symb1> variable type\n")
                sys.stderr.write(f"                VAR  - {inst.arg2_text} - <{var_type_1}>, {var_data_1}\n")
                sys.stderr.write(f"                INST - {inst.order}. - {inst.opcode} <{var_type_1}> <{inst.arg3_type}>\n")
                sys.exit(53)

        # [2] - get the var data from the instruction
        elif inst.arg2_type in check_type_1:

            # analyze the the text variable
            var_data_1, _ = self.inspect.analyze_arg(inst.arg2_text, inst.arg2_type)
            var_type_1 = inst.arg2_type
        else:
            sys.stderr.write(f"[interpret.py]: ERROR (53) - FrameStackProtocol - symt_get_symb1_symb2()\n")
            sys.stderr.write(f"                NOTE - Invalid <symb1> variable type\n")
            sys.stderr.write(f"                VAR  - {inst.arg2_text} - <{var_type_1}>, {var_data_1}\n")
            sys.stderr.write(f"                INST - {inst.order}. - {inst.opcode} <{var_type_1}> <{inst.arg3_type}>\n")
            sys.exit(53)


        # [3] - get the third var data from the symbol table
        if inst.arg3_type == "var":
            var_type_2, var_data_2 = self.symt_gather_var(inst.arg3_text)

            # check if the variable has a data type
            if var_type_2 is None:
                sys.stderr.write(f"[interpret.py]: ERROR (56) - FrameStackProtocol - symt_get_symb1_symb2()\n")
                sys.stderr.write(f"                NOTE - Variable <symb2> has no data_type\n")
                sys.stderr.write(f"                VAR  - {inst.arg3_text} - <{var_type_2}>, {var_data_2}\n")
                sys.stderr.write(f"                INST - [{inst.order}] - {inst.opcode} <{var_type_1}> <{var_type_2}>\n")
                sys.exit(56)
            
            # they should be the same type  
            if type_similarity == "same":
                if var_type_2 != var_type_1:
                    sys.stderr.write(f"[interpret.py]: ERROR (53) - FrameStackProtocol - symt_get_symb1_symb2()\n")
                    sys.stderr.write(f"                NOTE - Invalid <symb2> variable type\n")
                    sys.stderr.write(f"                VAR  - {inst.arg3_text} - <{var_type_2}>, {var_data_2}\n")
                    sys.stderr.write(f"                INST - [{inst.order}] - {inst.opcode} <{var_type_1}> <{var_type_2}>\n")
                    sys.exit(53)
        
            # they can be different types
            elif type_similarity == "different":
                if var_type_2 not in check_type_2:
                    sys.stderr.write(f"[interpret.py]: ERROR (53) - FrameStackProtocol - symt_get_symb1_symb2()\n")
                    sys.stderr.write(f"                NOTE - Invalid <symb2> variable type\n")
                    sys.stderr.write(f"                VAR  - {inst.arg3_text} - <{var_type_2}>, {var_data_2}\n")
                    sys.stderr.write(f"                INST - [{inst.order}] - {inst.opcode} <{var_type_1}> <{var_type_2}>\n")
                    sys.exit(53)
            
            # internal error wrong type_similarity
            else:
                sys.stderr.write(f"[interpret.py]: ERROR (99) - FrameStackProtocol - symt_get_symb1_symb2()\n")
                sys.stderr.write(f"                NOTE - (Internal error), invalid type_similarity argument  \n")
                sys.exit(99)


        # [4] - get the third var data from the instruction
        else:
            # they should be the same type
            if type_similarity == "same":
                if inst.arg3_type == var_type_1:

                    # analyze the the text variable
                    var_data_2, _ = self.inspect.analyze_arg(inst.arg3_text, var_type_1)
                    var_type_2 = var_type_1
                else:
                    sys.stderr.write(f"[interpret.py]: ERROR (53) - FrameStackProtocol - symt_get_symb1_symb2()\n")
                    sys.stderr.write(f"                NOTE - Invalid <symb2> variable type\n")
                    sys.stderr.write(f"                VAR  - {inst.arg3_text} - <{var_type_2}>, {var_data_2}\n")
                    sys.stderr.write(f"                INST - [{inst.order}] - {inst.opcode} <{var_type_1}> <{var_type_2}>\n")
                    sys.exit(53)
            
            # they can be different types
            elif type_similarity == "different":
                if inst.arg3_type in check_type_2:

                    # analyze the the text variable
                    var_data_2, _ = self.inspect.analyze_arg(inst.arg3_text, inst.arg3_type)
                    var_type_2 = inst.arg3_type
                else:
                    sys.stderr.write(f"[interpret.py]: ERROR (53) - FrameStackProtocol - symt_get_symb1_symb2()\n")
                    sys.stderr.write(f"                NOTE - invalid <symb2> variable type\n")
                    sys.stderr.write(f"                VAR  - {inst.arg3_text} - <{var_type_2}>, {var_data_2}\n")
                    sys.stderr.write(f"                INST - [{inst.order}] - {inst.opcode} <{var_type_1}> <{var_type_2}>\n")
                    sys.exit(53)
            
            # internal error wrong type_similarity
            else:
                sys.stderr.write(f"[interpret.py]: ERROR (99) - FrameStackProtocol - symt_get_symb1_symb2()\n")
                sys.stderr.write(f"                NOTE - (Internal error), invalid type_similarity argument  \n")
                sys.exit(99)
            
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
            sys.stderr.write(f"[interpret.py]: ERROR (55) - FrameStack - push_frame()\n")
            sys.stderr.write(f"                NOTE - Temporary frame doesn't exists, (nothing to push)\n")
            sys.exit(55)

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
            sys.stderr.write(f"[interpret.py]: ERROR (55) - FrameStack - pop_frame()\n")
            sys.stderr.write(f"                NOTE - Frame stack is empty, (nothing to pop)\n")
            sys.exit(55)

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
            sys.stderr.write(f"[interpret.py]: ERROR (52) - SymbolTableData - insert_key()\n")
            sys.stderr.write(f"                NOTE - Variable already exists in the data-frame\n")
            sys.stderr.write(f"                VAR  - {key}\n")
            sys.exit(52)

    # inserts or replaces the value and the type of the key
    def set_var(self, key, data, data_type):
        if key in self.table:
            self.table[key] = (data, data_type)
        else:
            # raise an error or handle the case where the key is not found
            sys.stderr.write(f"[interpret.py]: ERROR (54) - SymbolTableData - set_var()\n")
            sys.stderr.write(f"                NOTE - Variable not found in the data-frame\n")
            sys.stderr.write(f"                VAR  - {key} - <{data_type}>, {data}\n")
            sys.exit(54)
    
    # return the value and the type of the key
    def get_var(self, key):
        
        if key in self.table:
            var_data, var_value = self.table.get(key)
            return var_data, var_value
        else:
            # raise an error or handle the case where the key is not found
            sys.stderr.write(f"[interpret.py]: ERROR (54) - SymbolTableData - set_var()\n")
            sys.stderr.write(f"                NOTE - Variable not found in the data-frame\n")
            sys.stderr.write(f"                VAR  - {key}\n")
            sys.exit(54)
    
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
            sys.stderr.write(f"[interpret.py]: ERROR (56) - DataStack - pop()\n")
            sys.stderr.write(f"                NOTE - Stack is empty, (nothing to pop)\n")
            sys.exit(56)

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
            sys.stderr.write(f"[interpret.py]: ERROR (56) - FuncCallStack - pop()\n")
            sys.stderr.write(f"                NOTE - Stack is empty, (nothing to pop)\n")
            sys.exit(56)

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
            sys.stderr.write(f"[interpret.py]: ERROR (52) - SymbolTableJump - add_label()\n")
            sys.stderr.write(f"                NOTE  - Label already exists, can't add new label\n")
            sys.stderr.write(f"                LABEL - {label}, {inst_order}\n")
            sys.exit(52)

        # add the label to the table
        else:
            self.table[label] = int(inst_order)

    # get label inst_order from the table
    def get_label(self, label):

        # if the label is not in the table, raise an error
        if label not in self.table:
            sys.stderr.write(f"[interpret.py]: ERROR (52) - SymbolTableJump - get_label()\n")
            sys.stderr.write(f"                NOTE  - Label not found, nowhere to jump to\n")
            sys.stderr.write(f"                LABEL - {label}, None\n")
            sys.exit(52)
        
        # return the label inst_order
        else:
            return self.table[label]
    
    # check if label exists in the table
    def check_label(self, label):
        if label not in self.table:
            sys.stderr.write(f"[interpret.py]: ERROR (52) - SymbolTableJump - get_label()\n")
            sys.stderr.write(f"                NOTE  - Label not found, nowhere to jump to\n")
            sys.stderr.write(f"                LABEL - {label}, None\n")
            sys.exit(52)

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

    # initialize the interpret class
    interpret = Interpret()

    # read arguments -> optional for the user -> if not given the program will run with default values
    # to note instructions READ won't work because of the missing arguments
    interpret.read_args()

    # runs the given code the code
    interpret.run_script()