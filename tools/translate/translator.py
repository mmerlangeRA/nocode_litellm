from injector import inject, singleton
from settings.settings import Settings
import deepl


class TranslateOptions:
    deepL_Languages = [ "DE", "ES", "IT", "NL", "PL", "PT", "RU", "ZH"]
    use_deepL = False
    def __init__(self, source_lang: str, target_lang: str):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.use_deepL= target_lang in self.deepL_Languages


@singleton
class TranslatorComponent:
    settings : Settings

    @inject
    def __init__(self, settings: Settings) -> None:
       self.settings = settings

    def translate(self, text:str, options:TranslateOptions) -> str:
        if(options.use_deepL):
            translator = deepl.Translator(self.settings.deepl.api_key)
            result = translator.translate_text(text, target_lang=options.target_lang)
            return result.text
        else:
            return text
