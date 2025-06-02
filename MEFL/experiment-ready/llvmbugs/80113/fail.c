int printf(const char *, ...);
short a, f = 6;
int b, e, g;
int c[7][1];
static int *d = &b;
long h;
int *const *i;
static unsigned char j(long k, short *n) {
  int *l = &c[5][0];
  int *const **m = &i;
  i = &l;
  *d = 0;
  for (; e < 60; e++)
    ***m = ((h = *d == (1 ^ k)) & *n + f) - 2;
  return 0;
}
int main() {
  j(1, &a);
  printf("%d\n", c[5][0]);
}