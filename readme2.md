**Implementační dokumentace k 2. úloze do IPP 2022/2023**

**Jméno a příjmení:** Nikolas Nosál

**Login:** xnosal01

## Introduction

This document provides instructions for using a interpret.py, interpret which executes ippcode23.xml.
In this documents are also notes of how the interpret works and the design process/principles.

The interpret is meant to be used in combination with script parse.php .
Script parse.php is script which takes in raw ippcode and transforms it onto ippcode23.xml file.


## Requirements
To use this script, you will need:

- Python 3.10 installed in your system
- XML (ippcode23) file which has been created by the script parse.php which parsed raw ippcode23 file


## Input

Interpret script has two input sources which are set by arguments, (--source=<file>.xml) and (--input=<file>).
 - If one of these arguments is not set than the (--source) or (--input) is set as defalut, (stdin)
 - If none of these arguments is set then the interpret (won't start)

Input arguments
- (--source) - is the (XML ippcode23), file which will be executed by the interpret 
- (--input) - is the interpret input from which can user of the interpret interact while the interpret is running


## Output

Interpret has one main output which is (stdout) and second optional output set by argument (--stati=<file>)
 - (--stati) argument has other other optional arguments, which specify the (--stati) argument
 - these (--stati) args are ("--insts", "--hot", "--vars", "--frequent", "--eol") 

Output arguemnts
- (stdout) - is the output of the interpreted (XML ippcode23) file
- (--stati) - output of statistics which reflect the interpreted (XML ippcode) file


## Usage

Here are examples of how to use the interpret

The default, in this case the interpret.py executes ippcode23.xml file, and all print messages sends to stdout. User can interact with the interpret through stdin.
 - source = ippcode23.xml, input = stdin, output = stdout
 - $ interpret.py --source=ippcode23.xml

In this case the interpret.py executes source from stdin and and all print messages sends to stout. User can't interact with the interpret. When instruction READ appears in the source, the interpret will just read the line in the file.txt
 - source = stdin, input = file.txt, output = stdout
 - $ interpret.py --input=file.txt



## Description of the desing process


## Design of the Classes


The interpret is entirerly designed in OOP.

 - Interpret       - 
 - InputParser         -
 - VariableAnalysis    -
 - ExecuteInstruction
 - FrameStackProtocol
 - FrameStack
 - SymbolTableData
 - DataStack
 - FuncCallStack
 - SymbolTableJump

Together they create this heirarchy

## The other design aspects of the interpret