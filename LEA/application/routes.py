from flask import render_template, url_for, redirect, request, flash
from application import app
from application.forms import TemplateForm, PolicyForm, YForm, EmailForm
from trinsic.service_clients import CredentialsClient, ServiceClientCredentials
import smtplib

from flask_mail import Mail
from flask_mail import Message

# insert in apy_key your api key for Trinsic
api_key = '#'
credentials_client = CredentialsClient(ServiceClientCredentials(api_key))

#insert in app.config['SECRET_KEY'] your key for the application
app.config['SECRET_KEY'] = "#"


@app.route("/")
def homepage():
    return render_template("homepage.html")


@app.route("/about")
def about():
    return render_template("about_page.html")



@app.route("/credential", methods=["GET", "POST"])
def credential():
    form = TemplateForm()
    if form.validate_on_submit():
        attributes = [form.attribute1.data, form.attribute2.data, form.attribute3.data, form.attribute4.data,
                      form.attribute5.data]
        credential_definition = credentials_client.create_credential_definition({
            "name": form.name.data,
            "version": form.version.data,
            "attributes": attributes,
            "supportRevocation": form.supportRevocation.data,  # Enable revocation at a later date
            "tag": form.tag.data  # Tag to identify the schema
        })

        return redirect(url_for('credentials_template'))

    return render_template("create_template.html", form=form)



@app.route("/credentials_template", methods=["GET", "POST"])
def credentials_template():
    credential_definitions = credentials_client.list_credential_definitions()
    return render_template("credentials_template.html", credential_definitions=credential_definitions)



@app.route("/templates/<string:definition_id>", methods=["GET", "POST"])
def template_detail(definition_id):
    credential_definition = credentials_client.get_credential_definition(definition_id)
    return render_template("template_detail.html", credential_definition=credential_definition)



@app.route("/templates/<string:definition_id>/delete", methods=["POST"])
def template_delete(definition_id):
    credentials_client.delete_credential_definition(definition_id)
    return redirect(url_for('credentials_template'))


@app.route("/create_policy", methods=["GET", "POST"])
def create_policy():
    form = PolicyForm()
    if form.validate_on_submit():
        attribute_policies = [
            {
                "policyName": form.credential_name.data,  # Name for policy
                "attributeNames": [form.attribute1.data, form.attribute2.data, form.attribute3.data,
                                   form.attribute4.data],  # List of names of attributes to request
                "restrictions": [
                    {
                        "schemaId": form.schema_id.data,  # Optionally restrict by schema identifier
                        "issuerDid": form.issuer_did.data

                    }
                ]
            }
        ]

        # Create the verification policy
        verification_policy = credentials_client.create_verification_policy({
            "name": form.name.data,
            "version": form.version.data,
            "attributes": attribute_policies,

        })

        return redirect(url_for("policies"))

    return render_template("create_policy.html", form=form)


@app.route("/policies")
def policies():
    verification_policies = credentials_client.list_verification_policies()
    return render_template("policies.html", verification_policies=verification_policies)


@app.route("/policy/<string:policy_id>", methods=["GET", "POST"])
def policy_detail(policy_id):
    verification_policy = credentials_client.get_verification_policy(policy_id)
    return render_template("policy_detail.html", verification=verification_policy)


@app.route("/policies/<string:policy_id>/delete", methods=["POST"])
def policy_delete(policy_id):
    credentials_client.delete_verification_policy(policy_id)
    return redirect(url_for('policies'))


@app.route("/get_credential", methods=["GET", "POST"])
def get_credential():
    # insert in policy_id the id of your policy
    policy_id = "#"
    verification = credentials_client.create_verification_from_policy(policy_id)
    qrCodeUrl = "https://chart.googleapis.com/chart?cht=qr&chl=" + str(
        verification.verification_request_url) + "&chs=300x300&chld=L|1"

    return render_template("verification_connection.html", verification=verification, url=qrCodeUrl)


@app.route("/verification_state/<string:verification_id>", methods=["GET", "POST"])
def verification_state(verification_id):
    verification = credentials_client.get_verification(verification_id)
    if verification.state == "Accepted":
        name = None
        connection_id = None
        multi_party = False
        connection = credentials_client.create_connection({
            "multiParty": multi_party,
            "name": name,
            "connectionId": connection_id
        })

        qrCodeUrl = "https://chart.googleapis.com/chart?cht=qr&chl=" + str(
            connection.invitation_url) + "&chs=300x300&chld=L|1"

        return render_template("connection.html", connection=connection, url=qrCodeUrl)

    else:

        return render_template("state_error.html")


@app.route("/connections")
def connections():
    state = "Connected"  # Can be None | "Invited" | "Negotiating" | "Connected"
    connections = credentials_client.list_connections(state)
    return render_template("connections.html", connections=connections)


@app.route("/connections/<string:connection_id>", methods=["GET", "POST"])
def connection_detail(connection_id):
    connection = credentials_client.get_connection(connection_id)
    return render_template("connection_detail.html", connection=connection)


@app.route("/connections/<string:connection_id>/delete", methods=["POST"])
def connection_delete(connection_id):
    credentials_client.delete_connection(connection_id)
    return redirect(url_for('connections'))


