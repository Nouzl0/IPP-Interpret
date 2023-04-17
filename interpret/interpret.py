
# - - - - - - - - - - - #
#       LIBRARIES       #
# - - - - - - - - - - - #
#   -   -   -   -   -   -   -   -
import sys
import re
import argparse
import xml.etree.ElementTree as ET



# -   # - - - - - - - - - - - - - - #
# -   #       INTERPRET CLASS       #
# -   # - - - - - - - - - - - - - - #
#
# usage:
# - Is the main class of the interpret.py script -> interface for the user
# - The user can use the Interpret class to interpret the xml source file
# - run_script() method runs interprets the source file
# - read_args() method reads the arguments of the interpret.py script (optional)
#
# dependencies:
# - InputParser class
# - ExecuteInstruction class
# - SymbolTableJump class
class Interpret:

    def __init__(self):
        self.input_parse = InputParser()    # input parser class
        self.run = ExecuteInstruction()
        self.symt_jump = SymbolTableJump()
        self.source = sys.stdin             # default = stdin -> xml_file source
        self.input = None                   # default = None  -> read input
        self.stati = None                   # default = None  -> stati file
        self.stati_args = None              # default = None  -> stati arguments

    # read_args():
    # - pub. method which reads interpret.py arguments from the command line
    # - method sets up the source file, input file, stati file and stati arguments
    # - this function doesn't need to be called by the user if he doesn't want to read the arguments
    #
    # return error codes:
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
                sys.stderr.write(f"[interpret.py]: ERROR (11) Interpret - read_args()\n")
                sys.stderr.write(f"                NOTE - Can't open source file {self.source}\n")
                sys.exit(11)
        
        # open input file if possible
        if self.input != None:
            try:
                self.input = open(self.input, "r")
            except FileNotFoundError or PermissionError:
                sys.stderr.write(f"[interpret.py]: ERROR (11) - Interpret - read_args()\n")
                sys.stderr.write(f"                NOTE - Can't open input file {self.input}\n")
                sys.exit(11)

        # set stdin for the input file
        if self.input == None:
            self.input = sys.stdin

        # set up the stati file
        if self.stati != None:
            try:
                self.stati = open(self.stati, "w")
            except FileNotFoundError or PermissionError:
                sys.stderr.write(f"[interpret.py]: ERROR (12) - Interpret - read_args()\n")
                sys.stderr.write(f"                NOTE - Can't write to stati file {self.stati}\n")
                sys.exit(12)

    # run_script():
    # - publ. method which runs the interpret.py script, 
    # - interprets the source file and executes the instructions
    def run_script(self): 

        # parse the instructions onto an array of instructions
        inst = self.input_parse.parse_instructions(self.source)

        # run the instructions
        self.__init_symt_jump(inst)                        # searches for labels and saves their position
        self.__run_instructions(inst, self.symt_jump)      # runs every instruction in the array of instructions


    # init_symt_jump():
    # - initializes the symt_jump class 
    # - saves the position of every label in the source file
    def __init_symt_jump(self, inst):

        # initialize the symt_jump table for jumps
        i = 0
        while i < len(inst):    
            if inst[i].opcode == "LABEL":
                self.symt_jump.add_label(inst[i].arg1_text, i)

            i += 1

    # run_instructions():
    # - executes every instruction in the array of instructions
    # - calls the appropriate method for every instruction
    #
    # return error codes:
    # = 32 - invalid instruction -> instruction not found in the opcode_inst_methods dictionary
    def __run_instructions(self, inst, symt_jump):

        # [1] - methods with instrusction data
        opcode_inst_methods = {
            "MOVE" : self.run.execute_move,               # Data frames
            "DEFVAR" : self.run.execute_defvar,
            "CREATEFRAME" : self.run.execute_createframe,    
            "PUSHFRAME" : self.run.execute_pushframe,
            "POPFRAME" : self.run.execute_popframe,
            "PUSHS" : self.run.execute_pushs,             # Data stack
            "POPS" : self.run.execute_pops,
            "ADD" : self.run.execute_add,                 # Arithmetic
            "SUB" : self.run.execute_sub,
            "MUL" : self.run.execute_mul,
            "IDIV" : self.run.execute_idiv,
            "LT" : self.run.execute_lt,                   # Relational
            "GT" : self.run.execute_gt,
            "EQ" : self.run.execute_eq,
            "AND" : self.run.execute_and,                 # Logical
            "OR" : self.run.execute_or,
            "NOT" : self.run.execute_not,
            "INT2CHAR" : self.run.execute_int2char,       # Conversion
            "STRI2INT" : self.run.execute_stri2int,
            "WRITE" : self.run.execute_write,             # I/O  
            "CONCAT" : self.run.execute_concat,           # String operations
            "STRLEN" : self.run.execute_strlen,
            "GETCHAR" : self.run.execute_getchar,
            "SETCHAR" : self.run.execute_setchar,
            "TYPE" : self.run.execute_type,               # Type           
            "LABEL" : self.run.execute_label,             # Program flow
            "EXIT" : self.run.execute_exit,                        
            "DPRINT" : self.run.execute_dprint,           # Debugging
            "BREAK" : self.run.execute_break,
        }

        # [2] - methods with instrusction data which return a jump value
        opcode_jump_methods = {
            "JUMP" : self.run.execute_jump,                   # Program flow
            "JUMPIFEQ" : self.run.execute_jumpifeq,
            "JUMPIFNEQ" : self.run.execute_jumpifneq,
        }

        # [3] - call method
        opcode_call_method = {
            "CALL" : self.run.execute_call,                   # Function calls         
        }

        # [4] - return method
        opcode_return_method = {
            "RETURN" : self.run.execute_return,               # Function calls
        }

        # [5] - methods which require input/output
        opcode_read_method = {
           "READ" : self.run.execute_read,                   # Input/Output
        }


        # reading instructions and calling the corresponding execution method
        i = 0
        while i < len(inst):

            # [0] - debug
            #sys.stderr.write(f"{inst[i].order} - {inst[i].opcode}\n")
            #sys.stderr.write(f"              {inst[i].arg1_type} {inst[i].arg1_text}\n")
            #sys.stderr.write(f"              {inst[i].arg2_type} {inst[i].arg2_text}\n")
            #sys.stderr.write(f"              {inst[i].arg3_type} {inst[i].arg3_text}\n")

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


            # [3] - call instruction
            elif inst[i].opcode in opcode_call_method:

                # get the next instruction index
                inst_order = opcode_call_method[inst[i].opcode](inst[i], symt_jump, i)

                # if the instruction is not a jump, then continue with the next instruction
                if inst_order == -1:
                    i += 1
                else:
                    i = inst_order

            # [4] - return instruction
            elif inst[i].opcode in opcode_return_method:

                # get the next instruction index
                inst_order = opcode_return_method[inst[i].opcode](inst[i])

                # if the instruction is not a jump, then continue with the next instruction
                if inst_order == -1:
                    i += 1
                else:
                    i = inst_order

            # [5] - read instruction
            elif inst[i].opcode in opcode_read_method:
                opcode_read_method[inst[i].opcode](inst[i], self.input)
                i += 1

            # [6] - unknown instruction
            else:
                sys.stderr.write(f"[interpret.py]: ERROR (32) - Interpret - run_instructions()\n")
                sys.stderr.write(f"                NOTE - Unknown instruction ({inst[i].opcode})\n")
                sys.exit(32)



