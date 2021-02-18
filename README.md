# cykel-ttn
A The Things Network adapter for sending bike positions to [cykel](https://github.com/stadtulm/cykel). This is the adapter for GPS based trackers. For wifi based trackers use [cykel-ttn-wifi](https://github.com/stadtulm/cykel-ttn-wifi).

This adapter is now only compatible with the TheThingsNetwork v3 Stack.

## Prerequisites

* Python (≥3.7)

## Installation

Install the required packages using `pip install -r requirements.txt`. It is recommended to use a virtualenv with your choice of tool, e.g. `pipenv`, in which case you can run `pipenv install` (and `pipenv shell` or prefix `pipenv run` to run commands).

## Decoder
To use the cykel-ttn adapter you need to bring the incoming bytes from your lora device into a readable format. The TTN Console supports decoders/converters and validators for this use case. Look into the [tracker-ttn-decoders](https://github.com/stadtulm/tracker-ttn-decoders) repository to find javascript, which you can use as decoder function.

Visit `https://eu1.cloud.thethings.network/console/applications/<application id>/payload-formatters/uplink` to set the *Payload Format* for *Uplink* to *Javascript* and enter the decoder function there.

## Configuration

cykel-ttn is configured with environment variables. You may want to create a `.env` file, which you can `source .env` before running cykel-ttn.

The following envionment variables are needed:
```
export TTN_HOST="<public host:port address from the ttn integration/mqtt page>"
export TTN_USERNAME="<username@tenant from the ttn integration/mqtt page>"
export TTN_API_KEY="<a fresh ttn api key>"
export ENDPOINT="https://<your cykel host>/api/bike/updatelocation"
export ENDPOINT_AUTH_HEADER="Api-Key <your api key for cykel>"
export PORT=8081
```

You can create the *ttn api key* on the ttn console, the only needed right is `Read application traffic (uplink and downlink)`.

For the cykel API Key (`ENDPOINT_AUTH_HEADER`), visit your cykel administrative interface and create a new API key.

## Run it

(load your virtualenv, if you have one)

`python3 app.py`

## Metrics

On your configured port (env `PORT`) cykel-ttn serves metrics at `/metrics` in the [Prometheus Text-based format](https://prometheus.io/docs/instrumenting/exposition_formats/). You may use this to build monitoring and alerting for your devices.
