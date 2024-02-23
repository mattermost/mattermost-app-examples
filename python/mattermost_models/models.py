"""Models for the app template API"""
from __future__ import annotations

from typing import Any, List, Literal, TypedDict, Union


class Models:
    """Models for the app template API"""

    ExpandOptions = Literal["all", "id", "summary", "+all", "+id", "+summary"]

    class Expand(TypedDict, total=False):
        """Base model for the expand field of a request"""

        app: Models.ExpandOptions
        acting_user: Models.ExpandOptions
        acting_user_access_token: Models.ExpandOptions
        locale: Models.ExpandOptions
        channel: Models.ExpandOptions
        channel_member: Models.ExpandOptions
        team: Models.ExpandOptions
        team_member: Models.ExpandOptions
        root_post: Models.ExpandOptions
        post: Models.ExpandOptions
        user: Models.ExpandOptions
        oauth2_app: Models.ExpandOptions
        oauth2_user: Models.ExpandOptions

    class Call(TypedDict, total=False):
        """Call field for the forms"""

        path: str
        expand: Models.Expand
        state: dict

    class SelectField(TypedDict, total=False):
        """Select field for the forms"""

        # Label is the display name/label for the option's value.
        label: str
        value: str
        icon_data: str

    class Lookup(TypedDict, total=False):
        """Lookup field for the forms"""

        # Label is the display name/label for the option's value.
        type: Literal["ok", "error", "form", "navigate"]
        data: List[Models.SelectField]

    class Field(TypedDict, total=False):
        """Field model for the forms
        https://pkg.go.dev/github.com/mattermost/mattermost-plugin-apps/apps#Field
        """

        # Name is the name of the JSON field to use.
        name: str
        type: Literal[
            "text", "static_select", "dynamic_select", "bool", "channel", "markdown"
        ]

        is_required: bool
        readonly: bool
        # Present (default) value of the field
        value: Any

        # Field description. Used in modal and autocomplete
        description: str

        label: str
        hint: str
        position: int
        modal_label: str
        multiselect: bool
        refresh: bool
        options: List[Models.SelectField]
        lookup: Models.Call

        # Text props
        subtype: Literal["input", "textarea", "email", "number", "tel", "url"]
        min_length: int
        max_length: int

    class BaseForm(TypedDict, total=False):
        """Base model for forms in the mattermost app"""

        # Source is the call to make when the form's definition is required (i.e. it has no fields, or needs to be refreshed from the app). A simple call can be specified as a path (string).
        source: Models.Call
        # Title, Header, and Footer are used for Modals only.
        title: str
        header: str
        footer: str

        # A fully-qualified URL, or a path to the form icon.
        icon: str

        # Submit is the call to make when the user clicks a submit button (or enter for a command). A simple call can be specified as a path (string). It will contain no expand/state.
        submit: Models.Call

        # SubmitButtons refers to a field name that must be a FieldTypeStaticSelect or FieldTypeDynamicSelect. In Modal view, the field will be rendered as a List of buttons at the bottom. Clicking one of them submits the Call, providing the button
        # reference as the corresponding Field's value. Leaving this property blank, displays the default "OK". In Autocomplete, it is ignored.
        submit_buttons: str

        # Fields is the List of fields in the form.
        fields: List[Models.Field]

    class CallResponse(TypedDict, total=False):
        """Base model for the response of a call"""

        type: Literal["ok", "error", "form", "navigate"]

        # Text is used for OK and Error response, and will show the text in the proper output.
        text: str

        # Optional. Force refresh bindings for acting user
        refresh_bindings: bool

        # Used in CallResponseTypeCall
        call: Models.Call

        # Used in CallResponseTypeForm
        form: Models.BaseForm

        # Used in CallResponseTypeNavigate
        navigate_to_url: str
        use_external_browser: bool

        # Used in CallResponseTypeOK to return the displayable, and JSON results
        data: Union[dict, List]

    class Binding(TypedDict, total=False):
        """Bindings model for the app"""

        app_id: str
        location: str
        icon: str
        label: str
        hint: str
        description: str
        submit: Models.Call
        form: Models.BaseForm
        bindings: List[Models.Binding]

    class Manifest(TypedDict, total=False):
        """Manifest for the app."""

        app_id: str

        version: str

        homepage_url: str

        display_name: str
        description: str

        icon: str

        bindings: Models.Call

        on_install: Models.Call

        on_uninstall: Models.Call

        on_enable: dict

        on_disable: dict

        get_oauth2_connect_url: dict

        on_oauth2_complete: dict

        on_remote_webhook: dict

        requested_permissions: List[str]

        remote_webhook_auth_type: str

        requested_locations: List[str]

        http: dict[str, Any]
