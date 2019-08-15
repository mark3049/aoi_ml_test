import os
import numpy as np
from sklearn.metrics import confusion_matrix

from model import combin_model
from train import DataSet
from makedataset import read_json

if __name__ == "__main__":
    config = read_json(os.path.join('dataset', 'config.json'))
    verifyset = DataSet('/home/mark/result/test', config)
    model = combin_model(len(config['MachineDefect']), len(config['AlgorithmDefect']))
    model.load_weights('model_1.h5')

    count = 0
    y_true = []
    y_predict = []
    total = verifyset.size//512
    print("total", total)

    for X, Y_true in verifyset.data_gen(batch_size=512):
        Y_predict = model.predict(X)
        for i in range(512):
            y_true.append(np.argmax(Y_true[i]))
            y_predict.append(np.argmax(Y_predict[i]))

        count += 1
        print('\r', count, end=' ', flush=True)
        if count > total:
            break
    c = confusion_matrix(y_true, y_predict)
    print(c)
    pass
