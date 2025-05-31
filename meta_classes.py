class ModelAdminMeta(type):
    def __new__(cls, name, bases, namespace):
        class_meta = type('Meta', (), {})
        namespace.update({ 'Meta': class_meta })
        class_ = super().__new__(cls, name, bases, namespace)
        return class_
