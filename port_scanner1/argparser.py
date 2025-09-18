import re
#where opt here stand for the option
#time complexity : O(n*m) ,where n is the number of args and options , m is the avg length of every argument/option ;
def argparse(command:'str')->'dict':
    """
    this is an argparser funtion
    it parses the command entered , extracts arguments , and options in the form of
    --option=option-argument  , or long POSIX options like : --option, so it does not literally adhere to GNU standards
    However , this function Does not check whether the entered command is in correct form or not
    """
    lexemes={}
    command_parts=command.split()
    for part in command_parts:
        if re.match(r"^(--\w+=.+)$",part):
            option_parts=part.split('=')
            lexemes[option_parts[0]]=option_parts[1]
        elif re.match(r"^(--\w+)$",part):
            lexemes[part] = None
        else:
            lexemes[part]=None
    return lexemes
