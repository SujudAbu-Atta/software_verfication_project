import json

conditional_node_type = "conditional"
statement_node_type = "statement"

selection = "selection_statement"
compound = "compound_statement"
block = "block_item_list"
function = "function_definition"
jump = 'jump_statement'


init_exp = 'init_declarator'
assignment_exp = 'assignment_expression'


def CFG_build(current, next_tree):
    assert current is not None and (current['type'] == compound or ends_with_semicolon(current))

    if ends_with_semicolon(current):
        node = {
            "node_type": statement_node_type,
            "is_assignment": is_assignment(current['children'][-2]),
            "node_content": get_content_as_string(current),
            "next": next_tree if current['type'] != jump else None
        }
        return node

    #compound
    for child in reversed(current['children'][1]['children']):
        if child['type'] == ';':
            continue
        # easy - normal statement
        if child['type'] != selection:
            assert ends_with_semicolon(child)
            node = CFG_build(child, next_tree)

        # selection statement
        else:
            # if there are 5 children then IF without ELSE
            assert len(child['children']) == 5 or len(child['children']) == 7
            node = {
                "node_type": conditional_node_type,
                "node_content": get_content_as_string(child['children'][2]),
                "true_next": CFG_build(child['children'][4], next_tree),
                "false_next": CFG_build(child['children'][6], next_tree) if len(child['children']) > 5 else next_tree
            }
        next_tree = node
    return node


def ends_with_semicolon(current):
    return current['children'][-1]['text'] == ';'

'''
R = list of conditions (strings)
T = list of expressions 
'''

def get_TRs(CFG_node, function_node):
    if CFG_node is None:
        return [(get_T(function_node, []), ['True'])]
    if CFG_node['node_type'] == statement_node_type and CFG_node['is_assignment'][0]:
        (left, right) = CFG_node['is_assignment'][1], CFG_node['is_assignment'][2]
        TRs = get_TRs(CFG_node['next'], function_node)
        for (T, R) in TRs:
            T = update(T, left, right)
            R = update(R, left, right)
        return TRs
    if CFG_node['node_type'] == conditional_node_type:
        true_TRs = get_TRs(CFG_node['true_next'], function_node)
        false_TRs = get_TRs(CFG_node['false_next'], function_node)
        for (T, R) in true_TRs:
            R.append(CFG_node['node_content'])
        for (T, R) in false_TRs:
            R.append(' ! (' + CFG_node['node_content'] + ') ')
        return true_TRs + false_TRs

    return get_TRs(CFG_node['next'], function_node)


def update(expArr, left, right):
    for i in range(len(expArr)):
        if left in expArr[i]:
            expArr[i] = expArr[i].replace(left, right)
    return expArr



def get_content_as_string_aux(node, str):
    if node is None:
        return str
    if node['children'] is None:
        return str + node['text'] + ' '

    for child in node['children']:
        str = get_content_as_string_aux(child, str)
    return str

def get_T(func_declaration_AST_node, identifiers):
    if func_declaration_AST_node['children'] is None:
        return identifiers
    for child in func_declaration_AST_node['children']:
        if child['type'] == 'IDENTIFIER' and (' ' + child['text'] + ' ') not in identifiers:
            identifiers.append(' ' + child['text'] + ' ')
        if child['type'] == 'postfix_expression' and (get_content_as_string(child)) not in identifiers:
            identifiers.append(get_content_as_string(child))
        identifiers = get_T(child, identifiers)
    return identifiers

def is_assignment(AST_node):
    if AST_node['type'] != assignment_exp and AST_node['type'] != init_exp:
        return (False, None, None)
    return (True, get_content_as_string(AST_node['children'][0]),
                                        get_content_as_string(AST_node['children'][2]))

def get_content_as_string(node):
    str = get_content_as_string_aux(node, '')
    if str is None or str == '':
        return ''
    if str[0] == '(' and str[-2] == ')':
        return str[1:-2]
    else:
        return ' ' + str

def CFG_build_aux(json_file):

    AST = json.load(json_file)
    functions_compound_statements = [child['children'][2] for child in AST['children'] if child['type'] == function]

    return [CFG_build(function_compound_statements, None)
            for function_compound_statements in functions_compound_statements]


if __name__ == '__main__':
    f2 = open('array.c.ast.json')
    AST = json.load(f2)
    functions = [child for child in AST['children'] if child['type'] == function]
    functions_compound_statements = [child['children'][2] for child in AST['children'] if child['type'] == function]

    CFGs = [CFG_build(function_compound_statements, None)
            for function_compound_statements in functions_compound_statements]

    TRs = get_TRs(CFGs[2], functions[2])


    x = 2







