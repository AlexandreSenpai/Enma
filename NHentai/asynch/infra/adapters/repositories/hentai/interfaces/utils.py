from enum import Enum, unique

@unique
class Mimes(Enum):
  J: str = 'jpg'
  P: str = 'png'
  G: str = 'gif'