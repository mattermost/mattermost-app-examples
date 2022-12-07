package main

import (
	_ "embed"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/mattermost/mattermost-plugin-apps/apps"
	"github.com/mattermost/mattermost-plugin-apps/apps/appclient"
	"github.com/mattermost/mattermost-plugin-apps/utils/httputils"
)

//go:embed icon.png
var IconData []byte

var Manifest = apps.Manifest{
	AppID:       "hello-timer",
	Version:     "v1.1.0",
	DisplayName: "Hello, timers!",
	Icon:        "icon.png",
	HomepageURL: "https://github.com/mattermost/mattermost-app-examples/golang/timers",
	RequestedPermissions: []apps.Permission{
		apps.PermissionActAsBot,
		apps.PermissionActAsUser,
	},

	RequestedLocations: []apps.Location{
		apps.LocationCommand,
	},

	Deploy: apps.Deploy{
		HTTP: &apps.HTTP{
			RootURL: "http://mattermost-apps-golang-timers:8085",
		},
	},
}

var Bindings = []apps.Binding{
	{
		Location: "/command",
		Bindings: []apps.Binding{
			{
				Icon:        "icon.png",
				Label:       "timer",
				Description: "Create a timer",
				Form: &apps.Form{
					Submit: apps.NewCall("/timer/create").WithExpand(apps.Expand{
						ActingUserAccessToken: apps.ExpandAll,
						Channel:               apps.ExpandID,
						Team:                  apps.ExpandID,
					}),
					Fields: []apps.Field{
						{
							Name:                 "duration",
							Label:                "duration",
							Description:          "duration until the timer expires in seconds",
							IsRequired:           true,
							AutocompletePosition: 1,
							Type:                 apps.FieldTypeText,
							TextSubtype:          apps.TextFieldSubtypeNumber,
						},
					},
				},
			},
		},
	},
}

func main() {
	http.HandleFunc("/manifest.json",
		httputils.DoHandleJSON(Manifest))
	http.HandleFunc("/static/icon.png",
		httputils.DoHandleData("image/png", IconData))

	http.HandleFunc("/bindings",
		httputils.DoHandleJSON(apps.NewDataResponse(Bindings)))

	http.HandleFunc("/timer/create", CreateTimer)

	http.HandleFunc("/timer/execute", ExecuteTimer)

	addr := ":8085"
	fmt.Println("Listening on", addr)
	fmt.Println("Use '/apps install http http://mattermost-apps-golang-timers" + addr + "/manifest.json' to install the app")
	log.Fatal(http.ListenAndServe(addr, nil))
}

func CreateTimer(w http.ResponseWriter, req *http.Request) {
	creq := apps.CallRequest{}
	json.NewDecoder(req.Body).Decode(&creq)

	client := appclient.AsActingUser(creq.Context)

	durationString := creq.GetValue("duration", "")
	durcation, _ := strconv.Atoi(durationString)
	at := time.Now().Add(time.Second * time.Duration(durcation))

	t := &apps.Timer{
		At:   at.UnixMilli(),
		Call: *apps.NewCall("/timer/execute").WithExpand(apps.Expand{ActingUser: apps.ExpandID}),
	}

	err := client.CreateTimer(t)
	if err != nil {
		panic(err)
	}

	httputils.WriteJSON(w,
		apps.NewTextResponse("Successfully set a timer to `%v`.", at.String()))
}

func ExecuteTimer(w http.ResponseWriter, req *http.Request) {
	creq := apps.CallRequest{}
	json.NewDecoder(req.Body).Decode(&creq)

	appclient.AsBot(creq.Context).DM(creq.Context.ActingUser.Id, "Received timer")

	httputils.WriteJSON(w,
		apps.NewTextResponse(""))

}
