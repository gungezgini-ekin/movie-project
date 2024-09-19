from django_elasticsearch_dsl import Document, fields, Index
from django_elasticsearch_dsl.documents import DocType
from movies.models import Movie, Director, Genre
from users.models import User, ListName

# Define the Elasticsearch index
movie_index = Index('movies')
movie_index.settings(number_of_shards=1, number_of_replicas=0)


@movie_index.doc_type
class MovieDocument(DocType):
    class Django:
        model = Movie

    title = fields.TextField()


# Similar setup for Director, User, and List
director_index = Index('directors')
director_index.settings(number_of_shards=1, number_of_replicas=0)


@director_index.doc_type
class DirectorDocument(DocType):
    class Django:
        model = Director

    name = fields.TextField()


genre_index = Index('genres')
genre_index.settings(number_of_shards=1, number_of_replicas=0)


@genre_index.doc_type
class GenreDocument(DocType):
    class Django:
        model = Genre

    name = fields.TextField()


user_index = Index('users')
user_index.settings(number_of_shards=1, number_of_replicas=0)


@user_index.doc_type
class UserDocument(DocType):
    class Django:
        model = User

    username = fields.TextField()


list_index = Index('lists')
list_index.settings(number_of_shards=1, number_of_replicas=0)


@list_index.doc_type
class ListDocument(DocType):
    class Django:
        model = ListName

    name = fields.TextField()
    is_private = fields.BooleanField()
    user = fields.IntegerField()

    def get_instances_from_related(self, related_instance):
        """
        Return an iterable of model instances related to this document.
        """
        if isinstance(related_instance, User):
            return ListName.objects.filter(user=related_instance)
        return super().get_instances_from_related(related_instance)

    def prepare_user(self, instance):
        """
        Return the user ID as an integer to be indexed.
        """
        return instance.user.id if instance.user else None

