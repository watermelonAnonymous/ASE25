#include <stdio.h>
#include <stdint.h>
static uint16_t
(safe_lshift_func_uint16_t_u_s)(uint16_t left, int right )
{
  return
    ((((int)right) < 0) || (((int)right) >= 32) || (left > ((65535) >> ((int)right)))) ?
    ((left)) :
    (left << ((int)right));
}
static int16_t
(safe_unary_minus_func_int16_t_s)(int16_t si )
{
  return
    -si;
}
static int32_t
(safe_lshift_func_int32_t_s_u)(int32_t left, unsigned int right )
{
  return
    ((left < 0) || (((unsigned int)right) >= 32) || (left > ((2147483647) >> ((unsigned int)right)))) ?
    ((left)) :
    (left << ((unsigned int)right));
}
long smin(long d, long p) { return d < p ? d : p; }
struct e { uint32_t f; } static g[] = {1, 36};
int64_t h, i;
uint8_t j(uint64_t m) {
  if (safe_lshift_func_uint16_t_u_s(
          smin(m, safe_unary_minus_func_int16_t_s(
                                safe_lshift_func_int32_t_s_u(1, g[1].f))),
          3))
     h = 0;
  return m;
}
int8_t k() {
  j(0);
  struct e *l[] = {&g[1], &g[1], &g[1], &g[1], &g[1],
                   &g[1], &g[1], &g[1], &g[1]};
  return i;
}
int main() {
  printf("%d\n", k());
  return 0;
}