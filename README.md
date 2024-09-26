# 提示词解析工具

将输入的提示词进行解析
> 知其然，亦要知其所以然

## 功能

- [x] 支持novel-ai与webui的提示词格式解析
- [x] 支持novel-ai转换为webui格式
- [x] 支持读取部分AI生成的图片数据并输出解析
- [x] 使用自动标记模型对输入的图片进行标记并输出解析
- [ ] 开启**严格模式**将不符合[danbooru标准](https://danbooru.donmai.us/wiki_pages/howto%3Atag "danbooru wiki中标记图片的标准")的提示词统统干掉！  
*（将提示词变得完全符合danbooru标准完全是作者个人的恶趣味）*
- [ ] 标签词典

## 关于自动标记

自动标记功能需要安装onnx运行时onnxruntime(ORT)才能正常运行，这部分考虑到不同运行环境的差异需要自行手动安装

```bash
./venv/Scripts/activate #激活虚拟环境
pip install onnxruntime
```

如果你拥有NVIDIA20系以上的显卡，你可以尝试安装onnxruntime-gpu来加速推理

具体安装说明可以参考[onnx官方文档](https://onnxruntime.ai/docs/install/#python-installs)
