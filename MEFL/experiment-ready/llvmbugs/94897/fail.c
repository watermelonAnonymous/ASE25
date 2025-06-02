int a;
char b(char c, char d) { return c - d; }
int main() {
  int e;
  for (a = -10; a > -11; a--)
    e = b(a, -1);
  if (e > -2)
    __builtin_abort();
  return 0;
}