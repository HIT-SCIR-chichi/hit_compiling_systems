/*
* 创建者：张景润
* 描述：这是一个针对词法分析的正确测试
*/

// 声明语句：变量声明、数组声明、记录声明、过程声明
int a;
float b;
char c;
char d[2][0x2]; // 多维数组声明

struct student{ // 记录声明
    int a;
    double b;
    float c;
    char d;
};
proc do_something;{ // 过程声明
    char i;
    i = d[1][1];
}

// 表达式及赋值语句：数组元素的引用和赋值
b = - (10*2) + 3;
d[1][1] = '\n';
c = d[1][0];

// 分支、循环语句
while a >= b do {
    b = b + 1;
    if b == 0 then b = d[0][1];
    else
        if a == b and not (a ==0) then a =1;}

// 过程调用语句
call do_something(a+d[1][0], 10*12, 1.0e-3);