# -  # - - - - - - - - - - - - - - #
# -  #    INPUT-PARSER CLASS       #
# -  # - - - - - - - - - - - - - - #
#
# usage:
# - used for parsing the source code and instructions
# - encapsulates parsing capabilities of interpret.py
class InputParser:

    # Instruction class:
    # - contains all the information about the instruction
    # - used for easier access to the instruction data, used like c like structure
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

    # run_instructions():
    # - parses the xml file and saves the instructions into a list of Instruction class
    # - method returns the list of instructions
    #
    # return errors codes:
    # = 31 - invalid xml file -> missing/wrong root, etc.
    # = 32 - invalid xml structure -> missing/wrong args, opcode, order, etc.
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

        # check root arg
        if tree_root.tag != "program" or tree_root.attrib.get("language") != "IPPcode23":
            sys.stderr.write(f"[interpret.py]: ERROR (32) - InputParser - parse_instructions()\n")
            sys.stderr.write(f"                NOTE - Unknown root xml argument ({tree_root.tag})\n")
            sys.exit(32)
        
        # get xml_tree children data
        tree_children = list(tree_root)

        # go through the children and check if the order and args are valid
        for child in tree_children:

            # check if the root arg is valid
            if (child.tag != "instruction"):
                sys.stderr.write(f"[interpret.py]: ERROR (32) - InputParser - parse_instructions()\n")
                sys.stderr.write(f"                NOTE - Unknown child xml argument ({child.tag})\n")
                sys.exit(32)

            # check if opcode exists
            if child.attrib.get('opcode') is None:
                sys.stderr.write(f"[interpret.py]: ERROR (32) - InputParser - parse_instructions()\n")
                sys.stderr.write(f"                NOTE - Missing opcode xml argument ({child.attrib.get('opcode')})\n")
                sys.exit(32)

            # check the order type if it is a number and if it is positive
            if (child.attrib.get('order') is None) or (not child.attrib.get('order').isdigit()) or (int(child.attrib.get('order')) < 0):
                sys.stderr.write(f"[interpret.py]: ERROR (32) - InputParser - parse_instructions()\n")
                sys.stderr.write(f"                NOTE - Wrong xml instruction order ({child.attrib.get('order')})\n")
                sys.exit(32)

        # try to sort the children by the order
        try:
            tree_children.sort(key=lambda child: int(child.attrib.get('order') or 0))
        except:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - InputParser - parse_instructions()\n")
            sys.stderr.write(f"                NOTE - Wrong xml instruction order ({child.attrib.get('order')})\n")
            sys.exit(32)

        # reading tree_children -> instruction data
        order = 0
        for child in tree_children:

            # check if the instruction has been sorted correctly by the order
            if (int(child.attrib.get('order')) <= order):
                sys.stderr.write(f"[interpret.py]: ERROR (32) - InputParser - parse_instructions()\n")
                sys.stderr.write(f"                NOTE - Wrong xml instruction order ({child.attrib.get('order')})\n")
                sys.exit(32)
            
            # get instruction data
            instruction = self.Instruction(child.attrib.get("opcode").upper(), child.attrib.get("order"), None, None, None, None, None, None)
            order = int(child.attrib.get('order'))

            # get xml_tree sub_children data
            tree_sub_children = list(child)
            
            # sort the sub_children by the arg + number
            try:
                tree_sub_children.sort(key=lambda sub_child: sub_child.tag)
            except:
                sys.stderr.write(f"[interpret.py]: ERROR (32) - InputParser - parse_instructions()\n")
                sys.stderr.write(f"                NOTE - Unknown subchild xml argument ({sub_child.tag})\n")
                sys.exit(32)
            
            # reading tree_sub_children -> instruction arguments
            sub_child_index = 0
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
        return inst
    
    # parse_arguments():
    # - parses the arguments from the command line
    # - uses the argparse library
    # - returns the interpret.py arguments as (source_file, input_file, stati_file, stati_args[])
    #
    # return error codes:
    # = 10 - missing/wrong arguments
    def parse_arguments(self):

        # initialize the argument parser
        parser = argparse.ArgumentParser()

        # default arguments
        parser.add_argument("--source", help="source file -> path to ippcode23.xml file, default is (stdin)", required=False)       # source file input
        parser.add_argument("--input", help="input file -> path to a file, defalut is (stdin)", required=False)                     # input file input

        # stati arguments -> to be implemented
        parser.add_argument("--stati", help="statistics file -> file where statistics are writen", required=False)                  # stati file output
        parser.add_argument("--insts", help="  stati arg (insts)", required=False)                                                  # insts
        parser.add_argument("--hot", help="  stati arg (hot)", required=False)                                                      # hot
        parser.add_argument("--vars", help="  stati arg (vars)", required=False)                                                    # vars
        parser.add_argument("--frequent", help="  stati arg (frequent)", required=False)                                            # frequent
        parser.add_argument("--eol", help="  stati arg (eol)", required=False)                                                      # eol

        # parse the arguments
        arg_source = parser.parse_args().source
        arg_input = parser.parse_args().input
        arg_stati = parser.parse_args().stati
        stati_args = [arg_stati, parser.parse_args().insts, parser.parse_args().vars, parser.parse_args().hot, parser.parse_args().frequent, parser.parse_args().eol]

        # check arg_souce and arg_input args -> one must be present
        if arg_source == None and arg_input == None:
            sys.stderr.write("[interpret.py]: ERROR (10) - InputParser - parse_arguments()\n")
            sys.stderr.write("                NOTE - Missing arguments: --source and --input\n")
            sys.exit(10)

        # return the arguments
        return arg_source, arg_input, arg_stati, stati_args



