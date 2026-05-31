#include <iostream>
using namespace std;

int main()
{
    int* ptr;

    *ptr = 10;

    int* arr = new int[5];

    for(int i=0;i<=5;i++)
    {
        arr[i] = i;
    }

    return 0;
}