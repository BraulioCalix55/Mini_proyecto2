import json
import os

path = os.getcwd()
name_list = os.listdir('./training_set')
f = open('./gt_train_set.json')
data = json.load(f)
val = []

def find(val,marca):
    flag = True
    for i in val:
        if i == marca:
            flag = False
            break;
    return flag

for i in name_list:
    marca = data[str(i)]['marca']
    if len(val) == 0:
        val.append(marca)
        os.system('mkdir "' + path + str(chr(92)) + "training_set" + str(chr(92)) + marca + '"')
        os.system('move "' + path + str(chr(92)) + "training_set" + str(chr(92)) + i + '" '
                  + '"'+ path + str(chr(92)) + "training_set" + str(chr(92)) + marca +'"')

    else:
        if find(val,marca):
            val.append(marca)
            os.system('mkdir "'+path+str(chr(92))+"training_set"+str(chr(92))+marca+'"')
            os.system('move "' + path + str(chr(92)) + "training_set" + str(chr(92)) + i + '" '
                      + '"' + path + str(chr(92)) + "training_set" + str(chr(92)) + marca + '"')

        else:
            os.system('move "' + path + str(chr(92)) + "training_set" + str(chr(92)) + i + '" '
                      + '"' + path + str(chr(92)) + "training_set" + str(chr(92)) + marca + '"')


f.close()