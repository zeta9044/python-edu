#반응형 아키텍처, 어니언 아키텍처
#상태모델 - 일급함수
#파이썬은 여러줄의 익명함수를 쓸 수 없다.
class ValueStatus:
    def __init__(self):
        self.result = 0
        pass
    def current_value(self,val):
        return val
    def update_value(self,func):
        old_value = current_value
        new_value = func(old_value)
        current_value = new_value
        return current_value
    def value_cell(self,initial_value):
        return 



def value_cell(initial_value):
    def set_value():
        current_value = initial_value
        return current_value
    def update(f):
        old_value = set_value()
        new_value = f(old_value)
        current_value = new_value
        return current_value
    
    return dict(val=set_value(),update=update)

# print(value_cell(1))
# print(value_cell(1)['val'])
# print(value_cell(1)['update'](lambda x:x+1))

# chatGPT가 알려준 코드
class ValueCell:
    def __init__(self, initial_value):
        self._value = initial_value
    def val(self):
        return self._value
    def update(self, f):
        self._value = f(self._value)
        return self._value


add = value_cell(1)
print(add['val'])
print(add['update'](lambda x:x+1))

print(add)

add = ValueCell(1)
print(add)
print(add.update(lambda x : x+5))
print(add.val())
print(add.update(lambda x : x-5))
print(add.val())


