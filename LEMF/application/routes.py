from flask import render_template, url_for, redirect, request, flash
from application import app
from application.forms import PolicyDataForm
from trinsic.service_clients import CredentialsClient, ServiceClientCredentials

# insert in api_key your api key for the Trinsic platform
api_key = '#'
credentials_client = CredentialsClient(ServiceClientCredentials(api_key))

# insert in app.config['SECRET_KEY'] your secret key for the application
app.config['SECRET_KEY'] = "#"


@app.route("/")
def homepage():
    return render_template("homepage.html")


@app.route("/about")
def about():
    return render_template("about_page.html")


@app.route("/create_policy", methods=["GET", "POST"])
def create_policy():
    form = PolicyDataForm()
    if form.validate_on_submit():
        attribute_policies = [
            {
                "policyName": form.credential_name.data,  # Name for policy
                "attributeNames": [form.attribute1.data, form.attribute2.data, form.attribute3.data,
                                   form.attribute4.data, form.attribute5.data],
                # List of names of attributes to request
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


@app.route("/AccessData", methods=["GET", "POST"])
def access_data():
    # Insert in policy_id the policy ID of your Verification Policy
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
