from ply import yacc

import ast as AST
from lexer import CoolPyLexer

class CoolPyParser():

    def __init__(self,
                 build_parser   = True,
                 debug          = False,
                 write_tables   = True,
                 optimize       = True,
                 outputdir      = '',
                 yacctab        = 'pycoolc.yacctab',
                 debuglog       = None,
                 errorlog       = None):
        
        self.tokens     = None
        self.lexer      = None
        self.parser     = None
        self.error_list = []

        self._debug         = debug
        self._write_tables  = write_tables
        self._optimize      = optimize
        self._outputdir     = outputdir
        self._yacctab       = yacctab
        self._debuglog      = debuglog
        self._errorlog      = errorlog

        if build_parser is True:
            self.build(debug        = debug, 
                       write_tables = write_tables, 
                       optimize     = optimize, 
                       outputdir    = outputdir,
                       yacctab      = yacctab, 
                       debuglog     = debuglog, 
                       errorlog     = errorlog)

    precedence = (
        ('right', 'ASSIGN'),
        ('right', 'NOT'),
        ('nonassoc', 'LTEQ', 'LT', 'EQ'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE'),
        ('right', 'ISVOID'),
        ('right', 'INT_COMP'),
        ('left', 'AT'),
        ('left', 'DOT')
    )

    def p_program(self, parse):
        '''
        program : class_list
        '''
        parse[0] = AST.Program(classes = parse[1])

    def p_class_list(self, parse):
        '''
        class_list : class_list class SEMICOLON
                   | class SEMICOLON
        '''
        if len(parse) == 3:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[2],)

    def p_class(self, parse):
        '''
        class : CLASS TYPE LBRACE features_list_option RBRACE
        '''
        parse[0] = AST.Class(name = parse[2], parent = 'Object', features = parse[4])

    def p_class_inherits(self, parse):
        '''
        class : CLASS TYPE INHERITS TYPE LBRACE features_list_option RBRACE
        '''
        parse[0] = AST.Class(name = parse[2], parent = parse[4], features = parse[6])

    def p_features_list_option(self, parse):
        '''
        features_list_option : features_list
                             | empty
        '''
        parse[0] = tuple() if parse.slice[1].type == 'empty' else parse[1]

    def p_features_list(self, parse):
        '''
        features_list : features_list feature SEMICOLON
                      | feature SEMICOLON
        '''
        if len(parse) == 3:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[2],)

    def p_feature_method(self, parse):
        '''
        feature : ID LPAREN formal_parameters_list RPAREN COLON TYPE LBRACE expression RBRACE
        '''
        parse[0] = AST.Method(name = parse[1], formal_parameters = parse[3], return_type = parse[6], body = parse[8])

    def p_feature_method_no_formal_paramters(self, parse):
        '''
        feature : ID LPAREN RPAREN COLON TYPE LBRACE expression RBRACE
        '''
        parse[0] = AST.Method(name = parse[1], formal_parameters = tuple(), return_type = parse[5], body = parse[7])

    def p_feature_attribute_initialized(self, parse):
        '''
        feature : ID COLON TYPE ASSIGN expression
        '''
        parse[0] = AST.Attribute(name = parse[1], attribute_type = parse[3], expression = parse[5])

    def p_feature_attribute(self, parse):
        '''
        feature : ID COLON TYPE
        '''
        parse[0] = AST.Attribute(name = parse[1], attribute_type = parse[3], expression = None)

    def p_formal_paramters_list(self, parse):
        '''
        formal_parameters_list  : formal_parameters_list COMMA formal_parameter
                                | formal_parameter
        '''
        if len(parse) == 2:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[3],)

    def p_formal_paramter(self, parse):
        '''
        formal_parameter : ID COLON TYPE
        '''
        parse[0] = AST.FormalParameter(name = parse[1], parameter_type = parse[3])

    def p_expression_object_identifier(self, parse):
        '''
        expression : ID
        '''
        parse[0] = AST.Object(name = parse[1])

    def p_expression_integer_constant(self, parse):
        '''
        expression : INTEGER
        '''
        parse[0] = AST.Integer(content = parse[1])

    def p_expression_boolean_constant(self, parse):
        '''
        expression : BOOLEAN
        '''
        parse[0] = AST.Boolean(content = parse[1])

    def p_expression_string_constant(self, parse):
        '''
        expression : STRING
        '''
        parse[0] = AST.String(content = parse[1])

    def p_expression_self(self, parse):
        '''
        expression  : SELF
        '''
        parse[0] = AST.Self(name = 'SELF')

    def p_expression_block(self, parse):
        '''
        expression : LBRACE block_list RBRACE
        '''
        parse[0] = AST.Block(expression_list = parse[2])

    def p_block_list(self, parse):
        '''
        block_list : block_list expression SEMICOLON
                   | expression SEMICOLON
        '''
        if len(parse) == 3:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[2],)

    def p_expression_assignment(self, parse):
        '''
        expression : ID ASSIGN expression
        '''
        parse[0] = AST.Assignment(AST.Object(name = parse[1]), expression = parse[3])

    def p_expression_dispatch(self, parse):
        '''
        expression : expression DOT ID LPAREN arguments_list_option RPAREN
        '''
        parse[0] = AST.DynamicDispatch(instance = parse[1], method = parse[3], arguments = parse[5])

    def p_arguments_list_option(self, parse):
        '''
        arguments_list_option : arguments_list
                              | empty
        '''
        parse[0] = tuple() if parse.slice[1].type == 'empty' else parse[1]

    def p_arguments_list(self, parse):
        '''
        arguments_list : arguments_list COMMA expression
                       | expression
        '''
        if len(parse) == 2:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[3],)

    def p_expression_static_dispatch(self, parse):
        '''
        expression : expression AT TYPE DOT ID LPAREN arguments_list_option RPAREN
        '''
        parse[0] = AST.StaticDispatch(instance = parse[1], dispatch_type = parse[3], method = parse[5], arguments = parse[7])

    def p_expression_self_dispatch(self, parse):
        '''
        expression : ID LPAREN arguments_list_option RPAREN
        '''
        parse[0] = AST.DynamicDispatch(instance = AST.Self('SELF'), method = parse[1], arguments = parse[3])

    def p_expression_math_operations(self, parse):
        '''
        expression : expression PLUS expression
                   | expression MINUS expression
                   | expression MULTIPLY expression
                   | expression DIVIDE expression
        '''
        if parse[2] == '+':
            parse[0] = AST.Addition(first = parse[1], second = parse[3])
        elif parse[2] == '-':
            parse[0] = AST.Subtraction(first = parse[1], second = parse[3])
        elif parse[2] == '*':
            parse[0] = AST.Multiplication(first = parse[1], second = parse[3])
        elif parse[2] == '/':
            parse[0] = AST.Division(first = parse[1], second = parse[3])

    def p_expression_math_comparisons(self, parse):
        '''
        expression : expression LT expression
                   | expression LTEQ expression
                   | expression EQ expression
        '''
        if parse[2] == '<':
            parse[0] = AST.LessThan(first = parse[1], second = parse[3])
        elif parse[2] == '<=':
            parse[0] = AST.LessThanOrEqual(first = parse[1], second = parse[3])
        elif parse[2] == '=':
            parse[0] = AST.Equal(first = parse[1], second = parse[3])

    def p_expression_with_parenthesis(self, parse):
        '''
        expression : LPAREN expression RPAREN
        '''
        parse[0] = parse[2]

    def p_expression_if_conditional(self, parse):
        '''
        expression : IF expression THEN expression ELSE expression FI
        '''
        parse[0] = AST.If(predicate = parse[2], then_body = parse[4], else_body = parse[6])

    def p_expression_while_loop(self, parse):
        '''
        expression : WHILE expression LOOP expression POOL
        '''
        parse[0] = AST.WhileLoop(predicate = parse[2], body = parse[4])

    def p_expression_let(self, parse):
        '''
         expression : let_expression
        '''
        parse[0] = parse[1]

    def p_expression_let_simple(self, parse):
        '''
        let_expression : LET ID COLON TYPE IN expression
                       | nested_lets COMMA LET ID COLON TYPE
        '''
        parse[0] = AST.Let(instance = parse[2], return_type = parse[4], expression = None, body = parse[6])

    def p_expression_let_initialized(self, parse):
        '''
        let_expression : LET ID COLON TYPE ASSIGN expression IN expression
                       | nested_lets COMMA LET ID COLON TYPE ASSIGN expression
        '''
        parse[0] = AST.Let(instance = parse[2], return_type = parse[4], expression = parse[6], body = parse[8])

    def p_inner_lets_simple(self, parse):
        '''
        nested_lets : ID COLON TYPE IN expression
                    | nested_lets COMMA ID COLON TYPE
        '''
        parse[0] = AST.Let(instance = parse[1], return_type = parse[3], expression = None, body = parse[5])

    def p_inner_lets_initialized(self, parse):
        '''
        nested_lets : ID COLON TYPE ASSIGN expression IN expression
                    | nested_lets COMMA ID COLON TYPE ASSIGN expression
        '''
        parse[0] = AST.Let(instance = parse[1], return_type = parse[3], expression = parse[5], body = parse[7])

    def p_expression_case(self, parse):
        '''
        expression : CASE expression OF actions_list ESAC
        '''
        parse[0] = AST.Case(expression = parse[2], actions = parse[4])

    def p_actions_list(self, parse):
        '''
        actions_list : actions_list action
                     | action
        '''
        if len(parse) == 2:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[2],)

    def p_action_expr(self, parse):
        '''
        action : ID COLON TYPE ACTION expression SEMICOLON
        '''
        parse[0] = (parse[1], parse[3], parse[5])

    def p_expression_new(self, parse):
        '''
        expression : NEW TYPE
        '''
        parse[0] = AST.NewObject(parse[2])

    def p_expression_isvoid(self, parse):
        '''
        expression : ISVOID expression
        '''
        parse[0] = AST.IsVoid(parse[2])

    def p_expression_integer_complement(self, parse):
        '''
        expression : INT_COMP expression
        '''
        parse[0] = AST.IntegerComplement(parse[2])

    def p_expression_boolean_complement(self, parse):
        '''
        expression : NOT expression
        '''
        parse[0] = AST.BooleanComplement(parse[2])

    def p_empty(self, parse):
        '''
        empty :
        '''
        parse[0] = None

    def p_error(self, parse):
        '''
        Error rule for Syntax Errors handling and reporting.
        '''
        if parse is None:
            print('Error! Unexpected end of input!')
        else:
            error = f'Syntax error! Line: {parse.lineno}, position: {parse.lexpos}, character: {parse.value}, type: {parse.type}'
            self.error_list.append(error)
            self.parser.errok()

    def build(self, **kwargs):
        if kwargs is None or len(kwargs) == 0:
            debug           = self._debug  
            write_tables    = self._write_tables
            optimize        = self._optimize
            outputdir       = self._outputdir
            yacctab         = self._yacctab
            debuglog        = self._debuglog
            errorlog        = self._errorlog
        else:
            debug           = kwargs.get('debug', self._debug)
            write_tables    = kwargs.get('write_tables', self._write_tables)
            optimize        = kwargs.get('optimize', self._optimize)
            outputdir       = kwargs.get('outputdir', self._outputdir)
            yacctab         = kwargs.get('yacctab', self._yacctab)
            debuglog        = kwargs.get('debuglog', self._debuglog)
            errorlog        = kwargs.get('errorlog', self._errorlog)

        self.lexer = CoolPyLexer(debug       = debug, 
                                optimize    = optimize, 
                                outputdir   = outputdir, 
                                debuglog    = debuglog,
                                errorlog    = errorlog)

        self.tokens = self.lexer.tokens

        self.parser = yacc.yacc(module          = self, 
                                write_tables    = write_tables, 
                                debug           = debug, 
                                optimize        = optimize,
                                outputdir       = outputdir, 
                                tabmodule       = yacctab, 
                                debuglog        = debuglog, 
                                errorlog        = errorlog)

    def parse(self, program_source_code: str) -> AST.Program:
        if self.parser is None:
            raise ValueError('Parser was not build, try building it first with the build() method.')

        return self.parser.parse(program_source_code)

if __name__ == '__main__':
    import sys

    parser = CoolPyParser(build_parser = True)

    if len(sys.argv) > 1:
        if not str(sys.argv[1]).endswith('.cl'):
            print('Source code files must end with .cl extension.')
            print('Usage: ./parser.py program.cl')
            exit()

        input_file = sys.argv[1]
        with open(input_file, 'r') as file:
            cool_program_code = file.read()

        parse_result = parser.parse(cool_program_code)

        from helpers import print_readable_ast

        print_readable_ast(parse_result)
    else:
        print('coolpy Parser: Interactive Mode.\r\n')
        while True:
            try:
                s = input('cool >>> ')
            except EOFError:
                break
            if not s:
                continue
            result = parser.parse(s)
            if result is not None:
                print(result)