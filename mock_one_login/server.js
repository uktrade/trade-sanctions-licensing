/* eslint-disable no-console */

const assert = require('assert');
const camelCase = require('camelcase');

const Provider = require('oidc-provider');
const configLoader = require("./configLoader");


const host = process.env.HOST || 'localhost';
const port = process.env.PORT || 3000;

const config = ['CLIENT_ID', 'CLIENT_SECRET', 'CLIENT_REDIRECT_URI', 'CLIENT_LOGOUT_REDIRECT_URI'].reduce((acc, v) => {
    assert(process.env[v], `${v} config missing`);
    acc[camelCase(v)] = process.env[v];
    return acc;
}, {});

const people_config = configLoader.getConfig('./mock-people.yaml');


const oidcConfig = {
    features: {
        devInteractions: true,
        discovery: true,
        registration: false,
        revocation: true,
        sessionManagement: false
    },
    format: {
        default: 'jwt',
            AccessToken: 'jwt',
            RefreshToken: 'jwt'
    },
    claims: {
        acr: null,
        sid: null,
        auth_time: null,
        iss: null,
        openid: ['sub', 'name', 'email']
    },
    findById: function (ctx, id) {
        console.log("findById called with id ", id)
        if (people_config.people[id]) {
            let person = people_config.people[id];
            return {
                accountId: id,
                async claims(use, scope) {
                    return {
                        sub: id,
                        name: person.name,
                        email: person.email,
                    };
                },
            };
        }
    }
};

const oidc = new Provider(`http://${host}:${port}`, oidcConfig);

const clients = [
    {
        client_id: config.clientId,
        client_secret: config.clientSecret,
        redirect_uris: [config.clientRedirectUri],
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
];

let server;
(async () => {
    await oidc.initialize({clients});
    console.log("starting server with config ", config)
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
