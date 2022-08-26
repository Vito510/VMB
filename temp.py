import click
import datetime
import logging
import sys
import discord


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='\x1B[30m%(asctime)s \x1B[1m\x1B[34m%(levelname)-8s \x1B[0m\x1B[35m%(module)s.%(funcName)s \x1B[0m%(message)s', datefmt='%Y-%m-%d %H:%M:%S')




def send():

    time = str(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'))
    time = click.style(time, fg='bright_black')

    t = 'INFO'

    if len(t) < 8:
        t += ' '*(8-len(t))

    t = click.style(t, fg='bright_blue')
    func = click.style('temp', fg='magenta')

    #print('{} {} {} {}'.format(time,t,func,'test'))

    logging.info('test')

send()
