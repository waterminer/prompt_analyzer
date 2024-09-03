from typing import Iterator
from .database import Database
from dataclasses import dataclass


@dataclass
class _Tag:
    def __init__(self, tag: str, weight: float) -> None:
        self.name = tag.strip()
        self.name = self.name.replace(" ", "_")
        self.weight: float = weight
        self.detail: dict | None = None
        with Database() as db:
            sql_res = db.query(
                f"""
                SELECT * FROM Tag
                WHERE name="{self.name}" 
                OR id IN (
                SELECT TagAlias.consequent_id
                FROM TagAlias
                WHERE name="{self.name}")
                """
            ).fetchone()
        if sql_res:
            (
                id,
                name,
                category,
                is_deprecated,
                post_count,
                translation,
                description,
                wiki,
            ) = sql_res
            self.detail = {
                "id": id,
                "name": name,
                "category": category,
                "is_deprecated": is_deprecated,
                "post_count": post_count,
                "translation": translation,
                "wiki": wiki,
                "description": description,
            }

    def set_weight(self, weight: float):
        self.weight = weight
        return self


def nai_prompt_parser(string_iter: Iterator, bracket=None, weight=1) -> list[_Tag]:
    def combine_character():
        if uncombined_character:
            name = "".join(uncombined_character)
            res.append(_Tag(name, weight))
            uncombined_character.clear()

    uncombined_character = []
    res = []
    for character in string_iter:
        match character:
            case "{":
                res.extend(nai_prompt_parser(string_iter, character, weight * 1.05))
            case "[":
                res.extend(nai_prompt_parser(string_iter, character, weight * 0.95))
            case char if (bracket == "{" and char == "}") or (
                bracket == "[" and char == "]"
            ):
                combine_character()
                return res
            case "," | "|":
                combine_character()
            case _:
                uncombined_character.append(character)
    combine_character()
    if bracket is not None:
        raise UnmatchedBracketError("语法错误，请检查括号匹配情况")
    return res


def webui_prompt_parser(string_iter: Iterator, bracket_flag=None) -> list[_Tag]:
    res: list[_Tag] = []
    uncombined_character: list[str] = []

    def get_weight():
        uncombined_character = []
        NUM = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]
        for character in string_iter:
            if character in NUM:
                uncombined_character.append(character)
            elif character == ")":
                return float("".join(uncombined_character))
            else:
                raise GrammarError("语法错误，请检查输入")

    def skip_to_closed(close_bracket: str):
        for character in string_iter:
            if character == close_bracket:
                return

    def convert_prompt_editing():
        for character in string_iter:
            match character:
                case ":":
                    skip_to_closed("]")
                    break
                case ",":
                    combine_character()
                case "(" | ")" | "[":
                    raise GrammarError("语法错误，请检查输入")
                case "]":
                    break
                case _:
                    uncombined_character.append(character)
        combine_character()

    def combine_character():
        if uncombined_character:
            name = "".join(uncombined_character)
            res.append(_Tag(name, 1.0))
            uncombined_character.clear()

    def escape(func):
        def warper(*args, **kwargs):
            if uncombined_character:
                if uncombined_character[-1] == "\\":
                    uncombined_character[-1] = character
                else:
                    combine_character()
                    func()
            else:
                func()

        return warper

    @escape
    def colon():
        if bracket_flag == "(":
            combine_character()
            for tag in res:
                tag.set_weight(get_weight())
        if bracket_flag == "[":  # 遇到方括号则判断为动态提示
            combine_character()
            convert_prompt_editing()

    @escape
    def bracket():
        res.extend(webui_prompt_parser(string_iter, "("))

    @escape
    def square_brackets():
        res.extend(webui_prompt_parser(string_iter, "["))

    @escape
    def angle_brackets():
        skip_to_closed(">")

    for character in string_iter:
        match character:
            case ":":
                colon()
                return res
            case "<":  # 跳过lora引用框
                angle_brackets()
            case "(":
                bracket()
            case "[":
                square_brackets()
            case char if (bracket_flag == "(" and char == ")") or (
                bracket_flag == "[" and char == "]"
            ):
                if uncombined_character:
                    if uncombined_character[-1] == "\\":
                        uncombined_character[-1] = character
                        continue
                    else:
                        combine_character()
                if bracket_flag == "(":
                    res = [tag.set_weight(tag.weight * 1.1) for tag in res]
                    return res
                elif bracket_flag == "[":
                    res = [tag.set_weight(tag.weight * 0.9) for tag in res]
                    return res
            case ",":
                combine_character()
            case _:
                uncombined_character.append(character)
    combine_character()
    if bracket_flag is not None:
        raise UnmatchedBracketError("语法错误，请检查括号匹配情况")
    return res


def analyze_prompt(texture: str, *, mode="nai"):
    pretreatment_text = texture.lower()
    string_iter = iter(pretreatment_text)
    match mode:
        case "nai":
            return nai_prompt_parser(string_iter)
        case "webui":
            return webui_prompt_parser(string_iter)
        case _:
            raise TypeError()


def get_image_meta():
    pass


class GrammarError(RuntimeError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UnmatchedBracketError(GrammarError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
