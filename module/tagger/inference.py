import onnxruntime as onnx
import numpy as np
from PIL import Image
from .model_class import Model, TaggerOption
from .models import load_model


class Tagger:

    def load_model(self):
        model = load_model(self.option)
        if isinstance(model.model, onnx.InferenceSession):
            self._model = model.model
            _, height, width, _ = model.model.get_inputs()[0].shape
            self.target_size = max([height, width])
        else:
            raise RuntimeError()
        self.labels = model.labels

    def unload_model(self):
        del self._model
        self._model = None
        self.target_size = None
        self.labels = None

    def _model_loaded(func):
        def wrapper(self, *args, **kwargs):
            if not self._model:
                raise RuntimeError("model is not loaded!")
            return func(self, *args, **kwargs)

        return wrapper

    def __enter__(self):
        if not self._model:
            load_model()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.unload_model()
        return

    def __init__(self, option: TaggerOption) -> None:
        self.option = option
        self.target_size = None
        self._model = None
        self.labels = None
        self.load_model()

    @_model_loaded
    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        size = max(image.size)
        img = Image.new("RGB", (size, size), (255, 255, 255))
        pad_left = (size - image.width) // 2
        pad_top = (size - image.height) // 2
        img.paste(image, (pad_left, pad_top))
        resample = (
            Image.Resampling.BILINEAR
            if size > self.target_size
            else Image.Resampling.LANCZOS
        )
        img = img.resize((self.target_size, self.target_size), resample=resample)
        return np.array(img).astype(np.float32)

    # def preprocess_image(self,image:Image.Image) -> np.ndarray:
    #     img = np.array(image)
    #     size = max(img.shape[0:2])
    #     pad_x = size - img.shape[1]
    #     pad_y = size - img.shape[0]
    #     pad_left = pad_x // 2
    #     pad_top = pad_y // 2
    #     img = np.pad(
    #         img,
    #         ((pad_top, pad_y - pad_top),
    #         (pad_left, pad_x - pad_left), (0, 0)),
    #         mode="constant",
    #         constant_values=255
    #         )
    #     img = Image.fromarray(img)
    #     resample = Image.Resampling.BILINEAR if size > self.target_size else Image.Resampling.LANCZOS
    #     img = img.resize((self.target_size,self.target_size),resample=resample)
    #     return np.array(img)

    @_model_loaded
    def inference(self, image: Image.Image):
        img = self.preprocess_image(image)
        img = np.expand_dims(img, axis=0)
        input_name = self._model.get_inputs()[0].name
        label_name = self._model.get_outputs()[0].name
        predicts = self._model.run([label_name], {input_name: img})[0]
        return self.parse_predicts(predicts)

    @_model_loaded
    def parse_predicts(self, predicts):
        tag_names = self.labels[0]
        rating_indexes = self.labels[1]
        general_indexes = self.labels[2]
        character_indexes = self.labels[3]
        labels = list(zip(tag_names, predicts[0].astype(float)))
        ratings_names = [labels[i] for i in rating_indexes]
        general_names = [labels[i] for i in general_indexes]
        character_names = [labels[i] for i in character_indexes]
        rating = tuple(ratings_names)
        general = tuple(general_names)
        character = tuple(character_names)
        return (rating, general, character)
