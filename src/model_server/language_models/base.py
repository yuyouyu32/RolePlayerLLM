import torch
from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    def _get_model(self, path):
        pass

    @abstractmethod    
    def predict(self):
        pass
    
    @abstractmethod
    @torch.inference_mode()
    def predict_stream(self):
        pass
