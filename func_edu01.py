
import copy as COPY

def object_set(object,key,value):
    copy = COPY.deepcopy(object)
    copy[key] = value
    return copy

def incrementField(item,field):
    return update_field(item,field,lambda value:value+1)


def update_field(item,field,modify):
    value = item[field]
    new_value = modify(value)
    new_item = object_set(item,field,new_value)
    return new_item

def update(object,key,modify):
    value = object[key]
    new_value = modify(value)
    new_object = object_set(object,key,new_value)
    return new_object
    
dic_test={'test':1}
print(incrementField(dic_test,'test'))

employee = dict(name="kim",salary=12000)

def raise_10persent(salary):
    return int(salary * 1.1)

print(update(employee,"salary",raise_10persent))

shirt = dict(name="shirt",price=13,options=dict(color="blue",size=3))
print(shirt)


def increment_size(item):
    options = item['options']
    size = options['size']
    new_size = size + 1
    new_options = object_set(options,'size',new_size)
    new_item = object_set(item,'options',new_options)
    return new_item

print(increment_size(shirt))

def increment_size2(item):
    return update(item,'options',lambda options:update(options,'size',lambda size:size+1))

print(increment_size2(shirt))