# -  # - - - - - - - - - - - - - - #
# -  #    INPUT-PARSER CLASS       #
# -  # - - - - - - - - - - - - - - #
#
# usage:
# - checks the text of a and type or a variable
# - encapsulates regexes and other important type checks for the interpret.py
# - class has also decododing capabilities
class VariableAnalysis:

    # analyze_arg():
    # - analyzes the given variable with the given type
    # - returns the variable scope if var and value
    #
    # return error codes:
    # = 32 - Variable has no type -> id doesn't exist
    # = 32 - Uknonwn variable type -> variable is not valid
    def analyze_arg(self, inst_arg, inst_type):

        var_scope = None 
        var_value = None

        # check the use case
        if inst_type == None:
            sys.stderr.write("[interpret.py]: ERROR (32) - VariableAnalysis - analyze_arg()\n")
            sys.stderr.write(f"               NOTE - Variable has no type -> id doesn't exist\n")
            sys.exit(32)

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

    # analyze_var():
    # - analyzes the given variable name/scope
    # - returns the variable scope and value
    #
    # return error codes:
    # = 32 - Wrong var operand format -> variable name or scope is wrong
    def analyze_var(self, input_var):

        # regex for checkign the input_var format
        if not re.match(r"^(GF|LF|TF)@([a-zA-Z0-9-_&%$*!?]+)$", input_var):
            sys.stderr.write("[interpret.py]: ERROR (32) - VariableAnalysis - analyze_var()\n")
            sys.stderr.write(f"               NOTE   - Wrong var operand format\n")
            sys.stderr.write(f"               BAR - {input_var}\n")
            sys.exit(32)

        # check if the variable does not start with a number
        if re.match(r"^(GF|LF|TF)@[0-9]", input_var):
            sys.stderr.write("[interpret.py]: ERROR (32) - VariableAnalysis - analyze_var()\n")
            sys.stderr.write(f"               NOTE   - Wrong var operand format\n")
            sys.stderr.write(f"               BAR - {input_var}\n")
            sys.exit(32)

        # split the string into parts -> first @ indicates the split symbol
        var_data = input_var.split("@", 1)

        return var_data[0], var_data[1]

    # analyze_string():
    # - analyzes the given string
    # - returns the string value
    #
    # return error codes:
    # = 32 - Wrong string operand format -> string uses illegal characters
    def analyze_string(self, input_string):

        # check if the string is empty
        if input_string == "" or input_string is None:
            return ""

        # check if the string var starts with string@ and does not contain ["#", " "]
        if not re.match(r"^[^# ]*$", input_string):
            sys.stderr.write("[interpret.py]: ERROR (32) - VariableAnalysis - analyze_string()\n")
            sys.stderr.write(f"               NOTE   - Wrong string operand format\n")
            sys.stderr.write(f"               STRING - {input_string}\n")
            sys.exit(32)

        # if '\' is in the string allow use only with the combination '[\][0-9]{3}'
        if not re.match(r"^(?!.*\\(?![0-9]{3})).*$", input_string):
            sys.stderr.write("[interpret.py]: ERROR (32) - VariableAnalysis - analyze_string()\n")
            sys.stderr.write(f"               NOTE   - Wrong string operand format\n")
            sys.stderr.write(f"               STRING - {input_string}\n")
            sys.exit(32)

        # decode the "[\][0-9]{3}" into the correct characters the three digits represent UTF-8 code
        input_string = re.sub(r"\\([0-9]{3})", lambda x: chr(int(x.group(1))),input_string)

        # return the new string
        return input_string

    # analyze_int():
    # - analyzes the given int
    # - returns the int value in string format
    #
    # return error codes:
    # = 32 - Wrong int operand format -> int is not a number
    def analyze_int(self, input_int):

        # check if the string var starts with int@
        if not re.match(r"^[-+]?[0-9]+$", input_int):
            sys.stderr.write("[interpret.py]: ERROR (32) - VariableAnalysis - analyze_int()\n")
            sys.stderr.write(f"               NOTE - Wrong int operand format\n")
            sys.stderr.write(f"               INT  - {input_int}\n")
            sys.exit(32)
        
        # try to convert the string into int
        try:
            input_int = int(input_int)
        except ValueError:
            sys.stderr.write("[interpret.py]: ERROR (32) - VariableAnalysis - analyze_int()\n")
            sys.stderr.write(f"               NOTE - Wrong int operand format\n")
            sys.stderr.write(f"               INT  - {input_int}\n")
            sys.exit(32)

        # return the new int
        return str(input_int)

    # analyze_bool():
    # - analyzes the given bool
    # - returns the bool value in string format
    #
    # return error codes:
    # = 32 - Wrong bool operand format -> bool is not true or false
    def analyze_bool(self, input_bool):

        # check if the string var starts with bool@
        if not re.match(r"^(true|false)$", input_bool):
            sys.stderr.write("[interpret.py]: ERROR (32) - VariableAnalysis - analyze_bool()\n")
            sys.stderr.write(f"               NOTE - Wrong bool operand format\n")
            sys.stderr.write(f"               BOOL - {input_bool}\n")
            sys.exit(32)

        # return the new bool
        return input_bool

    # analyze_nil():
    # - analyzes the given nil
    # - returns the nil value in string format
    #
    # return error codes:
    # = 32 - Wrong nil operand format -> nil is not nil
    def analyze_nil(self, input_nil):

        # check if the string var starts with nil@
        if input_nil == "nil" or input_nil == "":
            pass
        else:
            sys.stderr.write("[interpret.py]: ERROR (32) - VariableAnalysis - analyze_string()\n")
            sys.stderr.write(f"               NOTE - Wrong nil operand format\n")
            sys.stderr.write(f"               NIL  - {input_nil}\n")
            sys.exit(32)

        # return the new nil
        return ""

    # analyze_label():
    # - analyzes the given label
    # - returns the label value in string format
    #
    # return error codes:
    # = 32 - Wrong label operand format -> label uses illegal characters
    def analyze_label(self, input_label):
            
        # check if the string var starts with label@ and does not contain ["#", " "]
        if not re.match(r"^[^# ]*$", input_label):
            sys.stderr.write("[interpret.py]: ERROR (32) - VariableAnalysis - analyze_label()\n")
            sys.stderr.write(f"               NOTE  - Wrong label operand format\n")
            sys.stderr.write(f"               LABEL - {input_label}\n")
            sys.exit(32)

        # return the new label
        return input_label

    # analyze_type():
    # - analyzes the given type
    # - returns the type value in string format
    #
    # return error codes:
    # = 32 - Wrong type operand format -> type is not a type
    def analyze_type(self, input_type):
            
        # check if the string var starts with type@ and does not contain ["#", " "]
        if not re.match(r"^[^# ]*$", input_type):
            sys.stderr.write("[interpret.py]: ERROR (32) - VariableAnalysis - analyze_type()\n")
            sys.stderr.write(f"               NOTE  - Wrong label operand format\n")
            sys.stderr.write(f"               TYPE - {input_type}\n")
            sys.exit(32)

        # return the new type
        return input_type



