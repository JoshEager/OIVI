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
The order matters here:
1. Your **PC** is set up by hand, using the plugin's onboarding wizard. This also fills your empty database with your vault.
2. Then your PC **generates a Setup URI** (a link that starts with `obsidian://setuplivesync`). It contains all your settings, locked with a passphrase.
3. Your **phone** uses that Setup URI, so you never have to type the settings in on a tiny keyboard.


Before you start, two quick warnings:
- **Back up your vault** (just copy the folder somewhere). The first sync is a big operation and a backup costs you nothing.
- If this vault is already synced some other way (Obsidian Sync, iCloud, OneDrive, etc.), turn that off for this vault. Two sync tools fighting over the same files is a recipe for duplicates.

You're going to end up with three different secrets, so it helps to know which is which up front:
| Secret | Where it comes from | What it's for |
| --- | --- | --- |
| CouchDB password | Printed by `setup.py` (also in `.env`) | Logging in to your server |
| Encryption passphrase | You make it up during the wizard | Encrypting your notes. **Every device needs it, and if you lose it your synced data is unreadable** |
| Setup URI passphrase | You make it up when you create the Setup URI | Unlocking the Setup URI on your phone. Only needed once |

Use a different one for each. A password manager is perfect for keeping track of them.

> The button names below come from the plugin's own [quick setup guide](https://github.com/vrtmrz/obsidian-livesync/blob/main/docs/quick_setup.md). The plugin changes fairly often, so if a label is slightly different in your version, pick whatever is closest.

### Step 1: Set up your PC
1. In Obsidian, go to Settings>Community plugins>Browse, search for **Self-hosted LiveSync**, install it, and enable it.
2. A "Welcome to Self-hosted LiveSync" notice pops up. Click it. If you already closed it, go to the plugin's settings and click **Rerun Onboarding Wizard** under Quick Setup.
3. Choose **I am setting this up for the first time**, and confirm that you want to set up a new synchronisation.
4. On "Connection Method", choose **Configure a remote manually**, then **Proceed with manual configuration**.
5. On "End-to-End Encryption", turn on **End-to-End Encryption** and type in your **encryption passphrase**. I highly recommend this. Your data never leaves your tailnet anyway, but with encryption on, even the database on your own server only ever sees scrambled data. Save this passphrase somewhere safe *now*.
6. On "Choose a synchronisation remote", choose **CouchDB**, then **Continue to CouchDB setup**.
7. Fill in the connection details:
   - **Server URI**: `https://obsidian.<your tailnet>.ts.net` (use your hostname if you changed it, and no port or trailing slash)
   - **Username**: the CouchDB username from `setup.py` (`obsidian` unless you changed it)
   - **Password**: the CouchDB password from `setup.py`
   - **Database Name**: anything lowercase, for example `obsidian`. The plugin creates it for you. Use a different database name for each vault you want to sync.
8. You can click **Check server requirements** if you want to. OIVI already configures CouchDB the way LiveSync wants, so everything should come back fine and you shouldn't need any of the fixes it offers.
9. Click **Create or connect to database and continue**. This tests the connection, and the wizard won't let you continue until it works. If it fails, jump to [Troubleshooting](#troubleshooting).
10. Click **Restart and Initialise Server**. You'll get a scary warning about overwriting the server. That's expected here, since your database is brand new and your PC is the source of truth. Click **I Understand, Overwrite Server**.
11. If it says "No Synchronisation Settings Found", click **Use this device's settings**. That just means the database is new.
12. Acknowledge the message about optional features being disabled, then **leave Obsidian open** until the progress indicators in the corner go away. For a big vault, this can take a while.
13. Finally, pick how you want to sync. Go to the plugin settings>Sync Settings and set **Sync Mode** to **LiveSync**. That syncs changes in real time, as you type.

Make a quick test note so you can check that the phone gets it later.

### Step 2: Create a Setup URI on your PC
1. Open the command palette (Ctrl+P) and run **Self-hosted LiveSync: Copy settings as a new Setup URI**.
2. Make up a **Setup URI passphrase** and click OK. This is *not* your encryption passphrase. It only protects the link.
3. If it asks about "Setup URI availability", the default **Time-bound** option is fine. The link expires within a week, which is a good thing since it contains your server password. You can always make a new one.
4. The Setup URI is now copied to your clipboard. Get it to your phone somehow, like a note to yourself in an app you trust. Don't post it anywhere public. It's encrypted, but it does contain your login.

### Step 3: Set up your phone
1. Install the **Tailscale** app, sign in, and make sure it's **connected**. Your phone can't reach the server without it. If you want, open `https://obsidian.<your tailnet>.ts.net` in your phone's browser. A login popup means the phone can see the server.
2. Install Obsidian and create a new, **empty** vault. Don't turn on iCloud sync for it.
3. Go to Settings>Community plugins, then install and enable **Self-hosted LiveSync**.
4. Click the "Welcome to Self-hosted LiveSync" notice (or **Rerun Onboarding Wizard** in the plugin settings).
5. Choose **I am adding a device to an existing synchronisation setup** and confirm.
6. On "Device Setup Method", choose **Use a Setup URI (Recommended)**.
7. Paste the Setup URI, type your **Setup URI passphrase**, and click **Test Settings and Continue**. 
8. Click **Restart and Fetch Data**. When it asks what to do with files, choose **Overwrite all with remote files**. That's safe because the phone's vault is empty.
9. Keep Obsidian open until everything has downloaded. Your test note should show up. Edit a note on your phone and check that the change appears on your PC.

That's it! Any other device (a laptop, a tablet) works exactly like the phone: make a new Setup URI on a device that already syncs, then follow Step 3.

**Remember:** the Tailscale app must be **connected** on your phone for syncing to work. If Tailscale is off, your phone can't see the server, and LiveSync will catch up once it can.

# Troubleshooting
## TLS / certificate errors
This almost always means https isn't enabled on your tailnet. Go to your [admin dashboard](https://console.tailscale.com), click Settings>General>Https>Enable https, then restart the stack with `docker compose restart`. Also make sure you're using the full `https://<hostname>.<your tailnet>.ts.net` address and not an IP address, since the certificate is only valid for the name.

## CORS errors
OIVI's CORS settings live in `couchdb/config/livesync.ini` and allow the Obsidian desktop app and the Obsidian mobile apps. If you've changed that file, run `docker compose restart couchdb` so CouchDB picks up the change. Also double check your server URI doesn't have a trailing slash or a port on it.

## The server doesn't show up in the tailscale admin console
Check the tailscale container's logs with `docker compose logs tailscale`. Usually it's a typo in the auth key. You can fix the key in `.env` and run `docker compose up -d` again.

## The Setup URI doesn't work on my phone
Make sure you're typing the **Setup URI passphrase** (the one you made up in Step 2), not your encryption passphrase or the CouchDB password. If it says the URI has expired, or you just can't remember the passphrase, run **Copy settings as a new Setup URI** on your PC again to make a fresh one.

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
