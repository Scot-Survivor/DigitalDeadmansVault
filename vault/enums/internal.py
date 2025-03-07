import yaml

from enum import Enum
from typing import Any


class SerializableEnum(Enum):
    @classmethod
    def serializer(cls, dumper: yaml.Dumper, data: Enum) -> Any:
        return dumper.represent_scalar(cls.__name__, data.value)

    @classmethod
    def deserializer(cls, loader: yaml.Loader | yaml.FullLoader, node: yaml.Node | yaml.ScalarNode) -> Any:
        value = loader.construct_scalar(node)
        return cls(value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        yaml.add_constructor(self.__class__.__name__, self.__class__.deserializer)
        yaml.add_representer(self.__class__, self.__class__.serializer)
        yaml.add_multi_representer(self.__class__, self.__class__.serializer)
        for member in self.__class__.__members__.values():
            # "<DocumentChecksumAlgorithm.SHA256: 'sha256'>"
            # breakpoint()
            # yaml.add_constructor(member, self.__class__.deserializer)
            yaml.add_representer(member, self.__class__.serializer)
            yaml.add_multi_representer(member, self.__class__.serializer)
