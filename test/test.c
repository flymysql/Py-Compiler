
// 兰州小红鸡的注释测试
int main(){
    int a = 0;
    int b = 1;
    int c = 1;
    int index = 0;
    // 求０～２０的斐波那契数列
    while(index < 20){
        printf(a);
        int tmp = c;
        c = a + b;
        a = b;
        b = tmp;
        index = index + 1;
    }
    if(c == a+b){
        printf(c);
    }
    printf(a,b);

    /*printf和控制语句的四元式还没写
    多行注释测试
    */
}