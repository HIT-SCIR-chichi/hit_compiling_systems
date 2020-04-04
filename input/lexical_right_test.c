/*
* 创建者：张景润
* 描述：这是一个针对词法分析的正确测试
*/

// 常数测试：8、10、16进制；科学计数法；有、无符号数；字符、字符串；布尔型
unsigned a = 12; // 无符号10进制常数
int _a1, _a2 = -12, +12; // 有符号10进制常数
int b, c = 07, 0x1f; // 8进制常数，16进制常数
float d, e = 1.5e-32, -0.3e+01; // 无符号科学计数法，有符号科学计数法
char f = '1'; // 普通字符常量
char g, h, i, j, k, l, m, n, o, p, q = '\n','\t','\r','\v','\b','\a','\f','\\','\'','\"','\0'; // 转义符字符常量
char *r = "This is a string test."; // 普通字符串常量
char *s = "\n\t\r\a\b\\\'\"\0中文字符测试"; // 特殊的字符串测试
bool t, u = true, false; // 布尔型常量

// 运算符：算术运算符、关系运算符、逻辑运算符、位运算符
_a1 = _a2 % _a1 * (-1) / (2 ^ 5); // 算术运算符
_a1++; // ++算术运算符
_a2--; // --算数运算符
t, u, t = a > b, a <= b, a != b; // 关系运算符
t, u, t = t && u, t || u, !t // 逻辑运算符
a|b, a&b// 位运算符

// 界限符：单界限符、双界限符
char a[3] = [0,1,2]; // []界限符
int my_function(int a, int b) { // {}界限符
    a = b + 1; // ；界限符
    print("%d", a);
}

// 关键字
struct student{
    int age = 0;
    double height = 100.0;
    long weight = 50;
}
if(a > b){
    do{
        my_function(1,2);
    }while(1>2);
} else{
    switch a:{
        case 1:
            break;
        default:
            break;
    }
}

// 注释
// 带有转义符的特殊单行注释：\n\r\t\b
/*
* 带有转义符的特殊多行注释：\n\r\t\b\0
*/