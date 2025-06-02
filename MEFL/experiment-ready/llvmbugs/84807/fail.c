#include <stdint.h>
#include <stdio.h>
struct a {
  int16_t b;
  uint64_t c;
} f = {1};
uint8_t d, h;
static struct a *g[] = {&f, &f, &f, &f};
int32_t i;
static struct a j(struct a *q) {
  for (d = 5; d < 6; d = d + 1)
    f.b = h;
  return *q;
}
int main() {
  struct a *l = g[3];
  *l = j(l);
  i = f.b;
  printf("%d\n", i);
}