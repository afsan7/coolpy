from ply import yacc

import ast as AST
from lexer import CoolPyLexer

class CoolPyParser:
    '''
    CoolPyParser provides methods to parse the input Cool source code and create an AST.
    
    ...
    
    Attributes
    ----------
    parser : LRParser
        An instance of LRParser used to access all the public methods of LRParser.
    lexer : Lexer
        An instance of Lexer used to access all the public methods of Lexer.
    tokens : list
        A list of syntax tokens of the Cool programming language.  
    build_parser : bool
        A flag to determine whether the parser should be built upon initialization or not.
    _debug : bool
        A flag to determine whether 'debug' mode should be on or not.
    _optimize : bool
        A flag to determine whether 'optimize' mode should be on or not.
    _outputdir : str
        Output directory for the parser's output.
    _debuglog : str
        Path to the parser's debug log.
    _errorlog : str
        Path to the parser's error log.

    Methods
    -------
    build(**kwargs)
        Builds the CoolPyParser instance with yacc.yacc().
    parse(source_code) 
        Parses the Cool program provided as the input.
    '''

    def __init__(self,
                 build_parser   = True,
                 debug          = False,
                 write_tables   = True,
                 optimize       = True,
                 outputdir      = '',
                 yacctab        = 'pycoolc.yacctab',
                 debuglog       = None,
                 errorlog       = None):
        '''
        PARAMETERS
        ----------
        build_parser : bool
            A flag to determine whether the parser should be built upon initialization or not.
        _debug : bool
            A flag to determine whether 'debug' mode should be on or not.
        _optimize : bool
            A flag to determine whether 'optimize' mode should be on or not.
        _outputdir : str
            Output directory for the parser's output.
        _debuglog : str
            Path to the parser's debug log.
        _errorlog : str
            Path to the parser's error log.
        '''

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

    # Define precedence and associativity of different operators in the Cool programming language.
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

    # A single Cool program can consist of multiple classes.
    # Hence, the production rule: 
    #   program -> class_list
    def p_program(self, parse):
        '''
        program : class_list
        '''
        parse[0] = AST.Program(classes = parse[1])


    # A single Cool program can consist of one or more classes, with each 
    # class definition ending with a semicolon (;).
    # Hence, the production rules:
    #   class_list -> class_list class ;
    #   class_list -> class ;
    def p_class_list(self, parse):
        '''
        class_list : class_list class SEMICOLON
                   | class SEMICOLON
        '''
        if len(parse) == 3:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[2],)


    # A class definition in Cool is of the form - 
    #   
    #   class <type> [ inherits <type> ] {
    #       <feature_list>
    #   };
    # 
    # The notation [ ...] denotes an optional construct.
    #
    # Hence, the production rule(s):
    #   class -> CLASS TYPE { features_list_optional }
    #   class -> CLASS TYPE INHERITS TYPE { features_list_optional }
    # 
    # The second production rule has been defined in a separate function.
    # Also, since we used ; (SEMICOLON) in the previous production rule, we are not using it in this case.
    def p_class(self, parse):
        '''
        class : CLASS TYPE LBRACE features_list_optional RBRACE
        '''
        parse[0] = AST.Class(name = parse[2], parent = 'Object', features = parse[4])

    def p_class_inherits(self, parse):
        '''
        class : CLASS TYPE INHERITS TYPE LBRACE features_list_optional RBRACE
        '''
        parse[0] = AST.Class(name = parse[2], parent = parse[4], features = parse[6])


    # The body of a class definition consists of a list of feature definitions. 
    # A feature is either an attribute or a method.
    def p_features_list_optional(self, parse):
        '''
        features_list_optional : features_list
                               | empty
        '''
        parse[0] = tuple() if parse.slice[1].type == 'empty' else parse[1]


    # Each feature is separated by a semicolon (;).
    # Hence, the production rule:
    #   features_list -> features_list feature ;
    #   features_list -> feature ;
    def p_features_list(self, parse):
        '''
        features_list : features_list feature SEMICOLON
                      | feature SEMICOLON
        '''
        if len(parse) == 3:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[2],)


    # A feature in Cool can be either a class method or an attribute.
    # A method defination is of the form - 
    #   
    #   <method_name>( <formal_paramters_list> ) : <return_type> { expression(s) }
    #   
    #   Example:    
    #   init(hd : Int, tl : List) : Cons {
    #       {
    #           xcar <- hd;
    #           xcdr <- tl;
    #           self;
    #       }
    #   }
    # 
    # Hence, the production rule:
    #   feature -> ID ( formal_paramters_list ) : TYPE { expression } 
    #
    def p_feature_method(self, parse):
        '''
        feature : ID LPAREN formal_parameters_list RPAREN COLON TYPE LBRACE expression RBRACE
        '''
        parse[0] = AST.Method(name = parse[1], formal_parameters = parse[3], return_type = parse[6], body = parse[8])

    
    # A method defination with no parameters is also valid!
    def p_feature_method_no_formal_paramters(self, parse):
        '''
        feature : ID LPAREN RPAREN COLON TYPE LBRACE expression RBRACE
        '''
        parse[0] = AST.Method(name = parse[1], formal_parameters = tuple(), return_type = parse[5], body = parse[7])


    # A feature in Cool can be either a class method or an attribute.
    # An attribute declaration is of the form -
    #   
    #   <attribute_name> : <type> [ <- <expression>]
    #
    # Example:
    #   number : Int <- 124
    #
    # The notation [ ...] denotes an optional construct.
    # Hence, the production rule:
    #   feature -> ID : TYPE <- expression
    def p_feature_attribute_initialized(self, parse):
        '''
        feature : ID COLON TYPE ASSIGN expression
        '''
        parse[0] = AST.Attribute(name = parse[1], attribute_type = parse[3], expression = parse[5])


    # Since, the initialization part of an attribute declaration is optional, the following production
    # rule is also valid:
    #   feature -> ID : TYPE 
    #
    # Example:
    #   number : Int
    def p_feature_attribute(self, parse):
        '''
        feature : ID COLON TYPE
        '''
        parse[0] = AST.Attribute(name = parse[1], attribute_type = parse[3], expression = None)


    # A formal parameters list (method arguments) consists of comma-separated paramter.
    # Hence, the production rule:
    #   formal_parameters_list -> formal_parameters_list, formal_parameter
    #   formal_parameters_list -> formal_paramter
    def p_formal_paramters_list(self, parse):
        '''
        formal_parameters_list  : formal_parameters_list COMMA formal_parameter
                                | formal_parameter
        '''
        if len(parse) == 2:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[3],)


    # A formal paramter is of the form:
    #   <paramter_name> : <parameter_type>
    #
    # Example:
    #   a: Int
    # Hence, the production rule:
    #   formal_parameter -> ID : TYPE
    def p_formal_paramter(self, parse):
        '''
        formal_parameter : ID COLON TYPE
        '''
        parse[0] = AST.FormalParameter(name = parse[1], parameter_type = parse[3])


    # An expression in Cool can consist of just an identifier.
    # Hence, the production rule:
    #   expression -> ID
    def p_expression_object_identifier(self, parse):
        '''
        expression : ID
        '''
        parse[0] = AST.Object(name = parse[1])


    # An expression in Cool can consist of just an integer.
    # Hence, the production rule:
    #   expression -> INTEGER
    def p_expression_integer_constant(self, parse):
        '''
        expression : INTEGER
        '''
        parse[0] = AST.Integer(content = parse[1])


    # An expression in Cool can consist of just an boolean.
    # Hence, the production rule:
    #   expression -> BOOLEAN
    def p_expression_boolean_constant(self, parse):
        '''
        expression : BOOLEAN
        '''
        parse[0] = AST.Boolean(content = parse[1])


    # An expression in Cool can consist of just an string.
    # Hence, the production rule:
    #   expression -> STRING
    def p_expression_string_constant(self, parse):
        '''
        expression : STRING
        '''
        parse[0] = AST.String(content = parse[1])


    # An expression in Cool can consist of just SELF_TYPE.
    # Hence, the production rule:
    #   expression -> SELF
    def p_expression_self(self, parse):
        '''
        expression  : SELF
        '''
        parse[0] = AST.Self(name = 'SELF')


    # An expression in Cool can consist of a code block. A code block in Cool is a set of 
    # statements/expressions enclosed between curly braces.
    # Hence, the production rule:
    #   expression -> { block_list }
    def p_expression_block(self, parse):
        '''
        expression : LBRACE block_list RBRACE
        '''
        parse[0] = AST.Block(expression_list = parse[2])


    # A code block can consists of several code blocks.
    # Hence, the production rules:
    #   block_list -> block_list expression ;
    #   block_list -> expression ;
    #
    # Note: Semi-colons are used as terminators in lists of expressions (e.g., the block syntax above) 
    # and not as expression separators.
    def p_block_list(self, parse):
        '''
        block_list : block_list expression SEMICOLON
                   | expression SEMICOLON
        '''
        if len(parse) == 3:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[2],)

    
    # An expression can also be assignment expression.
    def p_expression_assignment(self, parse):
        '''
        expression : ID ASSIGN expression
        '''
        parse[0] = AST.Assignment(AST.Object(name = parse[1]), expression = parse[3])


    # An expression can also be method call on an object.
    #   <object>.<method_name>(argument_list_optional)
    #
    # Hence, the production rule:
    #   expression -> expression.ID(argument_list_optional)
    def p_expression_dispatch(self, parse):
        '''
        expression : expression DOT ID LPAREN arguments_list_optional RPAREN
        '''
        parse[0] = AST.DynamicDispatch(instance = parse[1], method = parse[3], arguments = parse[5])

    
    # The argument list can also be empty in a method call!
    def p_arguments_list_optional(self, parse):
        '''
        arguments_list_optional : arguments_list
                                | empty
        '''
        parse[0] = tuple() if parse.slice[1].type == 'empty' else parse[1]

    # The argument list can consist of multiple comma-separated expressions.
    # Hence, the production rules:
    #   argument_list -> argument_list, expression
    #   argument_list -> expression
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
        expression : expression AT TYPE DOT ID LPAREN arguments_list_optional RPAREN
        '''
        parse[0] = AST.StaticDispatch(instance = parse[1], dispatch_type = parse[3], method = parse[5], arguments = parse[7])


    # A class method can also be invoked without the use of any object.
    # A common scenario - method is called from inside of another class method.
    def p_expression_self_dispatch(self, parse):
        '''
        expression : ID LPAREN arguments_list_optional RPAREN
        '''
        parse[0] = AST.DynamicDispatch(instance = AST.Self('SELF'), method = parse[1], arguments = parse[3])


    # An expression may consists of arithmetic expressions.
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


    # An expression may consists of comparision expression.
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

    
    # An expression may be enclosed within paranthesis (in order to define precedence).
    # Hence, the production rule:
    #   expression -> (expression)
    def p_expression_with_parenthesis(self, parse):
        '''
        expression : LPAREN expression RPAREN
        '''
        parse[0] = parse[2]


    # An if statement in Cool has the following construct - 
    #
    #   if <condition> then {
    #       <statment>;
    #       <statment>;
    #       <statment>; 
    #       . 
    #       .
    #   } else {
    #       <statment>;
    #       <statment>;
    #       <statment>; 
    #       . 
    #       .
    #   } fi
    # 
    # '{}' can be omitted if the there is only a single statement following 'then' or 'else'.
    # Hence, the production rule:
    #   expression -> IF expression THEN expression ELSE expression FI
    #
    # Note: expression -> { block_list } have been defined earlier. So, if the 'if' or 'else' block
    # has more than one statment, the aforementioned production rule will be used.
    # Also, expression can also be reduced to conditional expression. A production rule for doing so has
    # been defined before.
    def p_expression_if_conditional(self, parse):
        '''
        expression : IF expression THEN expression ELSE expression FI
        '''
        parse[0] = AST.If(predicate = parse[2], then_body = parse[4], else_body = parse[6])


    # A while loop in Cool has the following construct - 
    #   
    #   while <condition> LOOP {
    #       <statment>;
    #       <statment>;
    #       <statment>; 
    #       . 
    #       .
    #   } POOL
    #
    # Hence, the production rule:
    #   expression -> WHILE expression LOOP expression POOL
    def p_expression_while_loop(self, parse):
        '''
        expression : WHILE expression LOOP expression POOL
        '''
        parse[0] = AST.WhileLoop(predicate = parse[2], body = parse[4])

    
    # An expression can also be a let expression in Cool.
    # A let expression is of the form - 
    #   let <id1> : <type1> [ <- <expr1> ], ..., <idn> : <typen> [ <- <exprn> ] in <expr>
    # 
    # The optional expressions (inside []) are initialization; the other expression is the body. 
    # A let is evaluated as follows. 
    # First <expr1> is evaluated and the result bound to <id1>. Then <expr2> is evaluated and the
    # result bound to <id2>, and so on, until all of the variables in the let are initialized. 
    # (If the initialization of <idk> is omitted, the default initialization of type <typek> is used.) 
    # Next the body of the let is evaluated. The value of the let is the value of the body.
    # 
    # The let identifiers <id1>,...,<idn> are visible in the body of the let. Furthermore, identifiers
    # <id1>,...,<idk> are visible in the initialization of <idm> for any m > k.
    # If an identifier is defined multiple times in a let, later bindings hide earlier ones. 
    # 
    # Identifiers introduced by let also hide any definitions for the same names in containing scopes. 
    # Every let expression must introduce at least one identifier.
    # The type of an initialization expression must conform to the declared type of the identifier. 
    # The type of let is the type of the body.
    # 
    # The following five functions define the production rules for the above construct.
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

    
    # A case expression has the form -
    #   case <expr0> of
    #       <id1> : <type1> => <expr1>;
    #       . . .
    #       <idn> : <typen> => <exprn>;
    #   esac
    #
    # Case expressions provide runtime type tests on objects. 
    # First, expr0 is evaluated and its dynamic type C noted (if expr0 evaluates to void a run-time error is produced). 
    # Next, from among the branches the branch with the least type <typek> such that C ≤ <typek> is selected. 
    # The identifier <idk> is bound to the value of <expr0> and the expression <exprk> is evaluated. 
    # The result of the case is the value of <exprk>. 
    # If no branch can be selected for evaluation, a run-time error is generated. 
    # Every case expression must have at least one branch.
    #
    # The following three functions define the production rules for the above construct.
    def p_expression_case(self, parse):
        '''
        expression : CASE expression OF actions_list ESAC
        '''
        parse[0] = AST.Case(expression = parse[2], actions = parse[4])

    
    # A case expression can consist of multiple actions (or cases). 
    # Hence, the production rules:
    #   actions_list -> actions_list action
    #   actions_list -> action
    def p_actions_list(self, parse):
        '''
        actions_list : actions_list action
                     | action
        '''
        if len(parse) == 2:
            parse[0] = (parse[1],)
        else:
            parse[0] = parse[1] + (parse[2],)


    # An action expression of a Cool case expression is of the form (as can be seen in the example above) -
    #   <identifier> : <type> => <expression>;
    #
    # Hence, the production rule:
    #   action -> ID : TYPE => expression;
    def p_action_expression(self, parse):
        '''
        action : ID COLON TYPE ACTION expression SEMICOLON
        '''
        parse[0] = (parse[1], parse[3], parse[5])


    # A new expression has the form -
    #   new <type>
    # 
    # The value is a fresh object of the appropriate class. 
    # If the type is SELF TYPE, then the value is a fresh object of the class of self in the current scope. 
    def p_expression_new(self, parse):
        '''
        expression : NEW TYPE
        '''
        parse[0] = AST.NewObject(parse[2])


    # The expression
    #   isvoid expression
    # 
    # evaluates to true if expression is void and evaluates to false if expression is not void.
    def p_expression_isvoid(self, parse):
        '''
        expression : ISVOID expression
        '''
        parse[0] = AST.IsVoid(parse[2])

    
    # A complement of an Int in Cool can be evaluated using the ~ operator.
    # Hence, the production rule:
    #   expression -> ~expression
    def p_expression_integer_complement(self, parse):
        '''
        expression : INT_COMP expression
        '''
        parse[0] = AST.IntegerComplement(parse[2])


    # A complement of a Bool in Cool can be evaluated using the not/NOT operator.
    # Hence, the production rule:
    #   expression -> not expression
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
        '''
        Builds the CoolPyParser instance with yacc.yacc().
        '''

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
        '''
        Parses the Cool program provided as the input.
        Returns the AST formed as a result of the parsing.
        '''

        if self.parser is None:
            raise ValueError('Parser was not build, try building it first with the build() method.')

        return self.parser.parse(program_source_code)

if __name__ == '__main__':
    import sys

    parser = CoolPyParser(build_parser = True)

    if len(sys.argv) > 1:
        if not str(sys.argv[1]).endswith('.cl'):
            print('Source code files must end with .cl extension.')
            print('Usage: python parser.py <file_name.cl>')
            exit()

        input_file = sys.argv[1]
        with open(input_file, 'r') as file:
            cool_program_code = file.read()

        parse_result = parser.parse(cool_program_code)

        from helpers import print_readable_ast

        print_readable_ast(parse_result)
    else:
        print('Provide the path to the Cool program source file.')
        print('Usage: python parser.py <file_name.cl>')
        exit()
