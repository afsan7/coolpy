from ply import lex

class CoolPyLexer():
    '''
    CoolPyLexer provides methods to tokenize the input Cool source code.
    
    ...
    
    Attributes
    ----------
    lexer : Lexer
        An instance of Lexer used to access all the public methods of Lexer.
    reserved : dict
        A dictionary of the reserved keywords of the Cool programming language.
    tokens : list
        A list of syntax tokens of the Cool programming language.
    last_token : 
        The last token returned when iterated over an instance of PyCoolLexer (after tokenization).  
    build_lexer : bool
        A flag to determine whether the lexer should be built upon initialization or not.
    _debug : bool
        A flag to determine whether 'debug' mode should be on or not.
    _optimize : bool
        A flag to determine whether 'optimize' mode should be on or not.
    _outputdir : str
        Output directory for the lexer's output.
    _debuglog : str
        Path to the lexer's debug log.
    _errorlog : str
        Path to the lexer's error log.

    Methods
    -------
    build(**kwargs)
        Builds the CoolPyLexer instance with lex.lex().
    input(source_code)
        A wrapper for Lexer's input(source_code: str) method. Tokenizes the Cool program 
        provided as the input.
    '''

    def __init__(self,
                 build_lexer = True,
                 debug       = False,
                 lextab      = 'coolpy.lextab',
                 optimize    = True,
                 outputdir   = '',
                 debuglog    = None,
                 errorlog    = None):
        '''
        Paramters
        ---------
        build_lexer : bool, optional
            A flag to determine whether the lexer should be built upon initialization or not.
        debug : bool, optional
            A flag to determine whether 'debug' mode should be on or not.
        optimize : bool, optional
            A flag to determine whether 'optimize' mode should be on or not.
        outputdir : str, optional
            Output directory for the lexer's output.
        debuglog : str, optional
            Path to the lexer's debug log. By default, the lexer logs to stderr.
        errorlog : str, optional
            Path to the lexer's error log. By default, the lexer logs to stderr.
        '''

        self.lexer = None

        # Dictionary of reserved keywords of the Cool programming language.
        self.reserved = {
            'class': 'CLASS',
            'inherits': 'INHERITS',
            'if': 'IF',
            'in': 'IN',
            'then': 'THEN',
            'else': 'ELSE',
            'fi': 'FI',
            'while': 'WHILE',
            'loop': 'LOOP',
            'pool': 'POOL',
            'let': 'LET',
            'in': 'IN',
            'case': 'CASE',
            'of': 'OF',
            'esac': 'ESAC',
            'new': 'NEW',
            'self': 'SELF',
            'isvoid': 'ISVOID',
        }

        # List of token names.
        self.tokens = [
            'TYPE', 'ID',
            'INTEGER', 'STRING', 'BOOLEAN',
            'ACTION',
            'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COLON', 'COMMA', 'DOT', 'SEMICOLON', 'AT',
            'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'EQ', 'LT', 'LTEQ', 'ASSIGN', 'INT_COMP', 'NOT',
        ] + list(self.reserved.values())

        self.last_token = None

        self._debug     = debug
        self._lextab    = lextab
        self._optimize  = optimize
        self._outputdir = outputdir
        self._debuglog  = debuglog
        self._errorlog  = errorlog

        if build_lexer is True:
            self.build(debug     = debug, 
                       lextab    = lextab, 
                       optimize  = optimize, 
                       outputdir = outputdir, 
                       debuglog  = debuglog,
                       errorlog  = errorlog)
    
    # Regular expression rules for simple tokens.
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_COLON = r'\:'
    t_COMMA = r'\,'
    t_DOT = r'\.'
    t_SEMICOLON = r'\;'
    t_AT = r'\@'
    t_MULTIPLY = r'\*'
    t_DIVIDE = r'\/'
    t_PLUS = r'\+'
    t_MINUS = r'\-'
    t_INT_COMP = r'~'
    t_LT = r'\<'
    t_EQ = r'\='
    t_LTEQ = r'\<\='
    t_ASSIGN = r'\<\-'
    t_ACTION = r'\=\>'

    # Regular expression rules with some action code.
    def t_INTEGER(self, token):
        r'[0-9]+'
        token.value = int(token.value)
        return token

    def t_STRING(self, token):
        r'"[^"]*"'
        token.value = token.value[1:-1]
        return token

    def t_BOOLEAN(self, token):
        r'true|false'
        token.value = True if token.value == 'true' else False
        return token
    
    def t_SINGLE_LINE_COMMENT(self, token):
        r'\-\-[^\n]*'
        pass

    def t_NOT(self, token):
        r'[nN][oO][tT]'
        return token

    def t_TYPE(self, token):
        r'[A-Z][A-Za-z0-9_]*'
        return token

    # ID ~ Identifier
    def t_ID(self, token):
        r'[a-z][A-Za-z0-9_]*'
        token.type = self.reserved.get(token.value.lower(), 'ID')
        return token
    
    def t_newline(self, token):
        r'\n+'
        token.lexer.lineno += len(token.value)

    # Handling multi-line comments using states.
    @property
    def states(self):
        return (
            ('COMMENT', 'exclusive'),
        )

    def t_start_comment(self, token):
        r'\(\*'
        token.lexer.push_state('COMMENT')
        token.lexer.comment_count = 0

    def t_COMMENT_startanother(self, token):
        r'\(\*'
        token.lexer.comment_count += 1

    def t_COMMENT_newline(self, token):
        r'\n+'
        token.lexer.lineno += len(token.value)

    def t_COMMENT_end(self, token):
        r'\*\)'
        if token.lexer.comment_count == 0:
            token.lexer.pop_state()
        else:
            token.lexer.comment_count -= 1

    def t_COMMENT_error(self, token):
        token.lexer.skip(1)

    t_COMMENT_ignore = ''

    def t_error(self, token):
        print(f'Illegal character! Line: {token.lineno}, character: {token.value[0]}')
        token.lexer.skip(1)

    t_ignore = ''.join([' ', '\t'])

    def build(self, **kwargs):
        '''Builds the CoolPyLexer instance with lex.lex().

        Paramters
        ---------
        debug : bool, optional
            A flag to determine whether 'debug' mode should be on or not.
        optimize : bool, optional
            A flag to determine whether 'optimize' mode should be on or not.
        outputdir : str, optional
            Output directory for the lexer's output.
        debuglog : str, optional
            Path to the lexer's debug log. By default, the lexer logs to stderr.
        errorlog : str, optional
            Path to the lexer's error log. By default, the lexer logs to stderr.
        '''
        if kwargs is None or len(kwargs) == 0:
            debug       = self._debug
            lextab      = self._lextab 
            optimize    = self._optimize 
            outputdir   = self._outputdir 
            debuglog    = self._debuglog
            errorlog    = self._errorlog
        else:
            debug       = kwargs.get('debug', self._debug)
            lextab      = kwargs.get('lextab', self._lextab)
            optimize    = kwargs.get('optimize', self._optimize)
            outputdir   = kwargs.get('outputdir', self._outputdir)
            debuglog    = kwargs.get('debuglog', self._debuglog)
            errorlog    = kwargs.get('errorlog', self._errorlog)
    
        self.lexer = lex.lex(module     = self, 
                             lextab     = lextab, 
                             debug      = debug, 
                             optimize   = optimize, 
                             outputdir  = outputdir,
                             debuglog   = debuglog, 
                             errorlog   = errorlog)

    def input(self, source_code: str):
        '''A wrapper for Lexer's input(source_code: str) method. Tokenizes Cool program 
        provided as the input.

        Parameters
        ----------
        source_code : str
            The Cool program to be tokenized (as a string).
        '''
        if self.lexer is None:
            raise Exception('Lexer was not built. Try building the lexer with the build() method.')
        self.lexer.input(source_code)

    def token(self):
        if self.lexer is None:
            raise Exception('Lexer was not built. Try building the lexer with the build() method.')
        self.last_token = self.lexer.token()
        return self.last_token

    def __iter__(self):
        return self

    def __next__(self):
        t = self.token()
        
        if t is None:
            raise StopIteration
        
        return t

    def next(self):
        return self.__next__()


if __name__ == '__main__':

    import sys
    if len(sys.argv) != 2:
        print('Usage: python lexer.py program.cl')
        exit()
    elif not str(sys.argv[1]).endswith('.cl'):
        print('Source code files must end with .cl extension.')
        print('Usage: python lexer.py program.cl')
        exit()

    input_file = sys.argv[1]
    with open(input_file, 'r') as file:
        source_code = file.read()
    
    lexer = CoolPyLexer()
    lexer.input(source_code)
    for token in lexer:
        print(token)
