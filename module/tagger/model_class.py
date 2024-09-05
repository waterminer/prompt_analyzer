from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


class ModelType(ABC):
    pass


class WD_Model(ModelType, ABC):
    MODEL_FILENAME = "model.onnx"
    LABEL_FILENAME = "selected_tags.csv"
    MODEL_AUTHOR_ID = "SmilingWolf"

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    def repo_id(self) -> str:
        return f"{self.MODEL_AUTHOR_ID}/{self.id}"


class Wd14MoatV2(WD_Model):
    _ID = "wd-v1-4-moat-tagger-v2"

    @property
    def id(self) -> str:
        return self._ID


class Wd14VitV2(WD_Model):
    _ID = "wd-v1-4-vit-tagger-v2"

    @property
    def id(self) -> str:
        return self._ID


class Wd14Swinv2V2(WD_Model):
    _ID = "wd-v1-4-swinv2-tagger-v2"

    @property
    def id(self) -> str:
        return self._ID


class Wd14ConvnextV2(WD_Model):
    _ID = "wd-v1-4-convnext-tagger-v2"

    @property
    def id(self) -> str:
        return self._ID


class Wd14Convnext2V2(WD_Model):
    _ID = "wd-v1-4-convnextv2-tagger-v2"

    @property
    def id(self) -> str:
        return self._ID


class WdVitV3(WD_Model):
    _ID = "wd-vit-tagger-v3"

    @property
    def id(self) -> str:
        return self._ID


class WdSwinV2V3(WD_Model):
    _ID = "wd-swinv2-tagger-v3"

    @property
    def id(self) -> str:
        return self._ID


class WdConvnextV3(WD_Model):
    _ID = "wd-convnext-tagger-v3"

    @property
    def id(self) -> str:
        return self._ID


class Model(ABC):
    model: any
    labels: any

    def __init__(self, model, labels) -> None:
        self.model = model
        self.labels = labels


@dataclass
class TaggerOption:
    force_download: bool = field(default=False)
    model_type: ModelType = field(default=WdConvnextV3())
    model_path: str = field(default="./models")
    undesired_tags: str = field(default="")
    batch_size: int = field(default=1)
    max_data_loader_n_workers: int = field(default=None)
    remove_underscore: bool = field(default=True)
    thresh: float = field(default=0.35)
    character_threshold: float = field(default=None)
    general_threshold: float = field(default=None)
    order_by_name: bool = field(default=False)
    use_cpu: bool = field(default=False)

    TYPE_LIST = [
        "wd-v1-4-moat-tagger-v2",
        "wd-v1-4-vit-tagger-v2",
        "wd-v1-4-swinv2-tagger-v2",
        "wd-v1-4-convnext-tagger-v2",
        "wd-v1-4-convnextv2-tagger-v2",
        "wd-vit-tagger-v3",
        "wd-swinv2-tagger-v3",
        "wd-convnext-tagger-v3"
    ]

    def set_model_type(self, type: str):
        match type:
            case "wd-v1-4-moat-tagger-v2":
                self.model_type = Wd14MoatV2()
            case "wd-v1-4-vit-tagger-v2":
                self.model_type = Wd14VitV2()
            case "wd-v1-4-swinv2-tagger-v2":
                self.model_type = Wd14Swinv2V2()
            case "wd-v1-4-convnext-tagger-v2":
                self.model_type = Wd14ConvnextV2()
            case "wd-v1-4-convnextv2-tagger-v2":
                self.model_type = Wd14Convnext2V2()
            case "wd-vit-tagger-v3":
                self.model_type = WdVitV3()
            case "wd-swinv2-tagger-v3":
                self.model_type = WdSwinV2V3()
            case "wd-convnext-tagger-v3":
                self.model_type = WdConvnextV3()
            case _:
                raise RuntimeError("Invalid Input Error")