# -   # - - - - - - - - - - - - - - - - - - - #
# -   #       EXECUTE-INSTRUCTION CLASS       #
# -   # - - - - - - - - - - - - - - - - - - - #
#
# usage:
# - Class where methods are used to execute instructions one by one
# - Every method has instructure as an argument -> Instruction class object which is is then executed by the method
#
# dependencies:
# - DataStack class             - used to store data in stack -> PUSHS, POPS
# - FuncCallStack class         - used to store jump addresses in stack -> CALL, RETURN
# - FrameStackProtocol class    - used to store data in frames -> CREATEFRAME, DEFVAR, MOVE
# - VariableAnalysis class      - used to check/decode variables -> STRLEN, JUMP
class ExecuteInstruction:

    def __init__(self):
        self.data_stack = DataStack()            # data stack
        self.func_stack = FuncCallStack()        # function call stack
        self.frame_data = FrameStackProtocol()   # interface for the frame stack
        self.inspect = VariableAnalysis()        # decode variable quirks


    # - DATA-FRAMES - # 

    # execute_defvar():
    # - saves the variable name/tag into the var frame
    #
    # return error codes:
    # = 32 - Too many arguments -> expected - DEFVAR <var>
    def execute_defvar(self, inst):        

        # check if inst has only <var> as an arguments
        if inst.arg2_text != None or inst.arg2_type != None or inst.arg3_text != None or inst.arg3_type != None:
            sys.stderr.write("[interpret.py]: ERROR (32) - ExecuteInstruction - execute_defvar()\n")
            sys.stderr.write(f"               NOTE - Too many arguments, expected - MOVE <var>\n")
            sys.exit(32)
        
        # insert the variable into the symbol table
        self.frame_data.symt_insert_var(inst.arg1_text)

    # execute_move():
    # - moves the value of the second argument into the variable
    #
    # return error codes:
    # = 32 - Too many arguments -> expected - MOVE <var> <symb>
    def execute_move(self, inst):

        # check if inst has only <var> <symb> as arguments
        if inst.arg3_text != None or inst.arg3_type != None:
            sys.stderr.write("[interpret.py]: ERROR (32) - ExecuteInstruction - execute_move()\n")
            sys.stderr.write(f"               NOTE - Too many arguments, expected - MOVE <var> <symb>\n")
            sys.exit(32)
        
        # get the variable data from the symbol table and update the variable
        var_type, var_data = self.frame_data.symt_get_symb(inst, "universal", "arg2", "raw")

        # update the variable
        self.frame_data.symt_update_var(inst.arg1_text, var_type, var_data)

    # execute_createframe():
    # - creates a new temporary frame
    #
    # return error codes:
    # = 32 - Too many arguments -> expected - CREATEFRAME
    def execute_createframe(self, inst):

        # check if all the arguments are empty
        if inst.arg1_type is not None or inst.arg1_text is not None or inst.arg2_type is not None or inst.arg2_text is not None or inst.arg3_type is not None or inst.arg3_text is not None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_createrfame()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected - CREATEFRAME\n")
            sys.exit(32)

        # create temporary frame
        self.frame_data.frame_stack_create()

    # execute_pushframe():
    # - pushes the temporary frame to the stack
    #
    # return error codes:
    # = 32 - Too many arguments -> expected - PUSHFRAME
    def execute_pushframe(self, inst):

        # check if all the arguments are empty
        if inst.arg1_type is not None or inst.arg1_text is not None or inst.arg2_type is not None or inst.arg2_text is not None or inst.arg3_type is not None or inst.arg3_text is not None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_pushframe()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected - PUSHFRAME\n")
            sys.exit(32)

        # push the temporary frame to the stack
        self.frame_data.frame_stack_push()

    # execute_popframe():
    # - pops the top frame from the stack
    #
    # return error codes:
    # = 32 - Too many arguments -> expected - POPFRAME
    def execute_popframe(self, inst):

        # check if all the arguments are empty
        if inst.arg1_type is not None or inst.arg1_text is not None or inst.arg2_type is not None or inst.arg2_text is not None or inst.arg3_type is not None or inst.arg3_text is not None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_popframe()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected input - POPFRAME\n")
            sys.exit(32)

        # pop frame from the stack
        self.frame_data.frame_stack_pop()


    # - FUNCTION-CALLS - # 

    # execute_call():
    # - calls the function - saves the current instruction order to the stack and jumps to the label
    # - returns the instruction order
    #
    # return error codes:
    # = 32 - Too many arguments -> expected - CALL <label>
    def execute_call(self, inst, symt_jump, push_inst_order):

        # check if inst has only <label> as an argument
        if inst.arg2_type is not None or inst.arg2_text is not None or inst.arg3_type is not None or inst.arg3_text is not None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_call()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected input - CALL <label>\n")
            sys.exit(32)

        self.inspect.analyze_arg(inst.arg1_text, "label")
        inst_order = symt_jump.get_label(inst.arg1_text)

        # push the current instruction order to the stack
        self.func_stack.push(push_inst_order)

        # return the instruction order
        return inst_order

    # execute_return():
    # - returns from the function - pops the instruction order from the stack and jumps to the instruction order
    # - returns the instruction order
    #
    # return error codes:
    # = 32 - Too many arguments -> expected - RETURN
    def execute_return(self, inst):

        # check if inst has no arguments
        if inst.arg1_type is not None or inst.arg1_text is not None or inst.arg2_type is not None or inst.arg2_text is not None or inst.arg3_type is not None or inst.arg3_text is not None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_return()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected input - RETURN\n")
            sys.exit(32)
        
        # get the instruction order from the stack
        inst_order = self.func_stack.pop()
        inst_order += 1

        # return the instruction order
        return inst_order


    # - DATA-STACK - #

    # execute_pushs():
    # - pushes the symb and type to the stack
    #
    # return error codes:
    # = 32 - Too many arguments -> expected - PUSHS <symb>
    def execute_pushs(self, inst):

        # check if inst has only <symb> as an argument
        if inst.arg2_type is not None or inst.arg2_text is not None or inst.arg3_type is not None or inst.arg3_text is not None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_pushs()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected input - PUSHS <symb>\n")
            sys.exit(32)

        # get the variable
        var_type, var_data = self.frame_data.symt_get_symb(inst, "universal", "arg1", "raw")

        # push the variable to the stack
        self.data_stack.push(var_data, var_type)

    # execute_pops():
    # - pops the symb and type from the stack and updates the variable
    #
    # return error codes:
    # = 32 - Too many arguments -> expected - POPS <var>
    def execute_pops(self, inst):

        # check if inst has only <var> as an argument
        if inst.arg2_type is not None or inst.arg2_text is not None or inst.arg3_type is not None or inst.arg3_text is not None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_pops()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected input - POPS <var>\n")
            sys.exit(32)

        # get the variables from the stack
        var_data, var_type = self.data_stack.pop()

        # update the variable
        self.frame_data.symt_update_var(inst.arg1_text, var_type, var_data)
    

    # - ARITHMETIC - #

    # execute_add():
    # - adds (int) the symb1 and symb2 and updates the variable with the result
    def execute_add(self, inst):

        # get the variables
        _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "arithmetic", "same", "decoded")

        # add the variables
        var_add = int(var_data_1) + int(var_data_2)

        # update the variable
        self.frame_data.symt_update_var(inst.arg1_text, "int", str(var_add))

    # execute_sub():
    # - subtracts (int) the symb1 and symb2 and updates the variable with the result
    def execute_sub(self, inst):

            # get the variables
            _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "arithmetic", "same", "decoded")

            # add the variables
            var_sub = int(var_data_1) - int(var_data_2)

            # update the variable
            self.frame_data.symt_update_var(inst.arg1_text, "int", str(var_sub))

    # execute_mul():
    # - multiplies (int) the symb1 and symb2 and updates the variable with the result
    def execute_mul(self, inst):

        if inst.arg1_type == "var":

            # get the variables
            _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "arithmetic", "same", "decoded")

            # add the variables
            var_mul = int(var_data_1) * int(var_data_2)

            # update the variable
            self.frame_data.symt_update_var(inst.arg1_text, "int", str(var_mul))

    # execute_idiv():
    # - divides (int) the symb1 and symb2 and updates the variable with the result
    #
    # return error codes:
    # = 57 - Illegal division by zero
    def execute_idiv(self, inst):

        # get the variables
        _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "arithmetic", "same", "decoded")

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


    # - RELATIONAL - #

    # execute_lt():
    # - compares the symb1 and symb2 and updates the variable with lt result (bool)
    #
    # return error codes:
    # = 53 - Invalid operand type -> expected - symb1 and symb2 to be the same type
    def execute_lt(self, inst):
        
        # get the variables
        var_type_1, var_data_1, var_type_2, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "relational", "same", "decoded")

        # compare the int variables
        if var_type_1 == "int" and var_type_2 == "int":
            if int(var_data_1) < int(var_data_2):
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

        # compare the string variables
        elif var_type_1 == "string" and var_type_2 == "string":
            if var_data_1 < var_data_2:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

        # compare the bool variables
        elif var_type_1 == "bool" and var_type_2 == "bool":
            if var_data_1 == "false" and var_data_2 == "true":
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")
        else:
            sys.stderr.write(f"[interpret.py]: ERROR (53) - ExecuteInstruction - execute_lt()\n")
            sys.stderr.write(f"                NOTE - Wrong variable types, expected <int, bool, string>\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} - {inst.arg2_type} {inst.arg3_type}\n")
            sys.exit(53)   

    # execute_gt():
    # - compares the symb1 and symb2 and updates the variable with gt result (bool)
    #
    # return error codes:
    # = 53 - Invalid operand type -> expected - symb1 and symb2 to be the same type
    def execute_gt(self, inst):
    
        # get the variables
        var_type_1, var_data_1, var_type_2, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "relational", "different", "decoded")

        # compare the int variables
        if var_type_1 == "int" and var_type_2 == "int":
            if int(var_data_1) > int(var_data_2):
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

        # compare the string variables
        elif var_type_1 == "string" and var_type_2 == "string":
            if var_data_1 > var_data_2:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
            else:
                self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

        # compare the bool variables
        elif var_type_1 == "bool" and var_type_2 == "bool":
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

    # execute_eq():
    # - compares the symb1 and symb2 and updates the variable with eq result (bool)
    #
    # return error codes:
    # = 53 - Invalid operand type -> expected - symb1 and symb2 to be the same type
    def execute_eq(self, inst):
        
        # get the variables
        var_type_1, var_data_1, var_type_2, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "relational", "different", "decoded")

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


    # - LOGICAL - #

    # execute_and():
    # - used and operator on the symb1 and symb2 and updates the variable with the result (bool)
    #
    # return error codes:
    # = 53 - Invalid operand type -> expected - symb1 and symb2 to be bool
    def execute_and(self, inst):
        
        # get the variables
        _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "logical", "same", "decoded")

        # compare the bool variables
        if var_data_1 == "true" and var_data_2 == "true":
            self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")
        else:
            self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")

    # execute_or():
    # - uses or operator on the symb1 and symb2 and updates the variable with the result (bool)
    #
    # return error codes:
    # = 53 - Invalid operand type -> expected - symb1 and symb2 to be bool
    def execute_or(self, inst):

        # get the variables
        _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "logical", "same", "decoded")

        # compare the bool variables
        if var_data_1 == "false" and var_data_2 == "false":
            self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")
        else:
            self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")

    # execute_not():
    # - negates the symb and updates the variable with the result (bool)
    def execute_not(self, inst):
        
        # get the variables
        _, var_data = self.frame_data.symt_get_symb(inst, "boolean", "arg2", "decoded")

        # compare the bool variables
        if var_data == "true":
            self.frame_data.symt_update_var(inst.arg1_text, "bool", "false")
        else:
            self.frame_data.symt_update_var(inst.arg1_text, "bool", "true")



    # - CONVERSIONS - #

    # execute_int2char():
    # - converts the symb to char and updates the variable with the result (char)
    #
    # return error codes:
    # = 32 - Invalid operand type -> expected - symb to be int
    # = 58 - Invalid operand value -> expected - int can't be converted to char
    def execute_int2char(self, inst):

        # check if inst has only <var> <symb> arguments
        if inst.arg3_type != None or inst.arg3_text != None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_int2char()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected - INT2CHAR <var> <symb>\n")
            sys.exit(32)
        
        # get the variables
        _, var_data = self.frame_data.symt_get_symb(inst, "integer", "arg2", "decoded")

        # convert the int to char
        try:
            char = chr(int(var_data))
            char = re.sub(r"([\W\s])", lambda m: fr"\{ord(m.group(1)):03d}", str(char))
        except ValueError:
            sys.stderr.write(f"[interpret.py]: ERROR (58) - ExecuteInstruction - execute_int2char()\n")
            sys.stderr.write(f"                NOTE - Int can't be converted into chat\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} {inst.arg2_text}\n")
            sys.exit(58)

        # update value
        self.frame_data.symt_update_var(inst.arg1_text, "string", char)

    # execute_stri2int():
    # - converts the symb to int and updates the variable with the result (int)
    #
    # return error codes:
    # = 58 - String index out of range
    def execute_stri2int(self, inst):

        # get the variables
        _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "string_int", "different", "decoded")
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


    # - INPUT-OUTPUT - #

    # execute_read():
    # - reads the input from input and updates the variable with the result (int, bool, string, nil)
    #
    # return error codes:
    # = 32 - Too many arguments -> expected - READ <var> <type>
    # = 53 - Invalid operand type -> expected - type to be int, bool or string
    def execute_read(self, inst, input_source):

        # check if inst has only <var> <type> arguments
        if inst.arg3_type != None or inst.arg3_text != None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_read()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected - READ <var> <type>\n")
            sys.exit(32)
        
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
    
    # execute_write():
    # - writes the symb to stdout
    #
    # return error codes:
    # = 32 - Too many arguments -> expected - WRITE <symb>
    def execute_write(self, inst):

        # check if inst has only <symb> argument
        if inst.arg2_type != None or inst.arg2_text != None or inst.arg3_type != None or inst.arg3_text != None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_write()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected - WRITE <symb>\n")
            sys.exit(32)

        # get variable data
        _, var_data = self.frame_data.symt_get_symb(inst, "universal", "arg1", "decoded")

        # print variable
        print(var_data, end="")


    # - STRING-OPERATIONS - #

    # execute_concat():
    # - concatenates two strings and updates the variable with the result
    def execute_concat(self, inst):
            
        # get the variables
        _, var_data_1, _, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "string_string", "same", "raw")

        # concatenate strings
        self.frame_data.symt_update_var(inst.arg1_text, "string", var_data_1 + var_data_2)

    # execute_strlen():
    # - gets the length of the string and updates the variable with the result
    #
    # return error codes:
    # = 32 - Too many arguments -> expected - STRLEN <var> <symb>
    def execute_strlen(self, inst):

        # check if inst has only <var> <symb> arguments
        if inst.arg3_type != None or inst.arg3_text != None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_strlen()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected - STRLEN <var> <symb>\n")
            sys.exit(32)

        # get the variables
        _, var_data = self.frame_data.symt_get_symb(inst, "string", "arg2", "decoded")

        # get the string length
        self.frame_data.symt_update_var(inst.arg1_text, "int", str(len(var_data)))

    # execute_getchar():
    # - gets the char from the string at the given index and updates the variable with the char
    #
    # return error codes:
    # = 58 - String index out of range
    def execute_getchar(self, inst):
        
        # get the variables
        _, var_string, _, var_int = self.frame_data.symt_get_symb1_symb2(inst, "string_int", "different", "decoded")

        # check the string index with char_pos position
        if len(var_string) < int(var_int) or int(var_int) < 0:
            sys.stderr.write(f"[interpret.py]: ERROR (58) - ExecuteInstruction - execute_getchar()\n")
            sys.stderr.write(f"                NOTE - String index out of range\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} {var_string} {var_int}\n")
            sys.exit(58)

        # get the char
        try:
            char = var_string[int(var_int)]
            char = re.sub(r"([\W\s])", lambda m: fr"\{ord(m.group(1)):03d}", str(char))
        except IndexError:
            sys.stderr.write(f"[interpret.py]: ERROR (58) - ExecuteInstruction - execute_getchar()\n")
            sys.stderr.write(f"                NOTE - String index out of range\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} {var_string} {var_int}\n")
            sys.exit(58)

        # update value
        self.frame_data.symt_update_var(inst.arg1_text, "string", char)

    # execute_setchar():
    # - sets the char at the given index in the string to the given char
    #
    # return error codes:
    # = 53 - Wrong variable type
    # = 58 - String index out of range
    def execute_setchar(self, inst):

        # get the variables
        _, var_int, _, var_string = self.frame_data.symt_get_symb1_symb2(inst, "int_string", "different", "decoded")

        # check the var and get the data
        var_type, var_data = self.frame_data.symt_gather_var(inst.arg1_text)

        # check the var type
        if var_type != "string":
            sys.stderr.write(f"[interpret.py]: ERROR (53) - ExecuteInstruction - execute_setchar()\n")
            sys.stderr.write(f"                NOTE - Wrong variable type\n")
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
        var_data = re.sub(r"([\W\s])", lambda m: fr"\{ord(m.group(1)):03d}", str(var_data))

        # update values
        self.frame_data.symt_update_var(inst.arg1_text, "string", var_data)


    # - TYPES - #

    # execute_type():
    # - gets the type of the variable and updates the variable with the result type in string format
    #
    # return error codes:
    # = 32 - Too many arguments -> expected - TYPE <var> <symb>
    # = 53 - Invalid variable type as second argument
    def execute_type(self, inst):

        # check if inst has only <label> argument
        if inst.arg3_type != None or inst.arg3_text != None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_type()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected - TYPE <var> <symb>\n")
            sys.exit(32)

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


    # - PROGRAM-FLOW - #

    # execute_label():
    # - does nothing, just checks if the label is defined correctly
    #
    # return error codes:
    # = 32 - Too many arguments -> expected - LABEL <label>
    def execute_label(self, inst):

        # check if inst has only <label> argument
        if inst.arg2_type != None or inst.arg2_text != None or inst.arg3_type != None or inst.arg3_text != None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_label()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected - LABEL <label>\n")
            sys.exit(32)

    # execute_jump():
    # - jumps to the given label
    #
    # return error codes:
    # = 32 - Too many arguments -> expected - JUMP <label>
    def execute_jump(self, inst, symt_jump):
        
        # check if inst has only <label> argument
        if inst.arg2_type != None or inst.arg2_text != None or inst.arg3_type != None or inst.arg3_text != None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_jump()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected - JUMP <label>\n")
            sys.exit(32)

        # return the opcode order
        return symt_jump.get_label(inst.arg1_text)
    
    # execute_jumpifeq():
    # - jumps to the given label if the two variables are equal
    #
    # return error codes:
    # = 53 - Invalid variable type as second argument
    def execute_jumpifeq(self, inst, symt_jump):

        # get the variables
        var_type_1, var_data_1, var_type_2, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "relational", "different", "decoded")

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

    # execute_jumpifneq():
    # - jumps to the given label if the two variables are not equal
    #
    # return error codes:
    # = 53 - Invalid variable type as second argument
    def execute_jumpifneq(self, inst, symt_jump):

        # get the variables
        var_type_1, var_data_1, var_type_2, var_data_2 = self.frame_data.symt_get_symb1_symb2(inst, "relational", "different", "decoded")

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

    # execute_exit():
    # - exits the program with the given exit code
    #
    # return error codes:
    # = 32 - Too many arguments, expected - EXIT <symb>
    # = 57 - Wrong value of the exit code, expected - <0,49>
    def execute_exit(self, inst):

        # check if inst has only <symb> argument
        if inst.arg2_type != None or inst.arg2_text != None or inst.arg3_type != None or inst.arg3_text != None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_exit()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected - EXIT <symb>\n")
            sys.exit(32)

        # get the variables
        _, var_data = self.frame_data.symt_get_symb(inst, "integer", "arg1", "decoded")

        # check if the integer is in interval <0,49>
        if int(var_data) < 0 or int(var_data) > 49:
            sys.stderr.write(f"[interpret.py]: ERROR (57) - ExecuteInstruction - execute_exit()\n")
            sys.stderr.write(f"                NOTE - Wrong value of the exit code, return value has to be in <0,49>\n")
            sys.stderr.write(f"                VAR  - <{inst.arg2_type}>, {inst.arg2_text}\n")
            sys.stderr.write(f"                INST - [{inst.order}] {inst.opcode} {var_data}\n")
            sys.exit(57)

        # exit the program
        exit(int(var_data))


    # - DEBUGING - #

    # execute_dprint():
    # - prints the value of the given variable to the stderr
    #
    # return error codes:
    # = 32 - Too many arguments, expected - DPRINT <symb>
    def execute_dprint(self, inst):

        # check if inst has only <symb> argument
        if inst.arg2_type != None or inst.arg2_text != None or inst.arg3_type != None or inst.arg3_text != None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_dprint()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected - DPRINT <symb>\n")
            sys.exit(32)
        
        # get variable data
        _, var_data = self.frame_data.symt_get_symb(inst, "universal", "arg1", "decoded")

        # print variable data    
        sys.stderr.write(var_data)

    # execute_break():
    # - prints information about the current state of the program
    #
    # return error codes:
    # = 32 - Too many arguments, expected - BREAK
    def execute_break(self, inst):
        
        # check if inst has no arguments
        if inst.arg1_type != None or inst.arg1_text != None or inst.arg2_type != None or inst.arg2_text != None or inst.arg3_type != None or inst.arg3_text != None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - ExecuteInstruction - execute_break()\n")
            sys.stderr.write(f"                NOTE - Too many arguments, expected - BREAK\n")
            sys.exit(32)
        
        # print information about the current state of the program
        sys.stderr.write(f"------------------ BREAK ------------------\n")
        sys.stderr.write(f"INST - [{inst.order}] {inst.opcode}\n")




