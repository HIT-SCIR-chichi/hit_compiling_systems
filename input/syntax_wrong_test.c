/*
* 创建者：张景润
* 描述：这是一个针对词法分析的错误测试
*/

// 缺少分号
int a
a = 1;

// 缺少括号
bool c;
c = (1!=2;

// 缺少运算符、运算分量
a = 1 2;
a = 1 * 2 *;

// 缺少花括号
struct student{
    long stu_num;
    unsigned age;
;