#반응형 아키텍처, 어니언 아키텍처
#상태모델 - 일급함수
#파이썬은 여러줄의 익명함수를 쓸 수 없다.
#javascript의 function은 python에서는 class로 만든다.

# chatGPT가 알려준 코드
class ValueCell:
    def __init__(self, initialValue):
        self.currentValue = initialValue

    def val(self):
        return self.currentValue

    def update(self, f):
        oldValue = self.currentValue
        newValue = f(oldValue)
        self.currentValue = newValue


mul = ValueCell(1)
mul.update(lambda x : (x+1)**2)
print(mul.val())
mul.update(lambda x : (x+1)**2)
print(mul.val())
