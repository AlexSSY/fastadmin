from admin.bases import ModelAdmin


class User(ModelAdmin):
    class Meta:
        sa_model = 'User'


class Animal(ModelAdmin):
    class Meta:
        sa_model = 'Animal'

