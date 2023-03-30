from expression import Secret
from protocol import ProtocolSpec
from test_integration import run_processes

"""
实际场景：
    1.有一个商圈里面有三个商家a,b,c
    2.三个商家都想知道商圈今年总的经济效益，以估计
    下一年自己是否可以继续在商圈里获得良好的效益
    3.三个商家都不想让别的商家知道自今年的收入情况
    4.使用smc协议
    5. a今年收入100元 b:200元 c:300 元
    6. 总收入total = a + b + c
"""


def test_custom_application():
    business_tom = Secret()
    business_bob = Secret()
    business_alice = Secret()

    tom_income = 156992
    bob_income = 298878
    alice_income = 400000

    expr = business_tom + business_bob + business_alice
    parties = {
        "Tom": {business_tom: tom_income},
        "Bob": {business_bob: bob_income},
        "Alice": {business_alice: alice_income}
    }

    expect_total_income = tom_income + bob_income + alice_income

    participants = list(parties.keys())
    prot = ProtocolSpec(expr=expr, participant_ids=list(parties.keys()))
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]
    total_income = run_processes(participants, *clients)
    for income in total_income:
        assert income == expect_total_income

