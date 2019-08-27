"""
Config file.
"""
import os


if os.environ['ENVIRONMENT'] == 'production':
    TOKEN = '736244244:AAGGaEdFAOtrP9YtLoJeJ3tQ8LtBuFGSbu4'

if os.environ['ENVIRONMENT'] == 'local':
    TOKEN = ':736244244:AAGGaEdFAOtrP9YtLoJeJ3tQ8LtBuFGSbu4'

URL = 'postgres://rikdrycw:O_P2Qr5FcLWHAU6aU8h3GfiKwjhDJoYE@baasu.db.elephantsql.com:5432/rikdrycw'
