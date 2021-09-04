from dataclasses import asdict

class BaseClass:
  def to_dict(self):
    return asdict(self)
