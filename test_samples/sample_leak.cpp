#include <iostream>
#include <vector>

void processData(int size) {
    // 1. Memory Leak: Allocated on heap, never freed
    int* dataArray = new int[size];
    
    // 2. Potential Segmentation Fault / Out of bounds if size <= 10
    for (int i = 0; i <= 10; ++i) {
        dataArray[i] = i * 2;
    }
    
    // 3. Uninitialized pointer vulnerability
    int* ptr;
    if (size > 100) {
        *ptr = 42; // Undefined behavior/crash if ptr is not initialized
    }
    
    std::cout << "Data processed successfully." << std::endl;
}

int main() {
    processData(5);
    return 0;
}
