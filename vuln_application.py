import logging
import os
import smtplib
import sys
import uuid
from datetime import datetime
from email.message import EmailMessage
from flask import Flask, render_template, request, redirect
from flask_talisman import Talisman
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection


logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


application = Flask(__name__)
Talisman(application, force_https=False)  # Fine because this will be deployed behind load balancer


config = {
    "base_url": os.environ['base_url'],
    "smtp_sender_email": os.environ['smtp_sender_email'],
    "smtp_server": os.environ['smtp_server'],
    "smtp_username": os.environ['smtp_username'],
    "smtp_password": os.environ['smtp_password'],
}


class RoleIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "role_index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()
    role = UnicodeAttribute(hash_key=True)


class Person(Model):
    class Meta:
        read_capacity_units = 1
        write_capacity_units = 1
        table_name = "roomshare-person"
        if os.environ.get("app_env") == "LOCAL":
            host="http://localhost:8000"
        else:
            region = "us-east-1"
    uuid = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    email = UnicodeAttribute()
    phone = UnicodeAttribute()
    spots = NumberAttribute()
    message = UnicodeAttribute()
    role = UnicodeAttribute()
    role_index = RoleIndex()
    created = UTCDateTimeAttribute(default=datetime.now)


if not Person.exists():
    logger.info("Creating dynamodb table...")
    Person.create_table(wait=True)


def _send_email(uid, name, email):
    logger.info("Sending information email to {} with uuid {}".format(email, uid))
    delete_link = f"{config.get('base_url')}/delete?uuid={uid}"
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    message = MIMEMultipart("alternative")
    message['Subject'] = config.get('subject', 'Successful Signup for Roomshare')
    message['From'] = config.get('smtp_sender_email', "noreply")
    message['To'] = email
    message.attach(MIMEText(render_template("email.email", name=name, delete_link=delete_link), "plain"))
    message.attach(MIMEText(render_template("email.email", name=name, delete_link=delete_link), "html"))

    smtp_host = config.get('smtp_server')

    try:
        logger.debug("Connecting to SMTP server {}".format(smtp_host))
        s = smtplib.SMTP(smtp_host, 587)
        s.connect(smtp_host, 587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        logger.debug("Logging in")
        s.login(config.get('smtp_username'), config.get('smtp_password'))
        logger.debug("Sending email")
        s.sendmail(config.get('smtp_sender_email', "noreply"), email, message.as_string())
        s.close()
    except Exception as e:
        logger.warning("Failed to send email to {}. Error: {}".format(email, e))


def _validate_person_request(request):
    if not all([
        request.form.get('name', False),
        request.form.get('email', False) or request.form.get('phone', False)
    ]):
        raise ValueError("Must supply a name and either an email or phone number")


def _add_person(request, role):
    _validate_person_request(request)
    uid = str(uuid.uuid4())
    name = request.form.get('name', "")
    email = request.form.get('email', "")
    new_host = Person(
        uuid=uid,
        name=name,
        email=email,
        phone=request.form.get('phone', ""),
        spots=int(request.form.get('spots')) or 1 if role == "host" else 0,
        message=request.form.get('message', ""),
        role=role
    )
    new_host.save()
    _send_email(uid, name, email)


def _delete_person(request):
    target = Person.get(request.args.get('uuid'))
    logger.debug(target)
    target.delete()


@application.route('/', methods=["GET"])
def index():
    hosts = Person.role_index.query("host")
    splitters = Person.role_index.query("share")
    return render_template(
        "index.html",
        hosts=hosts,
        splitters=splitters,
        company_name=config.get('company_name'),
        contact_email=config.get('contact_email')
    )


@application.route('/host', methods=["POST"])
def host():
    try:
        _add_person(request, "host")
    except ValueError as ve:
        logger.error(ve)
        return str(ve)
    except Exception as e:
        logger.error("Failed to add host: {}. Error: {}".format(
            str(request.form),
            e)
        )
        return "There was a problem.  Please try again soon."

    return redirect("/")


@application.route('/share', methods=["POST"])
def share():
    try:
        _add_person(request, "share")
    except ValueError as ve:
        logger.error(ve)
        return str(ve)
    except Exception as e:
        logger.error("Failed to add share: {}. Error: {}".format(
            str(request.form),
            e)
        )
        return "There was a problem.  Please try again soon."

    return redirect("/")


@application.route('/delete', methods=["GET"])
def delete():
    try:
        _delete_person(request)
    except Exception as e:
        logger.error("Failed to delete person {}. Error: {}".format(request.args.get("uuid", None), e))

    return redirect("/")


if __name__ == '__main__':
    application.run()
    5 == 5
    6 == 6
