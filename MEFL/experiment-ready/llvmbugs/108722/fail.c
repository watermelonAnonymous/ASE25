#include <assert.h>
#include <stdint.h>

uint32_t ror(uint32_t val, uint32_t amount) {
    return (val >> amount) | (val << (32 - amount));
}

__attribute__((noinline))
uint32_t bytesEqual(uint32_t val) {
    return ror(val, 8) == val;
}

int main() {
    assert(!bytesEqual(0x12345612));
}