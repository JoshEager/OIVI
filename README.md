# OIVI is the Easiest Way to Self Host your own Obsidian Sync
[Obsidian Sync](https://obsidian.md/sync) is great, but it's a monthly subscription. If you already self host things, you can get the same "edit on my PC, see it on my phone" experience for free with the community plugin [Self-hosted LiveSync](https://github.com/vrtmrz/obsidian-livesync). The catch is that LiveSync needs a CouchDB server, and that server needs to be reachable from your phone over HTTPS, which normally means exposing it to the public internet and dealing with certificates.

OIVI ("Obsidian In Vault, Instantly") handles all of that for you. It runs CouchDB preconfigured for LiveSync, and puts it behind a [tailscale](https://tailscale.com) container so it's only reachable from your own devices, with a real HTTPS certificate, and without opening a single port on your router.

# Quick Start

## Tailscale Setup
To get started, the first thing you need to do is create a free [tailscale](https://tailscale.com) account if you don't already have one. Follow the guide that they have and add your personal computer to your tailnet, as well as your phone and any other device you want your vault synced to.

Then, you need to generate an auth key. We will use this later in the setup. To do this, go to your [admin dashboard](https://console.tailscale.com) and click Settings>Keys>Generate Auth Key. Add a description and leave everything else default (unless you know what you're doing). Then simply copy the key it generates to your clipboard. Make sure not to lose this key from your clipboard as you won't be able to see it again. If you don't already have clipboard history on, I would recommend turning it on before copying this. If you don't want to do that, you can simply paste it into a text file to be safe.

You *must* **enable https on your tailnet**. Obsidian (especially on phones) will refuse to talk to a sync server that isn't using https. You can do that by going to your [admin dashboard](https://console.tailscale.com) and clicking Settings>General>Https>Enable https

You should also make sure that MagicDNS is enabled for your tailnet. It's on by default for new tailnets, and it's what lets your devices find the server at a nice name like `obsidian.<your tailnet>.ts.net`. You can find your tailnet's name on the DNS page of the admin dashboard.

## Docker Setup
If you don't already have docker installed on whatever machine you are planning on running this stack from, make sure you do that. A convenient guide can be found [here](https://docs.docker.com/engine/install/). You will also need docker compose. For installing docker compose, you can follow the guide [here](https://docs.docker.com/compose/install/) for your platform.

## Project Setup
All you need to do to setup this project is clone this repository and run setup.py
```bash
git clone https://github.com/JoshEager/OIVI.git && cd OIVI
```
```bash
python setup.py
```
The script will ask for your tailscale auth key. Please note that it will not show up when you type (or paste) for security reasons. It will also ask for a project name (anything lowercase, like `oivi`), a tailscale hostname (just press enter to use `obsidian`) and a CouchDB username (just press enter to use `obsidian`).

At the end, the script prints your **CouchDB username and password**. Copy these somewhere, you'll need them in a minute to set up the plugin. If you lose them, don't worry, they're stored in the `.env` file in the project folder.

After running the setup script, all you need to do is run the following command, and your server should be available at `https://obsidian.<your tailnet>.ts.net` (or whatever hostname you picked)
```bash
docker compose up -d
```
The first start can take a minute while tailscale gets its https certificate. If you open that address in a browser on a device that's on your tailnet, you should get a login popup. That means everything is working!

> **Note for Linux users:** CouchDB runs as user id 5984 inside its container, so after the first start you'll see that `couchdb/data` is owned by user 5984 on your machine. That's expected. The container fixes the permissions itself every time it starts, so you don't need to touch it.

## Setting up Self-hosted LiveSync in Obsidian
Set things up on your **PC first**, and then copy the settings over to your phone.

### On your PC
1. In Obsidian, go to Settings>Community plugins, search for **Self-hosted LiveSync**, install it, and enable it.
2. Open the plugin's settings and go to the remote database (CouchDB) configuration. Fill it in like this:
   - **Server URI**: `https://obsidian.<your tailnet>.ts.net` (no port, no trailing slash)
   - **Username**: the CouchDB username from the setup script
   - **Password**: the CouchDB password from the setup script
   - **Database name**: anything lowercase, for example `obsidian`. The plugin will create it for you. Use a different database name for each vault you want to sync.
3. Use the plugin's button to test the connection / check the database configuration. OIVI already configures CouchDB the way LiveSync wants, so everything should come back green.
4. I highly recommend turning on **end-to-end encryption** and picking a passphrase. Your data never leaves your tailnet anyway, but with encryption on, even the database on your server only ever sees scrambled data. Don't lose the passphrase, you'll need it on every device.
5. Pick a sync mode (LiveSync is the most "magic" one) and let it do its first sync.

### On your phone
The easiest way to get the exact same settings onto your phone is the plugin's **setup URI** feature. On your PC, open the command palette and run the LiveSync command to copy your current settings as a setup URI. It will ask you for a passphrase to protect the URI. Then get that URI to your phone (a note to yourself works), install Obsidian and the Self-hosted LiveSync plugin on your phone, and use the plugin's option to open/use a setup URI. Paste it in, enter the passphrase, and you're done.

You can also just type the same settings in by hand if you prefer.

**Remember:** the tailscale app must be installed and **connected** on your phone for syncing to work. If tailscale is off, your phone can't see the server, and LiveSync will just wait until it can.

# Troubleshooting
## TLS / certificate errors
This almost always means https isn't enabled on your tailnet. Go to your [admin dashboard](https://console.tailscale.com), click Settings>General>Https>Enable https, then restart the stack with `docker compose restart`. Also make sure you're using the full `https://<hostname>.<your tailnet>.ts.net` address and not an IP address, since the certificate is only valid for the name.

## CORS errors
OIVI's CORS settings live in `couchdb/config/livesync.ini` and allow the Obsidian desktop app and the Obsidian mobile apps. If you've changed that file, run `docker compose restart couchdb` so CouchDB picks up the change. Also double check your server URI doesn't have a trailing slash or a port on it.

## The server doesn't show up in the tailscale admin console
Check the tailscale container's logs with `docker compose logs tailscale`. Usually it's a typo in the auth key. You can fix the key in `.env` and run `docker compose up -d` again.

## Expired auth key
Tailscale auth keys expire (90 days by default), but that only matters the *first* time the server joins your tailnet. After that, it's remembered in `tailscale/state`. If you get an expired key error, generate a new key in the admin dashboard, put it in `.env` as `TS_AUTHKEY`, and run `docker compose up -d`. You may also want to disable key expiry for the `obsidian` machine in the admin console so it never gets logged out.

# License
The MIT License (MIT)

Copyright (c) 2026 Josh Eager

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
