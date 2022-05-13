import json
import abc
import re
from functools import reduce
import os
import random

from abot.models import SpanishVerbs
from abot import utils


class MessageProcessorException(Exception):
    pass


class BaseMessageProcessor(abc.ABC):
    """
    Clase base procesadora de mensajes la cual se encarga de segmentar y tokenizar un mensaje.
    """

    def __init__(self, message):
        if not isinstance(message, str):
            raise MessageProcessorException(
                "Message Processors message must be a str type"
            )

        self.message = message
        self.bot_response = self._set_bot_response(
            "Lo siento, no he entendido su pregunta"
        )

        # Separar oraciones
        self.message_sentences = list(
            map(lambda s: s.strip(), re.split("[.¡!/\\%¿?\n]+", self.message))
        )

        self.message_sentences = list(
            filter(lambda x: x if x is not None else _, self.message_sentences)
        )

        # Tokenizar oraciones
        """
        Aunque el ; y la , sirven de manera explicativa o para cuatificar, realmente 
        no nos interesa a nuestro contexto
        """
        self.message_sentences_tokenized = list()
        for sentence in self.message_sentences:
            self.message_sentences_tokenized.append(
                list(
                    map(
                        lambda w: w.strip().lower().replace(",", "").replace(";", "")
                        if w != ""
                        else _,
                        sentence.split(" "),
                    )
                )
            )

        # Tokenizar mensaje
        self.message_tokenized = list()
        for sentence_tokens in self.message_sentences_tokenized:
            self.message_tokenized += sentence_tokens
        self.message_tokenized = list(map(lambda w: w.lower(), self.message_tokenized))

        # Optimizar tokens
        self.optimize_tokens()

    @abc.abstractmethod
    def optimize_tokens(self):
        pass

    @abc.abstractmethod
    def process_message(self):
        pass

    @abc.abstractmethod
    def _set_bot_response(self, *args, **kwargs):
        pass


class SpanishMessageProcessor(BaseMessageProcessor):
    """
    Procesa mensajes en español de manera que se enfoca en los verbos y los sustantivos
    """

    def __init__(self, message):
        self.__resources_path = os.path.join(os.path.dirname(__file__), "languages/es")
        super().__init__(message)

    def process_message(self):
        """
        Se hace la lógica de procesamiento del mensaje
        """
        if self.__process_known_situations() == False:
            self.__process_related_situations()

    def __process_related_situations(self):
        """
        Procesa un mensaje en base a las palabras que emiten un mensaje o información relacionada a la palabra en sí
        """
        related_responses_path = os.path.join(
            self.__resources_path, "bot_related_responses.json"
        )
        related_responses = json.loads(open(related_responses_path, "r").read())
        responses = list()
        # Itera sobre las respuestas relacionadas que se concen
        for related_situtation in related_responses:
            # Itera sobre las palabras claves de esa situación
            for keyword in related_situtation["keywords"]:
                # La palabra está en los tokens de la oración
                if keyword.lower() in self.message_tokenized:
                    responses = [
                        *responses,
                        *self.__insert_message_data(related_situtation),
                    ]
        if len(responses) > 0:
            self.bot_response = self._set_bot_response(*responses)
        return len(responses) > 0

    def __insert_message_data(self, data):
        messages = data["response"]

        if not isinstance(data["response"], list):
            messages = [messages]

        if "require-data" in data.keys():
            # Itera sobre los datos requeridos
            for required_info in data["require-data"]:
                required_value = os.getenv(required_info)
                # Itera sobre los mensajes
                for i, message in enumerate(messages):
                    messages[i] = message.replace(f":{required_info}", required_value)
        return messages

    def __process_known_situations(self):
        """
        Procesa un mensaje según las situaciones conocidas
        """
        quick_responses_path = os.path.join(
            self.__resources_path, "bot_quick_responses.json"
        )
        quick_responses = json.loads(open(quick_responses_path, "r").read())
        # Itera sobe las situaciones conocidas
        for known_situtation in quick_responses:
            # Itera sobre las mesanjes de situaciones conocidas
            for situation in known_situtation["message"]:
                situation = situation.lower()
                message = self.message.lower()
                # Si la situación conocida es de solo es una palabra busca en los tokens de la oración
                single_word_condition = (
                    " " not in situation and situation in self.message_tokenized
                )
                # Si la situación conocida es de varias palabras, entonces se busca que exista en el mensaje.
                # Para la validación de la situación de palabra compuesta, se eliminan los acentos del mensaje
                #   ahorrándonos así algunas faltas de ortografías.
                composed_word_condition = " " in situation and utils.replaceAccents(
                    situation
                ) in utils.replaceAccents(message)

                if single_word_condition or composed_word_condition:
                    answers_qty = len(known_situtation["answers"])
                    answers_index = random.randint(0, answers_qty - 1)
                    self.bot_response = known_situtation["answers"][answers_index]
                    return True
        return False

    def _set_bot_response(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                return [i for i in args]
            else:
                return args[0]
        elif kwargs:
            return [kwargs[key] for key in args.keys()]
        else:
            return "Lo siento, no entiendo lo que me quiere decir"

    def optimize_tokens(self):
        """
        Optimiza los tokens de la oración al eliminar todo lo que no sea un sustantivo o
        un verbo. Los verbos los convertirá a su forma infinitiva y se crea una lista máscara
        para facilitar el posterior clasificaión de lde los tokens resultantes en verbos o
        sustantivos
        """
        # Carga sintaxis del español
        syntax_path = os.path.join(self.__resources_path, "sintax.json")
        syntax = json.loads(open(syntax_path, "r").read())

        self.message_sentences_tokens_optimized = list()
        self.message_sentences_tokens_optimized_verb_mask = list()

        # Itera sobre oraciones
        for sentence_index in range(len(self.message_sentences_tokenized)):
            is_previous_token_verb = False
            previews_word_token = None
            index_correction = 0

            # Itera sobre tokens de las oraciones
            for word_index in range(
                len(self.message_sentences_tokenized[sentence_index])
            ):
                # Quita las tildes
                # word_token = utils.replaceAccents(
                #     self.message_sentences_tokenized[sentence_index][word_index].lower()
                # )
                word_token = self.message_sentences_tokenized[sentence_index][
                    word_index
                ].lower()

                # Filtra solo los sustantivos y verbos
                if not (
                    word_token in syntax["Composed Tenses helper"]
                    or word_token in syntax["coordinating conjunctions"]
                    or word_token in syntax["prepositions"]
                    or word_token in syntax["articles"]
                    or word_token in syntax["possesives"]
                    or word_token in syntax["questions"]
                    or word_token in syntax["personal pronouns"]
                ):
                    infinitive = SpanishVerbs.query.filter(
                        (SpanishVerbs.conjugated_verb == word_token)
                        | (SpanishVerbs.infinitive_verb == word_token)
                    ).first()
                    if infinitive:
                        word_token = infinitive.infinitive_verb
                    self.message_sentences_tokens_optimized.append(word_token)
                    self.message_sentences_tokens_optimized_verb_mask.append(
                        infinitive is not None
                    )
                    continue
