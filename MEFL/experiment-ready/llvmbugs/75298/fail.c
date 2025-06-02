int printf(const char *, ...);
int a, c = 1, e;
long b;
static int *d = &a;
int main() {
  int *f = &c;
  for (; b <= 6; b++)
    *d ^= *f;
  int **g = &d;
  int **h = &d;
  b = &g == &h;
  printf("%d\n", a);
}