@app.route("/credentials_connection/<string:connection_id>", methods=["GET", "POST"])
def credentials_connection(connection_id):
    connection_id = connection_id  # Can be None | <connection identifier>
    state = None  # Can be None | "Offered" | "Requested" | "Issued" | "Rejected" | "Revoked"
    definition_id = None  # Can be None | <definition identifier>
    credentials = credentials_client.list_credentials(connection_id, state, definition_id)
    return render_template("credentials_connection.html", credentials=credentials, connection_id=connection_id)


@app.route("/verifications_connection/<string:connection_id>", methods=["GET", "POST"])
def verifications_connection(connection_id):
    connection_id = connection_id
    definition_id = None
    verifications = credentials_client.list_verifications(connection_id, definition_id)
    return render_template("verifications_connection.html", verifications=verifications, connection_id=connection_id)


@app.route("/credential_detail/<string:credential_id>", methods=["GET", "POST"])
def credential_detail(credential_id):
    credential = credentials_client.get_credential(credential_id)
    return render_template("credential_detail.html", credential=credential)


@app.route("/credentials/<string:credential_id>/revoke", methods=["POST"])
def credential_revoke(credential_id):
    credentials_client.revoke_credential(credential_id)
    return redirect(url_for('credential_detail', credential_id=credential_id))


@app.route("/send_credential/<string:connection_id>", methods=["GET", "POST"])
def send_credential(connection_id):
    form = YForm()
    if form.validate_on_submit():
        connection_id = connection_id
        automatic_issuance = True
        # insert in definition_id the id of your template
        definition_id = '#'
        credential_values = {
            "First Name": form.first_name.data,
            "Last Name": form.last_name.data,
            "Agency Name": form.agency_name.data,
            "Role": form.role.data,
            "LIID": form.LIID.data
        }
        credential = credentials_client.create_credential({
            "definitionId": definition_id,
            "connectionId": connection_id,
            "automaticIssuance": automatic_issuance,
            "credentialValues": credential_values
        })
        return redirect(url_for('credentials_connection', connection_id=connection_id))

    return render_template("send_credential.html", form=form)


@app.route("/send_verification/<string:connection_id>", methods=["GET", "POST"])
def send_verification(connection_id):
    connection_id = connection_id
    # insert in policy_id the id of your policy
    policy_id = "#"
    verification = credentials_client.send_verification_from_policy(connection_id, policy_id)
    return redirect(url_for('verifications_connection', connection_id=connection_id))


@app.route("/all_verifications", methods=["GET", "POST"])
def all_verifications():
    connection_id = None
    definition_id = None
    verifications = credentials_client.list_verifications(connection_id, definition_id)
    return render_template("all_verifications.html", verifications=verifications)


@app.route("/verification_detail/<string:verification_id>", methods=["GET", "POST"])
def verification_detail(verification_id):
    verification = credentials_client.get_verification(verification_id)
    return render_template("verification_detail.html", verification=verification)


@app.route("/verifications/<string:verification_id>/delete", methods=["POST"])
def verification_delete(verification_id):
    credentials_client.delete_verification(verification_id)
    return redirect(url_for('all_verifications'))


@app.route("/email1/", methods=["GET", "POST"])
def send_email():
    form = EmailForm()
    if form.validate_on_submit():
        try:
            smtp_object = smtplib.SMTP('smtp.gmail.com', 587)
            print(smtp_object.ehlo())
            print(smtp_object.starttls())


            email = form.email.data
            password = form.password.data
            smtp_object.login(email, password)

            from_address = form.email.data
            to_address = form.email_to.data
            name = None
            connection_id = None
            multi_party = False
            connection = credentials_client.create_connection({
                "multiParty": multi_party,
                "name": name,
                "connectionId": connection_id
            })

            url = str(connection.invitation_url)
            qrCodeUrl = "https://chart.googleapis.com/chart?cht=qr&chl=" + str(
                connection.invitation_url) + "&chs=300x300&chld=L|1"

            subject = form.object.data
            message = form.message.data + '\n' + url + '\n' + '<img src=' + qrCodeUrl + '>'
            msg = "Subject: " + subject + '\n' + message

            smtp_object.sendmail(from_address, to_address, msg)
            smtp_object.quit()

            return redirect(url_for('connections'))

        except Exception as exception:

            return render_template("error_email.html")

    return render_template("create_email.html", form=form)


@app.route("/email/", methods=["GET", "POST"])
def send_message():
    form = EmailForm()
    if form.validate_on_submit():
        try:

            app.config['MAIL_SERVER'] = 'smtp.gmail.com'
            app.config['MAIL_PORT'] = 587
            app.config['MAIL_USERNAME'] = form.email.data
            app.config['MAIL_PASSWORD'] = form.password.data
            app.config['MAIL_USE_TLS'] = True
            app.config['MAIL_USE_SSL'] = False
            mail = Mail(app)

            msg = Message(form.object.data, sender=form.email.data, recipients=[form.email_to.data])

            name = None
            connection_id = None
            multi_party = False
            connection = credentials_client.create_connection({
                "multiParty": multi_party,
                "name": name,
                "connectionId": connection_id
            })
            url = str(connection.invitation_url)
            qrCodeUrl = "https://chart.googleapis.com/chart?cht=qr&chl=" + str(
                connection.invitation_url) + "&chs=300x300&chld=L|1"

            msg.html = "<p>" + form.message.data + " " + url + "</p><br><img src=" + qrCodeUrl + "></img>"
            mail.send(msg)
            return redirect(url_for('connections'))

        except Exception as exception:
            print(exception)
            return render_template("error_email.html")

    return render_template("create_email.html", form=form)
