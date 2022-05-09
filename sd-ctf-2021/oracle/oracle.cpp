#include <iostream>
#include <cstring>

char *numbers;
char *check;

void fill_check()
{
    char *pbVar1;

    pbVar1 = new char[0x2a];
    pbVar1[0] = 0x30;
    pbVar1[1] = 6;
    pbVar1[2] = 0x7a;
    pbVar1[3] = -0x56;
    pbVar1[4] = -0x49;
    pbVar1[5] = -0x3b;
    pbVar1[6] = 0x4e;
    pbVar1[7] = 0x54;
    pbVar1[8] = 0x69;
    pbVar1[9] = -0x77;
    pbVar1[10] = -0x24;
    pbVar1[0xb] = -0x76;
    pbVar1[0xc] = 0x46;
    pbVar1[0xd] = 0x11;
    pbVar1[0xe] = 0x65;
    pbVar1[0xf] = -0x55;
    pbVar1[0x10] = 0x37;
    pbVar1[0x11] = -0x26;
    pbVar1[0x12] = -0x5b;
    pbVar1[0x13] = 0x20;
    pbVar1[0x14] = -0x12;
    pbVar1[0x15] = -0x6b;
    pbVar1[0x16] = 0x35;
    pbVar1[0x17] = 99;
    pbVar1[0x18] = -0x4a;
    pbVar1[0x19] = 0x43;
    pbVar1[0x1a] = 0x59;
    pbVar1[0x1b] = 0x78;
    pbVar1[0x1c] = -0x29;
    pbVar1[0x1d] = 0x7a;
    pbVar1[0x1e] = -100;
    pbVar1[0x1f] = -0x46;
    pbVar1[0x20] = 0x22;
    pbVar1[0x21] = -0x6f;
    pbVar1[0x22] = 0x15;
    pbVar1[0x23] = -0x80;
    pbVar1[0x24] = 0x4e;
    pbVar1[0x25] = 0x1b;
    pbVar1[0x26] = 0x7b;
    pbVar1[0x27] = -0x67;
    pbVar1[0x28] = 0x24;
    pbVar1[0x29] = 0x57;
    check = pbVar1;
}

void firstPass_void()
{
    char *pbVar1;
    char bVar2;
    int iVar3;

    iVar3 = 0;
    while (true)
    {
        if (0x29 < iVar3)
            break;
        pbVar1 = numbers;
        bVar2 = (char)iVar3;
        pbVar1[iVar3] ^= bVar2 * 3 * bVar2 + bVar2 * 5 + 0x65 + (char)(iVar3 % 2);
        iVar3++;
    }
    return;
}

void secondPass_void()
{
    char *pbVar1;
    int iVar2;

    pbVar1 = new char[42];
    iVar2 = 0;
    while (true)
    {
        if (0x29 < iVar2)
            break;
        pbVar1[iVar2] =
            (char)((int)numbers[(iVar2 + 0x29) % 0x2a] << 4) |
            (char)((numbers[iVar2] & 0xff) >> 4);
        iVar2++;
    }
    numbers = pbVar1;
    return;
}

void thirdPass_void()
{
    char *pbVar1;
    char bVar2;
    int iVar3;

    iVar3 = 0;
    while (true)
    {
        if (0x29 < iVar3)
            break;
        pbVar1 = numbers;
        bVar2 = (char)iVar3;
        pbVar1[iVar3] += bVar2 * 7 * bVar2 + bVar2 * 0x1f + 0x7f + (char)(iVar3 % 2);
        iVar3++;
    }
    return;
}

int main()
{
    numbers = new char[42];
    std::fread(numbers, 1, 42, stdin);

    fill_check();
    firstPass_void();
    secondPass_void();
    thirdPass_void();

    char bVar3 = 0;
    int iVar4 = 0;
    while (true)
    {
        if (0x29 < iVar4)
            break;
        bVar3 |= check[iVar4] ^ numbers[iVar4];
        iVar4++;
    }
    if (bVar3 != 0)
    {
        std::exit(1);
    }

    std::puts("Good job. You found the flag!");
    return 0;
}