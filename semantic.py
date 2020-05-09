#!/usr/bin/python
# -*- coding: utf-8 -*-


class Attribute:
    def __init__(self, type='', width=0, val='', addr='', offset='', next=None, true=None, false=None, quad=0):
        self.type = type  # 变量声明语句中的类型
        self.width = width  # 变量声明语句中的类型宽度
        self.val = val  # 词法值

        self.addr = addr  # 表达式赋值的综合属性
        self.offset = offset  # 数组表达式赋值语句的综合属性

        self.next = next if next else []  # 控制流语句
        self.true = true if true else []  # bool表达式语句
        self.false = false if false else []
        self.quad = quad  # M->null语句


class Tbl:  # 符号表
    def __init__(self):
        self.outer_idx = 0  # 外围符号表索引 todo
        self.symbol_lst = {}  # {name:(type, offset, width)}

    def add_symbol(self, name, type, offset, width=0):
        self.symbol_lst[name] = (type, offset, width)

    def __contains__(self, item):
        return item in self.symbol_lst


class Semantic:
    def __init__(self):
        self.offset = 0  # 偏移量
        self.symbol = {}  # 符号表
        self.info = {'t': '', 'w': 0}  # 传递语法树信息

        self.tbl_lst = []  # 符号表列表，列表元素为Tbl
        self.tbl_ptr = []  # 符号表指针栈[index]index指向self.tbl_lst中的一个符号表
        self.offset_ptr = []  # 偏移指针栈

        self.para_q = []  # 过程调用中断的参数栈，队首在列表最后位置，队尾在index=0处

        self.temp_ptr = -1  # 生成临时变量

        self.code = {}  # 三地址指令和四元式表示{0: (three_addr, quaternion), 1: (three_addr, quaternion)}

        self.attr_stack = []  # 最后位置为栈顶位置

    def mk_tbl(self):  # 创建一个符号表，并返回其对应的指针（即位置索引）
        self.tbl_lst.append(Tbl())  # todo 添加外围符号表标识
        return len(self.tbl_lst) - 1

    def enter(self, index: int, name, type, offset: int):
        if not self.tbl_lst:
            self.tbl_lst.append([])
        self.tbl_lst[index].add_symbol(name, type, offset)

    def look_up(self, name, index=-1):
        if index != -1:
            res = self.tbl_lst[index].symbol_lst[name] if name in self.tbl_lst[index] else None
        else:
            for idx, tbl in enumerate(self.tbl_lst):
                if name in tbl:
                    return self.tbl_lst[idx].symbol_lst[name]  # todo 查询外层引用而非所有引用

    def new_temp(self):
        self.temp_ptr += 1
        return 't%d' % self.temp_ptr

    def get_type_width(self, type: str):
        if type.startswith('array'):
            type = type[type.index('(') + 1:len(type) - 1]
            num, type = type[:type.index(',')], type[type.index(',') + 1:]
            return int(num) * self.get_type_width(type)
        else:
            return 1 if type in ('bool', 'char') else 2 if type == 'short' else 8 if type in ('long', 'double') else 4

    def next_quad(self):
        return len(self.code)

    def back_patch(self, lst: list, quad: int):
        for idx in lst:
            self.code[idx] = (self.code[idx][0] + quad, self.code[idx][1] + quad)

    """下面是声明语句翻译语句语句对应的动作"""

    def rule_12(self):
        # D->proc id ; N1 D S {t=top(tblptr); addwidth(t, top(offset)); pop(tblptr); pop(offset); enterproc(top(tblptr),id.name,t)
        t = self.tbl_ptr.pop()
        self.offset_ptr.pop()
        self.enter(self.tbl_ptr[-1], self.attr_stack[-5].val, 'proc', t)
        self.attr_stack = self.attr_stack[:-6] + [Attribute(val='D')]

    def rule_62(self):
        # N1->null，t=mktable(top(tblptr)); push(t, tblptr); push(0, offset)
        self.tbl_ptr.append(self.mk_tbl())
        self.offset_ptr.append(0)
        self.attr_stack.append(Attribute(val='N1'))

    def rule_13(self):
        # D->X id C
        x_attr, id_name, c_attr = self.attr_stack[-3], self.attr_stack[-2].val, self.attr_stack[-1]
        self.attr_stack = self.attr_stack[:-3] + [Attribute(val='D')]
        if self.look_up(id_name, self.tbl_ptr[-1]):
            print('重复声明')  # todo 错误处理
        else:
            self.enter(self.tbl_ptr[-1], id_name, c_attr.type, self.offset_ptr[-1])
            self.offset_ptr += c_attr.width  # 栈顶偏移量变化
            self.offset += c_attr.width  # 程序偏移量变化

    def rule_14(self):
        # D->struct id { N2 D } ;
        id_name = self.attr_stack[-6].val
        self.attr_stack = self.attr_stack[:-7] + [Attribute(val='D')]
        if self.look_up(id_name, self.tbl_ptr[-1]):
            print('重复声明')  # todo 错误处理
        else:
            d_offset = self.offset_ptr.pop()
            self.tbl_ptr.pop()  # todo 这里可以对record类型进行具体化
            self.enter(self.tbl_ptr[-1], id_name, 'record', d_offset)
            self.offset_ptr += d_offset
            self.offset += d_offset

    def rule_63(self):
        # N2->null {t=mk_tbl(nil); push(t, tbl_ptr), push(0, offset_ptr)}
        self.tbl_ptr.append(self.mk_tbl())
        self.offset_ptr.append(0)
        self.attr_stack.append(Attribute(val='N2'))

    def rule_15_22(self):
        # X->long|double|float|int|unsigned|short|bool|char
        val = self.attr_stack.pop().val
        width = 1 if val in ('bool', 'char') else 2 if val == 'short' else 8 if val in ('long', 'double') else 4
        self.info['t'], self.info['w'] = val, width  # 临时变量，用于计算数组类型及宽度
        self.attr_stack.append(Attribute(type=val, width=width))

    def rule_23(self):
        # C->[Num]C {C.type=array(num.val,C1.type); C.width=num.val*C1.width;}
        num, c1 = self.attr_stack[-3].val, self.attr_stack[-1]
        self.attr_stack = self.attr_stack[:-4] + [Attribute(type='array(%d,%s)' % (num, c1.type), width=num * c1.width)]

    def rule_24(self):
        # C->null {C.type=t; C.width=w;}
        self.attr_stack.append(Attribute(type=self.info['t'], width=self.info['w']))

    def rule_25_30(self):
        # Num->dec|oct|hex|const_int|const_float|e-notation
        right = self.attr_stack.pop()
        self.attr_stack.append(Attribute(val=right.val, type=right.type))

    """下面是赋值语句翻译语句语句对应的动作"""

    def rule_5(self):
        # S->id=E; {p=lookup(id.lexeme); if p==nil then error; gencode(p'='E.addr); S.nextlist=null}
        id_name, e_addr = self.attr_stack[-4].val, self.attr_stack[-2].addr
        self.attr_stack = self.attr_stack[:-4] + [Attribute(next=[])]
        if self.look_up(id_name):  # 查到对应引用
            self.code[len(self.code)] = ('%s = %s' % (id_name, e_addr), '= %s _ %s' % (e_addr, id_name))
        else:
            print('未经声明的变量%s' % id_name)  # todo 错误处理

    def rule_6(self):
        # S->L=E; {gencode(L.array'['L.offset']''='E.addr); S.nextlist=null}
        l_attr, e_attr = self.attr_stack[-4], self.attr_stack[-2]
        three_addr = '%s [ %d ] = %s' % (l_attr.val, l_attr.offset, e_attr.addr)
        quaternion = '[]= %s %d %s' % (e_attr.addr, l_attr.val, l_attr.offset)
        self.code[len(self.code)] = (three_addr, quaternion)
        self.attr_stack = self.attr_stack[:-4] + [Attribute(next=[])]

    def rule_31(self):
        # E->E Op E {E.addr=newtemp(); gencode(E.addr '=' E1.addr 'op' E2.addr);}
        new_temp = self.new_temp()  # todo 类型判断与自动转换
        e1_attr, op_attr, e2_attr = self.attr_stack[-3], self.attr_stack[-2], self.attr_stack[-1]
        three_addr = '%s = %s %s %s' % (new_temp, e1_attr.addr, op_attr.val, e2_attr.addr)
        quaternion = '%s %s %s %s' % (op_attr.val, e1_attr.addr, e2_attr.addr, new_temp)
        self.code[len(self.code)] = (three_addr, quaternion)
        self.attr_stack = self.attr_stack[:-3] + [Attribute(addr=new_temp, type=e1_attr.type)]

    def rule_32(self):
        # E->-E {E.addr=newtemp(); gencode(E.addr'=''uminus'E1.addr)}
        e_attr, new_temp = self.attr_stack[-1], self.new_temp()
        self.code[len(self.code)] = ('%s = - %s' % (new_temp, e_attr.addr), '- %s _ %s' % (e_attr.addr, new_temp))
        self.attr_stack = self.attr_stack[:-2] + [Attribute(type=e_attr.type, addr=new_temp)]

    def rule_33(self):
        # E->(E) {E.addr=E1.addr}
        e1_attr = self.attr_stack[-2]
        self.attr_stack = self.attr_stack[:-3] + [Attribute(type=e1_attr.type, addr=e1_attr.addr)]

    def rule_34(self):
        # E->id {E.addr=lookup(id.lexeme); if E.addr==null then error;}
        id_name = self.attr_stack.pop().val
        id_info = self.look_up(id_name)
        if id_info:
            self.attr_stack.append(Attribute(type=id_info[0], addr=id_name))
        else:
            print('未经声明的变量%s' % id_name)  # todo 错误处理

    def rule_35(self):
        # E->L {E.addr=newtemp(); gencode(E.addr'='L.array'['L.offset']');}
        l_attr, new_temp = self.attr_stack.pop(), self.new_temp()
        three_addr = '%s = %s [ %d ]' % (new_temp, l_attr.val, l_attr.offset)
        quaternion = '=[] %s %d %s' % (l_attr.val, l_attr.offset, new_temp)
        self.code[len(self.code)] = (three_addr, quaternion)
        self.attr_stack.append(Attribute(addr=l_attr.val, type=l_attr.type))

    def rule_36_38(self):
        # E->Num|const_char|const_string {}
        num = self.attr_stack.pop()
        self.attr_stack.append(Attribute(val=num.val, type=num.type))

    def rule_39_44(self):
        # Op->+|-|*|/|%|^
        op_val = self.attr_stack.pop().val
        self.attr_stack.append(Attribute(val=op_val))

    def rule_45(self):
        # L->id[E] {L.array=lookup(id.lexeme); if L.array==nil then error; L.type=L.array.type.elem; L.offset=newtemp(); gencode(L.offset'='E.addr'*'L.type.width);}
        id_name, e_attr = self.attr_stack[-4].val, self.attr_stack[-2]
        l_symbol = self.look_up(id_name)
        type = l_symbol[0][l_symbol[0].index(',') + 1:len(l_symbol[0]) - 1]
        width = self.get_type_width(type)
        if l_symbol:
            if 'array' in l_symbol[0]:
                new_temp = self.new_temp()
                self.attr_stack = self.attr_stack[:-4] + [Attribute(offset=new_temp, val=id_name, type=type)]
                three_addr = '%s = %s * %d' % (new_temp, e_attr.addr, width)
                quaternion = '* %s %d %s' % (e_attr.addr, width, new_temp)
                self.code[len(self.code)] = (three_addr, quaternion)
            else:
                print('对非数组变量使用数组操作符')
        else:
            print('未经声明的变量%s' % id_name)  # todo 错误处理

    def rule_46(self):
        # L->L[E] {L.array=L1.array; L.type=L1.type.elem; t=newtemp(); gencode(t'='E.addr'*'L.type.width); L.offset=newtemp(); gencode(L.offset'='L1.offset'+'t);}
        l_attr, e_attr = self.attr_stack[-4], self.attr_stack[-2]
        new_temp0, new_temp1 = self.new_temp(), self.new_temp()
        type = l_attr.type[l_attr.type.index(',') + 1:len(l_attr.type) - 1]
        width = self.get_type_width(type)
        three_addr = '%s = %s * %d' % (new_temp0, e_attr.addr, width)
        quaternion = '* % s %s %s' % (e_attr.addr, width, new_temp0)
        self.code[len(self.code)] = (three_addr, quaternion)
        self.attr_stack = self.attr_stack[:-4] + [Attribute(val=l_attr.val, type=type, offset=new_temp1)]
        three_addr = '%s = %s + %s' % (new_temp1, l_attr.offset, new_temp0)
        quaternion = '+ %s %s %s' % (l_attr.offset, new_temp0, new_temp1)
        self.code[len(self.code)] = (three_addr, quaternion)

    """布尔表达式语句的回填相关语义动作"""

    def rule_47(self):
        # B->B1 or M B2 {backpatch(B1.falselist,M.quad); B.truelist=merge(B1.truelist,B2.truelist); B.falselist=B2.falselist}
        b2_attr = self.attr_stack.pop()
        m_attr = self.attr_stack.pop()
        self.attr_stack.pop()
        b1_attr = self.attr_stack.pop()
        self.attr_stack.append(Attribute(true=b1_attr.true + b2_attr.true, false=b2_attr.false))
        self.back_patch(b1_attr.false, m_attr.quad)

    def rule_65(self):
        # M->null {M.quad=nextquad}
        self.attr_stack.append(Attribute(quad=self.next_quad()))

    def rule_48(self):
        # B->B1 and M B2 {backpatch(B1.truelist, M.quad); B.truelist=B2.truelist; B.falselist=merge(B1.falselist, B2.falselist)}
        b2_attr = self.attr_stack.pop()
        m_attr = self.attr_stack.pop()
        self.attr_stack.pop()
        b1_attr = self.attr_stack.pop()
        self.attr_stack.append(Attribute(true=b2_attr.true, false=b1_attr.false + b2_attr.false))
        self.back_patch(b1_attr.true, m_attr.quad)

    def rule_49(self):
        #  B->not B1 {B.truelist=B1.falselist; B.falselist=B1.truelist}
        b1_attr = self.attr_stack.pop()
        self.attr_stack.pop()
        self.attr_stack.append(Attribute(true=b1_attr.false, false=b1_attr.true))

    def rule_50(self):
        # B->(B1) {B.truelist=B1.truelist;B.falselist=B1.falselist}
        self.attr_stack.pop()
        b1_attr = self.attr_stack.pop()
        self.attr_stack.pop()
        self.attr_stack.append(Attribute(true=b1_attr.true, false=b1_attr.false))

    def rule_51(self):
        # B->E Relop E {B.truelist=makelist(nextquad); B.falselist= makelist(nextquad+1) gencode('if' E1.addr relop.op E2.addr 'goto –'); gencode('goto –')}
        e2_addr = self.attr_stack.pop().addr
        relop_val = self.attr_stack.pop().val
        e1_addr = self.attr_stack.pop().addr
        self.attr_stack.append(Attribute(true=[self.next_quad()], false=[self.next_quad() + 1]))
        three_addr = 'if %s %s %s goto ' % (e1_addr, relop_val, e2_addr)
        quaternion = 'j%s %s %s ' % (relop_val, e1_addr, e2_addr)
        self.code[len(self.code)] = (three_addr, quaternion)
        self.code[len(self.code)] = ('goto ', 'j _ _ ')

    def rule_52_53(self):
        # B->true {B.truelist=makelist(nextquad); gencode('goto –')}
        # B->false {B.falselist=makelist(nextquad); gencode('goto –')}
        attr_val, make_lst = self.attr_stack.pop().val, [self.next_quad()]
        b_attr = Attribute(true=make_lst) if attr_val == 'true' else Attribute(false=make_lst)
        self.attr_stack.append(b_attr)
        self.code[len(self.code)] = ('goto ', 'j _ _ ')

    def rule_54_59(self):
        # Relop-><|<=|==|!=|>|>=
        attr = self.attr_stack.pop()
        self.attr_stack.append(Attribute(val=attr.val))

    """控制流语句的语义动作回填相关"""

    def rule_4(self):
        #  S->S1 M S2 {backpatch(S1.nextlist, M.quad); S.nextlist=S2.nextlist}
        s1_attr, m_attr, s2_attr = self.attr_stack[-3], self.attr_stack[-2], self.attr_stack[-1]
        self.attr_stack = self.attr_stack[:-3] + [Attribute(next=s2_attr.next)]
        self.back_patch(s1_attr.next, m_attr.quad)

    def rule_7(self):
        # S->if B then M S1 {backpatch(B.truelist, M.quad); S.nextlist=merge(B.falselist, S1.nextlist)}
        s1_attr, m_attr, b_attr = self.attr_stack[-1], self.attr_stack[-2], self.attr_stack[-4]
        self.attr_stack = self.attr_stack[:-5] + [Attribute(next=b_attr.false + s1_attr.next)]
        self.back_patch(b_attr.true, m_attr.quad)

    def rule_8(self):
        # S->if B then M1 S1 N else M2 S2  {backpatch(B.truelist, M1.quad); backpatch(B.falselist, M2.quad); S.nextlist=merge(S1.nextlist, merge(N.nextlist, S2.nextlist))}
        s2_attr, m2_attr, n_attr, s1_attr, m1_attr, b_attr = self.attr_stack[-1], self.attr_stack[-2], self.attr_stack[
            -4], self.attr_stack[-5], self.attr_stack[-6], self.attr_stack[-8]
        self.attr_stack = self.attr_stack[:-9] + [Attribute(next=s1_attr.next + s2_attr.next + n_attr.next)]
        self.back_patch(b_attr.true, m1_attr.quad)
        self.back_patch(b_attr.false, m2_attr.quad)

    def rule_64(self):
        # N->null {N.nextlist=makelist(nextquad); gencode('goto –')}
        self.attr_stack.append(Attribute(next=[self.next_quad()]))
        self.code[len(self.code)] = ('goto ', 'j _ _ ')

    def rule_9(self):
        # S->while M1 B do M2 S1 {backpatch(S1.nextlist, M1.quad); backpatch(B.truelist,M2.quad);S.nextlist=B.falselist; gencode('goto'M1.quad)}
        s_attr, m2_attr, b_attr, m1_attr = self.attr_stack[-1], self.attr_stack[-2], self.attr_stack[-4], \
                                           self.attr_stack[-5]
        self.attr_stack = self.attr_stack[:-6] + [Attribute(next=b_attr.false)]
        self.back_patch(s_attr.next, m1_attr.quad)
        self.back_patch(b_attr.true, m2_attr.quad)
        self.code[len(self.code)] = ('goto %d' % m1_attr.quad, 'j _ _ %d' % m1_attr.quad)

    """过程调用语句的语义动作相关"""

    def rule_10(self):
        # S->call id ( Elst ) ;   {n=0; for queue中的每个t do {gencode('param't); n=n+1} gencode('call'id.addr','n);} {S.nextlist=null;}
        elst_attr, id_val = self.attr_stack[-3], self.attr_stack[-5].val
        res = self.look_up(id_val)
        if res:
            if res[0] != 'proc':
                print('对%s类型使用非法的函数调用操作符' % res[0])
            else:
                for para in reversed(self.para_q):
                    self.code[len(self.code)] = ('param %s' % para, 'param _ _ %s' % para)
                self.code[len(self.code)] = (
                    'call %s , %d' % (id_val, len(self.para_q)), 'call %s %d _' % (id_val, len(self.para_q)))
                self.attr_stack = self.attr_stack[:-6] + [Attribute(next=[])]
        else:
            print('未经声明的函数')

    def rule_60(self):
        # Elst->Elst,E {将E.addr添加到q的队尾}
        e_attr = self.attr_stack[-1]
        self.attr_stack = self.attr_stack[:-3] + [Attribute()]
        self.para_q.insert(0, e_attr.addr)

    def rule_61(self):
        # Elst->E {将q初始化为只包含E.addr}
        e_attr = self.attr_stack.pop()
        self.para_q = [e_attr.addr]
        self.attr_stack.append(Attribute())

    def rule_0(self):
        # P'->P
        self.attr_stack.pop()
        self.attr_stack.append(Attribute(val='P'))

    def rule_1_2(self):
        # P->DP|SP
        self.attr_stack = self.attr_stack[:-2] + [Attribute(val='P')]

    def rule_3(self):
        # P->null
        self.attr_stack.append(Attribute(val='P'))

    def rule_11(self):
        # D->DD
        self.attr_stack = self.attr_stack[:-2] + [Attribute(val='D')]

    def semantic_run(self, tokens, nums_attr):  # 运行语义分析
        from syntax import Syntax
        syntax = Syntax()
        syntax.syntax_init('./help/syntax.json')


    def semantic_action(self):
        func_dic = {}
        for func in dir(Semantic):
            if func.startswith('rule_'):
                item = func.split('_')
                if len(item) == 2:
                    func_dic[int(item[1])] = func
                else:
                    idx, idy = int(item[1]), int(item[2])
                    for count in range(idx, idy + 1):
                        func_dic[count] = func
        print(len(func_dic))
        return func_dic


def main():
    semantic = Semantic()
    semantic.semantic_action()


if __name__ == '__main__':
    main()
