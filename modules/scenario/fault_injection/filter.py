import numpy as np
import cv2
import time

from scenario import Scenario

class Filter(object):
    @staticmethod
    def get_filters():
        return  (BrightnessFilter.get_filters() +
                ContrastFilter.get_filters() +
                GaussianFilter.get_filters() +
                RainFilter.get_filters() +
                SnowFilter.get_filters() +
                OcclusionFilter.get_filters())
    
    @staticmethod
    def get_filter(filter_name):
        left_bracket_index = filter_name.find("(")
        if left_bracket_index != -1:
            name = filter_name[:left_bracket_index]
            parameters = filter_name[left_bracket_index + 1 : -1].split(",")
        else:
            name = filter_name
        if name == "contrast":
            return ContrastFilter(float(parameters[0]))
        elif name == "brightness":
            return BrightnessFilter(float(parameters[0]))
        elif name == "gaussian":
            return GaussianFilter(int(parameters[0]))
        elif name == "rain":
            return RainFilter()
        elif name == "snow":
            return SnowFilter()
        elif name == "occlusion":
            return OcclusionFilter(int(parameters[0]))
        else:
            return None

    def apply(self, image):
        return image
    
    def __str__(self):
        return "Clean Filter"

class BrightnessFilter(Filter):
    @staticmethod
    def get_filters():
        return ["brightness(30)", "brightness(60)", "brightness(90)"]
    
    def __init__(self, beta):
        self.__beta = beta
    
    def apply(self, image):
        return np.clip(image.astype("float") + self.__beta, 0, 255).astype("uint8")
    
    def __str__(self):
        return "brightness({})".format(self.__beta)

class ContrastFilter(Filter):
    @staticmethod
    def get_filters():
        return ["contrast(1.5)", "contrast(2.0)", "contrast(2.5)"]
    
    def __init__(self, alpha):
        self.__alpha = alpha
    
    def apply(self, image):
        return np.clip(self.__alpha * image.astype("float"), 0, 255).astype("uint8")
    
    def __str__(self):
        return "contrast({})".format(self.__alpha)

class GaussianFilter(Filter):
    @staticmethod
    def get_filters():
        return ["gaussian(7)"]
    
    def __init__(self, kernel_size):
        self.__kernel_size = kernel_size
    
    def apply(self, image):
        return cv2.GaussianBlur(image, (self.__kernel_size, self.__kernel_size), 0)
    
    def __str__(self):
        return "gaussian({})".format(self.__kernel_size)

class RainFilter(Filter):
    @staticmethod
    def get_filters():
        return ["rain"]
    
    def __init__(self):
        self.__drop_height = 7
        self.__thickness = 1
        self.__drop_color = (200, 200, 200)
        self.__kernel_size = 3
        self.__alpha = 0.5
        self.__drop_points = 1500
    
    def apply(self, image):
        for i in range(self.__drop_points):
            x = np.random.randint(0, image.shape[1])
            y = np.random.randint(0, image.shape[0] - self.__drop_height)
            cv2.line(image, (x, y), (x, y + self.__drop_height), self.__drop_color, self.__thickness)
        image = cv2.blur(image, (self.__kernel_size, self.__kernel_size))
        image = np.clip(self.__alpha * image.astype("float"), 0, 255).astype("uint8")
        return image
    
    def __str__(self):
        return "rain"

