int printf(const char *, ...);
int a, b = 7, c;
int *d = &c;
int e() { return 1 & b; }
int main() {
  char f = -1;
  *d = a + f == e() + f + f;
  printf("%d\n", c);
}
