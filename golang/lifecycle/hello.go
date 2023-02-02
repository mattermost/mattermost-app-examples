package main

import (
	_ "embed"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/mattermost/mattermost-plugin-apps/apps"
	"github.com/mattermost/mattermost-plugin-apps/apps/appclient"
	"github.com/mattermost/mattermost-plugin-apps/utils/httputils"
)

//go:embed icon.png
var iconData []byte

const (
	host = "mattermost-apps-golang-lifecycle"
	port = 8083
)

var (
	rootURL = fmt.Sprintf("http://%s:%d", host, port)
)

var Manifest = apps.Manifest{
	AppID:       "hello-lifecycle",
	Version:     "v1.2.0",
	DisplayName: "Hello, Lifecycle!",
	HomepageURL: "https://github.com/mattermost/mattermost-app-examples/golang/lifecycle",
	Icon:        "icon.png",
	OnInstall: &apps.Call{
		Path: "/install",
		Expand: &apps.Expand{
			ActingUser: apps.ExpandID,
		},
	},
	OnVersionChanged: &apps.Call{
		Path: "/version_changed",
		Expand: &apps.Expand{
			ActingUser: apps.ExpandID,
		},
	},
	OnUninstall: &apps.Call{
		Path: "/uninstall",
		Expand: &apps.Expand{
			ActingUser: apps.ExpandID,
		},
	},
	OnEnable: &apps.Call{
		Path: "/enable",
		Expand: &apps.Expand{
			ActingUser: apps.ExpandID,
		},
	},
	OnDisable: &apps.Call{
		Path: "/disable",
		Expand: &apps.Expand{
			ActingUser: apps.ExpandID,
		},
	},
	RequestedPermissions: []apps.Permission{
		apps.PermissionActAsBot,
	},
	Deploy: apps.Deploy{
		HTTP: &apps.HTTP{
			RootURL: rootURL,
		},
	},
}

func main() {
	http.HandleFunc("/manifest.json",
		httputils.DoHandleJSON(Manifest))

	http.HandleFunc("/static/icon.png",
		httputils.DoHandleData("image/png", iconData))

	http.HandleFunc("/bindings", httputils.DoHandleJSONData([]byte("{}")))

	http.HandleFunc("/install", respondWithMessage("Thanks for installing me!"))

	http.HandleFunc("/uninstall", respondWithMessage("No, don't uninstall me!"))

	http.HandleFunc("/enable", respondWithMessage("I'm back up again"))

	http.HandleFunc("/disable", respondWithMessage("Taking a little nap"))

	addr := fmt.Sprintf(":%v", port)
	fmt.Printf("hello-lifecycle app listening on %q \n", addr)
	fmt.Printf("Install via /apps install http %s/manifest.json \n", rootURL)
	panic(http.ListenAndServe(addr, nil))
}

func respondWithMessage(message string) func(w http.ResponseWriter, req *http.Request) {
	return func(w http.ResponseWriter, req *http.Request) {
		creq := apps.CallRequest{}
		json.NewDecoder(req.Body).Decode(&creq)

		_, err := appclient.AsBot(creq.Context).DM(creq.Context.ActingUser.Id, message)
		if err != nil {
			json.NewEncoder(w).Encode(apps.NewErrorResponse(err))
			return
		}

		httputils.WriteJSON(w,
			apps.NewTextResponse("Created a post in your DM channel."))
	}
}
