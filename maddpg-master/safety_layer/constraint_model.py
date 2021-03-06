from torch.nn.init import uniform_
from safety_layer.config import Config
from safety_layer.net import Net


class ConstraintModel(Net):
    def __init__(self, observation_dim, action_dim):
        self.layers = [20, 20, 20]
        self.init_bound = 0.03
        
        super(ConstraintModel, self)\
            .__init__(observation_dim,
                      action_dim,
                      self.layers,
                      self.init_bound,
                      uniform_,
                      None)
