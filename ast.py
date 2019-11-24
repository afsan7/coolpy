class AST:
    def __init__(self):
        pass

    @property
    def class_name(self):
        return str(self.__class__.__name__)

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name)
        ])

    def to_readable(self):
        return f'{self.class_name}'

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.to_readable())


class Program(AST):
    def __init__(self, classes):
        super(Program, self).__init__()
        self.classes = classes

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name), 
            ('classes', self.classes)
        ])

    def to_readable(self):
        return f'{self.class_name}(classes={self.classes})'


class Class(AST):
    def __init__(self, name, parent, features):
        super(Class, self).__init__()
        self.name = name
        self.parent = parent
        self.features = features

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('name', self.name),
            ('parent', self.parent), 
            ('features', self.features)
        ])

    def to_readable(self):
        return f'{self.class_name}(name=\'{self.name}\', parent={self.parent}, features={self.features})'


class Method(AST):
    def __init__(self, name, formal_parameters, return_type, body):
        super(Method, self).__init__()
        self.name = name
        self.formal_parameters = formal_parameters
        self.return_type = return_type
        self.body = body

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('name', self.name),
            ('formal_params', self.formal_parameters),
            ('return_type', self.return_type),
            ('body', self.body)
        ])

    def to_readable(self):
        return f'{self.class_name}(name=\'{self.name}\', formal_parameters={self.formal_parameters}, return_type={self.return_type}, body={self.body})'


class Attribute(AST):
    def __init__(self, name, attribute_type, expression):
        super(Attribute, self).__init__()
        self.name = name
        self.attribute_type = attribute_type
        self.expression = expression

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('name', self.name),
            ('attribute_type', self.attribute_type),
            ('expression', self.expression)  
        ])

    def to_readable(self):
        return f'{self.class_name}(name=\'{self.name}\', attribute_type={self.attribute_type}, expression={self.expression})'

class FormalParameter(AST):
    def __init__(self, name, parameter_type):
        super(FormalParameter, self).__init__()
        self.name = name
        self.parameter_type = parameter_type

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('name', self.name),
            ('parameter_type', self.parameter_type)
        ])

    def to_readable(self):
        return f'{self.class_name}(name=\'{self.name}\', type={self.type})'


class Object(AST):
    def __init__(self, name):
        super(Object, self).__init__()
        self.name = name

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('name', self.name)
        ])

    def to_readable(self):
        return f'{self.class_name}(name=\'{self.name}\')'


class Self(AST):
    def __init__(self, name):
        super(Self, self).__init__()
        self.name = name

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('name', self.name)
        ])

    def to_readable(self):
        return f'{self.class_name}(name=\'{self.name}\')'


class Integer(AST):
    def __init__(self, content):
        super(Integer, self).__init__()
        self.content = content

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('content', self.content)
        ])

    def to_readable(self):
        return f'{self.class_name}(content={self.content})'


class String(AST):
    def __init__(self, content):
        super(String, self).__init__()
        self.content = content

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('content', self.content)
        ])

    def to_readable(self):
        return f'{self.class_name}(content={self.content})'

class Boolean(AST):
    def __init__(self, content):
        super(Boolean, self).__init__()
        self.content = content

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('content', self.content)
        ])

    def to_readable(self):
        return f'{self.class_name}(content={self.content})'


class NewObject(AST):
    def __init__(self, new_type):
        super(NewObject, self).__init__()
        self.type = new_type

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('type', self.type)
        ])

    def to_readable(self):
        return f'{self.class_name}(type={self.type})'


class IsVoid(AST):
    def __init__(self, expression):
        super(IsVoid, self).__init__()
        self.expression = expression

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('expression', self.expression)
        ])

    def to_readable(self):
        return f'{self.class_name}(expression={self.expression})'


class Assignment(AST):
    def __init__(self, instance, expression):
        super(Assignment, self).__init__()
        self.instance = instance
        self.expression = expression

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('instance', self.instance),
            ('expression', self.expression)
        ])

    def to_readable(self):
        return f'{self.class_name}(instance={self.instance}, expression={self.expression})'


class Block(AST):
    def __init__(self, expression_list):
        super(Block, self).__init__()
        self.expression_list = expression_list

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('expression_list', self.expression_list)
        ])

    def to_readable(self):
        return f'{self.class_name}(expression_list={self.expression_list})'


class DynamicDispatch(AST):
    def __init__(self, instance, method, arguments):
        super(DynamicDispatch, self).__init__()
        self.instance = instance
        self.method = method
        self.arguments = arguments if arguments is not None else tuple()

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('instance', self.instance),
            ('method', self.method),
            ('arguments', self.arguments)
        ])

    def to_readable(self):
        return f'{self.class_name}(instance={self.instance}, method={self.method}, arguments={self.arguments})'


class StaticDispatch(AST):
    def __init__(self, instance, dispatch_type, method, arguments):
        super(StaticDispatch, self).__init__()
        self.instance = instance
        self.dispatch_type = dispatch_type
        self.method = method
        self.arguments = arguments if arguments is not None else tuple()

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('instance', self.instance),
            ('dispatch_type', self.dispatch_type),
            ('method', self.method),
            ('arguments', self.arguments)
        ])

    def to_readable(self):
        return f'{self.class_name}(instance={self.instance}, dispatch_type={self.dispatch_type}, method={self.method}, arguments={self.arguments})'


