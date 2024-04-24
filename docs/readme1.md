**Implementační dokumentace k 1. úloze do IPP 2022/2023**

**Jméno a příjmení:** Nikolas Nosál

## Introduction

This document provides instructions for using a parse.php parsing script which creates XML file.
You can find here also a quick description of how the program works and the design process.

The parsing script is later going to be used as part of a bigger program of a interpret.py
- Input: input is a .IPPcode23 file -> [file]
- Output: output is an XML file -> [file].xml, this file is used by the interpret

## Requirements
To use this script, you will need:

- PHP 8.1 installed on your system
- The PHP XML library installed on your system
- A text file or string in the correct format for parsing - the format of the file is defined in ipp23spec.pdf (Zadání projektu z předmětu IPP 2022/2023)

## Usage
The parse.php is reading the file/string input through stdin.
So for example you can parse the file using this command:
- php parse.php < parse_this_file.IPPcode23

You can also use (--help) to see how to use this script, used like this:
- php parse.php --help

## Program design proces
The script parse.php is structured around a series of functions that manipulate data. Object oriented programing wasn't used in the script, except of the use of the Document Object Model DOM for creating the XML file. When designing the scripts structure it was considered that the script won't need any complex abstractions or design patterns. Therefore, the script is structured into four simple stages which are part of the main script. The separation of the script's logic mainly comes to dividing a conquering the problem. 

I think it also important to mention that the last stage is the most complicated one so there the logic is separated into functions. Here I preferred minimizing the state (using functions), than chopping the code into smaller pieces. This was mainly done for practical reasons as well as making the code more readable. All the script's functions are exclusively used in the last stage of the script, as mentioned. Down below is a quick description of every mentioned stage and function.

### Main
#### - Parsing program arguments -
In this stage the script parses the arguments like (--help) and then decides what to do next depending on what arguments have been used. If an error is found the script exits returns an error message.
#### - Getting input from stdin -
The script checks stdin for input, if it finds it the script goes to another stage.
#### - Reading the header -
Before the script starts creating XML file, it first checks the header string of the file. The script expects IPPCODE23 header.
#### - Creating the XML file -
The script parses the file and starts creating the XML output depending on the input.
In this stage and only in this stage the program will use the bellow mentioned functions. 
In the end it prints XML file as stdout output. 

### Functions
**write_label()** - Writes to XML object label argument depending on instruction and rank.

**write_var()** - Writes to XML object var argument depending on instruction and rank.

**write_type()** - Writes to XML object it's type, used only in one instance.

**write_symb()** - Write to XML object symb argument, this function uses function below as a helper function.

**write_symb_value_check()** - Checks for write_symb() function the symb argument, exits if error is found.