class SnowFilter(Filter):
    @staticmethod
    def get_filters():
        return ["snow"]
    
    def __init__(self):
        self.__kernel_size = 3
        self.__alpha = 0.5
        self.__sigma = 0.5
        self.__snow_points = 1500
    
    def apply(self, image):
        image = cv2.GaussianBlur(image, (self.__kernel_size, self.__kernel_size), 0)
        image = np.clip(self.__alpha * image.astype("float"), 0, 255).astype("uint8")
        snow_layer = np.zeros_like(image)
        for i in range(self.__snow_points):
            x = np.random.randint(0, image.shape[1])
            y = np.random.randint(0, image.shape[0])
            x_max = min(image.shape[1] - 1, x + 1)
            y_max = min(image.shape[0] - 1, y + 1)
            snow = (np.ones((y_max - y + 1, x_max - x + 1, 3)) * 255).astype("uint8")
            snow_layer[y : y_max + 1, x : x_max + 1] = snow
        snow_layer = cv2.GaussianBlur(snow_layer, (0, 0), self.__sigma)
        snow_mask = snow_layer > 0
        image = np.clip(np.logical_not(snow_mask) * image.astype("float") + snow_mask * snow_layer.astype("float"), 0, 255).astype("uint8")
        return image
    
    def __str__(self):
        return "snow"

class ContrastBrightnessFilter(Filter):
    @staticmethod
    def get_filters():
        contrast_range = np.linspace(1.2, 3.0, 5)
        brightness_range = np.linspace(10, 100, 5)
        filters = [ContrastBrightnessFilter(alpha, 0.0) for alpha in contrast_range]
        filters += [ContrastBrightnessFilter(1.0, beta) for beta in brightness_range]
        return filters

    def __init__(self, alpha, beta):
        self.__alpha = alpha
        self.__beta = beta
    
    def apply(self, image):
        return np.clip(self.__alpha * image.astype("float") + self.__beta, 0, 255).astype("uint8")
    
    def __str__(self):
        return "contrast_brightness_{}_{}".format(self.__alpha, self.__beta)
        #return "Contrast Brightness Filter[alpha={}, beta={}]".format(self.__alpha, self.__beta)

class BlurFilter(Filter):
    @staticmethod
    def get_filters():
        return [BlurFilter("average", 3), BlurFilter("average", 4), BlurFilter("average", 5), BlurFilter("average", 6),
                BlurFilter("gaussian", 3), BlurFilter("gaussian", 5), BlurFilter("gaussian", 7),
                BlurFilter("median", 3), BlurFilter("median", 5)]
    
    def __init__(self, mode, kernel_size):
        self.__mode = mode
        self.__kernel_size = kernel_size
    
    def apply(self, image):
        if self.__mode == "average":
            return cv2.blur(image, (self.__kernel_size, self.__kernel_size))
        elif self.__mode == "gaussian":
            return cv2.GaussianBlur(image, (self.__kernel_size, self.__kernel_size), 0)
        elif self.__mode == "median":
            return cv2.medianBlur(image, self.__kernel_size)
        else:
            return image
    
    def __str__(self):
        return "blur_{}_{}".format(self.__mode, self.__kernel_size)
        #return "Blur Filter[mode={}, kernel_size={}]".format(self.__mode, self.__kernel_size)

class OcclusionFilter(Filter):
    @staticmethod
    def get_filters():
        return ["occlusion(10)"]
    
    def __init__(self, occlusions_count):
        self.__sigma = 7.0
        self.__occlusions_count = occlusions_count
        self.__blur_offset = 5
    
    def apply(self, image):
        for i in range(self.__occlusions_count):
            x = np.random.randint(242, image.shape[1] - 242)
            y = np.random.randint(100, image.shape[0])
            radius = np.random.randint(5, 30)
            cv2.circle(image, (x, y), radius, (0, 0, 0), -1)
            x_min = max(0, x - radius - self.__blur_offset)
            x_max = min(image.shape[1] - 1, x + radius + self.__blur_offset)
            y_min = max(0, y - radius - self.__blur_offset)
            y_max = min(image.shape[0] - 1, y + radius + self.__blur_offset)
            pippo = cv2.GaussianBlur(image[y_min : y_max + 1, x_min : x_max + 1], (0, 0), self.__sigma)
            image[y_min : y_max + 1, x_min : x_max + 1] = pippo
        return image
    
    def __str__(self):
        return "occlusion"
        #return "Occlusion Filter[occlusions count={}]".format(self.__occlusions_count)

