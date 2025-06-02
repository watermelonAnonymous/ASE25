int printf(const char *, ...);
unsigned a;
int b, c = 1;
int main() {
  int d;
  a = -1;
  if (a < 1)
    goto e;
  d = c;
  if (d) {
  e:;
  }
  if (!d)
    __builtin_abort();
  if (b)
    goto e;
  return 0;
}