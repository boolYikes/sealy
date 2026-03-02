from enum import Enum as E


class Permission(E):
  read = "R"
  write = "W"


class UserType(E):
  organization = "organization"
  team = "team"
  individual = "individual"


# TBD
class Provider(E):
  password = "password"
  google = "google"
  apple = "apple"
