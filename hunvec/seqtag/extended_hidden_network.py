from math import sqrt

from hunvec.seqtag.word_tagger import WordTaggerNetwork
from pylearn2.models.mlp import CompositeLayer, Linear
from pylearn2.sandbox.nlp.models.mlp import ProjectionLayer
from pylearn2.space import CompositeSpace, IndexSpace, VectorSpace


class ExtendedHiddenNetwork(WordTaggerNetwork):
    def __init__(self, extender_dim, *args, **kwargs):
        self.extender_dim = extender_dim
        super(ExtendedHiddenNetwork, self).__init__(*args, **kwargs)

    def create_input_source(self):
        return ('words', 'features', 'tagger_out')

    def create_input_space(self):
        ws = (self.ws * 2 + 1)
        return CompositeSpace([
            IndexSpace(max_labels=self.vocab_size, dim=ws),
            IndexSpace(max_labels=self.total_feats, dim=self.feat_num),
            VectorSpace(dim=self.extender_dim)
        ])

    def create_input_layer(self):
        return CompositeLayer(
            layer_name='ext_input',
            layers=[
                ProjectionLayer(layer_name='ext_words', dim=self.edim, irange=.1),
                ProjectionLayer(layer_name='ext_feats', dim=self.fedim, irange=.1),
                Linear(layer_name='lin_embed', dim=self.extender_dim,
                       istdev=1. / sqrt(self.extender_dim)),
            ],
            inputs_to_layers={0: [0], 1: [1], 2: [2]}
        )