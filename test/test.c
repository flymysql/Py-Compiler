
// 兰州小红鸡的注释测试
int main(){
    int a = 1;
    int b = 1;
    int c = 2;
    int index = 0;
    // 求０～２０的斐波那契数列
    while(index < 10 ){
        int tmp = c;
        c = c+b;
        a = b;
        b = tmp;
        index = index + 1;
        printf("f(%d) = %d\n", index,a);
    }
    printf("斐波那契数列打印完成，由小鸡编译器提供\n");
}