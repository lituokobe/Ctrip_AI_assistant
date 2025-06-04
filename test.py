s = '[][(){}{}{}()(([))()()()]'

while True:
   a = len(s)
   s = s.replace('()','').replace('{}', '').replace('[]', '')
   if a == len(s):
       break

print(s=='')