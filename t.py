s1 = '/record   12x 3'

s2 = s1.split(' ', maxsplit=1)
print(s2[1])

num = ''.join(s2[1].split())
print(num)
print(num.isdigit())