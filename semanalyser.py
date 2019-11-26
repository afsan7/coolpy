UNBOXED_PRIMITIVE_VALUE_TYPE = "__prim_slot"
IO_CLASS = "IO"
OBJECT_CLASS = "Object"
INTEGER_CLASS = "Int"
BOOLEAN_CLASS = "Bool"
STRING_CLASS = "String"




class SemanticAnalysisError(Exception):
    pass


class SemanticAnalysisWarning(Warning):
    pass



class PyCoolSemanticAnalyser(object):
    def __init__(self):
        
        
        super(PyCoolSemanticAnalyser, self).__init__()
        
        # Initialize the internal program ast instance.
        self._program_ast = None

        
        self._classes_map = dict()

      
        self._inheritance_graph = defaultdict(set)
    
    def transform(self, program_ast: AST.Program) -> AST.Program:
    
        if program_ast is None:
            raise ValueError("Program AST object cannot be None!")
        elif not isinstance(program_ast, AST.Program):
            raise TypeError("Program AST object is not of type \"AST.Program\"!")
        
        self._init_collections(program_ast)

        # Run some passes
        self._default_undefined_parent_classes_to_object()
        self._invalidate_inheritance_from_builtin_classes()
        self._check_cyclic_inheritance_relations()
        
        return self._program_ast
    
   

if __name__ == '__main__':
    import sys
    from parser import make_parser
    from helpers import print_readable_ast

    if len(sys.argv) != 2:
        print("Usage: ./semanalyser.py program.cl")
        exit()
    elif not str(sys.argv[1]).endswith(".cl"):
        print("Cool program source code files must end with .cl extension.")
        print("Usage: ./semanalyser.py program.cl")
        exit()

    input_file = sys.argv[1]
    with open(input_file, encoding="utf-8") as file:
        cool_program_code = file.read()

   