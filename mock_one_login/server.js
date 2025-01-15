/* eslint-disable no-console */

import assert from 'assert'
import camelCase from 'camelcase'

import Provider from 'oidc-provider'

import fs from "fs"
import yaml from "js-yaml"

import wildcard from 'wildcard';
import psl from 'psl';

function getConfig(configSource) {
    const config = _getData(configSource);
    console.log(`Loaded config with ${config.people.length} people`);
    return config;
}

function _getData(configSource) {
    const data = fs.readFileSync(configSource).toString();
    if (configSource.endsWith(".yaml") || configSource.endsWith(".yml"))
        return yaml.safeLoad(data);
    else return JSON.parse(data);
}


const host = process.env.HOST || 'localhost';
const port = process.env.PORT || 3000;

const config = ['CLIENT_ID', 'CLIENT_SECRET', 'CLIENT_REDIRECT_URI', 'CLIENT_LOGOUT_REDIRECT_URI', 'DJANGO_SERVER_PORT'].reduce((acc, v) => {
    assert(process.env[v], `${v} config missing`);
    acc[camelCase(v)] = process.env[v];
    return acc;
}, {});

const people_config = getConfig('./mock-people.yaml');

// Generate a bunch of redirect URIs from 50000-60000 and the actual one to take into account the DjangoLiveServerTestCase potential ports
let redirect_uris = []
var i = 50000, max = 60000;
while (i < max) {
    let new_uri = config.clientRedirectUri.replace("{port}", i)
    redirect_uris.push(new_uri)
    i++
}

let actual_uri = config.clientRedirectUri.replace("{port}", config.djangoServerPort)
redirect_uris.push(actual_uri)

let clients = [
    {
        client_id: config.clientId,
        client_secret: config.clientSecret,
        redirect_uris: redirect_uris,
        post_logout_redirect_uris: [config.clientLogoutRedirectUri],
        token_endpoint_auth_method: 'private_key_jwt',
        jwks: {
            keys: [
                {
                    alg: 'RS256',
                    n: 'xwQ72P9z9OYshiQ-ntDYaPnnfwG6u9JAdLMZ5o0dmjlcyrvwQRdoFIKPnO65Q8mh6F_LDSxjxa2Yzo_wdjhbPZLjfUJXgCzm54cClXzT5twzo7lzoAfaJlkTsoZc2HFWqmcri0BuzmTFLZx2Q7wYBm0pXHmQKF0V-C1O6NWfd4mfBhbM-I1tHYSpAMgarSm22WDMDx-WWI7TEzy2QhaBVaENW9BKaKkJklocAZCxk18WhR0fckIGiWiSM5FcU1PY2jfGsTmX505Ub7P5Dz75Ygqrutd5tFrcqyPAtPTFDk8X1InxkkUwpP3nFU5o50DGhwQolGYKPGtQ-ZtmbOfcWQ',
                    e: 'AQAB',
                    kid: 'keystore-CHANGE-ME',
                    kty: 'RSA',
                    use: 'sig',
                },
            ],
        }
    }
]
console.log(clients)

const oidcConfig = {
    features: {
        devInteractions: {enabled: true},
        registration: {enabled: false},
        revocation: {enabled: true},
    },
    format: {
        default: 'jwt',
            AccessToken: 'jwt',
            RefreshToken: 'jwt'
    },
    pkce: {
        required: function () {
            return false
        }
    },
    claims: {
        acr: null,
        sid: null,
        auth_time: null,
        iss: null,
        openid: ['sub', 'name', 'email']
    },
    findAccount: function (ctx, sub, token) {
        console.log("findAccount called with id ", sub)
        if (people_config.people[sub]) {
            let person = people_config.people[sub];
            return {
                accountId: sub,
                async claims(use, scope) {
                    return {
                        sub: sub,
                        name: person.name,
                        email: person.email,
                    };
                },
            };
        }
    },
    clients: clients,
};

const oidc = new Provider(`http://${host}:${port}`, oidcConfig);

let server;
(async () => {
    server = oidc.listen(port, () => {
        console.log(
            `mock-oidc-user-server listening on port ${port}, check http://${host}:${port}/.well-known/openid-configuration`
        );
    });
})().catch(err => {
    if (server && server.listening) server.close();
    console.error(err);
    process.exitCode = 1;
});
