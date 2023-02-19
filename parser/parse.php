<?php

    # - - - - - - - - #
    # Script settings #
    # - - - - - - - - #

    ini_set('display_errors', 'stderr');
    error_reporting(E_ERROR | E_PARSE);


    # - - - - - - - - - - - - - - #
    # XML file creation functions #
    # - - - - - - - - - - - - - - #

    # function for writing the label into the XML file
    function write_label($xml, $rank, $instruction, $str) {
        $arg_rank = "arg$rank";

        # checking the label
        if (preg_match('/^[a-zA-Z0-9-_&%$*!?]+$/',$str) == false) {
            fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong <label> as the argument of the instruction <LABEL>\n");
            exit(23);
        }

        $arg = $xml->createElement($arg_rank, $str);
        $arg->setAttribute('type', 'label');
        $instruction->appendChild($arg);
    }

    # function for writing the var into the XML file
    function write_var($xml, $rank, $instruction, $str) {
        $arg_rank = "arg$rank";

        # checking the var
        if (preg_match('/^(GF|LF|TF)@([a-zA-Z0-9-_&%$*!?]+)$/', $str) == false) {
            fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong <var> as the argument of the instruction <DEFVAR>\n");
            exit(23);
        }
        
        #print("str = "); print($str); print("\n");
        $arg = $xml->createElement($arg_rank, $str);
        $arg->setAttribute('type', 'var');
        $instruction->appendChild($arg);
    }

    # function for writing the type into the XML file
    function write_type($xml, $rank, $instruction, $str) {
        $arg_rank = "arg$rank";
    
    # value
        if ($str == "int" || $str == "bool" || $str == "string" || $str == "nil") {
            $arg = $xml->createElement($arg_rank, $str);
            $arg->setAttribute('type', 'type');
            $instruction->appendChild($arg);
    
    # error
        } else {
            fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong <type> as the argument of the instruction <READ>\n");
            exit(23);
        }
    }


    function write_symb_value_check($type, $value) {
        switch ($type) {
            case 'int':
                if (is_numeric($value) == false) {
                    fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong <symb> argument\n");
                    exit(23);
                }
                break;
            
            case 'bool':
                if ($value != "true" && $value != "false") {
                    fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong <symb> argument\n");
                    exit(23);
                }
                break;

            case 'string':
                if (preg_match('/^([^\s#\\\\]|\\\\[0-9]{3})*$/', $value) == false) {
                    fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong <symb> argument\n");
                    exit(23);
                }
                break;

            case 'nil':
                if ($value != "nil") {
                    fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong <symb> argument\n");
                    exit(23);
                }
                break;
        }
    }


    # function for writing the symb into the XML file
    function write_symb($xml, $rank, $instruction, $str) {
        
        $symb = explode("@", $str);
        $arg_rank = "arg$rank";

        #print("symb[0] = "); print($symb[0]); print("\n");
        #print("symb[1] = "); print($symb[1]); print("\n");
        #print("arg_rank = "); print($arg_rank); print("\n");
        #print("str = "); print($str); print("\n");
        
        # variable
        if ($symb[0] == "GF" || $symb[0] == "LF" || $symb[0] == "TF") {

            # checking the var
            if (preg_match('/^(GF|LF|TF)@([a-zA-Z0-9-_&%$*!?]+)$/', $str) == false) {
                fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong <var> as the argument of the instruction <DEFVAR>\n");
                exit(23);
            }

            $arg = $xml->createElement($arg_rank, $str);
            $arg->setAttribute('type', 'var');
            $instruction->appendChild($arg);
        
        # value
        } else {
            # value
            if ($symb[0] == "int" || $symb[0] == "bool" || $symb[0] == "string" || $symb[0] == "nil") {
                write_symb_value_check($symb[0], $symb[1]);
                $arg = $xml->createElement($arg_rank, $symb[1]);
                $arg->setAttribute('type', $symb[0]);
                $instruction->appendChild($arg);
        
        # error
            } else {
                fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong type of the argument\n");
                exit(23);
            }
        }
    }


    # too many arguments
    if ($argc > 1) {
        # help argument
        if ($argv[1] == "--help") {
            print(" - [ parse.php ] -\n");
            print("Info: parse.php is parser for IPPcode23 used by interpret.py\n");
            print("Input: input is a .IPPcode23 file -> <file>\n");
            print("Output: output is a XML file -> <file>.xml, this file is used by the interpret\n");
            print("- - - - - - - - -\nUsage: php parse.php <file>\n");
            exit(10);
        } else {
            fwrite(STDERR, "[parse.php]: ERROR (10) - too many arguments\n");
            exit(10);
        }
    }

    # reading the file thorugh the stdin
    if (($file = file('php://stdin', FILE_SKIP_EMPTY_LINES)) == false) {
        $print_s = $argv[1];
        fwrite(STDERR, "[parse.php]: ERROR (11) - Cannot open file $print_s\n");
        exit(11);
    }

    # removing comments/special characters
    for ($i = 0; $i < count($file); $i++) {
        $file[$i] = trim($file[$i]);
        $file[$i] = preg_replace('/#.*/', '', $file[$i]);
        $file[$i] = preg_replace('/\s+/', ' ', $file[$i]);
#        print($file[$i]);
#        print(" - strlen = "); print(strlen($file[$i]));
#        print("\n");
    }

