import os

import fuc

print("\n\n\n")
try:
    user = fuc.login()
    while True:
        os.system("cls")
        a=input("请输入模式 【1】发【2】收 【3】退出")
        if a == '1':
            fuc.sent(user[0])
        elif a == '3':
            print("--再见--")
            os.system("pause")
            exit(0)
        else:
            fuc.get_a_msg()
except Exception as e:
    # 打印异常信息
    print(e)
    print('发生错误')
    fuc.roll()
    os.system("pause")
