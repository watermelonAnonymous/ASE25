struct a {
  int b;
  int c;
  int d;
  int e;
  int f;
} g, h = {1,0,0,0,0}, *i;
void j(struct a k) {
  struct a *l = &g;
  if (k.b)
    l = i = &k;
  if (l != &k)
    __builtin_abort();
}
int main() {
  j(h);
  return 0;
}