from threading import Thread
import vk_bot
import tg_bot


if __name__ == '__main__':
    t1 = Thread(target=vk_bot.start_vk_bot)
    t2 = Thread(target=tg_bot.main)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