class Let(AST):
    def __init__(self, instance, return_type, expression, body):
        super(Let, self).__init__()
        self.instance = instance
        self.return_type = return_type
        self.expression = expression
        self.body = body

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('instance', self.instance),
            ('return_type', self.return_type),
            ('expression', self.expression),
            ('body', self.body)
        ])

    def to_readable(self):
        return f'{self.class_name}(instance={self.instance}, return_type={self.return_type}, expression={self.expression}, body={self.body})'


class If(AST):
    def __init__(self, predicate, then_body, else_body):
        super(If, self).__init__()
        self.predicate = predicate
        self.then_body = then_body
        self.else_body = else_body

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('predicate', self.predicate),
            ('then_body', self.then_body),
            ('else_body', self.else_body)
        ])

    def to_readable(self):
        return f'{self.class_name}(predicate={self.predicate}, then_body={self.then_body}, else_body={self.else_body})'


class WhileLoop(AST):
    def __init__(self, predicate, body):
        super(WhileLoop, self).__init__()
        self.predicate = predicate
        self.body = body

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('predicate', self.predicate),
            ('body', self.body)
        ])

    def to_readable(self):
        return f'{self.class_name}(predicate={self.predicate}, body={self.body})'


class Case(AST):
    def __init__(self, expression, actions):
        super(Case, self).__init__()
        self.expression = expression
        self.actions = actions

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('expression', self.expression),
            ('actions', self.actions)
        ])

    def to_readable(self):
        return f'{self.class_name}(expression={self.expression}, actions={self.actions})'


class Action(AST):
    def __init__(self, name, action_type, body):
        super(Action, self).__init__()
        self.name = name
        self.action_type = action_type
        self.body = body

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('name', self.name),
            ('action_type', self.action_type),
            ('body', self.body)
        ])

    def to_readable(self):
        return f'{self.class_name}(name=\'{self.name}\', action_type={self.action_type}, body={self.body})'


class IntegerComplement(AST):
    def __init__(self, integer_expression):
        super(IntegerComplement, self).__init__()
        self.symbol = '~'
        self.integer_expression = integer_expression

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('integer_expression', self.integer_expression)
        ])

    def to_readable(self):
        return f'{self.class_name}(expression={self.integer_expression})'


class BooleanComplement(AST):
    def __init__(self, boolean_expression):
        super(BooleanComplement, self).__init__()
        self.symbol = '!'
        self.boolean_expression = boolean_expression

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('boolean_expression', self.boolean_expression)
        ])

    def to_readable(self):
        return f'{self.class_name}(expression={self.boolean_expression})'


class Addition(AST):
    def __init__(self, first, second):
        super(Addition, self).__init__()
        self.symbol = '+'
        self.first = first
        self.second = second

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('first', self.first),
            ('second', self.second)
        ])

    def to_readable(self):
        return f'{self.class_name}(first={self.first}, second={self.second})'


class Subtraction(AST):
    def __init__(self, first, second):
        super(Subtraction, self).__init__()
        self.symbol = '-'
        self.first = first
        self.second = second

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('first', self.first),
            ('second', self.second)
        ])

    def to_readable(self):
        return f'{self.class_name}(first={self.first}, second={self.second})'


class Multiplication(AST):
    def __init__(self, first, second):
        super(Multiplication, self).__init__()
        self.symbol = '*'
        self.first = first
        self.second = second

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('first', self.first),
            ('second', self.second)
        ])

    def to_readable(self):
        return f'{self.class_name}(first={self.first}, second={self.second})'


class Division(AST):
    def __init__(self, first, second):
        super(Division, self).__init__()
        self.symbol = '/'
        self.first = first
        self.second = second

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('first', self.first),
            ('second', self.second)
        ])

    def to_readable(self):
        return f'{self.class_name}(first={self.first}, second={self.second})'


class Equal(AST):
    def __init__(self, first, second):
        super(Equal, self).__init__()
        self.symbol = '='
        self.first = first
        self.second = second

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('first', self.first),
            ('second', self.second)
        ])

    def to_readable(self):
        return f'{self.class_name}(first={self.first}, second={self.second})'


class LessThan(AST):
    def __init__(self, first, second):
        super(LessThan, self).__init__()
        self.symbol = '<'
        self.first = first
        self.second = second

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('first', self.first),
            ('second', self.second)
        ])

    def to_readable(self):
        return f'{self.class_name}(first={self.first}, second={self.second})'


class LessThanOrEqual(AST):
    def __init__(self, first, second):
        super(LessThanOrEqual, self).__init__()
        self.symbol = '<='
        self.first = first
        self.second = second

    def to_tuple(self):
        return tuple([
            ('class_name', self.class_name),
            ('first', self.first),
            ('second', self.second)
        ])

    def to_readable(self):
        return f'{self.class_name}(first={self.first}, second={self.second})'
