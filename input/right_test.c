int m,z=0x12;   /*连续声明，赋值，8进制、16进制*/
m = 2+3*4;      /*赋值，生成三地址指令时，考虑优先级*/
char c= 'a';	/*字符型声明，识别字符常数*/
real b = 1;     /*浮点型声明，自动类型转化*/
int[2][4] h;    /*多维数组的声明*/
int[3] a;       /*数组声明*/
a[0] = 2;       /*数组的赋值和引用*/
while(m>2)      /*循环语句*/
do
if(m<8)  	/*嵌套的分支语句*/
then m = m +1;
else m = m*2;
switch(m){	/*switch语句的识别和应用*/
  case 1:
  m = m +1;
  case 2:
  m = m + 3;
  default:
  m = m +6;
}
int i;
for(i = 0;i<10;i++){  /*for语句*/
  m = m+2;
}
record stack{    /*记录的声明，这里声明了一个栈结构*/
  int num;
  char value;
}
/*过程声明，声明一个返回值为int的求和函数*/
proc int getSum(int x,int y){
   int j = x;
   int k = y;
   return j+k;
}
call getSum(1,2);    /*函数调用*/