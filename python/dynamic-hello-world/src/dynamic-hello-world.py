"""Hello-world Example App in Python."""
import copy
import logging
import os
from pathlib import Path
from typing import List

from flask import Flask, request

from python.mattermost_models.models import Models

logging.basicConfig(level=logging.DEBUG)

static_path = Path.cwd().joinpath() / "python/dynamic-hello-world/src/static"
app = Flask(
    __name__,
    static_folder=static_path.as_posix(),
    static_url_path="/static",
)

default_port = 8090
default_host = "mattermost-apps-python-hello-world"
default_root_url = f"http://{default_host}:{default_port}"

DYNAMIC_FORM = Models.BaseForm(
    title="I am a Dynamic form!",
    icon="icon.png",
    fields=[
        Models.Field(
            name="choice_1",
            modal_label="What is 1 + 1?",
            type="dynamic_select",
            is_required=True,
            refresh=True,
            hint="The answer is 2.",
            lookup={"path": "/lookup"},
        ),
    ],
    source=Models.Call(
        path="/dynamic_source",
        expand=Models.Expand(
            app="all",
            acting_user="all",
        ),
    ),
    submit=Models.Call(
        path="/submit",
        expand=Models.Expand(
            app="all",
            acting_user="all",
        ),
    ),
)


@app.route("/manifest.json")
def manifest() -> Models.Manifest:
    return Models.Manifest(
        app_id="dynamic-hello-world",
        display_name="Hello world app in a Dynamic Form",
        homepage_url="https://github.com/mattermost/mattermost-app-examples/tree/master/python/dynamic-hello-world",
        icon="icon.png",
        requested_permissions=["act_as_bot"],
        on_install=Models.Call(
            path="/install",
            expand=Models.Expand(
                app="all",
            ),
        ),
        bindings=Models.Call(
            path="/bindings",
        ),
        requested_locations=["/channel_header", "/command"],
        http={
            "root_url": os.environ.get("ROOT_URL", default_root_url),
        },
    )


def first_answer() -> List[Models.SelectField]:
    """Return a list of the first answer options"""
    return [
        Models.SelectField(
            label=f"{i}",
            value=f"{i}",
        )
        for i in range(10)
    ]


def second_answer() -> List[Models.Field]:
    """Return a list of the second answer options"""
    return [
        Models.Field(
            type="static_select",
            modal_label="What is 10 + 10?",
            name="choice_2",
            is_required=True,
            hint="The answer is 20.",
            options=[
                Models.SelectField(
                    label=f"{i}",
                    value=f"{i}",
                )
                for i in range(10, 21)
            ],
        ),
    ]


def set_values(request_json) -> Models.BaseForm:
    """Return a new form with the values set to the previous selections"""

    # Make a deep copy so we don't modify the original form.
    form = copy.deepcopy(DYNAMIC_FORM)
    form["fields"][0]["value"] = request_json["values"]["choice_1"]
    return form


@app.route("/lookup", methods=["POST", "GET"])
def lookup() -> Models.CallResponse:
    """This is the lookup for the dynamic form's first question."""

    return Models.CallResponse(
        type="ok",
        data={
            "items": first_answer(),
        },
    )


@app.route("/dynamic_source", methods=["POST", "GET"])
def dynamic_source() -> Models.CallResponse:
    """This is the source for the dynamic form. It is called when the form is opened and when the form needs refreshed."""

    # check if the user is just opening the form. If so present the first options.
    if j := request.json:
        choice = j.get("selected_field", "")
        if not choice:
            return Models.CallResponse(
                type="form",
                form=copy.deepcopy(DYNAMIC_FORM),
            )
        # since an answer was provided get a new form and set the values to the previous selections.
        form = set_values(j)

        if choice == "choice_1":
            # Add the second question
            form["fields"].extend(second_answer())

            return Models.CallResponse(
                type="form",
                form=form,
            )

    return Models.CallResponse(
        type="error",
        text="Something went wrong.",
    )


@app.route("/submit", methods=["POST"])
def on_form_submit() -> Models.CallResponse:
    print(request.json)
    return Models.CallResponse(
        type="ok",
        text="This was an example of a dynamic form. The form was refreshed with new options.",
    )


@app.route("/bindings", methods=["GET", "POST"])
def on_bindings() -> Models.CallResponse:
    print(f"bindings called with {request.json}")
    return Models.CallResponse(
        type="ok",
        data=[
            Models.Binding(
                location="/channel_header",
                bindings=[
                    Models.Binding(
                        location="send-button",
                        icon="icon.png",
                        label="send hello message",
                        form=DYNAMIC_FORM,
                    ),
                ],
            ),
        ],
    )


@app.route("/ping", methods=["POST"])
def on_ping() -> Models.CallResponse:
    logging.debug("ping...")
    return Models.CallResponse(type="ok")


@app.route("/install", methods=["GET", "POST"])
def on_install() -> Models.CallResponse:
    print(
        f"on_install called with payload , {request.args}, {request.json}",
        flush=True,
    )
    return Models.CallResponse(type="ok", data={})


if __name__ == "__main__":
    app.run(
        debug=True,
        host=os.environ.get("APP_HOST", default_host),
        port=int(os.environ.get("APP_PORT", default_port)),
        use_reloader=False,
    )
