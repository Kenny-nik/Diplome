from rest_framework import serializers
from .models import Author

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id","name","country","birth_year","death_year","about","created_at","updated_at"]
        read_only_fields = ["id","created_at","updated_at"]
