#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif

int main(void) {
#ifdef _WIN32
    Sleep(30000);
#else
    sleep(30);
#endif
    return 0;
}
