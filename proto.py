from importlib import import_module
from abc import ABC, abstractmethod


class Request:
    pass


class IRequestParser(ABC):
    
    @abstractmethod
    def parse(self, request):
        pass


class FastAPIRequestParser(IRequestParser):
    
    def parse(self, request):
        pass


class DjangoRequestParser(IRequestParser):
    
    def parse(self, request):
        pass


class FlaskRequestParser(IRequestParser):
    
    def parse(self, request):
        pass


def url(r_path, callback, name):
    return (r_path, callback, name)

urls = [
    url(r'^/')
]


print(import_module("os"))
print(import_module("os").__dict__)
