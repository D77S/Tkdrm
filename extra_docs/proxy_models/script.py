from app.models import CustPlace1Acc, Rtu

# CustPlace1Acc.objects.bulk_create([
#     CustPlace1Acc(title="Тест название 1",
#                       code="Тест код 1", address="Тест адрес 1",
#                       type=CustPlace1Acc.Type.RTU),
#     CustPlace1Acc(title="Тест название 2",
#                       code="Тест код 2", address="Тест адрес 2",
#                       type=CustPlace1Acc.Type.RTU),
#     CustPlace1Acc(title="Тест название 1",
#                       code="Тест код 3", address="Тест адрес 3",
#                       type=CustPlace1Acc.Type.CUST_HOUSE),
#     ])
print(Rtu.objects.all())
# не надо указывать тип
Rtu.objects.create(title="Ещё какое-то РТУ",
                   code="Код",
                   address="улица Пушкина, дом Колотушкина")
print(Rtu.objects.all())