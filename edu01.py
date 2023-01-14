import pickle

test=[]
with open('test.pickle','wb') as f:
    pickle.dump([1,2,3],f)

with open('test.pickle','rb') as r:
    x = pickle.load(r)

print(x)

print(locals())
