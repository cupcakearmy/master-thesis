package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"strings"
)

var SERVICE = os.Getenv("SERVICE")

func getIPs() []string {
	out, err := exec.Command("dig", "+short", "+search", SERVICE).Output()
	if err != nil {
		log.Fatal(err)
		return []string{}
	}

	trimmed := strings.TrimSpace(fmt.Sprintf("%s", out))
	if trimmed == "" {
		return []string{}
	} else {
		return strings.Split(trimmed, "\n")
	}
}

func main() {
	http.HandleFunc("/discoverable", func(w http.ResponseWriter, r *http.Request) {
		ips := getIPs()
		plain := r.URL.Query().Get("format") == "plain"
		if plain {
			fmt.Fprintf(w, "%s\n", strings.Join(ips, "\n"))
		} else {
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(ips)
		}
	})

	log.Fatal(http.ListenAndServe(":42069", nil))

}
