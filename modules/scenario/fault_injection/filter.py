import numpy as np
import cv2

class Filter(object):
    @staticmethod
    def get_filters():
        return  ContrastBrightnessFilter.get_filters() +
                BlurFilter.get_filters()

    def apply(self, image):
        return image
    
    def __str__(self):
        return "Clean Filter"

class ContrastBrightnessFilter(Filter):
    @staticmethod
    def get_filters():
        brightness_range = np.linspace(1.2, 3.0, 10)
        contrast_range = np.linspace(10, 100, 10)
        combinations = np.array(np.meshgrid(brightness_range, contrast_range)).T.reshape(-1, 2)
        return [ContrastBrightnessFilter(alpha, beta) for alpha, beta in combinations]

    def __init__(self, alpha, beta):
        self.__alpha = alpha
        self.__beta = beta
    
    def apply(self, image):
        return np.clip(self.__alpha * image.astype("float") + self.__beta, 0, 255).astype("uint8")
    
    def __str__(self):
        return "Contrast Brightness Filter{alpha={}, beta={}}".format(self.__alpha, self.__beta)

class BlurFilter(Filter):
    @staticmethod
    def get_filters():
        return []
    
    def __init__(self, mode, kernel_size):
        self.__mode = mode
        self.__kernel_size = kernel_size
    
    def apply(self, image):
        if self.__mode == "average":
            return cv2.blur(image, self.__kernel_size)
        elif self.__mode == "gaussian":
            return cv2.GaussianBlur(image, self.__kernel_size, 0)
        elif self.__mode == "median":
            return cv2.medianBlur(image, self.__kernel_size)
        else:
            return image
    
    def __str__(self):
        return "Blur Filter{mode={}, kernel_size={}}".format(self.__mode, self.__kernel_size)