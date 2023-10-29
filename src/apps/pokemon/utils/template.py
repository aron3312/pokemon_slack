import copy

from src import config


class TemplateGenerator(object):
    def __init__(self):
        self.slack_simple_text_markdown_message = {"text": None, "mrkdwn": 'true'}
        self.slack_attachment_markdown_message = {
            'text': None,
            'attachments':[],
            "mrkdwn": 'true'
        }

    def render_help_messages(self):
        response = copy.deepcopy(self.slack_simple_text_markdown_message)
        response["text"] = config.HELP_MESSAGES
        return response

    def render_pure_text_message(self, text):
        response = {"text": text}
        return response

    def render_no_account_notice(self):
        response = copy.deepcopy(self.slack_simple_text_markdown_message)
        response["text"] = config.NO_ACCOUNT_MESSAGES
        return response

    def render_catch_first_pokemon_message(self, pokemon_dict: dict):
        response = copy.deepcopy(self.slack_attachment_markdown_message)
        response["text"] = f"你已經獲得你的第一隻寶可夢囉！\n他的資訊是：\n{'　　'.join([':'.join([str(k) for k in list(p)]) for p in pokemon_dict.items()])}"
        image_attachment = {'image_url': pokemon_dict.get("picture")}
        response['attachments'].append(image_attachment)
        return response

    def render_own_pokemons_message(self, pokemons_dict_lst: list):
        response = copy.deepcopy(self.slack_attachment_markdown_message)
        output_message = '\n=============\n:pokeball:'.join(
            ['\n'.join([':'.join([str(k) for k in list(p)]) for p in pokemon_dict.items()]) for pokemon_dict in
             pokemons_dict_lst])
        response["text"] = f"您的神奇寶貝如下，他們的資訊是：\n{output_message}"
        response["attachments"] = [{'image_url': pokemon_dict.get("picture")} for pokemon_dict in pokemons_dict_lst]
        return response
