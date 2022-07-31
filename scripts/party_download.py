from party_downloader.core import Downloader
import logging, sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


dl = Downloader("./output", execute=True)
dl.download_creator("https://kemono.party/fantia/user/14169")
