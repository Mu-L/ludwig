from typing import Dict, TYPE_CHECKING

import torch
from torch import nn

from ludwig.features.feature_utils import get_module_dict_key_from_name, get_name_from_module_dict_key

# Prevents circular import errors from typing.
if TYPE_CHECKING:
    from ludwig.models.ecd import ECD


class PredictModule(nn.Module):
    """Wraps prediction for pre-processed inputs.

    The purpose of the module is to be scripted into Torchscript for native serving. The nn.ModuleDict attributes of
    this module use keys generated by feature_utils.get_module_dict_key_from_name in order to prevent name collisions
    with keywords reserved by TorchScript.

    TODO(geoffrey): Implement torchscript-compatible feature_utils.LudwigFeatureDict to replace
    get_module_dict_key_from_name and get_name_from_module_dict_key usage.
    """

    def __init__(self, model: "ECD"):
        super().__init__()

        model.cpu()
        self.model = model.to_torchscript()

        self.predict_modules = nn.ModuleDict()
        for feature_name, feature in model.output_features.items():
            module_dict_key = get_module_dict_key_from_name(feature_name)
            self.predict_modules[module_dict_key] = feature.prediction_module

    def forward(self, preproc_inputs: Dict[str, torch.Tensor]):
        with torch.no_grad():
            outputs: Dict[str, torch.Tensor] = self.model(preproc_inputs)
            predictions: Dict[str, Dict[str, torch.Tensor]] = {}
            for module_dict_key, predict in self.predict_modules.items():
                feature_name = get_name_from_module_dict_key(module_dict_key)
                predictions[feature_name] = predict(outputs, feature_name)

            return predictions