# -   # - - - - - - - - - - - - - - - - - - - #
# -   #       FRAME-STACK-PROTOCOL CLASS      #
# -   # - - - - - - - - - - - - - - - - - - - #
#
# usage:
# - Used by executeInstruction class for easy access of the frame-stack
# - Class can be thought of as an interface for the frame-stack
#
# dependencies:
# - FrameStack class        - for saving the symtables into the frame-stack
# - SymbolTableData class   - for saving the variables into the symtables
class FrameStackProtocol:

    def __init__(self):
        self.frame_stack = FrameStack()     # frame-stack
        self.symt_gf = SymbolTableData()    # global frame
        self.symt_tf = None                 # temporary frame
        self.symt_lf = None                 # local frame
        self.inspect = VariableAnalysis()   # variable analysis class


    # - FRAME-STACK - #

    # frame_stack_create():
    # - creates temporary frame
    def frame_stack_create(self):

        # create temporary frame
        self.symt_tf = SymbolTableData()

    # frame_stack_push():
    # - pushes temporary frame into the frame-stack
    def frame_stack_push(self):
        
        # push and return the head of the frame-stack
        self.symt_lf = self.frame_stack.push_frame(self.symt_tf)

        # delete temporary frame
        self.symt_tf = None

    # frame_stack_pop():
    # - pops the head of the frame-stack
    def frame_stack_pop(self):

        # pop and return the head and the popped frame
        self.symt_lf, self.symt_tf = self.frame_stack.pop_frame()


    # - SET/GET-SYMT - #

    # symt_get_symb():
    # - inserts the variable into the symbol table
    #
    # return error codes:
    # = 32 - Variable doesn't exists
    # = 55 - Variable is not accessible from the variable given scope
    def symt_insert_var(self, var_text):
        
        if var_text == None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - FrameStackProtocol - symt_insert_var()\n")
            sys.stderr.write(f"                NOTE  - Variable doesn't exists\n")
            sys.stderr.write(f"                VAR   - {var_text}\n")
            sys.exit(32)

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

    # symt_get_symb():
    # - updates variable in the symbol table
    #
    # return error codes:
    # = 32 - Variable doesn't exists
    # = 55 - Variable is not accessible from the variable given scope
    def symt_update_var(self, var_text, var_type, var_value):

        if var_text == None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - FrameStackProtocol - symt_update_var()\n")
            sys.stderr.write(f"                NOTE  - Variable doesn't exists\n")
            sys.stderr.write(f"                VAR   - {var_text}\n")
            sys.exit(32)
        
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
    
    # symt_get_symb():
    # - gets variable from the symbol table and returns its value and type
    #
    # return error codes:
    # = 55 - Variable is not accessible from the variable given scope
    # = 56 - Variable has not been initialized
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

        # return the variable data
        return var_type, var_data

    # symt_get_symb():
    # - gets variable type from the symbol table and returns its type (doesn't do any type checking)
    #
    # return error codes:
    # = 55 - Variable is not accessible from the variable given scope
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


    #  - INSTRUCTION SYMT METHODS - #
    
    # symt_get_symb():
    # - gets symb from the symbol table or instruction and returns its value and type
    # - used for easy access to the symbol table and instruction
    #
    # type_options
    # - WRITE, DPRINT, PUSHS      - type_option =  "universal" - any 
    # - STRLEN,                   - type_option =  "string" - str
    # - EXIT, STRLEN              - type_option =  "integer" - int
    # - NOT,                      - type_option =  "boolean" - bool
    #
    # arg_num
    # - arg2 - second argument
    # - arg1 - first argument
    # - arg3 - third argument
    #
    # output_type
    # - raw -> returns the orginal data -> <string> = "/065/032/066"
    # - decoded -> returns the decoded data -> <string> = "A B"
    def symt_get_symb(self, inst, type_option, arg_num, output_type):
        
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
                sys.stderr.write(f"[interpret.py]: ERROR (53) - FrameStackProtocol - symt_get_symb()\n")
                sys.stderr.write(f"                NOTE - Invalid <symb> variable type\n")
                sys.stderr.write(f"                VAR  - {arg_text} - <{var_type}>, {var_data}\n")
                sys.exit(53)

        # get the var data from the instruction
        elif arg_type in check_type:
            var_data, _ = self.inspect.analyze_arg(arg_text, arg_type)
            var_type = arg_type
        
        # no type was given
        elif arg_type is None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - FrameStackProtocol - symt_get_symb()\n")
            sys.stderr.write(f"                NOTE - Variable doesn't exist\n")
            sys.stderr.write(f"                VAR  - {arg_text} - <{var_type}>, {var_data}\n")
            sys.exit(32)

        # invalid type
        else:
            sys.stderr.write(f"[interpret.py]: ERROR (53) - FrameStackProtocol - symt_get_symb()\n")
            sys.stderr.write(f"                NOTE - Invalid <symb> variable type\n")
            sys.stderr.write(f"                VAR  - {arg_text} - <{var_type}>, {var_data}\n")
            sys.exit(53)

        # return the var data in the correct type
        # raw
        if output_type == "raw":
            if var_type == "string":
                var_data = re.sub(r"([\W\s])", lambda m: fr"\{ord(m.group(1)):03d}", str(var_data))
        
        # decoded
        elif output_type == "decoded":
            pass

        # return the var data and type
        return var_type, var_data


    # symt_get_var():
    # - gets symb1 and symb2 from the symbol table or instruction and returns their value and type
    # - used for easy access to the symbol table and instruction
    #
    # type_options
    # - ADD, SUB, MUL, IDIV   - type_check =  "arithmetic" - int, int
    # - AND, OR, NOT          - type_check =  "logical" - bool, bool
    # - LT, GT, EQ            - type_check =  "relational" - string or int or bool, string or int or bool
    # - JUMPIFEQ, JUMPIFNEQ   - type_check =  "jump" - string or int or bool
    # - STR2INT, GETCHAR      - type_check =  "string_int" - string, int
    # - SETCHAR               - type_check =  "int_string" - int, string
    # - CONCAT                - type_check =  "concat" - string, string
    #
    # type_similarity
    # - "same" -> ADD, SUB, MUL, IDIV, AND, OR, NOT, LT, GT, EQ, JUMPIFEQ, JUMPIFNEQ, CONCAT  p
    # - "different" -> STR2INT, GETCHAR, SETCHAR          
    #
    # output_type
    # - "raw" -> returns the orginal data -> <string> = "/065/032/066"
    # - "decoded" -> returns the decoded data -> <string> = "A B"
    def symt_get_symb1_symb2(self, inst, type_option, type_similarity, output_type):

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
        
        # no type was given
        elif inst.arg2_type is None:
            sys.stderr.write(f"[interpret.py]: ERROR (32) - FrameStackProtocol - symt_get_symb1_symb2()\n")
            sys.stderr.write(f"                NOTE - No type was given\n")
            sys.stderr.write(f"                VAR  - {inst.arg2_text} - <{var_type_1}>, {var_data_1}\n")
            sys.stderr.write(f"                INST - {inst.order}. - {inst.opcode} <{var_type_1}> <{inst.arg3_type}>\n")
            sys.exit(32)
        
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
                
                # no type was given
                elif inst.arg3_type is None:
                    sys.stderr.write(f"[interpret.py]: ERROR (32) - FrameStackProtocol - symt_get_symb1_symb2()\n")
                    sys.stderr.write(f"                NOTE - No type was given\n")
                    sys.stderr.write(f"                VAR  - {inst.arg3_text} - <{var_type_2}>, {var_data_2}\n")
                    sys.stderr.write(f"                INST - [{inst.order}] - {inst.opcode} <{var_type_1}> <{var_type_2}>\n")
                    sys.exit(32)

                # invalid type
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
                
                # no type was given
                elif inst.arg3_type is None:
                    sys.stderr.write(f"[interpret.py]: ERROR (32) - FrameStackProtocol - symt_get_symb1_symb2()\n")
                    sys.stderr.write(f"                NOTE - No type was given\n")
                    sys.stderr.write(f"                VAR  - {inst.arg3_text} - <{var_type_2}>, {var_data_2}\n")
                    sys.stderr.write(f"                INST - [{inst.order}] - {inst.opcode} <{var_type_1}> <{var_type_2}>\n")
                    sys.exit(32)
                
                # invalid type
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

        # [5] - change the data in the correct form
        # raw output
        if output_type == "raw":
            if var_type_1 == "string":
                var_data_1 = re.sub(r"([\W\s])", lambda m: fr"\{ord(m.group(1)):03d}", str(var_data_1))

            if var_type_2 == "string":
                var_data_2 = re.sub(r"([\W\s])", lambda m: fr"\{ord(m.group(1)):03d}", str(var_data_2))
        
        # decoded output
        elif output_type == "decoded":
            pass

        # [6] - return the variables    
        return var_type_1, var_data_1, var_type_2, var_data_2 
        


