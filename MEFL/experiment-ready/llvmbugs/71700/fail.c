int a, c;
char b = -50;
long d = 10;
int main() {
  int e = -1, f = ~(a / -1U);
  if (b)
    e = f;
  a = ~(-((e - b) % d) | ~e);
 if (a <= c)
   __builtin_abort();
 return 0;
}
