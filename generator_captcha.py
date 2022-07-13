from claptcha import Claptcha
from random import sample, choice
import string
import os

def generate_str():
    alpha = string.ascii_letters + string.digits
    rand_string = ''.join(sample(alpha, 4))
    return rand_string


def generate_captcha():
    ttfs = [ttf for ttf in os.listdir() if 'ttf' in ttf]
    captha_text = generate_str()
    c = Claptcha(captha_text, f'{choice(ttfs)}')
    c.write(f'captchas/{captha_text.lower()}.png')
    return f'captchas/{captha_text.lower()}.png', captha_text

def delete_captcha(path):
    os.remove(path)


if '__name__' == '__main__':
    num = int(input('Введите колво капч, которое хотите создать: '))
    for i in range(num):
        generate_captcha()