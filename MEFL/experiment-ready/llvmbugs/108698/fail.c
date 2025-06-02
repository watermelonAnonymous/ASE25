char a[8];
int b = 1, c;
int main() {
  for (; c < 8; c++)
    a[c] = !c >> b;
  if (a[0] != 0)
    __builtin_abort();
  return 0;
}