# -   # - - - - - - - - - - - - - - #
# -   #      FRAME-STACK CLASS      #
# -   # - - - - - - - - - - - - - - #
#
# usage:
# - Implements the frame stack which is used for the local and temporary frames
# - The local frame is created when the program enters the function and deleted when the program leaves the function
class FrameStack:
    
    def __init__(self):
        self.__frame_stack = []                 # stack of frames -> stack of symtables  

    # push_crame():
    # - pushes the temporary frame to stack and lf will point to the head of the stack
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
        
    # pop_frame():
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



# -   # - - - - - - - - - - - - - - - - - #
# -   #      SYMBOL-TABLE-DATA CLASS      #
# -   # - - - - - - - - - - - - - - - - - #
#
# usage:
# - Implements the symbol table data which is used to store variables and their values
# - Implemented as python dictionary with the following structure: {key: (value, type)}
class SymbolTableData:

    def __init__(self):
        self.__table = {}                # symbol table data
    
    # insert_key():
    # - insert the key and nothing else
    def insert_key(self, key):

        # check if the key is already in the table
        if key not in self.__table:
            self.__table[key] = (None, None)
        else:
            sys.stderr.write(f"[interpret.py]: ERROR (52) - SymbolTableData - insert_key()\n")
            sys.stderr.write(f"                NOTE - Variable already exists in the data-frame\n")
            sys.stderr.write(f"                VAR  - {key}\n")
            sys.exit(52)

    # set_var():
    # inserts or replaces the value and the type of the key
    def set_var(self, key, data, data_type):
        if key in self.__table:
            self.__table[key] = (data, data_type)
        else:
            # raise an error or handle the case where the key is not found
            sys.stderr.write(f"[interpret.py]: ERROR (54) - SymbolTableData - set_var()\n")
            sys.stderr.write(f"                NOTE - Variable not found in the data-frame\n")
            sys.stderr.write(f"                VAR  - {key} - <{data_type}>, {data}\n")
            sys.exit(54)    
    
    # get_var():
    # return the value and the type of the key
    def get_var(self, key):
        
        if key in self.__table:
            var_data, var_value = self.__table.get(key)
            return var_data, var_value
        else:
            # raise an error or handle the case where the key is not found
            sys.stderr.write(f"[interpret.py]: ERROR (54) - SymbolTableData - set_var()\n")
            sys.stderr.write(f"                NOTE - Variable not found in the data-frame\n")
            sys.stderr.write(f"                VAR  - {key}\n")
            sys.exit(54)
    
    # clears the hash table
    def empty_table(self):
        self.__table = {}



