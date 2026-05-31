#include <iostream>
using namespace std;

int findMax(int arr[], int n)
{
    int maxVal = 0;   // BUG: fails for all-negative arrays

    for(int i = 0; i <= n; i++) // BUG: out-of-bounds access
    {
        if(arr[i] > maxVal)
        {
            maxVal = arr[i];
        }
    }

    return maxVal;
}

int main()
{
    int* data = new int[5]; // Memory allocated

    for(int i = 0; i < 5; i++)
    {
        data[i] = -i - 1;
    }

    cout << findMax(data, 5) << endl;

    // BUG: missing delete[]

    return 0;
}