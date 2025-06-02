int a, b;
short c;
char d, e;
int main() {
  int h, i = 32768;
  for (a = 0; a < 32; a++) {
    b = i ^= 1;
    i |= e;
    h = i + c;
    d |= h;
  }
  if (b != 32768)
    __builtin_abort();
  return 0;
}