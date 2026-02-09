from dataclasses import dataclass, field


@dataclass(eq=False)
class BaseEntity:
    id: int = field(init=False)

    _id_counter = 0

    def __post_init__(self):
        cls = type(self)
        cls._id_counter += 1
        self.id = cls._id_counter


@dataclass(eq=True)
class Medicament(BaseEntity):
    name: str
