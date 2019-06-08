int main(){
    int arr[2];
    arr[1] = 1;
    arr[0] = 0;
    int b = 0;

    int c = arr[arr[b+1]];
    printf("\n\n这个例子展示了在printf语句中的参数，可以是一个表达式。\n例如b*2 +(4+5)*3 = %d", b*2 +(4+5)*3 );
    printf("\n\n这个例子展示了数组内下标的可用变量表示，并且可递归嵌套\nint c = arr[arr[b+1]] = %d\n\n", c);
}