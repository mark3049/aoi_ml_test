from keras.preprocessing import image
import numpy as np


class ImageDataPreprocessing:
    def __init__(
        self,
        rotation_range=None,
        width_shift_range=None,
        height_shift_range=None,
        shear_range=None,
        zoom_range=None,
        horizontal_flip=False,
    ):
        self.rotation_range = rotation_range
        self.width_shift_range = width_shift_range
        self.height_shift_range = height_shift_range
        self.shear_range = shear_range

        self.zoom_range = [1 - zoom_range, 1 + zoom_range] if zoom_range else None
        self.horizontal_flip = horizontal_flip

    def apply(self, x):
        if self.rotation_range:
            x = image.random_rotation(x, self.rotation_range)
        if self.width_shift_range and self.height_shift_range:
            x = image.random_shift(
                x, self.width_shift_range, self.height_shift_range)
        if self.shear_range:
            x = image.random_shear(x, self.shear_range)
        if self.zoom_range:
            x = image.random_zoom(x, self.zoom_range)
        return x


if __name__ == "__main__":
    datagen = image.ImageDataGenerator(
        rotation_range=5,
        width_shift_range=0.02,
        height_shift_range=0.02,
        horizontal_flip=True
    )
    p = ImageDataPreprocessing(
        #rotation_range=5,
        #width_shift_range=0.2,
        #height_shift_range=0.2,
        shear_range=0.9,
        # zoom_range=0.05,
    )
    x = image.load_img("t.png")
    im = image.img_to_array(x)
    ims = np.array([im])
    for i in range(50):
        a = datagen.random_transform(im)
        dest = "test/test{0}.jpg".format(i)
        image.save_img(dest, image.array_to_img(a))
    print("finish")
