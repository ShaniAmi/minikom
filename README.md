# Minikom - like Komodor, just mini __[••]__

Congratulations for receiving Komodor home assignment!

If you made it this far, it means we're curious, and would love to see your code.

For this exercise we've created a miniature version of Komodor, in which __you__ will implement a key component of Komodor.

This exercise will give you a sense of development at Komodor, and we hope you will find it enjoyable.

## Background
Komodor's system consists of three main components:
1. Komodor agent - a stable, efficient process that watches for updates in Kubernetes resources and routes them to Komodor server
2. Komodor server - a highly-available, scalable backend that gets information from Komodor agent, and organizes it so it can be later visible through Komodor app
3. Komodor app - a user-friendly web application that is loved by hundreds of developers and dev-ops engineers

In this exercise you will implement a simplified version of the Komodor server, __Minikom__.

We have already included a very simplified version of the Komodor agent, __Komobox__.

### How Komobox works
* In our environment, which Komobox monitors, we have a few services. At any certain point, each service can be in exactly one state: `idle`, `deploy` or `issue`.
* While a service is in a state of `deploy` or `issue`, Komobox will attempt every second to send an event to Minikom with the current state.
* While a service is in a state of `idle`, Komobox won't send anything about the service.
* Komobox might send events in a small delay (up to 10 seconds) and does not guarantee the order of the events.
* Komobox code is given to you for reference. The basic terms of event delay and order cannot be changed.

## Getting started
1. Fork this repository
2. Clone your fork to your dev machine
3. Run `docker compose up` to confirm your runtime works (see [docker compose](https://docs.docker.com/compose/))

## Instructions
You need to implement Minikom, an HTTP server that accepts events from Komobox, and exposes the endpoints below.  

```yaml
# Accept a single event from Komobox
Method: POST
Endpoint: /event
Request type: JSON object
Request structure: {
  "service_name": string
  "state": "deploy" or "issue"
  "timestamp": number (unix time) # the time the event took place at the source
}
Response: 200 OK # No body
```

```yaml
# List all services that have been seen by Minikom so far
Method: GET
Endpoint: /services
Response type: JSON object
Response structure: {
  <service_name>: {
    state: "idle" or "deploy" or "issue" # latest state of the service
    since: number (unix time) # the time the latest state started
  }
}
```

```yaml
# List latest events (max: 50) for service
Method: GET
Endpoint: /services/<service_name>/latest-events
Response type: JSON array
Response structure: [{ # element per event
   state: "deploy" or "issue" # the state type (idle should not be included)
   start_time: number (unix time) # the time the state started
   end_time: number (unix time) or null # the time the state ended (null if still ongoing)
}]
```

### Notes
1. You may implement the server in Python, Javascript, or Typescript
1. Minikom should be accessible to Komobox via docker compose
1. We should be able to run the entire system just by running `docker compose up`
1. The server should be exposed to the local machine on port `8080`
1. Please include system tests with your solution, with instructions how to run them

Good luck!  
Komodor __[••]__