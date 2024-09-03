from module import analyze_prompt, GrammarError, read_image_info
from json import dumps
import gradio as gr
from git.repo import Repo
from PIL.Image import Image

head = """
<head>
    <script>
        function main(input) {
            let data = JSON.parse(input);
            let div = document.getElementById("result");
            div.innerHTML="<p><b>标签说明</b></p>"
            function get_text_style(category){
                let text_style;
                switch (category) {
                        case 0:
                            text_style = "color: var(--general_color);";
                            break;
                        case 1:
                            text_style = "color: var(--artist_color);";
                            break;
                        case 3:
                            text_style = "color: var(--copyright_color);";
                            break;
                        case 4:
                            text_style = "color: var(--character_color);";
                            break;
                        case 5:
                            text_style = "color: var(--meta_color);";
                            break;
                        default:
                            text_style = "color: var(--wrong_color);";
                            break;
                    }
                return text_style
            }
            function showInfo(tag) {
                let element = document.getElementById("tag_info");
                element.innerHTML = "";
                element.style.visibility = "visible";
                element.style.opacity = 1;
                innerHTML = `<h1 style="color:var(--wrong_color);">未被登记的标签</h1><h3>数据库中无该标签信息，它可能是一个拼写错误的标签</h3>`;
                if (tag.detail) {
                    title_style = get_text_style(tag.detail.category);
                    title = tag.detail.name;
                    post_count = tag.detail.post_count;
                    translation = tag.detail.translation;
                    description = tag.detail.description;
                    wiki = tag.detail.wiki;
                    innerHTML = `<h1><a href="https://danbooru.donmai.us/posts?tags=${title}" style="${title_style}text-decoration:none;" target="_blank">${title}</a></h1><h3>引用数:</h3>${post_count}`;
                    if (translation) {
                        innerHTML += `<h3>翻译:</h3>${translation}`;
                    }
                    if (description) {
                        innerHTML += `<h3>说明:</h3>${description}`;
                    }
                    if (wiki) {
                        innerHTML += `<p><a style="color:gray;text-decoration: underline;" href="https://danbooru.donmai.us/wiki_pages/${wiki}" target="_blank">前往danbooru wiki了解更多</a></p>`;
                    }

                }
                element.style.height = "auto";
                innerElement = document.createElement("div");
                innerElement.style.transition = "opacity 1s var(--ease-out-quart)";
                innerElement.visibility = "hidden";
                innerElement.style.opacity = 0;
                innerElement.innerHTML = innerHTML;
                element.append(innerElement);
                innerElement.style.opacity = 1;
            }
            for (let element of data) {
                let text_style = "color: var(--wrong_color);";
                if (element.detail) {
                    text_style = get_text_style(element.detail.category);
                    if(element.detail.name != element.name){
                        text_style += "text-decoration: yellow wavy underline;";
                    }else if(element.detail.is_deprecated){
                        text_style += "text-decoration: red wavy underline;";
                    }else{
                        text_style += "text-decoration: none;";
                    }
                }else{
                    text_style += "text-decoration: none;";
                }
                let texture = document.createElement("a");
                texture.href = "#";
                texture.addEventListener("click", () => { showInfo(element) });
                texture.id = element.name;
                texture.style = text_style;
                texture.innerText = `${element.name}`;
                div.append(texture, " ");
            }
        }
    </script>
    <style>
        :root {
            --ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
            --general_color: #009be6;
            --artist_color: #ff8a8b;
            --copyright_color: #a800aa;
            --character_color: #00ab2c;
            --meta_color: #fd9200;
            --wrong_color: #ca0000;
        }

        #result {
            padding: 0.5cap;
            border: var(--block-border-width) solid var(--border-color-primary);
            border-radius: 8px;
            margin: 1cap;
            background: var(--border-color-primary);
        }

        .tag_info {
            padding: 0.5cap;
            margin: 1cap;
            width: auto;
            box-sizing: border-box;
            border: var(--block-border-width) solid var(--border-color-primary);
            border-radius: 8px;
            visibility: hidden;
            opacity: 0;
            background: var(--border-color-primary);
        }
    </style>
</head>
"""
html = """
<div id="result">
<h1>提示词解析工具</h1>
<p>输入提示词提交后将会在这里显示解析后结果</p>
<p><b style="color:var(--wrong_color);font-weight:bold;">红色</b>标签表示这个标签可能没有被danbooru收录或是被引用数过少，可能是无效的标签</p>
<p><b style="color:var(--general_color);font-weight:bold;text-decoration: yellow wavy underline;">黄色波浪线</b>
表示这个标签有被danbooru收录，但是它是一个别称，可能是无效的标签</p>
<p><b style="color:var(--general_color);font-weight:bold;text-decoration: red wavy underline;">红色波浪线</b>
表示这个标签曾经被danbooru收录，但是它现在已经被弃用，可能是无效的标签。弃用标签往往含义过于宽泛，删除有助于标签的简洁</p>
</div>
<div id="tag_info" class="tag_info">
"""
with gr.Blocks(head=head) as app:
    with gr.Tabs(selected="main") as tabs:
        with gr.Tab("主窗口",id="main") as main:
            with gr.Row():
                with gr.Column():
                    with gr.Group():
                        prompt = gr.Text(label="提示词",interactive=True)
                        prompt_type = gr.Radio(
                            [("novel ai", "nai"), ("webui", "webui")],
                            label="提示词类型",
                            value="nai",
                        )
                    submit = gr.Button(value="提交")
                    webui_prompt = gr.Text(label="nai→webui")
                    
                with gr.Column():
                    html_window = gr.HTML(html)
                    state = gr.State()
                    result_json = gr.Textbox(visible=False)

            @prompt_type.change(inputs=prompt_type, outputs=webui_prompt)
            def hide_webui_prompt(prompt_type):
                match prompt_type:
                    case "webui":
                        return gr.update(visible=False)
                    case "nai":
                        return gr.update(visible=True)

            @submit.click(inputs=[prompt, prompt_type], outputs=[result_json, state])
            def submit_onclick(prompt, prompt_type):
                try:
                    tag_list = analyze_prompt(prompt, mode=prompt_type)
                    res = dumps(
                        list(map(lambda x: x.__dict__, tag_list)),
                        ensure_ascii=False,
                    )
                except GrammarError as e:
                    raise gr.Error(e)
                except Exception as e:
                    res = []
                    print(e)
                return res, tag_list

            result_json.change(fn=None, inputs=result_json, js="(x)=>main(x)")

            @state.change(inputs=state, outputs=webui_prompt)
            def nai2webui(state):
                res_list = []
                for tag in state:
                    weight = tag.weight
                    name:str = tag.name.replace("(","\\(").replace(")","\\)")
                    if weight != 1:
                        name = f"({name}:{weight})"
                    res_list.append(name)
                return ",".join(res_list)

        with gr.Tab("读取图片",id="image_tools") as image_tools:
            with gr.Row():
                image = gr.Image(type="pil",height="512px")
                with gr.Column():
                    image_meta = gr.Text()
                    image_meta_state = gr.State()
                    send_to_prompt_analyzer_button = gr.Button("发送到分析工具")

                
            @image.change(inputs=image,outputs=[image_meta,image_meta_state])
            def show_meta(image:Image|None):
                metadata = read_image_info(image)
                if not metadata:
                    return "",image_meta_state.value
                res = f"""
            prompt:{metadata.prompt}\n
            negative_prompt:{metadata.negative_prompt}\n
            steps:{metadata.steps}\n
            resolution:{metadata.resolution[0]}x{metadata.resolution[1]}\n
            seed:{metadata.seed}\n
            sampler:{metadata.sampler}\n
            """
                return res,metadata

            @send_to_prompt_analyzer_button.click(inputs=image_meta_state,outputs=[prompt,tabs])
            def send_to_prompt_analyzer(metadata):
                if metadata:
                    return metadata.prompt,gr.Tabs(selected="main")
                return "",gr.Tabs(selected="image_tools")

if __name__ == "__main__":
    try:
        with Repo(".") as repo:
            print("initializing database...")
            repo.submodule_update(init=True)
    except Exception as e:
        print(f"initializing database failed!\n{e}")
    app.launch()