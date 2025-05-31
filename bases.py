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
