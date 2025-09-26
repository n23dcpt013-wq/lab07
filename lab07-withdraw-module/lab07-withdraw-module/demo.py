from atm import verify_pin, withdraw

CARD = "6222020000001234"
PIN_OK = "123456"
PIN_BAD = "000000"

print("== Verify PIN OK ==>", verify_pin(CARD, PIN_OK))
print("== Verify PIN BAD ==>", verify_pin(CARD, PIN_BAD))

print("== Withdraw 200000 ==>")
res = withdraw(CARD, 200000, atm_id=1)
print(res)

print("== Withdraw 999999999 (expect insufficient) ==>")
res = withdraw(CARD, 999999999, atm_id=1)
print(res)
