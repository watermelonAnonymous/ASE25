int printf(const char *, ...);
int a, d, e = 35435;
char b;
long c;
unsigned j;
short k, l;
int m(int n) {
  char f[] = {0, 9};
  char *g = f, *i = g;
  long h = n;
  do
    *i++ = h /= 10;
  while (h);
  c = i - g;
  while (g < i)
    b = *g++;
  a = c;
  return c;
}
void o(int n) {
  k = e;
  l = (j = k) > n;
  if (l)
    d = 3;
}
void p() {
  int q = m(17);
  o(q + 65533);
}
int main() {
  p();
  printf("%d\n", d);
}
