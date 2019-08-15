import cv2
import numpy as np
import csv
import os
import random
import keras
import shutil
from model import combin_model
from makedataset import read_json
from keras.preprocessing import image

tensorboard_logdir = './Graph'


class sample:
    def __init__(self, row):
        self.image = row[0]
        self.MachineDefect = int(row[1])
        self.ConfirmDefect = int(row[2])
        self.Status = int(row[3])
        self.AlgorithmDefect = int(row[4])


class SplitDataset:
    def __init__(self, filename, config, sample_scale=8, preprocess=None):
        self.config = config
        self.sample_scale = sample_scale
        self.preprocess = preprocess
        with open(filename+'_falsecall.csv') as f:
            rows = csv.reader(f)
            self.falsecall_rows = [sample(row) for row in rows]
        with open(filename+'_defect.csv') as f:
            rows = csv.reader(f)
            self.defect_rows = [sample(row) for row in rows]

        self.size = len(self.defect_rows)*sample_scale

        self.machine_i = np.identity(len(self.config['MachineDefect']))
        self.out_i = np.identity(2)
        self.algorithm_i = np.identity(len(self.config['AlgorithmDefect']))

    def getItem(self, rows):
        imfs = []
        machines = []
        OPs = []
        algorithms = []
        for sample in rows:
            machines.append(self.machine_i[sample.MachineDefect])
            algorithms.append(self.algorithm_i[sample.AlgorithmDefect])
            OPs.append(self.out_i[sample.ConfirmDefect])

            im = cv2.imread(sample.image)
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            if self.preprocess:
                im = self.preprocess.random_transform(im)
            imf = np.asarray(im, dtype=np.float)*1.0/255
            if imf.shape != (50, 50, 3):
                print(imf.shape)
            imfs.append(imf)
        t = []
        t.append(np.array(imfs))
        t.append(np.array(machines))
        t.append(np.array(OPs))
        t.append(np.array(algorithms))
        print(t[0].shape, t[1].shape, t[2].shape, t[3].shape)
        return t

    def getSample(self, batch_size):
        indices = []
        indices.extend(random.sample(self.defect_rows, batch_size//self.sample_scale))
        indices.extend(random.sample(self.falsecall_rows, batch_size-len(indices)))
        return indices

    def data_gen(self, batch_size=32):
        while True:
            indices = self.getSample(batch_size)
            img, machines, op, algor = self.getItem(indices)
            Y = op
            X = {
                    'MachineDefect': machines,
                    'AlgorithmDefect': algor,
                    'AOI_Image': img
                }
            yield (X, Y)


class DataSet(SplitDataset):
    def __init__(self, filename, config):
        super(DataSet, self).__init__(filename, config)
        self.rows = []
        self.rows.extend(self.falsecall_rows)
        self.rows.extend(self.defect_rows)
        random.shuffle(self.rows)
        self.size = len(self.rows)

    def getSample(self, batch_size):
        return random.sample(self.rows, batch_size)


def train(config, trainset, verifyset, batch_size=128, save_weight='model_1.h5'):
    from keras.callbacks import TensorBoard

    if os.path.isdir(tensorboard_logdir):
        shutil.rmtree(tensorboard_logdir, ignore_errors=True)
    os.mkdir(tensorboard_logdir)

    tbCallback = TensorBoard(
        log_dir=tensorboard_logdir,
        histogram_freq=0,
        write_graph=True,
        write_images=True
        )
    # fine-tune the model
    callbacks = [tbCallback]

    model = combin_model(len(config['MachineDefect']), len(config['AlgorithmDefect']))
    model.compile(
        loss='categorical_crossentropy',
        optimizer=keras.optimizers.adam(lr=0.001, decay=4e-3),
        metrics=['accuracy']
    )
    model.summary()
    try:
        model.fit_generator(
            trainset.data_gen(batch_size=batch_size),
            steps_per_epoch=trainset.size//batch_size,
            epochs=200,
            validation_data=verifyset.data_gen(batch_size=batch_size),
            validation_steps=verifyset.size//batch_size,
            verbose=1,
            callbacks=callbacks
        )
    except KeyboardInterrupt:
        pass
    model.save_weights(save_weight)


if __name__ == "__main__":
    config = read_json(os.path.join('dataset', 'config.json'))
    datagen = image.ImageDataGenerator(
        rotation_range=5,
        width_shift_range=0.02,
        height_shift_range=0.02,
        horizontal_flip=True
    )
    trainset = SplitDataset('/home/mark/result/train', config, sample_scale=16, preprocess=datagen)
    verifyset = SplitDataset('/home/mark/result/test', config, sample_scale=2)
    print(trainset.size, verifyset.size)
    train(config, trainset, verifyset, batch_size=32)
