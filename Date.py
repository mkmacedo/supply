from datetime import date, datetime

a = date.today()
print(a)

datetime_obj = datetime.strptime('2020-02-02','%Y-%m-%d')


print(datetime_obj)


print('122.2'.replace('.', '').replace(',', '').isdigit())

print('1'.isdigit())