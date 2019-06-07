#include <stdio.h>
#include <stdlib.h>

int main(){
    int arr[25];
    int a = 1;
    int b = 1;
    int c = 2;
    int index = 2;
    arr[0] = 1;
    arr[1] = 2;
    arr[2] = 3;
    // 求０～２０的斐波那契数列
    while(index < 10*2 ){
        b = arr[index-2];
        c = arr[index-1];
        arr[index] = b+c;
        index = index + 1;
        printf("f(%d) = %d\n", index,c);
    }
    // printf("%d",arr[1]);
    printf("斐波那契数列打印完成，由小鸡编译器提供\n");
}