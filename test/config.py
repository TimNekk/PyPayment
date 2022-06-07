from environs import Env

env = Env()
env.read_env()

qiwi_secret_key = env.str("qiwi_secret_key")
