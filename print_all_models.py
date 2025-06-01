from sqlalchemy.orm import registry, RelationshipProperty
from db import *

# Предположим, у вас есть registry (либо вы создали declarative_base через registry)
# mapper_registry = registry()
mapper_registry = Base.registry
metadata = mapper_registry.metadata  # общая точка доступа к таблицам

def print_all_models_info(registry):
    print("== Информация о моделях ==")
    for mapper in registry.mappers:
        model_cls = mapper.class_
        table = mapper.local_table
        print(f"\nМодель: {model_cls.__name__}")
        print(f"Таблица: {table.name}")
        
        # Колонки
        print("  Колонки:")
        for column in table.columns:
            print(f"    - {column.name}: {column.type}, primary_key={column.primary_key}")
        
        # Отношения
        relationships = [
            (key, rel)
            for key, rel in mapper.relationships.items()
            if isinstance(rel, RelationshipProperty)
        ]
        if relationships:
            print("  Отношения:")
            for key, rel in relationships:
                target = rel.mapper.class_.__name__
                direction = "многие-к-одному" if rel.uselist is False else "один-ко-многим"
                print(f"    - {key} → {target} ({direction})")
        else:
            print("  Отношения: нет")

# Вызов
print_all_models_info(mapper_registry)
