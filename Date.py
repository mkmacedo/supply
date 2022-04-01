from datetime import date, datetime

a = date.today().strftime('%B')
print(a)

datetime_obj = datetime.strptime('2020-02-02','%Y-%m-%d')


print(datetime_obj)


print('122.2'.replace('.', '').replace(',', '').isdigit())

print('1'.isdigit())

print(str(date.today().strftime('%b/%Y')).lower())


#print(a)