import dataclasses


@dataclasses.dataclass
class Licensee:
    name: str
    label_name: str
    address: str = ""
