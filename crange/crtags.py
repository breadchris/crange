import os
from clang.cindex import Index, TranslationUnit, CursorKind

class CrTags:
    "Class CrTags"

    def __init__(self):
        self.opts  = dict()
        self.args  = list()  # Arguments passed from the command line.
        self.ast   = dict()  # List containing nodes present in a source file.

    def __del__(self):
        self.ast.clear()
        
    def debug(self, message):
        if self.opts.verbose:
            print message

    def get_diag_info(self, diag):
        return { 'severity' : diag.severity,
                 'location' : diag.location,
                 'spelling' : diag.spelling,
                 'ranges' : diag.ranges,
                 'fixits' : diag.fixits }

    def get_cursor_id(self, cursor, cursor_list = []):
        if not self.opts.showIDs:
            return None
                
        if cursor is None:
            return None

        # FIXME: This is really slow. It would be nice if the index API exposed
        # something that let us hash cursors.
        for i,c in enumerate(cursor_list):
            if cursor == c:
                return i
        cursor_list.append(cursor)
        return len(cursor_list) - 1

    ###### Node's key reference:
    # 1.  location   : node's filename    
    # 2.  line       : location line number
    # 3.  column     : location column number
    # 4.  offset     : location offset
    # 5.  start_line : extent start line
    # 6.  start_col  : extent start column
    # 7.  end_line   : extent end line
    # 8.  end_col    : extent end column
    # 9.  kind_name  : node kind name
    # 10. type_name  : node type name
    # 11. spelling   : spelling
    # 12. display    : display
    # 13. is_def     : node is a definition?
    # 14. def        : USR of node's definition.
    # 15. is_static  : node is a static method?
    # 16. is_ref     : node is a reference?
    # 17. ref        : USR of node's that is referenced.
    # 18. usr        : USR of this node.
    ######
    def node_to_tuple(self, loc, node):
        definition = node.get_definition().get_usr() if node.get_definition() else None
        referenced = node.referenced.get_usr() if node.referenced else None
        return (loc,
                node.location.line,
                node.location.column,
                node.location.offset,
                node.extent.start.line,
                node.extent.start.column,
                node.extent.end.line,
                node.extent.end.column,
                node.kind.name,
                node.type.kind.name,
                node.spelling,
                node.displayname,
                node.is_definition(),
                definition,
                node.is_static_method(),
                node.kind.is_reference(),
                referenced,
                node.get_usr())

    def crangepath(self, loc):
        crpath = os.path.relpath(loc)
        if '..' in crpath:
            crpath = os.path.realpath(loc)
        return crpath

    def get_info(self, node, depth=0):
        if self.opts.maxDepth is not None and depth >= self.opts.maxDepth:
            children = None
        else:
            # TODO: We should be pulling out function information here

            # void bnep_unregister_service(uint16_t service_uuid)
            # {
            #     log_info("BNEP_UNREGISTER_SERVICE #%04x", service_uuid);

            #     bnep_service_t *service = bnep_service_for_uuid(service_uuid);    
            #     if (!service) {
            #         return;
            #     }

            #     btstack_linked_list_remove(&bnep_services, (btstack_linked_item_t *) service);
            #     btstack_memory_bnep_service_free(service);
            #     service = NULL;
                
            #     l2cap_unregister_service(BLUETOOTH_PROTOCOL_BNEP);
            # }
            
            # `-FunctionDecl 0x7fef1b852cf0 prev 0x7fef1c0b4a60 <line:1620:1, line:1634:1> line:1620:6 bnep_unregister_service 'void (uint16_t)'
            #   |-ParmVarDecl 0x7fef1b852c68 <col:30, col:39> col:39 used service_uuid 'uint16_t':'unsigned short'
            #   `-CompoundStmt 0x7fef1b8535c8 <line:1621:1, line:1634:1>
            #     |-CallExpr 0x7fef1b852ec8 <src/btstack_debug.h:79:46, col:130> 'void'
            #     | |-ImplicitCastExpr 0x7fef1b852eb0 <col:46> 'void (*)(int, const char *, ...)' <FunctionToPointerDecay>
            #     | | `-DeclRefExpr 0x7fef1b852d98 <col:46> 'void (int, const char *, ...)' Function 0x7fef1c157be0 'hci_dump_log' 'void (int, const char *, ...)'
            #     | |-IntegerLiteral 0x7fef1b852dc0 <src/hci_dump.h:61:34> 'int' 1
            #     | |-ImplicitCastExpr 0x7fef1b852f30 <src/btstack_debug.h:79:70, src/classic/bnep.c:1622:14> 'const char *' <BitCast>
            #     | | `-ImplicitCastExpr 0x7fef1b852f18 <src/btstack_debug.h:79:70, src/classic/bnep.c:1622:14> 'char *' <ArrayToPointerDecay>
            #     | |   `-StringLiteral 0x7fef1b852de0 <src/btstack_debug.h:79:70, src/classic/bnep.c:1622:14> 'char [37]' lvalue "%s.%u: BNEP_UNREGISTER_SERVICE #%04x"
            #     | |-ImplicitCastExpr 0x7fef1b852f48 <line:38:26> 'char *' <ArrayToPointerDecay>
            #     | | `-StringLiteral 0x7fef1b852e38 <col:26> 'char [7]' lvalue "bnep.c"
            #     | |-IntegerLiteral 0x7fef1b852e68 <<scratch space>:549:1> 'int' 1622
            #     | `-ImplicitCastExpr 0x7fef1b852f78 <src/classic/bnep.c:1622:47> 'int' <IntegralCast>
            #     |   `-ImplicitCastExpr 0x7fef1b852f60 <col:47> 'uint16_t':'unsigned short' <LValueToRValue>
            #     |     `-DeclRefExpr 0x7fef1b852e88 <col:47> 'uint16_t':'unsigned short' lvalue ParmVar 0x7fef1b852c68 'service_uuid' 'uint16_t':'unsigned short'
            #     |-DeclStmt 0x7fef1b8530b0 <line:1624:5, col:66>
            #     | `-VarDecl 0x7fef1b852fa0 <col:5, col:65> col:21 used service 'bnep_service_t *' cinit
            #     |   `-CallExpr 0x7fef1b853068 <col:31, col:65> 'bnep_service_t *'
            #     |     |-ImplicitCastExpr 0x7fef1b853050 <col:31> 'bnep_service_t *(*)(uint16_t)' <FunctionToPointerDecay>
            #     |     | `-DeclRefExpr 0x7fef1b853000 <col:31> 'bnep_service_t *(uint16_t)' Function 0x7fef1b081b90 'bnep_service_for_uuid' 'bnep_service_t *(uint16_t)'
            #     |     `-ImplicitCastExpr 0x7fef1b853098 <col:53> 'uint16_t':'unsigned short' <LValueToRValue>
            #     |       `-DeclRefExpr 0x7fef1b853028 <col:53> 'uint16_t':'unsigned short' lvalue ParmVar 0x7fef1b852c68 'service_uuid' 'uint16_t':'unsigned short'
            #     |-IfStmt 0x7fef1b853158 <line:1625:5, line:1627:5>
            #     | |-<<<NULL>>>
            #     | |-<<<NULL>>>
            #     | |-UnaryOperator 0x7fef1b853108 <line:1625:9, col:10> 'int' prefix '!'
            #     | | `-ImplicitCastExpr 0x7fef1b8530f0 <col:10> 'bnep_service_t *' <LValueToRValue>
            #     | |   `-DeclRefExpr 0x7fef1b8530c8 <col:10> 'bnep_service_t *' lvalue Var 0x7fef1b852fa0 'service' 'bnep_service_t *'
            #     | |-CompoundStmt 0x7fef1b853140 <col:19, line:1627:5>
            #     | | `-ReturnStmt 0x7fef1b853128 <line:1626:9>
            #     | `-<<<NULL>>>
            #     |-CallExpr 0x7fef1b853290 <line:1629:5, col:81> 'int'
            #     | |-ImplicitCastExpr 0x7fef1b853278 <col:5> 'int (*)(btstack_linked_list_t *, btstack_linked_item_t *)' <FunctionToPointerDecay>
            #     | | `-DeclRefExpr 0x7fef1b853190 <col:5> 'int (btstack_linked_list_t *, btstack_linked_item_t *)' Function 0x7fef1c1079a8 'btstack_linked_list_remove' 'int (btstack_linked_list_t *, btstack_linked_item_t *)'
            #     | |-UnaryOperator 0x7fef1b8531e0 <col:32, col:33> 'btstack_linked_list_t *' prefix '&'
            #     | | `-DeclRefExpr 0x7fef1b8531b8 <col:33> 'btstack_linked_list_t':'btstack_linked_item_t *' lvalue Var 0x7fef1c29b9f8 'bnep_services' 'btstack_linked_list_t':'btstack_linked_item_t *'
            #     | `-CStyleCastExpr 0x7fef1b853250 <col:48, col:74> 'btstack_linked_item_t *' <BitCast>
            #     |   `-ImplicitCastExpr 0x7fef1b853238 <col:74> 'bnep_service_t *' <LValueToRValue>
            #     |     `-DeclRefExpr 0x7fef1b853200 <col:74> 'bnep_service_t *' lvalue Var 0x7fef1b852fa0 'service' 'bnep_service_t *'
            #     |-CallExpr 0x7fef1b853390 <line:1630:5, col:45> 'void'
            #     | |-ImplicitCastExpr 0x7fef1b853378 <col:5> 'void (*)(bnep_service_t *)' <FunctionToPointerDecay>
            #     | | `-DeclRefExpr 0x7fef1b8532c8 <col:5> 'void (bnep_service_t *)' Function 0x7fef1b8431c0 'btstack_memory_bnep_service_free' 'void (bnep_service_t *)'
            #     | `-ImplicitCastExpr 0x7fef1b8533c0 <col:38> 'bnep_service_t *' <LValueToRValue>
            #     |   `-DeclRefExpr 0x7fef1b8532f0 <col:38> 'bnep_service_t *' lvalue Var 0x7fef1b852fa0 'service' 'bnep_service_t *'
            #     |-BinaryOperator 0x7fef1b853498 <line:1631:5, /usr/include/sys/_types.h:52:33> 'bnep_service_t *' '='
            #     | |-DeclRefExpr 0x7fef1b8533d8 <src/classic/bnep.c:1631:5> 'bnep_service_t *' lvalue Var 0x7fef1b852fa0 'service' 'bnep_service_t *'
            #     | `-ImplicitCastExpr 0x7fef1b853480 </usr/include/sys/_types.h:52:23, col:33> 'bnep_service_t *' <NullToPointer>
            #     |   `-ParenExpr 0x7fef1b853460 <col:23, col:33> 'void *'
            #     |     `-CStyleCastExpr 0x7fef1b853438 <col:24, col:32> 'void *' <NullToPointer>
            #     |       `-IntegerLiteral 0x7fef1b853400 <col:32> 'int' 0
            #     `-CallExpr 0x7fef1b853580 <src/classic/bnep.c:1633:5, col:53> 'uint8_t':'unsigned char'
            #       |-ImplicitCastExpr 0x7fef1b853568 <col:5> 'uint8_t (*)(uint16_t)' <FunctionToPointerDecay>
            #       | `-DeclRefExpr 0x7fef1b8534c0 <col:5> 'uint8_t (uint16_t)' Function 0x7fef1c2231c0 'l2cap_unregister_service' 'uint8_t (uint16_t)'
            #       `-ImplicitCastExpr 0x7fef1b8535b0 <src/bluetooth_sdp.h:24:84> 'uint16_t':'unsigned short' <IntegralCast>
            #         `-IntegerLiteral 0x7fef1b8534e8 <col:84> 'int' 15
            #             children = [self.get_info(c, depth+1)
            #             for c in node.get_children()]

        loc = self.crangepath(str(node.location.file)) if node.location.file else None
        if loc is not None:
            if loc not in self.ast:
                self.ast[loc] = list()
            self.ast[loc].append(self.node_to_tuple(loc, node))
