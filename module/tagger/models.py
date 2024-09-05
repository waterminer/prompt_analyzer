import os
import pandas as pd
import numpy as np
import onnxruntime as onnx
from huggingface_hub import hf_hub_download

from .model_class import WD_Model,Model,TaggerOption


def read_label(data_frame:pd.DataFrame):
    name_series = data_frame["name"].tolist()
    rating_indexes = list(np.where(data_frame["category"] == 9)[0])
    general_indexes  = list(np.where(data_frame["category"] == 0)[0])
    character_indexes  = list(np.where(data_frame["category"] == 4)[0])
    return (name_series,rating_indexes,general_indexes,character_indexes)

def load_csv(path:str):
    csv = pd.read_csv(path)
    return read_label(csv)

def download_wd_model(model:WD_Model,model_path:str) -> Model:
    hf_hub_download(
        repo_id = model.repo_id,
        filename = model.MODEL_FILENAME,
        cache_dir = model_path,
        force_download=True,
        force_filename=model.MODEL_FILENAME
    )
    hf_hub_download(
        repo_id=model.repo_id,
        filename=model.LABEL_FILENAME,
        cache_dir=model_path,
        force_download=True,
        force_filename=model.LABEL_FILENAME
    )

def load_model(option:TaggerOption) -> Model:
    model_type = option.model_type
    path = option.model_path
    if isinstance(model_type,WD_Model):
        model_meta = model_type
        path = os.path.join(path,model_meta.id)
        if not os.path.exists(path) or option.force_download:
            os.makedirs(path,exist_ok=True)
            download_wd_model(model_meta,path)
        model_path = os.path.join(path,model_meta.MODEL_FILENAME)
        label_path = os.path.join(path,model_meta.LABEL_FILENAME)
        if not option.use_cpu and onnx.get_device()=="GPU":
            providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
        else:
            providers=['CPUExecutionProvider']
        try:
            model = onnx.InferenceSession(model_path,providers=providers)
        except:
            model = onnx.InferenceSession(model_path)
        labels = load_csv(label_path)
    else:
        raise RuntimeError()
    
    class Model_imp(Model):
        def __init__(self, model, labels) -> None:
            super().__init__(model, labels)

    return Model_imp(model,labels)
