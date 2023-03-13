<?php

    # - - - - - - - - #
    # Script settings #
    # - - - - - - - - #

    ini_set('display_errors', 'stderr');



    # - - - - - - - - - - - - - - - #
    #    FUNCTION - write_label     #
    # - - - - - - - - - - - - - - - #

    # function for writing the label into the XML file
    function write_label($xml, $rank, $instruction, $str) {
        $arg_rank = "arg$rank";

        # checking the label
        if (preg_match('/^[a-zA-Z0-9-_&%$*!?]+$/',$str) == false) {
            fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong <label> as the argument of the instruction <LABEL>\n");
            exit(23);
        }

        # adding the label to the XML file
        $arg = $xml->createElement($arg_rank, $str);
        $arg->setAttribute('type', 'label');
        $instruction->appendChild($arg);
    }



    # - - - - - - - - - - - - - - #
    #     FUNCTION - write_var    #
    # - - - - - - - - - - - - - - #

    # function for writing the var into the XML file
    function write_var($xml, $rank, $instruction, $str) {
        $arg_rank = "arg$rank";

        # checking the variable 
        if (preg_match('/^(GF|LF|TF)@([a-zA-Z0-9-_&%$*!?]+)$/', $str) == false) {
            fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong <var> as the argument of the instruction\n");
            exit(23);
        }

        # checking the variable name -> first symbol after @ can't be number (edge case)
        if (preg_match('/^(GF|LF|TF)@[0-9]/', $str) == true) {
            fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong <var> as the argument of the instruction\n");
            exit(23);
        }

        # adding the variable to the XML file
        $arg = $xml->createElement($arg_rank, htmlentities($str));
        $arg->setAttribute('type', 'var');
        $instruction->appendChild($arg);
    }



    # - - - - - - - - - - - - - - #
    #    FUNCTION - write_type    #
    # - - - - - - - - - - - - - - #

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



    # - - - - - - - - - - - - - - - - - - - - #
    #    FUNCTION - write_symb_value_check    #
    # - - - - - - - - - - - - - - - - - - - - #

    # function used by write_symb -> helps to identify / check the type of the symb
    function write_symb_value_check($type, $value) {
        switch ($type) {
            
            # int type
            case 'int':
                if (is_numeric($value) == false) {
                    fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong <symb> argument\n");
                    exit(23);
                }
                break;
            
            # bool type
            case 'bool':
                if ($value != "true" && $value != "false") {
                    fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong <symb> argument\n");
                    exit(23);
                }
                break;
            
            # string type
            case 'string':
                if (preg_match('/^([^\s#\\\\]|\\\\[0-9]{3})*$/', $value) == false) {
                    fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong <symb> argument\n");
                    exit(23);
                }
                break;
            
            # nil type
            case 'nil':
                if ($value != "nil") {
                    fwrite(STDERR, "[parse.php]: ERROR (23) - Wrong <symb> argument\n");
                    exit(23);
                }
                break;
        }
    }


    # - - - - - - - - - - - - - - #
    #    FUNCTION - write_symb    #
    # - - - - - - - - - - - - - - #

    # function for writing the symb into the XML file
    function write_symb($xml, $rank, $instruction, $str) {
        
        $symb = explode("@", $str);
        $arg_rank = "arg$rank";
        
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



    # - - - - - - - - - - - - - - - - - - - - #
    #       MAIN - Parsing program args       #
    # - - - - - - - - - - - - - - - - - - - - #

    # checking program args and parsing them
    if ($argc > 1) {
        if ($argc < 3) {
        
            switch($argv[1]) {

                # help arg [--help]
                case '--help':
                    print(" - [ parse.php ] -\n");
                    print("Info: parse.php is parser for Interpret-IPPcode23 used by interpret.py\n");
                    print("Input: input is a .IPPcode23 file -> <file>\n");
                    print("Output: output is a XML file -> <file>.xml, this file is used by the interpret\n");
                    print("\nUsage: php parse.php <file>\n");
                    print("Example: php parse.php < parse.IPPcode23\n");
                    exit(0);
                    break;
                
                # error - wrong argument
                default:
                    fwrite(STDERR, "[parse.php]: ERROR (10) - use: try using --help to get more info - wrong argument\n");
                    exit(10);
                    break;
            }

        # error - too many arguments
        } else {
            fwrite(STDERR, "[parse.php]: ERROR (10) - use: try using --help to get more info - too many arguments\n");
            exit(10);
        }
    }


    # - - - - - - - - - - - - - - - - - - - - - #
    #      MAIN - Getting input from stdin      #
    # - - - - - - - - - - - - - - - - - - - - - #

    # reading the file thorugh the stdin
    if (($file = file('php://stdin', FILE_SKIP_EMPTY_LINES)) == false) {
        $print_s = $argv[1];
        fwrite(STDERR, "[parse.php]: ERROR (11) - Cannot open file $print_s\n");
        exit(11);
    }

    # removing comments/special characters
    for ($i = 0; $i < count($file); $i++) {
        $file[$i] = trim($file[$i]);                            // removing special characters -> \n, \t, ...
        $file[$i] = preg_replace('/#.*/', '', $file[$i]);       // removing comments
        $file[$i] = preg_replace('/\s+/', ' ', $file[$i]);      // removing empty spaces
    }



    # - - - - - - - - - - - - - - - - - - - - #
    #        MAIN - Reading the header        #
    # - - - - - - - - - - - - - - - - - - - - #

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



    # - - - - - - - - - - - - - - - - - - - #
    #      MAIN - Creating the XML file     #
    # - - - - - - - - - - - - - - - - - - - #

    # XML - creating the new XML file
    $xml = new DOMDocument('1.0', 'UTF-8');
    $xml->formatOutput = true;

    # XML - creating the program element
    $program = $xml->createElement('program');
    $program->setAttribute('language', 'IPPcode23');
    $xml->appendChild($program);

    # going through the checked string array and skipping empty lines
    for ($i = 0, $j = 0; $i < count($file); $i++) {
        if (empty($file[$i]) == false) {

            # XML - creating and adding the instruction element
            $j++;                                                   // increasing the order of the instruction
            $instruction = $xml->createElement('instruction');      // creating the instruction element
            $instruction->setAttribute('order', $j);                // setting the order attribute
            
            # splitting the string and corecting it
            $str = explode(" ", $file[$i]);                  // splitting the string into a string array -> $str
            $str[0] = strtoupper($str[0]);                   // make the <instruction> uppercase
            $opcode = $str[0];                               // saving the <instruction> for the error messages

            # parsing the instructions
            switch ($str[0]) {

                # <instruction>
                ## CREATEFRAME, PUSHFRAME, POPFRAME, RETURN, BREAK
                case 'CREATEFRAME':
                case 'PUSHFRAME':
                case 'POPFRAME':
                case 'RETURN':
                case 'BREAK':  

                    # checking args [ = 1 ], XML - creating and adding instruction arguments
                    if  ((empty($str[1])) && (!empty($str[0]))) {
                        $instruction->setAttribute('opcode', $opcode);

                    # args error 
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - expected: $opcode - wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;                    


                # <instruction> <var>
                ## DEFVAR, POPS
                case 'DEFVAR':
                case 'POPS': 

                    # checking args [ = 2 ], XML - creating and adding instruction arguments
                    if ((empty($str[2])) && (!empty($str[1]))) {
                        $instruction->setAttribute('opcode', $opcode);
                        write_var($xml, '1', $instruction, $str[1]);
                    
                    # args error
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - expected: $opcode <var> - wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;   


                # <instruction> <symb>
                ## PUSHS, WRITE, EXIT, DPRINT
                case 'PUSHS':
                case 'WRITE':
                case 'EXIT':    
                case 'DPRINT': 

                    # checking args [ = 2 ], XML - creating and adding instruction arguments
                    if  ((empty($str[2])) && (!empty($str[1]))) {
                        $instruction->setAttribute('opcode', $opcode);
                        write_symb($xml, '1', $instruction, $str[1]);
                    
                    # args error
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - expected: $opcode <symb> - wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;                                  


                # <instruction> <label>
                ## CALL, LABEL, JUMP
                case 'CALL':
                case 'LABEL':
                case 'JUMP': 

                    # checking args [ = 2 ], XML - creating and adding instruction arguments
                    if ((empty($str[2])) && (!empty($str[1]))) {
                        $instruction->setAttribute('opcode', $opcode);
                        write_label($xml, '1', $instruction, $str[1]);

                    # args error
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - expected: $opcode <label> - wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;               


                # <instruction> <var> <type>
                ## READ
                case 'READ':

                    # checking args [ = 2 ], XML - creating and adding instruction arguments
                    if ((empty($str[3])) && (!empty($str[2]))) {
                        $instruction->setAttribute('opcode', $opcode);
                        write_var($xml, '1', $instruction, $str[1]);
                        write_type($xml, '2', $instruction, $str[2]);
                    
                    # args error
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - expected: $opcode <type> - wrong number of instruction arguments\n");
                        exit(23);
                    }
                    break;

                    
                # <instruction> <var> <symb>
                ## MOVE, NOT, INT2CHAR, STRLEN, TYPE
                case 'MOVE':
                case 'NOT':    
                case 'INT2CHAR':
                case 'STRLEN':
                case 'TYPE':

                    # checking args [ = 3 ], XML - creating and adding instruction arguments
                    if ((empty($str[3])) && (!empty($str[2]))) {
                        $instruction->setAttribute('opcode', $opcode);
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);

                    # args error
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - expected: $opcode <var> <symb> - wrong number of instruction arguments\n");
                        exit(23);
                    }             
                    break;


                # instruction <var> <symb> <symb>    
                ## ADD, SUB, MUL, IDIV, LT, GT, EQ, AND, OR, STRI2INT, CONCAT, GETCHAR, SETCHAR
                case 'ADD':
                case 'SUB':
                case 'MUL':
                case 'IDIV':
                case 'LT':
                case 'GT':
                case 'EQ':
                case 'AND':                
                case 'OR':
                case 'NOT':
                case 'STRI2INT':
                case 'CONCAT':
                case 'GETCHAR':
                case 'SETCHAR':

                    # checking args [ = 4 ], XML - creating and adding instruction arguments
                    if ((empty($str[4])) && (!empty($str[3]))) {   
                        $instruction->setAttribute('opcode', $opcode);
                        write_var($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);

                    # args error
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - expected: $opcode <var> <symb> <symb> - wrong number of instruction arguments\n");                 
                        exit(23);
                    }
                    break;
                
                # <instruction> <label> <symb> <symb>
                ## JUMPIFEQ, JUMPIFNEQ
                case 'JUMPIFEQ':
                case 'JUMPIFNEQ':

                   # checking args [ = 4 ], XML - creating and adding instruction arguments
                    if ((empty($str[4])) && (!empty($str[3]))) {
                        $instruction->setAttribute('opcode', $opcode);
                        write_label($xml, '1', $instruction, $str[1]);
                        write_symb($xml, '2', $instruction, $str[2]);
                        write_symb($xml, '3', $instruction, $str[3]);

                    # args error
                    } else {
                        fwrite(STDERR, "[parse.php]: ERROR (23) - expected: $opcode <label> <symb> <symb> - wrong number of instruction arguments\n"); 
                        exit(23);
                    }
                    break;
                
                # unknown instruction error
                default:
                    fprintf(STDERR, "[parse.php]: ERROR (22) - unknown instruction");
                    exit(22);
            }

            # XML - adding the instruction to the root element
            $program->appendChild($instruction);
        }
    }

    # XML - printing the xml code
    print($xml->saveXML());

    exit(0);
?>