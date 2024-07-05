# Cloud Sync

Cloud Sync supports automated account provisioning via an Azure automate script that connects Azure AD and Exchange Online with our SCIM endpoint.

The script performs the following:

-   Connects to Exchange Online via on the basis of System Managed Identities.
-   Connects to Zivver via the SCIM endpoint
-   Performs a synchronization between EXO accounts as the source of truth and disables/creates/updates accounts inside of Zivver.

Uses variables (encrypted API key and filter values) that can be set up in the beginning in the Azure Automate environment

### Setup

For developing new features, you first need to install the dependencies.

Its highly [recommend using Pyenv](https://github.com/pyenv/pyenv) to manage the global
python interpreters too, if this is your first time with Python dev. To install and set your python version to the one required type:

```sh
pyenv install 3.8
pyenv global 3.8
```

To begin you will need [Poetry](https://python-poetry.org/docs/) to install all the dependencies required. You can achieve so by running the following two commands.

```sh
pip install poetry
poetry install
```

### Setting up a QA environment (aka Ephemeral environment)

To setup a QA environment, go on this dashboard and create a new environment.
After creation, do the following steps:

- Connect as an admin to the environment and setup SSO.
  Just go in the organization admin panel (in the webapp), and add the following SSO url:
  ```
  https://zivver.okta.com/app/exk4jarz1mESRkc6x356/sso/saml/metadata
  ```
  Read this backend doc for more info: https://gitlab.zivver.org/zivver/zivver-backend#setting-up-local-sso
- Claim the Microsoft test environment domain on the QA env:
  To do so, go in the organization admin panel (in the webapp), and in the "Domains" section, add the following domain:
  ```
  zivvertest.onmicrosoft.com
  ```
  then, open the Mailpit UI (the link is in the QA environment dashboard) and you should see the confirmation email.
  Use the code in the confirmation email to claim the domain in the webapp.

Finally, in the QA environment dashboard, you will find the following information:
- The URL to the backend api, something like this:
  ```
  API URL (for SyncTool or ZOFP): https://cloud-sync-ftw.qa.zivver.org:8080/api
  ```
- The API key for accessing the SCIM endpoints, something like this:
  ```
  API key for the synctool:
  Z1.1.2.Ge-xEEMkK83753SyolWaVsS8_ANMHlzc1Jo4p8aAuFKKpohUvjWhTI0Uy_q1Mh_wtJ1l_AnxLMr2XilLtv4fZXJNTH2niPGYXwnxky_geaV7-ELdBHRJVMUz4WDsrloqQSLTOeNtUXA7vNUTihh6ihR-FM97Arz2eQvn8lf_WUcVcRcb__auTzeNMhFJYmjyXTk3YR8Bj3eifUDR4MadQVDLnrj86BEEmKocCJ71wundkmae3roMnzKBOw
  ```
Put the API key in the `.env` file in the root of the repo, and unset the env var in your shell just in case.

### Getting an EXO access token

To run CloudSync you require an access token retrieved from EXO. To retrieve this access token follow the following steps:
- Connect to https://portal.azure.com/#home with your test Microsoft account.
- Access the Automation Accounts section.
- Access the "account-provisioning" account.
- Search for the "Runbooks" section in the left column search bar.
- Open the `get_access_token` Python runbook.
- In the "Recent Jobs" section, there should be a run from 9:00 am this morning. If not, start a new "task" of the runbook manually.
- Once in the run, go to "All Logs" section, and click the row starting with `eyJ0...`
- Copy the whole token, and paste it in the `.env` file in the `CLOUD_SYNC__ACCESS_TOKEN` environment variable.

Repeat steps tomorrow, since the token expires after 24hrs. Think of automating? Don't. Not worth your time.

Once you have the access key, and also get a zivver api key, copy the .env.template file inside the root of the repo,
and replace the environment variable `CLOUD_SYNC__ACCESS_TOKEN` with the EXO access token and `CLOUD_SYNC__ZIVVER_API_KEY` with the zivver api key. Afterwardds you are able
to run the application with the following command:

```
poe run
```

### Property links between data sources

This links names of things between SCIM, Zivver, and Exchange Online, and ofc Cloud Sync.

<table><thead>
  <tr>
    <th>Zivver Backend</th>
    <th>SCIM Group</th>
    <th>SCIM User</th>
    <th>Exchange SharedMailbox</th>
    <th>Exchange UserMailbox</th>
  </tr></thead>
<tbody>
  <tr>
    <td>Principal</td>
    <td>externalId</td>
    <td>userName</td>
    <td>PrimarySmtpAddress</td>
    <td>PrimarySmtpAddress</td>
  </tr>
  <tr>
    <td>Full Name</td>
    <td>displayName</td>
    <td>name > formated</td>
    <td>DisplayName</td>
    <td>DisplayName</td>
  </tr>
  <tr>
    <td>Status</td>
    <td>len(members) > 0 </td>
    <td>active</td>
    <td>AccountDisabled</td>
    <td>AccountDisabled</td>
  </tr>
  <tr>
    <td>Aliases</td>
    <td>aliases</td>
    <td>urn:ietf:params:scim:schemas:zivver:0.1:User > aliases</td>
    <td>$_.EmailAddresses, only smtp-addresses (SMTP in capital is the primary?)</td>
    <td>$_.EmailAddresses, only smtp-addresses (SMTP in capital is the primary?)</td>
  </tr>
  <tr>
    <td>Delegations</td>
    <td>members</td>
    <td>urn:ietf:params:scim:schemas:zivver:0.1:User > delegates</td>
    <td>Generated From Mailbox Permissions</td>
    <td>Generated From Mailbox Permissions</td>
  </tr>
  <tr>
    <td>SSO Account Key</td>
    <td>not returned because secrets</td>
    <td>not returned because secrets</td>
    <td>Not Set</td>
    <td>ExternalDirectoryObjectId</td>
  </tr>
</tbody></table>

## Implementation edge cases

### Disabling a functional account (aka group)

We can't. So instead, we declare that a group with no members is "disabled". 
- When we read, if the group has no other members,
  we declare it disabled.
- When we write, when we see that a group should be disabled, we empty the list of members. 


# Try out the loader script

To try the loader script, do the following:

## 0. Make sure your .env file is set up and working

You need to have correct access tokens and API keys in your `.env` file to begin with.

## 1. Build the cloudsync wheel

Go to the root of the cloudsync repo and run the following command:

```sh
poetry build --format=wheel
```

## 2. Start a web server to serve the wheel file to the loader script

Go to the `dist` folder at the root of the repo, and start a web server 
to serve the wheel file:

```sh
# cd dist
python3 -m http.server 8080
```

## 3. Run the loader script inside Docker

To simulate the loader script downloading an running the cloudsync wheel in a completely 
blank environment (similar to Azure Automate VM), we use Docker's python3.8 image.

To run the loader script, navigate to the root of the repo, and run the following command:

```sh
docker run \
    --rm \
    --env-file ./.env \
    -v ./loader.py:/loader.py \
    -it python:3.8 \
    /usr/local/bin/python loader.py
```

Whenever you edit cloudsync, remember to run the `poetry build --format=wheel` 
command again, to update the wheel file. Then you can rerun the loader.