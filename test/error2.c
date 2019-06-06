#include <stdio.h>
#include <stdlib.h>
int main(){
    int a = 1;
    int b = 1;
    int c = 2;
    int index = 0;
    // 求０～２０的斐波那契数列
    while(index + 1 <= 20 ){
        int tmp = c;
        c = a;
        a = b;
        b = tmp;
        index = index + 1;
        printf("%d\n",a);
    }
}