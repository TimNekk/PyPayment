from environs import Env

env = Env()
env.read_env()

qiwi_secret_key = env.str("qiwi_secret_key")
yoomoney_access_token = env.str("yoomoney_access_token")
payok_api_key = env.str("payok_api_key")
payok_api_id = env.str("payok_api_id")
payok_shop_id = env.str("payok_shop_id")
payok_shop_secret_key = env.str("payok_shop_secret_key")
lava_token = env.str("lava_token")
lava_wallet = env.str("lava_wallet")