class FogFilter(Filter):
    @staticmethod
    def get_filters():
        return [FogFilter(5, 0.4), FogFilter(5, 0.6), FogFilter(5, 0.9),
                FogFilter(7, 0.4), FogFilter(7, 0.7), FogFilter(7, 0.9)]
    
    def __init__(self, kernel_size, alpha):
        self.__kernel_size = kernel_size
        self.__alpha = alpha
    
    def apply(self, image):
        random_noise = np.random.rand(*image.shape) * 100
        image = np.clip(image.astype("float") + random_noise, 0, 255).astype("uint8")
        image = cv2.GaussianBlur(image, (self.__kernel_size, self.__kernel_size), 0)
        image = np.clip(self.__alpha * image.astype("float"), 0, 255).astype("uint8")
        return image
    
    def __str__(self):
        return "fog_{}_{}".format(self.__alpha, self.__kernel_size)
        #return "Fog Filter[alpha={}, kernel size={}]".format(self.__alpha, self.__kernel_size)

#class SnowFilter(Filter):
#    @staticmethod
#    def get_filters():
#        return [SnowFilter(3, 0.5, 0.5)]
#    
#    def __init__(self, kernel_size, alpha, sigma):
#        self.__fog = FogFilter(kernel_size, alpha)
#        #super(FogFilter, self).__init__(kernel_size, alpha)
#        self.__sigma = sigma
#    
#    def apply(self, image):
#        image = self.__fog.apply(image)#super(FogFilter, self).apply(image)
#        snow_layer = np.zeros_like(image)
#        for i in range(1500):
#            x = np.random.randint(0, image.shape[1])
#            y = np.random.randint(0, image.shape[0])
#            x_max = min(image.shape[1] - 1, x + 1)
#            y_max = min(image.shape[0] - 1, y + 1)
#            snow = (np.ones((y_max - y + 1, x_max - x + 1, 3)) * 255).astype("uint8")
#            snow_layer[y : y_max + 1, x : x_max + 1] = snow
#        snow_layer = cv2.GaussianBlur(snow_layer, (0, 0), self.__sigma)
#        snow_mask = snow_layer > 0
#        image = np.clip(np.logical_not(snow_mask) * image.astype("float") + snow_mask * snow_layer.astype("float"), 0, 255).astype("uint8")
#        return image
#    
#    def __str__(self):
#        return "snow_{}_{}".format(self.__fog, self.__sigma)
#        #return "Snow Filter[{}, sigma={}]".format(self.__fog, self.__sigma)


    
if __name__ == "__main__":
    filters = Filter.get_filters()
    #print(len(filters))
    #for f in filters:
    #    print(f)

    scenario_path = Scenario.get_scenarios()[0]
    scenario = Scenario(scenario_path)

    #image = cv2.imread(scenario.images_paths[50], cv2.IMREAD_COLOR)
    #cv2.imshow("image",ContrastBrightnessFilter.get_filters()[8].apply(image))
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    for filter_name in Filter.get_filters():
        image = cv2.imread(scenario.images_paths[50], cv2.IMREAD_COLOR)
        filter = Filter.get_filter(filter_name)
        cv2.imshow(str(filter), filter.apply(image))
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    #for snow_filter in SnowFilter.get_filters():
        
    
    #filterr = SnowFilter(7, 0.4, 1)#ContrastBrightnessFilter(2.0, 0.0)
#
    #start = time.time()
#
    #image = cv2.imread(scenario.images_paths[50], cv2.IMREAD_COLOR)
    #filterr.apply(image)
#
    #end = time.time()
#
    #print((end - start) * 1000)

    #cv2.imshow('image', OcclusionFilter(10).apply(image))
    #cv2.waitKey(0)

    #cv2.imshow('image', BlurFilter("average", 6).apply(image))
    #cv2.waitKey(0)

    #cv2.imshow('image', ContrastBrightnessFilter(2.0, 0.0).apply(image))
    #cv2.waitKey(0)

    #cv2.imshow('image', SnowFilter(7, 0.4).apply(image))
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()