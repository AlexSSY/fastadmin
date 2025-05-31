from abc import ABC, abstractmethod

import meta_classes

# metaclass=meta_classes.ModelAdminMeta
class ModelAdmin():
    class Meta:
        pass


class Record:
    pass


class ContextProcessor(ABC):

    @abstractmethod
    def get_context(self, obj):
        ...

    @abstractmethod
    def get_list_context(self, objects):
        ...


class Partial:
    template = None

    def get_context(self):
        ...
