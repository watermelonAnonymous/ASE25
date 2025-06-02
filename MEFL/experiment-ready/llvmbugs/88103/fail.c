volatile int a, c;
char b, f, j;
int d, g, h, i;
unsigned char e;
int main() {
  f = i = 0;
  for (; i < 4; i++)
    for (j = 23; j > -18; j--)
      a;
  for (h = 2; h; h--)
    for (b = 0; b < 3; b++) {
      f ^= c;
      d += f >= g;
      g = --e;
    }
  if (d != 1)
    __builtin_abort();
  return 0;
}