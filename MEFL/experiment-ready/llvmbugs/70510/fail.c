int printf(const char *, ...);
int a, b, c;
long d;
unsigned short e;
short f = 5;
int *g = &a;
short(h)(short j, short k) { return j % k; }
int *l() {
  long m = 0;
  int i = 0;
  for (; i < 1; --d)
    for (; m <= 7; m++) {
      int n;
      for (; i < 6; i++)
        ;
      e = h(f++, 4);
      *g = !e;
      n = m == e;
      if (n)
        return &c;
    }
  return &b;
}
int main() {
  l();
  printf("%d\n", a);
}