# -   # - - - - - - - - - - - - - #
# -   #      DATA-STACK CLASS     #
# -   # - - - - - - - - - - - - - #
#
# usage:
# - Implements the data stack which is used by stack instructions
# - Implemented as python list with the following structure: [(data, type)]
class DataStack:

    def __init__(self):
        self.__stack = []             # data stack

    # push():
    # - pushes the data and the type to the stack
    def push(self, data, data_type):
        self.__stack.append((data, data_type))

    # pop():
    # - pops the data and the type from the stack
    def pop(self):
        if not self.is_empty():
            return self.__stack.pop()
        else:
            sys.stderr.write(f"[interpret.py]: ERROR (56) - DataStack - pop()\n")
            sys.stderr.write(f"                NOTE - Stack is empty, (nothing to pop)\n")
            sys.exit(56)

    # is_empty():
    # - returns True if the stack is empty
    def is_empty(self):
        return len(self.__stack) == 0

    # size():
    # - returns the size of the stack
    def size(self):
        return len(self.__stack)



# -   # - - - - - - - - - - - - - - - #
# -   #      FUNC-CALL-STACK CLASS    #
# -   # - - - - - - - - - - - - - - - #
#
# usage:
# - Implemention of stack which stores where to jump with instructions CALL and RETURN
# - Implemented as python list with the following structure: [instruction_order]
class FuncCallStack:

    def __init__(self):
        self.__stack = []           # function call stack
    
    # push():
    # - push the instruction order to the stack
    def push(self, inst_order):
        self.__stack.append(inst_order)

    # pop():
    # - pop the instruction order from the stack
    def pop(self):
        if not self.is_empty():
            return self.__stack.pop()
        else:
            sys.stderr.write(f"[interpret.py]: ERROR (56) - FuncCallStack - pop()\n")
            sys.stderr.write(f"                NOTE - Stack is empty, (nothing to pop)\n")
            sys.exit(56)

    # is_empty():
    # - check if the stack is empty
    def is_empty(self):
        return len(self.__stack) == 0
    
    # size():
    # - get the size of the stack
    def size(self):
        return len(self.__stack)
    


