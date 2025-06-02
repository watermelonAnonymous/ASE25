short a, e;
int b[2][5] = {{0, 0, 3, 0, 0}, {0, 0, 0, 0, 0}}, c, d, *f, *g;
short h(short j) { return j ? a % j : 0; }
void k() {
  int **l = &f;
  for (int i = 0; i < 2; i++)
    g = &c;
  d = 2;
  for (; d; d--) {
    *l = g;
    **l = 0;
    for (e = 0; e < 2; e++) {
      h(d);
      b[e][d + 2] = 0;
      if (d)
        *l = 0;
    }
  }
}
int main() {
  k();
  if (b[0][2] != 3)
    __builtin_abort();
  return 0;
}