#    print("\n");


    # reading the header of the file
    for ($i = 0; $i < count($file); $i++) {

        # removing spaces
        $file[$i] = trim($file[$i]);

        # skipping empty lines
        if (empty($file[$i]) == true) {
            continue;
        }
        
        # comparing the header
        if ((strcmp($file[$i], ".IPPcode23") !== 0)) {
            fwrite(STDERR, "[parse.php]: ERROR (21) - Wrong or missing header <.IPPcode23> in the file\n");
            exit(21);
        } else {

            # removing the header and exiting
            for ($j = 0; $j < ($i + 1); $j++) {
                array_shift($file);
            }

            # header found
            $header_found = true;
            break;
        }
    }

    # header not found
    if ($header_found == false) {
        fwrite(STDERR, "[parse.php]: ERROR (21) - Missing header <.IPPcode23> in the file\n");
        exit(21);
    }



    ##for ($i = 0; $i < count($file); $i++) {
    ##    print($file[$i]);
    ##    print("\n");
    ##}
##
    ##print("\n\n");


    # - - - - - - - - - - - #
    # Creating the XML file #
    # - - - - - - - - - - - #

    # creating the new XML file
    $xml = new DOMDocument('1.0', 'UTF-8');
    $xml->formatOutput = true;

    # creating the program element
    $program = $xml->createElement('program');
    $program->setAttribute('language', 'IPPcode23');
    $xml->appendChild($program);

    # going through the checked string array
    for ($i = 0, $j = 0; $i < count($file); $i++) {

        # skipping empty lines
        if (empty($file[$i]) == false) {

            # creating the instruction element
            $j++;
            $instruction = $xml->createElement('instruction');
            $instruction->setAttribute('order', $j);
            $str = explode(" ", $file[$i]);

            # parsing the instructions
            switch ($file[$i]) {

                # frames/function_calls/variables instructions
                ## MOVE
                case (preg_match('/^MOVE/', $file[$i]) ? true : false) :
                    if (empty($str[3])) {
                        $instruction->setAttribute('opcode', 'MOVE');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;  
                
                ## CREATEFRAME
                case (preg_match('/^CREATEFRAME/', $file[$i]) ? true : false) :

                    if (empty($str[1])) {
                        $instruction->setAttribute('opcode', 'CREATEFRAME');
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
            
                ## PUSHFRAME
                case (preg_match('/^PUSHFRAME/', $file[$i]) ? true : false) :

                    if (empty($str[1])) {
                        $instruction->setAttribute('opcode', 'PUSHFRAME');
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## POPFRAME
                case (preg_match('/^POPFRAME/', $file[$i]) ? true : false) :

                    if (empty($str[1])) {
                        $instruction->setAttribute('opcode', 'POPFRAME');
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## DEFVAR
                case (preg_match('/^DEFVAR/', $file[$i]) ? true : false) :

                    if (empty($str[2])) {
                        $instruction->setAttribute('opcode', 'DEFVAR');
                        write_var($xml, '1', $instruction, $str[1]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## CALL
                case (preg_match('/^CALL/', $file[$i]) ? true : false) :
                    
                    if (empty($str[2])) {
                        $instruction->setAttribute('opcode', 'CALL');
                        write_label($xml, '1', $instruction, $str[1]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## RETURN
                case (preg_match('/^RETURN/', $file[$i]) ? true : false) :
                    
                    if (empty($str[1])) {
                        $instruction->setAttribute('opcode', 'RETURN');
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                

                # data_stack instructions
                ## PUSHS
                case (preg_match('/^PUSHS/', $file[$i]) ? true : false) :
                    
                    if (empty($str[2])) {
                        $instruction->setAttribute('opcode', 'PUSHS');
                        write_symb($xml, '1', $instruction, $str[1]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## POPS
                case (preg_match('/^POPS/', $file[$i]) ? true : false) :
                    
                    if (empty($str[2])) {
                        $instruction->setAttribute('opcode', 'POPS');
                        write_var($xml, '1', $instruction, $str[1]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                

                # arithmetic instructions
                ## ADD
                case (preg_match('/^ADD/', $file[$i]) ? true : false) :
                    
                    if (empty($str[4])) {
                        $instruction->setAttribute('opcode', 'ADD');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## SUB
                case (preg_match('/^SUB/', $file[$i]) ? true : false) :
                    
                    if (empty($str[4])) {
                        $instruction->setAttribute('opcode', 'SUB');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## MUL
                case (preg_match('/^MUL/', $file[$i]) ? true : false) :
                    
                    if (empty($str[4])) {
                        $instruction->setAttribute('opcode', 'MUL');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## IDIV
                case (preg_match('/^IDIV/', $file[$i]) ? true : false) :
                    
                    if (empty($str[4])) {
                        $instruction->setAttribute('opcode', 'IDIV');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                

                # relational instructions
                ## LT
                case (preg_match('/^LT/', $file[$i]) ? true : false) :
                    
                    if (empty($str[4])) {
                        $instruction->setAttribute('opcode', 'LT');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## GT
                case (preg_match('/^GT/', $file[$i]) ? true : false) :
                    
                    if (empty($str[4])) {
                        $instruction->setAttribute('opcode', 'GT');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## EQ
                case (preg_match('/^EQ/', $file[$i]) ? true : false) :
                    
                    if (empty($str[4])) {
                        $instruction->setAttribute('opcode', 'EQ');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                

                # logical instructions
                ## AND
                case (preg_match('/^AND/', $file[$i]) ? true : false) :

                    if (empty($str[4])) {
                        $instruction->setAttribute('opcode', 'AND');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## OR
                case (preg_match('/^OR/', $file[$i]) ? true : false) :

                    if (empty($str[4])) {
                        $instruction->setAttribute('opcode', 'OR');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## NOT
                case (preg_match('/^NOT/', $file[$i]) ? true : false) :

                    if (empty($str[4])) {
                        $instruction->setAttribute('opcode', 'NOT');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                

                # conversion instructions
                ## INT2CHAR
                case (preg_match('/^INT2CHAR/', $file[$i]) ? true : false) :

                    if (empty($str[3])) {
                        $instruction->setAttribute('opcode', 'INT2CHAR');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## STRI2INT
                case (preg_match('/^STRI2INT/', $file[$i]) ? true : false) :

                    if (empty($str[4])) {
                        $instruction->setAttribute('opcode', 'STRI2INT');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                # input/output instructions
                ## READ
                case (preg_match('/^READ/', $file[$i]) ? true : false) :

                    if (empty($str[3])) {
                        $instruction->setAttribute('opcode', 'READ');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_type($xml, '2', $instruction, $str[2]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## WRITE
                case (preg_match('/^WRITE/', $file[$i]) ? true : false) :

                    if (empty($str[2])) {
                        $instruction->setAttribute('opcode', 'WRITE');
                        write_symb($xml, '1', $instruction, $str[1]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                

                # string instructions
                ## CONCAT
                case (preg_match('/^CONCAT/', $file[$i]) ? true : false) :

                    if (empty($str[4])) {
                        $instruction->setAttribute('opcode', 'CONCAT');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## STRLEN
                case (preg_match('/^STRLEN/', $file[$i]) ? true : false) :
                    if (empty($str[3])) {
                        $instruction->setAttribute('opcode', 'STRLEN');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## GETCHAR
                case (preg_match('/^GETCHAR/', $file[$i]) ? true : false) :
                    if (empty($str[4])) {
                        $instruction->setAttribute('opcode', 'GETCHAR');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## SETCHAR
                case (preg_match('/^SETCHAR/', $file[$i]) ? true : false) :
                    $instruction->setAttribute('opcode', 'SETCHAR');
                    if (empty($str[4])) {
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                

                # dynamic_type instruction
                ## TYPE
                case (preg_match('/^TYPE/', $file[$i]) ? true : false) :
                    if (empty($str[3])) {
                        $instruction->setAttribute('opcode', 'TYPE');
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                # control/jump instructions
                ## LABEL
                case (preg_match('/^LABEL/', $file[$i]) ? true : false) :
                    if (empty($str[2])) {
                        $instruction->setAttribute('opcode', 'LABEL');
                        write_label($xml, '1', $instruction, $str[1]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## JUMP
                case (preg_match('/^JUMP/', $file[$i]) ? true : false) :
                    if (empty($str[2])) {
                        $instruction->setAttribute('opcode', 'JUMP');
                        write_label($xml, '1', $instruction, $str[1]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## JUMPIFEQ
                case (preg_match('/^JUMPIFEQ/', $file[$i]) ? true : false) :
                    if (empty($str[4])) {
                        $instruction->setAttribute('opcode', 'JUMPIFEQ');
                        write_label($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## JUMPIFNEQ
                case (preg_match('/^JUMPIFNEQ/', $file[$i]) ? true : false) :
                    if (empty($str[4])) {
                        $instruction->setAttribute('opcode', 'JUMPIFNEQ');
                        write_label($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## EXIT
                case (preg_match('/^EXIT/', $file[$i]) ? true : false) :
                    if (empty($str[2])) {
                        $instruction->setAttribute('opcode', 'EXIT');
                        write_symb($xml, '1', $instruction, $str[1]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                

                # debug instructions
                ## DPRINT
                case (preg_match('/^DPRINT/', $file[$i]) ? true : false) :
                    if (empty($str[2])) {
                        $instruction->setAttribute('opcode', 'DPRINT');
                        write_symb($xml, '1', $instruction, $str[1]);
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;
                
                ## BREAK
                case (preg_match('/^BREAK/', $file[$i]) ? true : false) :
                    if (empty($str[1])) {
                        $instruction->setAttribute('opcode', 'BREAK');
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;

                default:
                    fprintf(STDERR, "[parse.php]: ERROR (23) Unknown instruction");
                    exit(23);
            }

            # adding the instruction to the root element
            $program->appendChild($instruction);
        }
    }

    # printing the xml code
    print($xml->saveXML());

    exit(0);
?>