# -   # - - - - - - - - - - - - - - - - #
# -   #      SYMBOL-TABLE-JUMP CLASS    #
# -   # - - - - - - - - - - - - - - - - #
#
# usage:
# - Implements the symbol table which is used to store labels and their instruction order
# - Implemented as python dictionary with the following structure: {label: instruction_order}
class SymbolTableJump:

    def __init__(self):
        self.__table = {}       # symbol with jump instruction order

    # add_label():
    # - add label to the table
    def add_label(self, label, inst_order):

        # if the label is already in the table, raise an error
        if label in self.__table:
            sys.stderr.write(f"[interpret.py]: ERROR (52) - SymbolTableJump - add_label()\n")
            sys.stderr.write(f"                NOTE  - Label already exists, can't add new label\n")
            sys.stderr.write(f"                LABEL - {label}, {inst_order}\n")
            sys.exit(52)

        # add the label to the table
        else:
            self.__table[label] = int(inst_order)
    
    # get_label():
    # - get label inst_order from the table
    def get_label(self, label):

        # if the label is not in the table, raise an error
        if label not in self.__table:
            sys.stderr.write(f"[interpret.py]: ERROR (52) - SymbolTableJump - get_label()\n")
            sys.stderr.write(f"                NOTE  - Label not found, nowhere to jump to\n")
            sys.stderr.write(f"                LABEL - {label}, None\n")
            sys.exit(52)
        
        # return the label inst_order
        else:
            return self.__table[label]
    
    # check_label():
    # - check if label exists in the table
    def check_label(self, label):
        if label not in self.__table:
            sys.stderr.write(f"[interpret.py]: ERROR (52) - SymbolTableJump - get_label()\n")
            sys.stderr.write(f"                NOTE  - Label not found, nowhere to jump to\n")
            sys.stderr.write(f"                LABEL - {label}, None\n")
            sys.exit(52)

    # empty_table():
    # - clears the table
    def empty_table(self):
        self.__table = {}



# -   # - - - - - - - - - #
# -   #        MAIN       #
# -   # - - - - - - - - - #
#
# - - Runs the interpret class

if __name__ == "__main__":

    # initialize the interpret class
    interpret = Interpret()

    # read arguments -> optional for the user -> if not given the program will run with default values
    # to note instructions READ won't work because of the missing arguments
    interpret.read_args()

    # runs the given code the code
    interpret.run_script()