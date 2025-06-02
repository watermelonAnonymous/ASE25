int printf(const char *, ...);
unsigned int IntArr[6];
unsigned int GlobIntONE = 1, GlobIntZERO = 0;
const unsigned int *GlobIntPtr = 0;
unsigned long Res;
unsigned long *ResPtr = &Res;
const unsigned int **GlobIntPtrPTr = &GlobIntPtr;
unsigned int *func() {
  int *GlobIntONEPtr = &GlobIntONE;
  for (int Idx = 0; Idx <= 7; Idx += 1) {
    int Idx2 = 1;
    if (Idx > 0) {
      for (; Idx2 <= 7; Idx2 += 1)
        ;
      return GlobIntONEPtr;
    }
  }
  0 != &GlobIntONEPtr;
  return &GlobIntZERO;
}

int main() {
  IntArr[GlobIntZERO] = GlobIntZERO;
  *GlobIntPtrPTr = func();
  unsigned char Byte = *GlobIntPtr;
  *ResPtr = Byte;
  printf("checksum = %X\n", Res);
}