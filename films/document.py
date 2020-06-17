from elasticsearch_dsl import Document, Index, Text, Integer, Completion, analyzer, tokenizer
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl.analysis import token_filter


edge_ngram_completion_filter = token_filter(
    'edge_ngram_completion_filter',
    type="edge_ngram",
    min_gram=1,
    max_gram=20
)

my_analyzer = analyzer(
    "my_analyzer",
    tokenizer="standard",
    filter=["lowercase", edge_ngram_completion_filter]
)

class MovieDocument(Document):
  orig_title = Text(
    analyzer=my_analyzer
  )
  ru_title = Text(
    analyzer=my_analyzer
  )
  id = Integer()

  class Meta:
    index = 'movie'
    using = 'default'

class ActorDocument(Document):
  name = Text(
    analyzer=my_analyzer
  )
  id = Integer()

  class Meta:
    index = 'actor'
    using = 'default'
