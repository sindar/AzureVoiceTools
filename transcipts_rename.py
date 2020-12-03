with open('transcipts.txt','r') as fin:
    lines = fin.readlines()
    with open('transcipts_m.txt', 'w') as fout:
        for line in lines:
            line = '10000' + line
            fout.write(line)
