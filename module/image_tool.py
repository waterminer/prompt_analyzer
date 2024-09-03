from PIL import Image
import json, re
from dataclasses import dataclass, field


@dataclass()
class Image_metadata:
    prompt: str = field(default="")
    negative_prompt: str = field(default="")
    steps: int = field(default=28)
    resolution: tuple[int, int] = field(default=(512, 512))
    seed: str = field(default="0")
    sampler: str = field(default="k_euler")


def resolution_nai_image(metadata: dict) -> Image_metadata:
    temp: dict = json.loads(metadata.get("Comment", "{}"))
    return Image_metadata(
        prompt=temp.get("prompt", ""),
        negative_prompt=temp.get("uc", ""),
        steps=temp.get("steps", 28),
        resolution=(temp.get("width", 512), temp.get("height", 512)),
        seed=temp.get("seed", "0"),
        sampler=temp.get("sampler", "unknown"),
    )


def resolution_webui_image(metadata: dict) -> Image_metadata:
    metadata = metadata.get("parameters", "")
    res = metadata.split("\n")
    pattern = re.compile(r"(.*?):(.*?)(?:,|$)")
    prompt = ",".join(res[0:-2])
    negative_prompt = res[-2].lstrip("Negative prompt: ")
    other_parameters = {k.strip(): v.strip() for k, v in pattern.findall(res[-1])}
    other_parameters["Size"] = tuple(map(int, other_parameters.get("Size").split("x")))
    return Image_metadata(
        prompt=prompt,
        negative_prompt=negative_prompt,
        steps=int(other_parameters.get("Steps", 28)),
        resolution=other_parameters.get("Size"),
        seed=other_parameters.get("Seed"),
        sampler=other_parameters.get("Sampler", "unknown"),
    )


def resolution_comfy_image(metadata: dict, *, size=(0, 0)):
    workflow: dict = json.loads(metadata.get("workflow", "{}"))
    input_data: dict = json.loads(metadata.get("prompt", "{}"))
    sampler_id = None
    for node in workflow.get("nodes"):
        if node.get("type") == "KSampler":
            sampler_id = str(node.get("id"))
            break
    if sampler_id is None:
        return None
    resolution = size
    sampler_node = input_data[sampler_id]["inputs"]
    latent_image = input_data.get(str(sampler_node["latent_image"][0]))
    match latent_image.get("class_type"):
        case "EmptyLatentImage":
            latent_image = latent_image.get("inputs")
            resolution = (latent_image["width"], latent_image["height"])
        case _:
            pass
    prompt = input_data.get(str(sampler_node["positive"][0]))["inputs"]["text"]
    negative_prompt = input_data.get(str(sampler_node["negative"][0]))["inputs"]["text"]
    steps = sampler_node.get("steps")
    seed = str(sampler_node.get("seed"))
    sampler = sampler_node.get("sampler")
    return Image_metadata(
        prompt=prompt,
        negative_prompt=negative_prompt,
        steps=steps,
        resolution=resolution,
        seed=seed,
        sampler=sampler
    )


def read_image_info(image: Image.Image | None) -> Image_metadata | None:
    if not image:
        return
    metadata = image.info
    match metadata.keys():
        case key if "Comment" in key:
            return resolution_nai_image(metadata)
        case key if "parameters" in key:
            return resolution_webui_image(metadata)
        case key if ("workflow" in key) and ("prompt" in key):
            return resolution_comfy_image(metadata, size=image.size)
        case _:
            return None
